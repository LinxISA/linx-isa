# 灵犀 SIMT 编译器支持的子集

最后更新: 2026-03-11

本页记录了 LLVM 灵犀 SIMT **当前实现的子集**
降低集中于
`compiler/llvm/llvm/lib/Target/ZXTERMEN40QXZ/ZXTERMEN40QXZSIMTAutoVectorize.cpp`。

它是一个实现状态页面，而不是架构契约。现场直播
架构方向定义为
`docs/architecture/v0.56-simt-compiler-contract.md`。

## 目的

本页回答了两个实际问题：

- 哪个环路形状的电流通道实际上准备降低，
- 如何解释 SIMT autovec 备注中列出的当前拒绝原因。

它的存在是为了让用户不必对后端行为进行逆向工程
程序集或来自 pass 源。

JSON 注释现在还公开了面向编译器的控制流分类
字段，`cf_strategy`，因此可以跟踪标准 SIMT 降低技术
而无需仅从组装中推断出它们。当前使用中的值
是：

- `if-converted-single-block`：简单钻石或嵌套钻石折叠
  在 SIMT 降低之前进入比较/选择形式
- `if-converted-diamond`：原始嵌套纯值内部菱形区域
  后端可以本地折叠为比较/选择形式，无需架构
  `p` 保存/恢复
- `active-replay`：使用编译器物化重放驱动的持续进展
  通道状态而不是一流的 EXEC 掩码恢复
- `exec-mask-save-restore-required`：需要分组拆分/重新加入
  架构 `p` 保存/恢复，因此分组降低并不声称已关闭

## 当前降低姿势

当前的传递仍然是正确性优先的启动实现。

它的默认姿势是：- 更喜欢 `MSEQ` 除非独立性在结构上是明显的，
- 保持可接受的循环子集狭窄，
- 更喜欢规范的分组布局，用于具有静态的计数、单位步长循环
  可整除的行程计数，
- 当尚未进行分组布局时，通过 `LB1` 回退到 标量 通道重播
  安全或尚未实施，
- 标量通过 `any-active-lane` 后备解决困难的内部控制流
  而不是成熟的发散-SIMT 降低。

这意味着该通行证目前最好理解为：

- 用于窄规范循环子集的可用 SIMT 内核生成器，
- 加上一个通往新冻结的发散型 `v0.56` SIMT 的实验桥
  合同。

## 当前接受的循环形状

当前通道适用于具有以下属性的循环：

- 仅最内层循环，
- 具有稳定的 pre块头/块头/锁存器结构的循环简化形式，
- 没有不支持的呼叫，
- 无 灵犀 瓦片/CUBE/TEPL 内在循环体，
- tripcount 可通过当前基于 ScalarEvolution 的扩展来表达，
- 为使用中的下降路径提供足够的仿射内存/索引，
- 至少一种有意义的循环副作用：
  - 商店，或
  - 支持重复/减少/存活路径，或
  - 主动重放驱动的退出行为。

目前最有力的成功案例是：

- 计算最里面的循环，
- 简单的仿射加载/存储，
- 没有不受支持的内部 CFG，
- 没有复杂的指针 phi 或 liveout 形状，
- 无易失性/原子存储器。

## 当前模式政策

该通证目前公开了三种政策模式：- `mseq`：始终选择`MSEQ`
- `mpar-safe`：当循环看起来依赖安全时允许 `MPAR`
- `auto`：默认正确性优先；更喜欢 `MSEQ` 除非循环是
  结构独立

今天的实践中：

- `MSEQ` 是复杂循环的稳定默认值，
- `MPAR` 目前仅适用于简单、无存储或明显安全的情况
  循环，
- 许多分支重或状态重的内核仍然通过类似重放的方式降低
  分组执行而不是成熟的发散-SIMT 策略。

该通道现在还公开了明确的布局策略：

- `auto`：当当前实现可以时更喜欢规范的分组布局
  证明安全的静态映射
- `ZXTERMEN44QXZ-replay`：强制保守的`LB0=1`、`LB1=tripcount`重播路径
- `grouped`：要求规范分组降低并拒绝循环，如果
  目前的实现不能满足它

## 当前分组重播回退

当前的实现仍然严重依赖分组重放
正确性：

- `LB1`仍然是保守路径中的主要重放/分组维度，
- 标量 重放仍用于动态行程计数、主动重放循环和
  当前分组子集之外的记忆形状，
- 分组车道现在具有明确的规范下降路径：
  - 单组：`LB0=tripcount`、`LB1=1`
  - 露天开采：`LB0=lanes-per-group`、`LB1=group-count`
- 分组布局时逻辑线程索引保持为`lc0 + lc1 * LB0`
  使用多个组。

这是实施状态，而不是最终预期的 `v0.56` SIMT 合约。## 当前内部控制流行为

该通行证现在可以发出第一个规范的 `p` 形式的结构化分支
内部控制流程：

- 向量 比较驱动的分支条件可能低于 `V.CMP.* ->p` 或
  `V.F* ->p`，
- 分支转移可以直接降低为 in-块体 `b.nz` / `b.z`，
- 这删除了旧的 `v.rdor ... ->t#1`“任意活动通道”桥
  涵盖比较驱动的案例，
- 覆盖的非循环内部 CFG 现在包括单级和嵌套前向
  具有直接 块体 本地标签的比较驱动分支。
- 中断退出内部分支分为内部CFG和下层分支
  标量 重播活动通道路径而不是被视为普通锁存器
  退出。

尚不成熟的地方：

- 完整掩码保存/恢复嵌套不同区域的纪律，
- 一般部分活动循环延续和重新收敛，
- 超出当前只进嵌套分支子集的运行时闭包。

当前的运行时证据现在涵盖了一个额外的 标量 重播活动通道
形状：- 块体-本地 `v.rdor ... ->t#1` 桥为 标量 `b.ne` 供电，
- 使用一组通道证明 块体 执行并写入重放 块体 结果
  当还原条件不触发时，
- 第二个通道组证明 标量 中断/跳过路径抑制了
  当前 标量-replay 迭代的 块体 存储在缩减条件时
  火灾。
- 使用直接 `->p` 分支传输加上 标量 重播 `if/else` 块体 形状
  块体-local `j` else-edge/rejoin，每次迭代结果检查证明
  所采取的真路径和跳转的假路径都返回到共享的块体
  正确终止符。
- 使用相同的直接分组 `if/else` 块体 形状（`LB0=4`、`LB1=1`）
  `->p` 拆分加上 块体-本地 `j` else-edge/rejoin，具有每通道结果
  检查证明当前重放模型也闭合分组直线
  拆分/重新加入案例。
- 具有多个 块体 局部 `j` 边的分组嵌套 `if/else` 块体 形状，
  共享的重新加入，以及公共的加入后尾部存储，证明了当前
  重播模式也关闭直线分组后继续进步
  第一次分裂/重新加入。
- 分组后沿 块体 循环，带有基于标签的 `j` 返回循环头，
  证明当前重放模型也闭合直线分组
  当每个车道可以独立完成时向后边缘进度。- 分组固定行程计数重放 块体，具有车道本地内存支持的活动
  状态，证明当前运行时间可以携带每通道持续进度
  编译器/具体化显式将该状态存储在 `p` 之外。

直接 `->p` 分支转账仍由现有专用专线覆盖
专用 MSEQ 块体 b.nz/b.z-on-p 和嵌套分支运行时回归。

编译器端边界也发生了变化：简单的主动重放循环
派生的最大行程计数和单位步长内存现在在分组布局下较低，
活动位在编译器草稿中具体化为逻辑通道状态。
`search_store_index_grouped_boundary` 对此进行了介绍，现在
降低为分组露天开采 `LB0=32, LB1=2`，而不是回落到 标量
重播。

该编译器形状现在也通过专用的运行时覆盖
`simt_autovec` QEMU套件，通过普通直接构建`clang -> object`
管道。它的编译阶段现在还直接检查发出的对象形状
对于 `BSTART.MSEQ`、`B.TEXT`、分组 `LB0/LB1`、`.brg` 内存操作和 块体
本地`p`-分支/跳转控制流。受保护的阳性病例有：- 分组主动重播搜索，在第一个条带挖掘组中命中，
- 分组主动重播搜索，并在尾部组中命中，
- 分组主动重放未命中返回 `-1`，
-直接-`clang`分组单块内部钻石if转换降低，
  具体化为 `V.FLT` 加 `V.CSEL`，
-直接`clang`分组单块嵌套钻石if转换降低，
  具体化为比较/选择链，无需 块体 本地拆分/重新加入 CFG。
- 直接 `clang` 分组相同地址存储钻石降低，验证于
  来自分支存储源形状的运行时，而不仅仅是来自 pre-if-converted
  价值SSA。
-直接`clang`分组TSVC风格元素最小/选择存储降低，
  在运行时和编译阶段从无分支 `min(a[i], b[i])` 进行验证
  源形状以 `v.flt + v.csel + v.sw.brg` 分组。
- 编译器覆盖范围现在还显式锁定 TSVC 分割：
  `ZXTERMEN42QXZ_min_select_store`是一组`if-converted-single-block`正，
  而 `ZXTERMEN42QXZ_shift_half_index` 仍然是显式的 标量/拒绝边界
  （`non_float_store_value`）而不是分组阳性。
- 现在也锁定了一个额外的 TSVC 式仿射正值：
  恒定移位输出存储（`a[i + 32] = a[i] + b[i]`）低于
  `grouped-single-group`，而步幅控制循环 (`i += inc`) 保留
  标量-重播而不是进入分组子集。
- 动态偏移变体（`a[i + M] = a[i] + b[i]`）现在也被锁定为
  标量-重播：它保留在 vblock 路径内，但具有通道数 `1`
  而不是分组发射几何形状。- TSVC 风格的控制流内核现在也被更明确地分割：
  当前目标值的简单屏蔽更新仍然被拒绝，因为
  `unsupported_value_expr:select`，同时嵌套双更新/双存储控制
  流落在边界的 `exec-mask-save-restore-required` 侧。
- 更多 TSVC 控制流细节现在也被锁定：独立条件
  双存储内核和依赖条件双更新内核均保持开启状态
  `unsupported_value_expr:select` 边界。换句话说，当前分组
  单块 if-conversion 可以很好地处理一个选定的结果，但不能处理
  多结果屏蔽更新包。

这些额外的优点与标准 SIMT 编译器技术一致：
早期的 标量 优化可以将简单的菱形转换为谓词并
选择形式，分组内核可以保留在当前规范的 `v0.56` 内
块体 合约（`BSTART.MSEQ`、`B.TEXT`、分组 `LB0/LB1`、向量 比较，以及
选择），无需一流的 EXEC 掩码保存/恢复或拆分/重新加入
重新收敛。

现在，这条积极的车道可以通过两种方式覆盖：- 将 `clang -O2` 直接放在早期 标量 通过 if-convert 的分支源上，
- 已转换 `select`-SSA IR 上的原始 `llc`，这是后端
  标准 SIMT if 转换技术的规范证明。
- 原始 `llc` 位于一类狭窄的嵌套结构内部金刚石区域上，其
  侧块是纯粹的投机价值生产者，其中间产品
  桥是仅限 PHI 的合并块；后端现在在本地进行 if-converts
  形成 `v.csel` 链并将其报告为
  `cf_strategy = if-converted-diamond`。
- 同一地址商店钻石的一小类原始 `llc`；当双方
  仅计算一个值并将其存储到相同的车道变化目的地，
  后端现在在本地将该形状重写为 `v.csel` 加上一个合并存储，
  而不是将其视为真正的 EXEC-mask 再收敛问题。
- 指针沉钻石上的原始 `llc`，其中值路径位于本地
  if-converted 但最终存储仍然通过现有的调度
  指针-PHI接收器机制；目前编译器将其覆盖为
  标量-重播阳性，不是分组阳性。
- TSVC 风格的移位半索引地址模式上的直接 `clang`
  (`a[i] = b[i] + c[i >> 1]`) 目前仍然是 标量 边界情况：它是
  `simt_autovec` 中运行时覆盖，但发出的对象仍然是 标量
  计数循环而不是分组的 `BSTART.MSEQ/B.TEXT` 块体。现在，一个额外的编译器边界是明确的：退出链副作用，例如
因为中断块中的 `store *out = i` 被拒绝
`unsupported_exit_side_effects`而不是被默默地丢弃。

早期的两级 `clang -emit-llvm` 加 `llc` 解决方法不再有效
需要：灵犀 目标现在在新的通道管理器上注册 SIMT autovec
`clang` 管道，和直接 `clang -> object` 路径发出相同的分组
`BSTART.MSEQ/B.TEXT` 形状作为此功能类的 `llc` 通道。

尚未声明的内容已关闭：

- 分组/发散 块体-需要真正部分主动的本地控制流
  通过架构掩模规则而不是继续或重新收敛
  比编译器物化逻辑通道内存状态，
- 掩码保存/恢复或类似掩码堆栈的嵌套再收敛行为，
- 块体 内的后向边缘控制流取决于发散的车道子集
  延续而不是每通道重播。

现在，一个具体的拦截器已被固定在 ISA/编码边界处。的
规范的 SIMT 文档允许编译器/运行时保存/恢复 `p` 当操作数
编码允许，但是当前的规范工具链表面没有可用的
该操作的承运人：

- 普通 标量 `add p, zero, ->t` / `add t, zero, ->p` 失败，因为
  标量形式仅携带5位寄存器字段，
- 规范的 `v0.56` 解析拒绝 `l.add ...` 旧语法，
- 因此目前没有公认的组域规范 asm 形状
  `p` 通过 标量 载体保存/恢复。现在已被 MC 回归锁定
`compiler/llvm/llvm/test/MC/ZXTERMEN40QXZ/simt-p-save-restore-gap.s`。

相关运行时警告：当前分组/嵌套 QEMU 回归
`v03_ZXTERMEN42QXZ` 仍然是面向重放的执行通道的证据，而不是
完整的架构执行掩码恢复。这些测试练习分组为 块体 CFG
在当前的重播模式下，但它们并没有被证明是一流的
保存/恢复 `p` 或真正的子集掩码重新收敛的载波。

编译器现在将原始多块内部 CFG 视为硬分组布局
边界，除非早期优化已经将该区域折叠成
单块 向量 形式（例如比较结果上的 `v.csel`）。在
当前编译器表面：- 仍然支持分组固定行程计数主动重播搜索/边界循环，
- 优化器-if-转换的单块内部条件可能仍然较低，因为
  分组 向量 机构，
- 狭窄的原始嵌套内部钻石子集也可能会降低为分组 向量
  当侧面区域是无副作用的投机价值生产者时的机构
  中间桥接块是仅 PHI 的合并，
- 狭窄的相同地址存储钻石子集也可能会降低为分组 向量
  当两个臂仅存储值和存储地址不同时的实体
  两边的表达方式相同，
- 实际上，这意味着直接 `clang -O2` 仍然可以生成分组
  标量/CFG 优化后的简单金刚石单块 SIMT 体，
  而原始多块 `llc` IR 只能逃避更严格的拆分/重新加入
  该 local-if-conversion 子集的边界，
- 但是原始的循环内分割/重新加入 CFG 需要一流的 EXEC 掩码
  保存/恢复回退到 `auto` 中的 标量 重播，并强制 `grouped`
  拒绝 `grouped_layout_requires_exec_mask_save_restore`。
- 不同地址存储分割/重新加入区域保留在拒绝侧
  该边界；它们不是本地 if-converted 并且仍然需要一个真正的
  建筑执行掩码保存/恢复故事。

该分组拒绝边界被锁定
`compiler/llvm/llvm/test/CodeGen/ZXTERMEN40QXZ/autovec_grouped_exec_mask_save_restore_reject.ll`。

## 拒绝分类法

当前拒绝原因按意图分组如下。

### 结构先决条件

这意味着环路形状超出了通行证的基本进入要求：- `function_already_lowered`
- `not_innermost_loop`
- `not_loop_simplify`
- `missing_preheader_or_header`
- `preheader_not_simple_branch`
- `missing_loop_latch`
- `no_exit_block`
- `no_unique_exit`
- `missing_terminator`

释义：

- 该通道在启动 SIMT 之前需要一个稳定的规范循环 CFG
  降低。

### 不支持的语义内容

这意味着循环包含有意从当前排除的结构
实施：

- `contains_call`
- `linx_tile_intrinsic_loop`
- `volatile_or_atomic_load`
- `volatile_or_atomic_store`

释义：

- 这些位于当前通用 SIMT autovec 切片之外，不应包含在其中
  被视为偶然回归。

### Tripcount 和规范化失败

这意味着通行证无法得出可用的行程计数或归纳模型：

- `no_tripcount_expr`
- `tripcount_expand_failed`
- `tripcount_non_integer`
- `grouped_layout_requires_static_tripcount`

释义：

- 根据架构合同，循环可能仍然是合法的，但当前的
  实施还不能降低它。

### 副作用/进度要求

这意味着循环 块体 与“值得”的当前定义不匹配
降低”或“安全降低”：

- `no_store_in_loop`

释义：

- 这是一个实现过滤器，而不是纯计算循环的声明
  在建筑上无效。

### 分支和终止符限制

这意味着传递命中控制流形成它还不能干净地降低：

- `unsupported_branch_condition`
- `unsupported_branch_fcmp_condition`
- `unsupported_branch_i1_condition`
- `unsupported_branch_predicate`
- `unsupported_terminator`
- `unsupported_switch_condition`
- `unsupported_switch_case`
- `unsupported_inner_backedge`
- `unsupported_inner_cycle`

释义：

- 这些是当前分支重的发散内核的主要阻碍因素。

### 存储/寻址限制这意味着内存降低无法保持当前的仿射/支持形式：

- `non_affine_store_address`
- `unsupported_store_stride`
- `non_float_store_value`
- `grouped_layout_requires_unit_stride_memory`

释义：

- 这些是内存形式选择和地址的当前实现限制
  重建。

### 布局策略限制

这意味着无法满足所选的启动布局策略：

- `grouped_layout_requires_masked_lane_state`
- `grouped_layout_unavailable`

释义：

- 这些不是一般的环形故障；它们是明确的信号
  循环超出了当前实现的规范分组子集。

### PHI / Liveout / 指针 PHI 限制

这些跨边沿或环外携带的平均状态超过了当前
降低型号：

- `value_live_out_unsupported_type`
- `unsupported_liveout_value`
- `liveout_bind_exhausted`
- `liveout_store_emit_failed`
- `invalid_exit_phi_plan`
- `exit_phi_bind_exhausted`
- `exit_phi_init_not_dominating`
- `exit_phi_no_init_incoming`
- `exit_phi_store_emit_failed`
- `exit_phi_unsupported_type`
- `exit_phi_value_emit_failed`
- `invalid_phi_edge`
- `missing_phi_incoming`
- `missing_phi_reg`
- `unsupported_inner_phi_type`
- `invalid_ptr_phi_plan`
- `missing_ptr_phi_edge`
- `missing_ptr_phi_plan`
- `ptr_phi_bind_exhausted`
- `ptr_phi_sel_emit_failed`
- `unsupported_ptr_phi_incoming`
- `unsupported_ptr_phi_store_gep`
- `unsupported_ptr_phi_store_index`
- `unsupported_ptr_phi_variant_incoming`
- `phi_incoming_addrec_emit_failed`
- `phi_incoming_emit_failed`

释义：

- 这些是状态模型成熟度差距，而不是 ISA 冲突。

### 递归和归纳限制

这些意味着循环携带状态存在，但当前的实现不能
安全地表示它：

- `invalid_recurrence_init`
- `invalid_recurrence_init_cast`
- `invalid_recurrence_liveout_cast`
- `invalid_recurrence_plan`
- `invalid_recurrence_slot_type`
- `recurrence_bind_exhausted`
- `recurrence_store_emit_failed`
- `recurrence_update_not_emitted`
- `invalid_f32_induction_plan`
- `f32_induction_not_emitted`
- `f32_induction_step_emit_failed`
- `f32_induction_store_emit_failed`

释义：- 这些是车道局部实时状态下一个成熟度切片的核心。

### 减少和资源限制

这意味着循环达到了有限的实现限制而不是语义限制
歧义：

- `too_many_reductions`
- `unsupported_reduction_value`
- `reduction_bind_exhausted`
- `ZXTERMEN42QXZ_reg_exhausted`
- `active_bind_exhausted`

释义：

- 这些是后端资源/模型限制，应该随着时间的推移而缩小。

### 排放/内部下降故障

这意味着该过程在概念上接受了循环形状，但失败了
实现降低：

- `active_cond_emit_failed`
- `active_load_failed`
- `active_store_emit_failed`

释义：

- 这些通常应被视为编译器错误，而不是不受支持的用户代码
  形状。

## 如何阅读备注

该通行证已经发出机器可读的注释，包括：

- `status`
- `reason`
- 选择模式
- `lane_count`
- `group_count`
- `force_ZXTERMEN44QXZ_lane`
- 重复/记忆/行程计数元数据

推荐解读：

- `reject` + 结构或语义内容原因：
  循环位于当前支持的子集之外。
- `reject` + 状态模型或控制流原因：
  Loop 是一个成熟度差距候选者。
- `reject` + 发出失败原因：
  可能是编译器错误或不完整的降低路径。

## 当前“支持”的含义

目前，当内核满足以下条件时，应将其视为受支持的子集：- 降低但没有拒绝备注，
- 生成稳定的 `MSEQ` 或明确合理的 `MPAR` 块头，
- 不依赖于当前未记录的暂存/布局约定
  发出的地址表达式，
- 当这样的门时，在相应的 QEMU/运行时通道中正确运行
  存在。

## 与其他页面的关系

- 建筑合同：
  `docs/architecture/v0.56-simt-compiler-contract.md`
- 架构规划：
  `docs/architecture/v0.56-simt-compiler-contract-plan.md`
- 编译器成熟度路线图：
  `docs/bringup/SIMT_COMPILER_MATURITY_PLAN.md`

每当通行证支持边界以某种方式发生变化时，应更新此页面
用户或下游验证必须理解。