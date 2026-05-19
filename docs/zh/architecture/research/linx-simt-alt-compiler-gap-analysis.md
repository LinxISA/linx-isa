# Alt-编译器 SIMT ASM 差距分析

## 总结

本文分析了 `/Users/zhoubot/linx-simt.s` 中的替代编译器输出：

- `/Users/zhoubot/linx-simt.c` 中的源意图
- 规范的 `v0.56` ISA 手册
- `compiler/llvm/llvm/lib/Target/ZXTERMEN40QXZ/ZXTERMEN40QXZSIMTAutoVectorize.cpp` 中当前的 LLVM 灵犀 SIMT 降低
- `emulator/qemu/target/linx/translate.c` 中的当前 QEMU 灵犀 向量-块体 执行模型

主要结果是，有趣的差距大多不是原始操作码的缺失。生成的程序集已使用大量现有的 向量/SIMT 表单。真正的差距在于围绕通道分组、发散、再收敛、通道本地状态的架构 SIMT 合约，以及使这些形式组成强大的 GPU 风格的 执行模型 所需的编译器/运行时模型。

## 工作负载形状

`/Users/zhoubot/linx-simt.c` 中的源代码是真实 SIMT 模型的良好应力情况：

- 每线程跨步迭代：
  `tid = thread_idx + thread_num * block_idx`，然后 `hashtable_insert` (`/Users/zhoubot/linx-simt.c:66-67`) 中的 `tid += thread_num * block_num` 和 `block_base_idx += thread_num * block_num` 加上 `callee` (`/Users/zhoubot/linx-simt.c:148-152`) 中的 `tid = block_base_idx + thread_idx`。
- 哈希和模重地址生成：
  `curr_slot = b % capacity` 和 `(curr_slot + 1) % capacity`（`/Users/zhoubot/linx-simt.c:97-99`、`/Users/zhoubot/linx-simt.c:120-123`、`/Users/zhoubot/linx-simt.c:183-185`、`/Users/zhoubot/linx-simt.c:206-208`）。
- 发散的数据相关循环退出：
  `while (true)` 与早期的 `break` 位于空槽、找到的钥匙或完整探头（`/Users/zhoubot/linx-simt.c:103-124`、`/Users/zhoubot/linx-simt.c:187-209`）上。
- 混合 标量 和每通道内存活动：
  标量 围绕 `capacity`、`entry_size` 进行设置，并导入指针，但每个线程的键/值查找和分散的槽流量。生成的装配体保留该形状。它通过 `BSTART.MPAR VS16`、`B.DIM zero, 1024, ->lb0` 和 `B.TEXT` (`/Users/zhoubot/linx-simt.s:48-55`) 启动，然后将 块体 降低为以下组合：

- 向量 ALU（`v.mul`、`v.srli`、`v.xor`、`v.rem`）（`/Users/zhoubot/linx-simt.s:110-149`）
- 向量 存储器（`v.ld`、`v.sw`、`v.sdi.u.local`、`v.lwi.u.local`）（`/Users/zhoubot/linx-simt.s:100-107`、`/Users/zhoubot/linx-simt.s:178-184`、`/Users/zhoubot/linx-simt.s:208-210`、`/Users/zhoubot/linx-simt.s:239-244`）
- 屏蔽/选择操作（`v.cmp.* ->p`、`v.psel`）（`/Users/zhoubot/linx-simt.s:68-71`、`/Users/zhoubot/linx-simt.s:154-173`、`/Users/zhoubot/linx-simt.s:184-191`）
- 标量 在 向量 块体 内部分支和跳转（`/Users/zhoubot/linx-simt.s:71-72`、`/Users/zhoubot/linx-simt.s:95-96`、`/Users/zhoubot/linx-simt.s:173-174`、`/Users/zhoubot/linx-simt.s:191-192`、`/Users/zhoubot/linx-simt.s:233-234`）

## 无间隙/已覆盖

这些并不是主要的缺失部分：

- `BSTART.MPAR`、`B.DIM` 和 `B.TEXT` 已作为一流 SIMT 块头/块体 机械存在于规范手册中（`docs/architecture/isa-manual/src/chapters/04_block_isa.adoc:498-532`、`docs/architecture/isa-manual/src/chapters/08_tile_blocks.adoc:40-50`）。
- `p` 已经是定义的内核 EXEC 掩码，与块控制谓词状态 (`docs/architecture/isa-manual/src/chapters/03_programming_model.adoc:107-119`) 不同。
- `.local` 向量 内存形式已经作为规范的图块本地访问 (`docs/architecture/isa-manual/src/chapters/04_block_isa.adoc:580-625`) 存在。
- asm 中出现的 `V.REM` 和 `V.PSEL` 本身并不是编码缺失的证据。更难的问题是他们周围的执行模型。
- QEMU 已经具有基本的解耦 SIMT 块体 模型，该模型进入 `B.TEXT` 块体 并通过 `LB/LC` 状态（`emulator/qemu/target/linx/translate.c:454-480`、`emulator/qemu/target/linx/translate.c:484-520`）重放它。

## 库存缺口

### 矢量 ISA 设计#### 差距 1：当前的 SIMT 模型是面向重放和组统一的，但此工作负载需要持续的每通道活跃度和发散进度- 分类：设计间隙
- 观察到的汇编证据：
  - 块体 充满了数据相关的退出和重新进入点：`b.ne` / `j` 将 块体 分成许多内部块（`/Users/zhoubot/linx-simt.s:71-72`、`/Users/zhoubot/linx-simt.s:95-96`、`/Users/zhoubot/linx-simt.s:173-174`、`/Users/zhoubot/linx-simt.s:191-192`、 `/Users/zhoubot/linx-simt.s:233-234`）。
  - 编译器在 `v.psel`、重复的 `v.cmp.* ->p` 和许多 `.local` 溢出/重新加载（`/Users/zhoubot/linx-simt.s:154-173`、`/Users/zhoubot/linx-simt.s:178-210`、`/Users/zhoubot/linx-simt.s:239-257`）的拆分中保持通道状态处于活动状态。
- 当前规范设计：
  - `v0.56` 手册为每组定义了一个 标量 统一控制流上下文以及 EXEC 掩码 `p` (`docs/architecture/isa-manual/src/chapters/03_programming_model.adoc:121-167`)。
  - SIMT 主体被定义为通过 `lc0..lc2` 元组 (`docs/architecture/isa-manual/src/chapters/04_block_isa.adoc:500-521`) 重放的单通道主体。
- 为什么这是一个差距：
  - 该合同足以满足重播风格的 向量 循环。
  - 仅仅表达具有明确架构意义的 GPU 式“有些车道已完成，有些车道仍在探测”模型是不够的。
  - asm 被迫在模型内模拟持久通道进度，该模型仅显式命名组统一的 标量 PC 和掩码。
- 对编译器/QEMU/RTL的影响：
  - 编译器必须积极地从头开始进行 if 转换和合成通道状态。
  - QEMU 可以重播 块体，但它没有要执行的每通道连续状态的架构概念。
  - RTL 必须猜测预期的机器是“仅重放”还是“部分完成的车道扭曲”。
- 推荐关闭方向：
  - 选择两个显式合约之一并使其架构化：- 预测优先 SIMT：将内核限制为结构化 if 转换形式，并表示超出掩码预测的每通道分歧超出范围，或者
    - 真正发散的 SIMT：添加一流的每通道或每子组延续/再收敛状态。
  - 不要将其保留为隐式编译器约定。

#### 差距 2：当前谓词模型（`BARG.CARG` 与 `p`）对于完整的 GPU 式发散和再收敛来说太弱- 分类：设计间隙
- 观察到的汇编证据：
  - 块体 反复将 向量 条件转换为 `p`，然后将 `p` 物化回 标量 临时条件，然后分支（`/Users/zhoubot/linx-simt.s:68-71`、`/Users/zhoubot/linx-simt.s:88-96`、`/Users/zhoubot/linx-simt.s:163-173`、`/Users/zhoubot/linx-simt.s:184-191`）。
  - 它还使用 `v.psel` 手动合并每通道状态 (`/Users/zhoubot/linx-simt.s:154-160`)。
- 当前规范设计：
  - `v0.56` 显式地将块控制谓词状态 (`BARG.CARG`) 与内核 EXEC 掩码 `p` (`docs/architecture/isa-manual/src/chapters/03_programming_model.adoc:109-119`) 分开。
  - `SETC.*` 不屏蔽 向量 通道； `V.CMP.* ->p`是规范的口罩生产商（`docs/architecture/isa-manual/src/chapters/04_block_isa.adoc:618-625`）。
- 为什么这是一个差距：
  - 当前模型提供了掩码寄存器，但没有提供用于发散执行的完整掩码控制代数。
  - 不存在以下一流的架构概念：
    - `any` / `all` / `none` 通过执行，
    - EXEC 子集的推送/弹出/保存/恢复，
    - 再汇聚点跟踪，
    - 在没有 标量izing 的情况下通过类似划痕的临时对象进行掩模分支。
  - asm 准确地显示了缺失的层。
- 对编译器/QEMU/RTL的影响：
  - 编译器必须将不同的条件转换为非明确架构的 标量ized 控制协议。
  - 仿真器和 RTL 仅当它们独立地重新发现相同的隐藏掩码协议时才能正确。
- 推荐关闭方向：
  - 定义一个小的规范 EXEC 控制子模型：
    -掩码查询操作（`any`、`all`、`none`）
    - 掩码保存/恢复或堆栈操作- 内部分支的显式收敛语义
  - 如果这对于 `v0.56` 来说太大，则编纂一个严格的仅预测子集并禁止像这样的代码形状从规范降低。

#### 差距 3：对于替代 SIMT 编译器未指定启动几何结构和组宽度- 分类：设计间隙
- 观察到的汇编证据：
  - 启动包装器使用 `BSTART.MPAR VS16` 和 `B.DIM zero, 1024, ->lb0`，并且没有可见的 `LB1` 设置 (`/Users/zhoubot/linx-simt.s:48-55`)。
  - 在 块体 内部，编译器使用 `lc1` 和 `lc0` 来重建逻辑索引（`/Users/zhoubot/linx-simt.s:62-67`、`/Users/zhoubot/linx-simt.s:77-87`）。
  - 这强烈表明隐式条带挖掘模型：1024 个逻辑线程被映射到 16 通道组，`lc1` 充当隐式组索引。
- 当前规范设计：
  - 当前的一维规范配置文件为 `LB0 = lane_count`、`LB1 = group_count`、`lc0 = lane index`、`lc1 = group index`（`docs/architecture/isa-manual/src/chapters/03_programming_model.adoc:159-167`、`docs/architecture/isa-manual/src/chapters/04_block_isa.adoc:517-521`）。
- 为什么这是一个差距：
  - asm 使用与当前规范合约不同的合约，或者至少是手册中未写出的更严格的解释。
  - 目前以下关系：
    - 块头 向量 尺寸 (`VS16`)
    - 逻辑线程计数（`1024`）
    - `LB0` / `LB1`
    - `lc0` / `lc1`
    - 物理组宽度
    不够明确，无法保证跨编译器的可移植性。
- 对编译器/QEMU/RTL的影响：
  - 替代编译器可以生成不兼容但表面上合法的内核。
  - QEMU 和 RTL 对于 块体 应执行多少次逻辑迭代以及 `lc1` 的含义可能存在分歧。
- 推荐关闭方向：
  - 添加明确的配置文件合同以启动露天采矿：
    - `VS*` 是物理宽度、逻辑宽度还是两者- `LB0`是否可以携带总逻辑线程而不是通道宽度
    - 当仅存在一个 `B.DIM` 时，如何导出 `lc1`
  - 需要规范降低才能发出：
    - 显式 `LB0 = lane_count`、`LB1 = group_count` 或
    - 一个新的 块头/profile 位，授权隐式剥离采矿。

### 编码/操作数模型

#### 间隙 4：操作数模型强制对逻辑上通道本地但控制流敏感的值进行过多的 标量-向量 穿梭- 分类：设计间隙
- 观察到的汇编证据：
  - 块体 充满了 `c.movr`、`l.ori`、`v.ori` 和 `p` 的 标量 化为 `t/u` 寄存器（`/Users/zhoubot/linx-simt.s:76-81`、`/Users/zhoubot/linx-simt.s:88-96`、 `/Users/zhoubot/linx-simt.s:164-173`、`/Users/zhoubot/linx-simt.s:211-217`、`/Users/zhoubot/linx-simt.s:245-257`）。
  - 这不仅仅是正常的 SSA 噪音。它是编译器支付操作数模型税来在 向量、掩码和 标量 控制域之间移动信息。
- 当前规范设计：
  - 标量统一指令在 `GPR`/`t/u`/`p` 中运行； 向量指令在`vt/vu/vm/vn`中运行；直接 `v.* -> ZXTERMEN44QXZ` 写入是非法的，除非减少或掩码生成形式 (`docs/architecture/isa-manual/src/chapters/03_programming_model.adoc:123-157`)。
  -向量指令必须通过`ri*`或允许的标量操作数导入标量值；在 `V.*` 形式中直接任意使用 标量 GPR 是非法的（`docs/architecture/isa-manual/src/chapters/04_block_isa.adoc:624-625`）。
- 为什么这是一个差距：
  - 当前的分割对于简单的 向量 算术来说是干净的。
  - 对于 SIMT 控制密集型程序来说，它的表达能力不够，其中通道局部值必须参与分支决策、phi 合并和循环进度簿记。
  - asm 显示编译器构建临时穿梭协议而不是使用一流的 ISA 结构。
- 对编译器/QEMU/RTL的影响：
  - 编译器生成冗长、脆弱的代码。
  - 仿真器/RTL 在掩模/标量/向量 切换方面面临的极端情况比 ISA 当前解释的要多。
- 推荐关闭方向：- 定义一小组一流的 SIMT 操作数域交叉：
    - 掩码到 标量 查询
    - 标量 具有显式语义的屏蔽广播
    - 可能是一个车道本地 标量 临时命名空间，或显式车道状态记录
  - 保持非 SIMT 向量 代码的当前干净分割，但停止通过通用 `movr`/`ori` 模式强制降低 SIMT 控制。

#### 差距 5：`.local` 存在，但编译器生成的通道本地暂存/溢出存储的架构含义未明确说明- 分类：设计间隙
- 观察到的汇编证据：
  - 块体 大量使用 `.local` 作为编译器簿记存储：
    - `v.sdi.u.local ... [to1, 1800]` (`/Users/zhoubot/linx-simt.s:100-105`)
    - `v.swi.u.local ... [to1, lc0<<2, 520]` (`/Users/zhoubot/linx-simt.s:178-183`)
    - `v.ldi.u.local ... [to1, lc0<<3, 776]` (`/Users/zhoubot/linx-simt.s:196-200`)
    - `v.lwi.u.local ... [to1, lc0<<2, 520]`（`/Users/zhoubot/linx-simt.s:208-210`、`/Users/zhoubot/linx-simt.s:244-245`）
  - 这些偏移量看起来像编译器生成的溢出槽或车道状态记录，而不是用户可见的切片有效负载。
- 当前规范设计：
  - `.local` 访问被描述为通过 `TA/TB/TC/TD/TO/TS` 的图块本地访问，受图块大小的限制； `TO/TS` 是输出/暂存底座 (`docs/architecture/isa-manual/src/chapters/04_block_isa.adoc:582-613`)。
- 为什么这是一个差距：
  - 手册说明了 `.local` 地址作为磁贴参考的含义。
  - 它没有定义使用 `.local` 作为每通道溢出、掩码堆栈、循环或 phi 分辨率存储的编译器 ABI。
  - asm 完全取决于未声明的合同。
- 对编译器/QEMU/RTL的影响：
  - 编译器没有对对齐、生命周期、别名或最小暂存占用空间的标准化保证。
  - 模拟器和 RTL 可以“正确地”实现 Tile 操作的 `.local`，但仍然不符合编译器生成的暂存期望。
- 推荐关闭方向：
  - 添加规范的 SIMT 临时合约：
    - 哪个图块基础是编译器暂存区域
    - 车道专用寻址公式
    - 对齐和尺寸规则
    - 暂存是按组还是按内核实例
    - 编译器溢出是否可能别名用户可见的 `.local` 访问
  - 如果意图是“TS 是编译器草稿”，请明确说明并定义 ABI。### 解码/执行模型

#### 差距 6：`B.TEXT` 定义了进入和终止，但不是 块体 内部的一流发散/重新加入协议- 分类：设计间隙
- 观察到的汇编证据：
  - 内核 块体 包含许多内部控制流区域和重复重新进入探测循环（`/Users/zhoubot/linx-simt.s:84-96`、`/Users/zhoubot/linx-simt.s:152-174`、`/Users/zhoubot/linx-simt.s:176-218`、`/Users/zhoubot/linx-simt.s:220-258`）。
- 当前规范设计：
  - 手册明确了`B.TEXT`进入合法性和终止条件（`docs/architecture/isa-manual/src/chapters/04_block_isa.adoc:523-532`、`docs/architecture/isa-manual/src/chapters/08_tile_blocks.adoc:40-50`）。
  - QEMU 通过输入 `cpu_ZXTERMEN46QXZ_tpc` 来镜像该模型，重播直到 `linx_vec_ZXTERMEN46QXZ_next`，然后返回到 块头 延续（`emulator/qemu/target/linx/translate.c:454-480`、`emulator/qemu/target/linx/translate.c:484-520`）。
- 为什么这是一个差距：
  - 指定进入和终止。
  - 部分活动车道的重新加入语义不是。
  - ISA 不清楚内部 块体 分支是否是：
    - 当前`p`下只有一个标量-uniform分支，
    - 请求拆分 EXEC 并稍后重新聚合，
    - 或者只是编译器管理的谓词，没有架构重新连接概念。
- 对编译器/QEMU/RTL的影响：
  - 编译器必须综合一个事实上的重新加入协议。
  - 仿真器/RTL 可以支持 块体 分支，但不知道当通道子集进展不同时架构意图是什么。
- 推荐关闭方向：
  - 使用一条显式语句扩展 `B.TEXT` SIMT 块体 合约：
    - “块体 控制流在当前 EXEC 下严格 标量 一致；不存在架构重新收敛”
    - 或“块体 控制流可以拆分 EXEC，架构提供重新收敛状态 X/Y/Z”。#### 差距 7：QEMU 当前的 向量-块体 模型是重播引擎，而不是 SIMT 控制状态问题的语义答案

- 分类：实现差距，但只有在上述设计差距解决之后
- 观察到的汇编证据：
  - 块体 期望 `.local` 中保存的掩码更新、分支和状态之间进行细粒度交互。
- 当前规范实施：
  - QEMU 通过从 `LB/LC` 状态步进到 `linx_vec_ZXTERMEN46QXZ_next` 来重放 块体，然后在 块体 终止 (`emulator/qemu/target/linx/translate.c:454-480`) 处返回。
  - 它将 `B.TEXT` 视为具有合法性检查的解耦 块头/块体 传输 (`emulator/qemu/target/linx/translate.c:484-520`)。
- 为什么这是一个差距：
  - 这对于当前面向重播的子集来说已经足够了。
  - 证明具有显式发散/重新加入状态的更丰富的 SIMT 模型的正确性是不够的，因为该状态在架构上尚不存在。
- 对编译器/QEMU/RTL的影响：
  - QEMU 只能近似替代编译器正在执行的操作，除非架构首先说明机器是什么。
  - RTL 验证也会遇到同样的歧义。
- 推荐关闭方向：
  - 不要先“修复”QEMU。
  - 首先冻结 SIMT 控制状态合约，然后扩展 QEMU 以精确建模该合约并添加目标 AVS 覆盖范围：
    - 部分活动循环
    - 嵌套的发散分支
    - 与幸存同伴完成车道

### SIMT 编译模型#### 差距 8：当前的 LLVM SIMT 降低合约仍然是正确性优先的重播子集，而不是此类内核的完整编译器合约- 分类：实施差距与配置文件合同漏洞
- 观察到的汇编证据：
  - 替代编译器显然愿意发出具有真正的 in-块体 分支的控制密集型 MPAR 块体，向量 比较馈送 `p`、`v.psel`、`.local` 溢出状态和基于模的探测循环（`/Users/zhoubot/linx-simt.s:60-258`）。
- 当前 LLVM 降低：
  - LLVM 拒绝许多循环形状并默认为 `mseq`，除非独立性在结构上是明显的 (`compiler/llvm/llvm/lib/Target/ZXTERMEN40QXZ/ZXTERMEN40QXZSIMTAutoVectorize.cpp:700-860`)。
  - 它明确强制通过 `LB1` 在启动路径 (`compiler/llvm/llvm/lib/Target/ZXTERMEN40QXZ/ZXTERMEN40QXZSIMTAutoVectorize.cpp:1589-1649`) 中重放 标量 通道。
  - 其内部控制流回退将 向量 谓词减少为使用 `v.rdor ... ->t#1` (`compiler/llvm/llvm/lib/Target/ZXTERMEN40QXZ/ZXTERMEN40QXZSIMTAutoVectorize.cpp:4182-4275`) 的 标量 `any-active-lane` 分支。
- 为什么这是一个差距：
  - 目前的实施并没有“错误”；这是故意保守的。
  - 但没有稳定的编译器合约规定何时更激进的 MPAR 降低（例如替代编译器的输出）是规范且合法的。
  - 如果没有这个契约，每个编译器都会发明自己的 SIMT 降低规则。
- 对编译器/QEMU/RTL的影响：
  - 后端可移植性较差。
  - AVS 无法区分“合法替代降低”和“编译器特定的未定义行为”。
- 推荐关闭方向：
  - 写下面向编译器的 SIMT 降低配置文件：
    - MPAR/MSEQ 体内的合法分支模式
    - 允许使用 `.local` 刮擦
    - 不同区域所需的 EXEC-mask 语义
    - 允许启动/组宽度映射- 然后要么将 LLVM 扩展到该配置文件，要么显式地将 LLVM 保留在仅重放子集上，并声明更丰富的 SIMT 内核目前是非规范的。

## 总体评估

替代编译器主要不是暴露丢失的单个指令。它暴露出当前的 `v0.56` SIMT 故事仍然是部分强化的重放模型，而这个哈希表内核需要更明确的类似 GPU 的执行合约。

最深的缺失是建筑方面的：

- 当`VS*`和`LB*`同时出现时，什么是一个组
- 部分活动车道如何继续通过内部控制流
- 编译器生成的车道本地状态所在的位置
- 掩码和分支如何在不依赖编译器私有约定的情况下交互

在这些被冻结之前，LLVM、QEMU 和 RTL 都可以做出局部合理的选择，但仍然存在分歧。

## 优先关闭顺序

1. 控制流/再收敛合约
2. Lane-本地状态/暂存模型
3. 启动几何/组宽度合约
4.编译器降级合约
5. 仿真器/解码器后续