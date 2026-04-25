# 低精度矩阵乘实现中内积式与外积式数据流的权衡

## 结论摘要

在低精度矩阵乘里，`外积好` 和 `内积好` 都不够准确。更可靠的结论是：

- 对 `dense GEMM` 的高吞吐硬件，通常优先选择 `外积 / 块外积(block outer product)` 风格的数据流，因为它更容易做规则阵列、局部通信和高输入复用。
- 对低精度数值正确性，关键瓶颈通常不是“乘法阵列是内积还是外积”，而是 `partial sum` 的处理方式，尤其是 `accumulator bit-width`、累加顺序、是否做分组累加和是否保留更高精度的局部和。
- 对 `INT8/INT4` 这类定点实现，主要风险是 `overflow`；对 `FP16/BF16/FP8` 这类浮点实现，主要风险是 `swamping`、舍入顺序和指数对齐误差。
- 因此工程上最常见、也最稳妥的组合不是“纯外积”或“纯内积”，而是：
  - `乘法阵列` 采用外积或块外积式复用；
  - `局部累加路径` 采用较宽 accumulator、分层归约、排序或分组累加；
  - 必要时把最终归约抽象成 dot-product 或 many-term dot-product 来做数值控制。

一句话概括：`dense 计算阵列通常偏外积，低精度数值稳健性通常偏重累加器设计。`

## 问题定义

矩阵乘 `C = A x B` 可以写成两种等价形式：

- 内积视角：
  `C[i, j] = sum_k A[i, k] * B[k, j]`
- 外积视角：
  `C += A[:, k] * B[k, :]`

如果用硬件语言表达：

- `内积式` 更像很多 dot-product lane 或 tile dot-product 指令。它强调“为某个输出元素或某个输出块，沿 K 维做归约”。
- `外积式` 更像每轮取 `A` 的一列块和 `B` 的一行块，对一个输出块做 rank-1 或 rank-k 更新。它强调“广播输入，重复更新一片输出块”。

实际芯片通常不会是纯粹的一维内积或纯粹的一维外积，而是：

- ISA 上暴露 tile MMA；
- 微架构上采用 systolic array 或规则二维阵列；
- 编译和 kernel 调度上按 `block outer product` 组织循环。

因此本文中的“内积/外积”主要是指 `数据流和 partial sum 组织方式`，不是指数学定义本身。

## 调研范围与边界

本文聚焦：

- `dense low-precision GEMM`，即 DNN/AI 加速器里最常见的矩阵乘核心。
- 低精度数据类型对数据流选择的影响，包括 `INT8/INT4` 和 `FP16/BF16/FP8`。
- `电路复杂度`、`片上数据流/存储`、`数值精度` 三个维度。

本文不把以下问题混在主结论里：

- `稀疏矩阵乘` 的最佳数据流。稀疏场景里 inner/outer 的优劣与 dense 明显不同，只把它当补充对照。
- 单纯的软件微内核优化。软件微内核与硬件阵列思路高度相关，但它不是本文的主对象。
- 某一款商用芯片的反向工程微细节。本文只使用公开论文和官方文档能支持的结论。

## 研究问题拆解

要回答“低精度矩阵乘到底外积好还是内积好”，至少要拆成四个子问题：

- 哪种数据流更容易构建 `高吞吐、规则、可扩展` 的乘法阵列？
- 哪种数据流对 `片上 SRAM / register file / interconnect` 更友好？
- 哪种数据流更容易处理 `partial sums`？
- 在低精度下，哪种数据流更容易保证 `overflow` 和 `rounding error` 可控？

如果不拆开，容易把“吞吐优势”和“数值优势”混为一谈。

## 与知乎文章的口径对齐

知乎文章《也说矩阵外积和内积，不打哑谜》有一个很重要的限定条件：它讨论的不是软件分块、不是 ISA 表层语义，而是 `最底层电路` 里的内积和外积。这个限定是对的，因为一旦落到电路，最关键的问题就不再是 GEMM 数学形式，而是：

- 每个输出元素在一次局部归约里会消耗多少乘积项；
- partial sums 在本地保存时采用什么数制；
- 每生成一个新乘积，是否都要触发一次高精度浮点累加与规格化。

为了避免语义混乱，本文引入一个更精确的记号：

- `k_u`：单次局部归约里，被融合到一次高精度累加中的乘积个数。

可以把几种常见设计放到同一坐标里理解：

- `k_u = 1`
  更接近电路级 `outer-product update`。每个新乘积或每个很小的乘积组，都会直接更新 psum。
- `k_u = 2 / 4 / 8 / 16`
  更接近电路级 `small dot product`。先在局部把若干乘积归约成一个 wider sum-of-products，然后再加到高精度 accumulator。
- `k_u = K_tile`
  是理想化的大内积。所有乘积都在本地精确归约后，只做一次最终高精度累加或一次最终舍入。

这样看，知乎文章真正批评的对象不是“数学上的外积”，而是：

- `k_u` 太小；
- psum 又要求保持 `FP32` 级语义；
- 结果导致高精度累加和规格化频率过高。

## Dense GEMM 的主流实现为什么通常偏外积

### 软件和硬件都倾向于块外积

高性能 dense GEMM 的经典 micro-kernel 通常把内层写成一串 rank-1 update。BLIS 论文明确指出，micro-kernel 是 “a loop around a rank-1 (i.e., outer product) update”，并把最内层写成对微块 `C` 的连续 rank-1 更新。[BLIS]

这说明即便在 CPU 软件里，当目标是高吞吐 GEMM 时，核心思路也倾向于：

- 固定一个输出微块；
- 每次读一小段 `A` 和一小段 `B`；
- 对该输出微块做一次块外积更新；
- 重复 K 方向的多个小更新，直到完成归约。

这个思路到硬件上更自然：

- `A` 片段和 `B` 片段可以在 PE 阵列内广播或脉动传播；
- 输出 tile 的 partial sums 在阵列局部停留更久；
- 阵列可以做成规则二维结构，时序和布线都更可预测。

Google TPU 论文直接说明，矩阵单元采用 systolic execution 来减少读写，数据从左侧流入、权重从顶部流入，并以对角波前穿过阵列。[TPU] 这本质上就是一种外积或块外积式数据流。

### 外积式的主要硬件优势

对 dense low-precision matmul，外积或块外积的常见优势是：

- `输入复用高`
  同一批 `A` 和 `B` 片段可以在多个 PE 上重复使用，减少从高层存储反复读取。
- `阵列规则`
  适合 systolic array、mesh、wavefront 这类规则拓扑，降低控制复杂度。
- `局部通信`
  数据在邻近 PE 之间转发，不需要大范围读写 shared buffer。
- `更容易达到高 MAC 利用率`
  特别是在 dense、规则 tile 的情况下，PE 阵列容易被填满。

Eyeriss 等数据流工作也反复强调，卷积和矩阵乘一类内核的能效高度受数据搬运支配，因此优先优化复用与局部通信，而不是只优化 MAC 数量。[Eyeriss]
这也是为什么大量张量核、CUBE 类矩阵单元、TPU 类阵列都更像 `tile MMA + systolic/block-outer-product`，而不是“很多独立 dot-product 单元拼起来”。

## 外积式不是免费午餐：partial sums 是它的核心代价

外积式最明显的问题不是乘法，而是 `partial sums`。

每做一次外积更新，都会同时触碰一整块输出。如果输出块不能完全留在寄存器或近端 SRAM 中，就会产生：

- 更大的 partial-sum buffer 需求；
- 更多的 psum 写回和重新读入；
- 更多归约或合并逻辑；
- 更强的写端口压力和同步需求。

这在 sparse 文献里被放大得最明显。OuterSPACE 指出，外积法虽然消除了 index matching 和很多冗余读，但代价是 `N` 个 partial product matrix 被流出再流回，显著增加内存系统压力。[OuterSPACE]
SpArch 则进一步说明，纯外积 sparse matmul 的核心问题是输出局部性差、partial matrix 太多，因此需要立即在片上 merge，减少 DRAM 往返。[SpArch]

虽然这些论文面向 sparse，但它们揭示了一个对 dense 也成立的规律：

- `外积改善输入复用`
- `但会把困难转移到 partial sums 的驻留、合并和写回`

dense 与 sparse 的区别只在于：

- dense 场景下输出块更规则，片上 tile 驻留更容易，因此外积更容易成功；
- sparse 场景下 partial sums 稀疏且不规则，外积副作用会被放大。

### 小 `k_u` 外积在 FP8 到 FP32 上为什么尤其吃亏

知乎文章举的例子本质上是在说：

- 如果对一个 `M x N` 输出 tile 采用 `k_u = 1` 的外积更新；
- 并且要求 psum 始终保持 `FP32` 语义；
- 那么每前进一步 K 维，都要对该 tile 的 `M x N` 个输出分别执行一次高精度浮点加法语义。

更抽象地写，若完整归约长度为 `K`，则高精度浮点累加触发次数大致为：

```text
FP-accumulate events ~= M * N * K / k_u
```

这里的关键不是乘法次数，乘法次数始终都是 `M * N * K`，而是：

- `k_u = 1` 时，每个乘积基本都要尽快并入高精度 psum；
- `k_u = 4` 的 DOT4，则每 4 个乘积只触发 1 次高精度累加；
- 若能做到更深的融合归约，则高精度浮点规格化和舍入的压力继续下降。

这正是知乎文章抓到的核心痛点。对浮点 psum 来说，真正贵的往往不是低比特乘法本身，而是：

- 对阶；
- 规格化；
- 舍入；
- 更宽的 add / carry / sticky 相关逻辑；
- 高精度 psum 的寄存和转发。

Arm 的 FP8 DOT4 论文能直接支持这一点。该工作专门讨论 `fused FP8 4-way dot product with scaling and FP32 accumulation`，指出离散的 multiplier + adder 方案会导致较大 area 和 latency，需要把若干乘积先融合成 SoP 再做一次高精度累加。[FP8-DOT4]
更具体地说，论文中的早累加方案会生成 `69-bit` 宽的对齐乘积，并使用 `94-bit` adder 来完成 unrounded fraction 的计算；其 5nm 综合结果中，FP8-DOT4-EA 面积为 `674 sq.um`，FP8-DOT4-LA 为 `1133 sq.um`，都明显不是“白送的便宜逻辑”。[FP8-DOT4]

因此，如果把电路问题表述得更精确：

- `小 k_u 外积` 的问题不在乘法阵列；
- 问题在于它把高精度浮点 psum 更新频率推得太高。

## 内积式的主要特点

内积式的好处是概念上更直接：

- 每个输出元素对应一条沿 K 维的归约链；
- 每个 PE 或 lane 可以专注完成一个 dot product；
- 如果输出规模小、K 受控、或 ISA 本身已经定义 tile dot-product，那么控制更直接。

Intel AMX 这类矩阵指令就明显偏向 dot-product 语义：`TDPBF16PS` 和相关指令都以 tile dot-product 为基本原语，先做成对乘法，再沿 K 做归约，累加到结果 tile 上。[AMX]

内积式的主要问题在 dense 阵列实现中也很明显：

- 同时需要拿到 `A` 的一行和 `B` 的一列；
- 若不做复杂缓存/转置/packing，数据供给不自然；
- 对大规模阵列而言，往往不如 systolic/block-outer-product 那样规则；
- 如果每个输出元素都有自己的长归约链，累加器和归约树可能变成瓶颈。

因此在大吞吐 dense GEMM 上，纯内积式通常不如块外积式自然。

### 但大 `k_u` 内积也不是免费午餐

知乎文章批评外积是对的，但如果据此推到“内积必胜”，也不准确。因为当 `k_u` 持续增大时，内积电路会遇到另一类成本：

- 多个乘积的对阶逻辑会更复杂；
- 需要更宽的内部 datapath；
- 对齐、压缩树、carry-save、最终进位传播的时序压力上升；
- 若追求 exact 或 near-exact dot product，内部 fixed-point accumulator 会迅速变宽。

Arm 的 FP8-DOT4 论文明确指出，传统做法里“根据最大指数对齐多个乘积”本身就很贵，而且随着乘积个数上升，alignment latency 会成为限制项。[FP8-DOT4]
同一篇论文还提到已有 exact dot-product 方案会把每个乘积扩展到 fixed-point，再把结果累加到 fixed-point accumulator 中；为大约 `4000` 个乘积预留 guard bits 时，需要额外 `12` 位，且 accumulator 宽度直接依赖 product count，此外 scaling 也会变得困难。[FP8-DOT4]

Berkeley 的 exact dot-product accelerator 也支持这个方向的判断。其 IEEE-754 exact dot product 加速器对 single precision 使用 `640-bit` fixed-point accumulator，对 double precision 使用 `4288-bit` fixed-point accumulator，说明“把乘法都先吞进去、最后只舍入一次”虽然数值漂亮，但电路并不轻量。[ExactDot]

所以电路上更现实的取值通常不是：

- 极端的 `k_u = 1`
- 也不是理想化的 `k_u = K`

而是某个中间值，例如 `2 / 4 / 8 / 16`，再辅以更高层的块级数据流和层级化累加。

## 低精度下真正的关键：accumulator 而不是 multiplier

### 定点场景：主要问题是 overflow

对 `INT8/INT4` 而言，乘法器位宽已经很窄，但 partial sum 的动态范围仍随 K 增长。若乘积位宽为 `p`，归约长度为 `K`，保守估算 accumulator 所需位宽通常近似为：

```text
acc_bits ~= product_bits + ceil(log2(K))
```

例如 INT8 x INT8 的乘积通常需要 16 位表示，若 K 很大，再加上 `ceil(log2 K)` 的增长，很快就把 accumulator 推到 24 位、32 位甚至更高。结果是：

- 乘法器已经因为低精度变得便宜；
- 但 accumulator、adder tree、psum SRAM 和写回带宽不一定同步变便宜；
- 低精度时代，瓶颈经常从 `multiply` 转移到 `accumulate`。

Google TPU 的公开数据也能说明这个趋势：TPU v1 的核心是 65,536 个 8-bit MAC，但 16-bit 乘积被收集到 `4 MiB of 32-bit Accumulators` 中。[TPU]
这说明即便乘法是 8-bit，工业级实现仍倾向于用明显更宽的累加器来换取精度和可编程性。

### 浮点场景：主要问题是 swamping 和舍入顺序

对 `FP16/BF16/FP8` 而言，危险不仅是 overflow，还包括：

- 小数与大数相加时，小数尾数右移过多而被吞掉；
- 累加顺序不同导致误差不同；
- 低 mantissa 宽度让长期 sequential summation 误差更敏感。

MGS 论文对这一点说得很直接：低比特浮点 dot product 的一个显著误差源是 `swamping`，即小项为了和大项对齐指数而丢失 mantissa；通过基于指数组织求和顺序，可以显著降低低比特浮点累加误差。[MGS]

这意味着：

- 低比特浮点的精度问题，核心在 `求和顺序` 和 `累加器设计`；
- 这和阵列采用外积还是内积并不一一对应；
- 即使乘法阵列是块外积，最后也常需要更“内积化”的归约控制手段来保证数值质量。

## 相关论文对 accumulator 的直接结论

### ABS：累加精度设计常被保守过度

Sakr 等人的 `Accumulation Bit-Width Scaling For Ultra-Low Precision Training Of Deep Networks` 指出，很多低精度训练系统虽然 aggressively quantize 权重和激活，但仍然对内积 partial sums 使用宽而保守的高精度 accumulator，因为缺少分析框架来估计真正需要的累加精度。[ABS]

该工作给出的核心信息有两点：

- 如果 accumulator 选得过窄，会导致 partial sum 信息损失，并表现为方差损失；
- 但 accumulator 也未必要机械地维持很高精度，可以根据 accumulation length 和统计特性做更紧的位宽设计。

这对本文问题的意义是：

- 低精度矩阵乘的关键设计变量是 `accumulation precision`；
- 讨论“外积还是内积”时，必须把 `K 长度` 和 `psum 的位宽/组织方式` 一起考虑；
- 单独比较数据流，不比较累加器，是不完整的。

### A2Q：accumulator 位宽直接影响 FPGA 资源效率

A2Q 明确把量化训练目标改成“保证在低精度 accumulator 下不 overflow”，并给出权重约束。论文摘要直接指出，`accumulator bit width significantly impacts the resource efficiency of FPGA-based accelerators`，并报告相对 32-bit accumulator 可达到 `up to 2.3x reduction in resource utilization`。[A2Q]

这对硬件设计的含义很直接：

- 当乘法器已经低比特化后，是否还能继续降面积/功耗，往往取决于 accumulator 能不能缩窄；
- 低精度设计真正值钱的优化对象，往往不是乘法器本身，而是 accumulator、psum SRAM 和相关互连。

### PQS：宽 accumulator 会拖累带宽和能效

PQS 论文进一步从推理侧指出，常规 8-bit dot product 仍需要宽 accumulator 来避免 overflow，而宽 accumulator 会 `increase memory bandwidth usage and reduce energy efficiency`。该工作通过 `prune + quantize + sorted accumulation`，在多个任务上达到 `2.5x reduction in accumulator bitwidth`。[PQS]

这说明在低精度实现里：

- 如果不处理累加顺序和动态范围，硬件往往被迫保留宽 accumulator；
- 一旦 accumulator 仍然很宽，外积/内积的数据流收益会被 psum 搬运部分明显吞掉。

## 对知乎文章几个核心判断的逐条评估

### 判断一：`FP8 -> FP32` 外积如果直接更新 FP32 psum，会显著增加规格化压力

这个判断 `基本成立`，而且是文章里最有价值的观点之一。

当 `k_u` 很小，尤其接近 1 时：

- 每生成一个乘积就要更频繁地与高精度 psum 相加；
- 若 psum 采用 IEEE-like `FP32` 语义，就需要频繁处理 exponent compare、alignment、normalization、rounding；
- 对大 tile 来说，这个压力会在整个输出平面上同时放大。

知乎文章把它表述成“如果做 64x1 @ 1x64 的外积，64x64 的输出直接和上一轮 C 累加，然后放寄存器；若中间结果要 FP32，就得频繁做 FP32 规格化”。这个说法在 `naive FP32 psum outer-product` 语境下是成立的。

但这里也要补一个工程限定：

- 这并不意味着外积在电路上必败；
- 它只说明 `小 k_u + 全程 FP32 psum` 这一具体组合代价很高。

### 判断二：内积式 dot-product 单元虽然更节省 FP32 更新次数，但内部 datapath 也会变宽

这个判断 `成立`。

Arm 的 FP8-DOT4 论文正是一个直接例子：

- 为了减少高精度累加次数，先在本地融合 4 个 FP8 乘积；
- 但代价是需要更宽的内部对齐结果、SoP 逻辑和更复杂的 adder；
- 论文报告的 69-bit aligned products、94-bit adders、674 到 1133 sq.um 面积，说明“先做点积再累加”不是零成本优化。[FP8-DOT4]

因此更准确的表述是：

- `内积` 通过更大的 `k_u` 换来更少的 FP32 更新次数；
- 但支付的是更宽的局部 SoP / alignment / reduction 电路。

### 判断三：DeepSeek 对 Hopper FP8 累加精度的批评，本质上是在批评 accumulator 精度不足

这个判断 `成立，但不应被过度外推`。

DeepSeek-V3 技术报告明确写到，Hopper Tensor Core 的 FP8 GEMM 使用 fixed-point accumulation，对 mantissa products 按最大指数右移对齐；他们的实验显示只保留了右移后乘积的最高若干 bit，并因此建议未来芯片提高 accumulation precision，或依据算法需求选择合适的 accumulation bit-width。[DeepSeek-V3]

这说明：

- 当前商用实现里的确存在 “低精度乘法 + 不足够精细的内部累加” 问题；
- 但这批评的主要对象是 `internal accumulation precision`；
- 它不能被简单解读为“所有外积架构都不行”。

如果未来芯片支持：

- 更高精度的内部 accumulator；
- group scaling；
- tile-wise / block-wise quantization；
- Tensor Core 内完成 partial sum accumulation 和 dequantization；

那么 DeepSeek 批评的那部分问题会明显缓解。[DeepSeek-V3]

### 判断四：分层或多级 accumulator 是现实可行的折中方向

这个判断 `成立`，并且已有多篇论文支持。

Dynamic Group Accumulation (DGA) 工作明确把累加拆成：

- `intra-group accumulation`
- `inter-group accumulation`

并报告可在保持精度的同时显著缩窄所需 accumulation bit-width，硬件侧给出 `8.8% area overhead` 的 E-DGA 功能和明显的功耗收益。[DGA]

另一篇 2024 年的低精度训练 MAC 论文则更激进，直接研究 `FP8 multiplier + FP12 accumulator`，并通过 stochastic rounding 缓解 swamping，报告相比 half/single-precision adder 方案在面积、时序和功耗上都有明显优势，同时维持接近基线的训练精度。[SR-FP12]

这说明知乎评论区里提到的：

- 每若干次做一次更高精度合并；
- 暴露两级或多级 accumulator；
- 用再量化、分组累加、纠偏来降低全程 FP32 的代价；

不是拍脑袋 workaround，而是已经被学术界和部分实现方向验证过的正经路线。

## 一个更细的工程结论

如果专门讨论知乎文章关心的那个场景：

- `底层电路`
- `floating-point low precision`
- `结果希望接近 FP32 语义`

那么更细的结论应当是：

- `k_u` 太小的外积，在电路上常常吃亏；
  因为它会把高精度浮点 psum 更新、规格化和寄存压力推得过高。
- `k_u` 适中的小点积更合理；
  比如 DOT2 / DOT4 / DOT8 这类局部融合归约，可以明显降低高精度更新频率。
- `k_u` 太大的大内积也不理想；
  因为 alignment、压缩树和宽 accumulator 会迅速变贵。
- 最常见的优选解是：
  - tile/block 级数据流仍然偏外积；
  - 电路级局部归约采用适中的 `k_u`；
  - psum 采用层级化 accumulator、分组累加、或 block-floating / group scaling 风格的折中。

这也是为什么现代矩阵单元很少会在一个层面上被简单归类为“内积派”或“外积派”。

## 从电路复杂度角度看，外积和内积分别“贵”在哪里

### 外积 / 块外积的主要硬件成本

- `psum 驻留成本`
  需要把一个输出 tile 的 partial sums 尽可能长期保存在局部存储里。
- `局部存储容量`
  输出 tile 越大、accumulator 越宽，局部 buffer 越贵。
- `多轮更新控制`
  需要支持对同一输出 tile 连续执行多次 rank-1 或 rank-k update。
- `写回合并`
  如果 tile 无法完整驻留，写回和重载会显著增多。

但外积通常能省下：

- 输入操作数反复读取；
- 大范围寄存器搬运；
- 大规模全连接归约网络。

### 内积 / dot-product 的主要硬件成本

- `归约链或 adder tree`
  沿 K 维归约是它的核心，K 越长，累加路径越关键。
- `输入组织`
  需要稳定供应行和列，常伴随 packing/transpose/crossbar 压力。
- `lane 利用率`
  若 K 或 tile 形状不规整，可能较难像规则 systolic 阵列那样饱和。
- `高精度 accumulator`
  同样无法回避，而且往往直接绑在每个 dot-product lane 上。

所以从电路复杂度看，二者不是谁绝对更简单，而是：

- 外积把复杂度更多放在 `局部状态保持和 psum 管理`；
- 内积把复杂度更多放在 `归约路径、输入供给和列/行组织`。

## 从数值精度角度看，二者的真实差别

### 对定点累加

若 accumulator 足够宽，内积与外积在数学上可以得到相同结果。它们的差别主要来自：

- 是否做中间截断或饱和；
- psum 是否在多层 buffer 间往返并被重新量化；
- 归约是否分段进行，分段后是否再量化。

因此对 INT8/INT4 来说，决定精度的第一因素是：

- `accumulator width`
- `什么时候截断`
- `psum 在层级之间是否保持高精度`

而不是“阵列看起来更像内积还是外积”。

### 对低比特浮点累加

低比特浮点更依赖求和顺序。顺序求和、树形求和、按指数排序求和的误差会明显不同。MGS 明确针对这一点提出以 exponent-aware 的方式重排求和顺序，并报告 `up to 34.1%` 的 dMAC 功耗下降，同时精度保持接近高精度基线。[MGS]

因此对 FP8/BF16/FP16：

- 若使用顺序累加，低精度误差可能迅速积累；
- 若使用 pairwise/tree/sorted/group accumulation，可以显著改善；
- 这类改进大多发生在 `accumulate` 阶段，而不是乘法阵列阶段。

## 为什么很多现代矩阵单元看起来“外积做乘法，内积做归约”

这是当前最合理的工程折中之一：

- 阵列层面采用 `systolic / block outer product`
  为了最大化输入复用、降低全局搬运、维持规则布局。
- 局部归约层面采用 `wider accumulator / fused sum / tree reduction / grouped accumulation`
  为了控制低精度误差与 overflow。

Google TPU 的公开描述就是这样一个典型例子：

- 计算阵列本身是 systolic；
- 16-bit products 被送入 32-bit accumulators；
- 软件从功能上看到的是矩阵乘累加，而不是阵列内部的波前传播细节。[TPU]

这也是为什么把现代矩阵单元硬分成“内积硬件”或“外积硬件”通常不够准确。更精确的说法是：

- `乘法数据流` 往往偏外积；
- `partial sum 数值管理` 往往偏内积/归约优化。

## Dense 与 sparse 的结论不能混用

需要单独强调一点：如果对象是 `sparse matmul`，结论会明显不同。

OuterSPACE 和 SpArch 都说明了：

- 纯 inner product 在 sparse 场景会有 index matching 和冗余访问；
- 纯 outer product 会有 partial matrix 爆炸、同步和输出局部性差的问题；
- 因此 sparse 领域常常更适合 hybrid、row-wise、merge-on-chip 之类折中方案。[OuterSPACE] [SpArch]

这并不推翻 dense 场景下对外积的偏好，只是说明：

- `dense`: 外积/块外积的输入复用优势通常能兑现；
- `sparse`: 外积的 psum 管理成本会被放大，纯外积不一定最优。

## 面向实现的建议

### 若目标是 dense INT8/INT4 推理阵列

更推荐：

- 使用 `块外积 + systolic / local broadcast` 组织乘法阵列；
- 输出 tile 的 psum 尽量留在局部 SRAM 或 register file；
- accumulator 位宽按 `K` 和饱和策略做精确预算，不要机械全用 32-bit；
- 如果系统允许，采用分段归约后再高精度合并，而不是每一段都早早量化。

不推荐：

- 为了“看起来更像内积”而牺牲数据复用，导致输入搬运成本过高；
- 为了省 accumulator 而过早截断，最后把误差转移到模型精度上。

### 若目标是 FP16/BF16/FP8 训练或高精度推理

更推荐：

- 阵列仍然采用块外积式高复用数据流；
- accumulator 至少比输入类型更宽；
- 对长 K 归约使用 pairwise、tree、grouped 或 exponent-aware 累加；
- 评估 swamping，而不只看 overflow。

不推荐：

- 只优化 multiplier，忽略 accumulation order；
- 假设“外积天然更不准”或“内积天然更准”。真实差异通常来自归约实现细节。

### 若目标是可编程通用矩阵扩展

如果 ISA 需要提供通用 tile 指令或 dot-product 指令：

- 可以在 ISA 上暴露 dot-product / MMA；
- 但在微架构上仍然优先考虑块外积式阵列；
- 软件可见语义和物理数据流不必一一对应。

这也是很多现代矩阵扩展的常见做法。

## 最终判断

如果问题被精确定义为：

> 在低精度 dense 矩阵乘里，从电路复杂度和精度综合来看，应该更偏向外积还是内积？

那么本文给出的判断是：

- `计算数据流` 上，通常更偏向 `外积 / 块外积`
  因为它更适合高吞吐阵列、更省输入搬运、更容易做规则局部通信。
- `数值实现` 上，必须高度重视 `accumulator`
  因为低精度时代真正难的是 partial sum 的动态范围和舍入误差，而不是低比特乘法本身。
- 因此最佳工程选择通常是：
  `外积式乘法阵列 + 更强的累加器与归约设计`

反过来说，如果只能在“纯外积 + 弱累加器”和“纯内积 + 强累加器”之间二选一，很多时候后者反而更容易得到可用精度。真正的高质量设计不会这样二选一，而是同时优化两边。

## 参考文献

- [BLIS] Tyler M. Smith et al., "Analytical Modeling Is Enough for High-Performance BLIS", discussion of GEMM micro-kernel as rank-1 outer-product updates.
  Link: <https://www.cs.utexas.edu/~flame/pubs/flawn74.pdf>

- [TPU] Norman P. Jouppi et al., "In-Datacenter Performance Analysis of a Tensor Processing Unit", ISCA 2017.
  Link: <https://www.cs.cmu.edu/~18742/papers/Jouppi2017.pdf>

- [AMX] Intel, `_tile_dpbf16ps` / Intel AMX BF16 tile dot-product documentation.
  Link: <https://www.intel.com/content/www/us/en/docs/cpp-compiler/developer-guide-reference/2021-8/tile-dpbf16ps.html>

- [Eyeriss] Yu-Hsin Chen, Tushar Krishna, Joel S. Emer, and Vivienne Sze, "Eyeriss: An Energy-Efficient Reconfigurable Accelerator for Deep Convolutional Neural Networks", IEEE JSSC 2017.
  Link: <https://people.csail.mit.edu/emer/media/papers/2016.06.isca.eyeriss_architecture.pdf>

- [FP8-DOT4] David R. Lutz et al., "Fused FP8 4-Way Dot Product With Scaling and FP32 Accumulation", ARITH 2024.
  Link: <https://www.ac.uma.es/arith2024/papers/Fused%20FP8%204-Way%20Dot%20Product%20with%20Scaling%20and%20FP32%20Accumulation.pdf>

- [DeepSeek-V3] DeepSeek-AI, "DeepSeek-V3 Technical Report", section 3.5.2 on hardware suggestions for FP8 accumulation precision.
  Link: <https://stardust108.github.io/DeepSeek-V3/DeepSeek_V3.pdf>

- [ABS] Charbel Sakr et al., "Accumulation Bit-Width Scaling For Ultra-Low Precision Training Of Deep Networks", ICLR 2019.
  Link: <https://arxiv.org/abs/1901.06588>

- [A2Q] Ian Colbert et al., "A2Q: Accumulator-Aware Quantization with Guaranteed Overflow Avoidance", 2023.
  Link: <https://arxiv.org/abs/2308.13504>

- [PQS] Vikas Natesh and H. T. Kung, "PQS (Prune, Quantize, and Sort): Low-Bitwidth Accumulation of Dot Products in Neural Network Computations", 2025 arXiv preprint.
  Link: <https://arxiv.org/abs/2504.09064>

- [MGS] Vikas Natesh, H. T. Kung, and David Kong, "MGS: Markov Greedy Sums for Accurate Low-Bitwidth Floating-Point Accumulation", 2025 arXiv preprint.
  Link: <https://arxiv.org/abs/2504.09072>

- [DGA] Yixiong Yang et al., "Toward Low-Bit Neural Network Training Accelerator by Dynamic Group Accumulation", ASP-DAC 2022 tutorial/slides.
  Link: <https://aspdac2022.github.io/taoka/pdf/6C-2.pdf>

- [SR-FP12] Sami Ben Ali, Silviu-Ioan Filip, and Olivier Sentieys, "A Stochastic Rounding-Enabled Low-Precision Floating-Point MAC for DNN Training", DATE 2024 / arXiv 2024.
  Link: <https://arxiv.org/abs/2404.14010>

- [ExactDot] Jack Koenig, "A Hardware Accelerator for Computing an Exact Dot Product", UC Berkeley Technical Report UCB/EECS-2018-51, 2018.
  Link: <https://www2.eecs.berkeley.edu/Pubs/TechRpts/2018/EECS-2018-51.html>

- [OuterSPACE] Austin Rovinski et al., "OuterSPACE: An Outer Product Based Sparse Matrix Multiplication Accelerator", HPCA 2018.
  Link: <https://blaauw.engin.umich.edu/wp-content/uploads/sites/342/2019/12/OuterSPACE-An-Outer-Product-based-Sparse-Matrix-Multiplication-Accelerator.pdf>

- [SpArch] Zhenyuan Zhang et al., "SpArch: Efficient Architecture for Sparse Matrix Multiplication", HPCA 2020.
  Link: <https://arxiv.org/abs/2002.08947>

## 附：本文的工作性判断

为了避免过度概括，本文对文献的使用方式如下：

- 对 `dense 外积更适合阵列化` 的判断，主要依据 BLIS 的 rank-1 update 组织方式，以及 TPU 的 systolic 数据流描述。
- 对 `低精度主要受 accumulator 约束` 的判断，主要依据 ABS、A2Q、PQS、MGS。
- 对 `外积会把问题转移到 partial sums` 的判断，dense 侧是工程推断，sparse 侧有 OuterSPACE 和 SpArch 的直接证据。

因此最稳妥的总结不是“外积更准”或“内积更省电”，而是：

- `dense 吞吐实现偏外积`
- `低精度稳健性偏重累加器`
- `真正最优方案往往是二者组合`
