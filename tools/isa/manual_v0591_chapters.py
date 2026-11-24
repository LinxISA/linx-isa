#!/usr/bin/env python3
"""Select architecture chapters and examples for the 0.59.1 instruction set."""

from __future__ import annotations

from functools import lru_cache
import re
from typing import Iterable


# These roots describe the retired two-level vector and memory-block model.
# Exact instruction articles are normally removed by catalog filtering.  The
# roots also cover family tutorials that have no one-to-one catalog row.
OBSOLETE_SOURCE_PARTS = (
    "/inst/misa_v/",
    "/blockIntro/vecinstrs/",
    "/blockIntro/vec_block/",
    "/blockIntro/mem_block/",
)

OBSOLETE_SOURCE_FILES = frozenset(
    {
        "docs/zh/isa/header/B.TEXT.md",
        "docs/zh/isa/header/BSTART.MPAR.md",
        "docs/zh/isa/header/BSTART.MSEQ.md",
        "docs/zh/isa/header/BSTART.VPAR.md",
        "docs/zh/isa/header/BSTART.VSEQ.md",
        "docs/zh/isa/header/C.BSTART.MPAR.md",
        "docs/zh/isa/header/C.BSTART.MSEQ.md",
        "docs/zh/isa/header/C.BSTART.VPAR.md",
        "docs/zh/isa/header/C.BSTART.VSEQ.md",
        "docs/zh/isa/arch/executemode.md",
        "docs/zh/isa/arch/corestate.md",
        "docs/zh/isa/register/common/vgpr.md",
        "docs/zh/isa/register/common/pred.md",
        "docs/zh/isa/register/ssr/LCFR.md",
        "docs/zh/isa/register/ssr/LCFR_EN.md",
    }
)

# These phrases name the removed programming model even when a page does not
# spell one of its opcodes.  They are intentionally narrower than generic
# words such as "vector", "lane" or "block", which remain valid for Tile VEC.
OBSOLETE_CONCEPT = re.compile(
    r"(?<![A-Za-z0-9_.])V\.[A-Z][A-Z0-9]*(?:\.[A-Z0-9]+)*\b|分离块|向量数据块|访存数据块|(?:Decoupled|Memory|Vector)\s+Block|"
    r"(?<![A-Za-z0-9_.])(?:MSEQ|MPAR|VSEQ|VPAR)(?![A-Za-z0-9_.])|"
    r"(?<![A-Za-z0-9_.])B\.(?:EQ|NE|LT|GE|LTU|GEU|Z|NZ)(?![A-Za-z0-9_.])|"
    r"(?<![A-Za-z0-9_.])LCFR(?:_EN)?(?![A-Za-z0-9_.])|"
    r"(?<![A-Za-z0-9_.])V(?:T|U|M|N)(?:#[1-4])?(?![A-Za-z0-9_.])",
    re.I,
)


ACTIVE_REPLACEMENTS = {
    "docs/zh/isa/blockIntro/tepl_block/intro.md": """# TEPL 编码载体

## 架构角色

TEPL 是 VEC 与 SFU Tile 操作共用的 Mode/Function 编码载体，不是执行单元。当前 0.59.1 Tile 目录把每个 TEPL selector 唯一归入一个语义引擎：VEC 有 32 个逐元素操作，SFU 有 47 个复杂操作。TLSU 的 28 个操作和 CUBE 的 12 个操作使用各自的命令编码族；四类合计 119 个直接 Tile 操作。

`BSTART.TEPL` 是编译后的译码身份。汇编器对 VEC 操作接受 `BSTART.VEC`，对 SFU 操作接受 `BSTART.SFU`；这两个名称是由操作归属决定的规范别名，不增加译码身份或编码空间。完整选择子及其命令页见[现行 Tile 操作目录](../../header/tileblock/intro.md)。

## VEC 操作（32）

VEC 只承担逐元素 Tile/Tile、Tile/标量和立即数计算：

`TADD`、`TSUB`、`TMUL`、`TAND`、`TOR`、`TXOR`、`TSHL`、`TSHR`、`TMAX`、`TMIN`、`TCMP`、`TABS`、`TNOT`、`TNEG`、`TRELU`、`TSEL`、`TCVT`、`TFMA`、`TADDS`、`TSUBS`、`TMULS`、`TANDS`、`TORS`、`TXORS`、`TSHLS`、`TSHRS`、`TMAXS`、`TMINS`、`TCMPS`、`TSELS`、`TEXPANDS`、`TLEA`。

代表性操作页：[TADD](../../header/tileblock/TADD.md) · [TCVT](../../header/tileblock/TCVT.md) · [TFMA](../../../architecture/isa-manual/supplements/tfma.md) · [TLEA](../../../architecture/isa-manual/supplements/tlea.md)

## SFU 操作（47）

SFU 承担除法、超越函数、归约、展开、重排和其他复杂操作：

`TDIV`、`TREM`、`TEXP`、`TLOG`、`TRECIP`、`TSQRT`、`TRSQRT`、`TDIVS`、`TREMS`、`TROWSUM`、`TROWMAX`、`TROWMIN`、`TROWPROD`、`TROWEXPAND`、`TROWEXPANDADD`、`TROWEXPANDSUB`、`TROWEXPANDMUL`、`TROWEXPANDDIV`、`TROWEXPANDMAX`、`TROWEXPANDMIN`、`TROWEXPANDEXPDIF`、`TROWARGMAX`、`TROWARGMIN`、`TCOLSUM`、`TCOLMAX`、`TCOLMIN`、`TCOLPROD`、`TCOLEXPAND`、`TCOLEXPANDADD`、`TCOLEXPANDSUB`、`TCOLEXPANDMUL`、`TCOLEXPANDDIV`、`TCOLEXPANDMAX`、`TCOLEXPANDMIN`、`TCOLEXPANDEXPDIF`、`TCOLARGMAX`、`TCOLARGMIN`、`TCI`、`TTRI`、`TGATHER`、`TSCATTER`、`TPERMUTE`、`TSHUF`、`TPACK`、`TUNPACK`、`TGPR2T`、`TEXPDIF`。

代表性操作页：[TDIV](../../header/tileblock/TDIV.md) · [TROWSUM](../../header/tileblock/TROWSUM.md) · [TPERMUTE](../../../architecture/isa-manual/supplements/tpermute.md) · [TEXPDIF](../../../architecture/isa-manual/supplements/texpdif.md)

## 块行为

TEPL 操作由块头完整描述。`B.DIM`、`B.DATR`、`B.IOT`、`B.IOS` 和 `B.IOR` 是否出现及其字段含义由所选操作的当前合同决定。每个操作页给出操作数、布局、数据类型、掩码、异常和结果发布条件。
""",
    "docs/zh/isa/blockIntro/cube_block/intro.md": """# CUBE 矩阵操作块

CUBE 提供 12 个完整块头驱动的矩阵乘和矩阵-向量操作。软件用 `B.DIM` 指定逻辑 M、N、K，用 `B.DATR` 指定 BType、CCTRL、舍入和饱和控制，用且仅用一条 `B.FPATR` 关闭后处理 schema，再通过 `B.IOT` 或合法的 `B.IOS` 绑定显式输入和目的。操作在提交边界完成预检并原子发布结果，不存在软件可见的隐藏 ACC。

## 当前操作

| 操作 | 说明 |
| --- | --- |
| [TMATMUL](../../header/tileblock/TMATMUL.md) | 矩阵乘，写新分配的显式目的 D |
| [TMATMUL_BIAS](../../header/tileblock/TMATMUL.BIAS.md) | 矩阵乘加显式 Bias |
| [TMATMUL_ACC](../../header/tileblock/TMATMUL.ACC.md) | 读取显式累加源 C，写不同的目的 D |
| [TMATMUL_MX](../../header/tileblock/TMATMULMX.md) | 带操作数 scale 的矩阵乘 |
| [TMATMUL_MX_BIAS](../../header/tileblock/TMATMULMX.BIAS.md) | 带 scale 和显式 Bias |
| [TMATMUL_MX_ACC](../../header/tileblock/TMATMULMX.ACC.md) | 带 scale，读取 C 并写不同的 D |
| [TGEMV](../../header/tileblock/TGEMV.md) | M 固定为 1 的矩阵-向量乘 |
| [TGEMV_BIAS](../../header/tileblock/TGEMV.BIAS.md) | 矩阵-向量乘加显式 Bias |
| [TGEMV_ACC](../../header/tileblock/TGEMV.ACC.md) | 读取显式 C，写不同的 D |
| [TGEMV_MX](../../header/tileblock/TGEMVMX.md) | 带 scale 的矩阵-向量乘 |
| [TGEMV_MX_BIAS](../../header/tileblock/TGEMVMX.BIAS.md) | 带 scale 和显式 Bias |
| [TGEMV_MX_ACC](../../header/tileblock/TGEMVMX.ACC.md) | 带 scale，读取 C 并写不同的 D |

## Local 布局、形状与类型

Local A 使用持久的 `CUBE_M16` 或 `CUBE_M32` 布局，Local B 使用 `CUBE_N8`，新目的 D 使用 A 的 M 布局。TMATMUL 的 M、N、K 是与每 PE Tile 容量独立的任意正值；TGEMV 固定 M=1，但 N、K 仍是任意正值。合法性由描述符、容量和具体操作合同决定，不存在统一的 M16、固定 512 B 分形或固定 1024 B 输出要求。

AType 与 BType 必须满足对应操作支持的数值类型合同。MX 形式按输入类型要求 E8M0 或 U32 scale；Bias 和后处理辅助 Tile 使用各自规定的布局与类型。实现不得在操作前把所有输入一律转换为 FP32 或 INT32；内部累加类型、最终 D 类型、舍入、饱和和可选后处理均以具体操作页为准。

## 累加与别名

所有成功操作都发布一个新目的 D。ACC 形式同时要求显式 Local 累加源 C；译码块中 C 的六位相对选择器必须在 rename 前与零扩展的 DstTile 不同，直接 Tile 调用中目的 TileIndex 也必须与累加 TileIndex 不同。C 在乘法前取快照，成功或拒绝后其描述符和数据都不改变。因此 `C == D` 非法，不能解释成读旧值后原位写回。

## Shared 边界

TMATMUL 可以按操作合同使用右侧 Shared 输入或两侧 Shared 输入；协作形式的非零 PE 掩码必须为 `1111`，并按 group_M、物理 pitch、发布就绪和可选 TransA/TransB 规则检查。TGEMV 是 Local-only，所有有效 Shared 绑定和非零 TransA/TransB 都在产生效果前拒绝。补充输入和所有目的保持 Local。

掩码为零的形式在描述符读取、故障、分配、就绪检查和生命周期效果前严格空操作。非零形式必须在第一个架构效果前完成完整的类型、形状、布局、别名、资源和后处理预检。
""",
    "docs/zh/isa/exception/exception.md": """# 异常模型

同步异常由当前指令检测，异步中断由指令流之外的事件触发。除具体操作另有明确规定外，发生异常的指令不提交架构可见效果；保存的位置指向原始指令，使软件在处理完成后能够重试。异常号、原因和附加参数使用当前 0.59.1 系统寄存器目录中的 `TRAPNO_ACRn`、`TRAPARG0_ACRn`、`ECSTATE_ACRn`、保存 PC 和块参数状态。[TRAPNO 说明](../register/ssr/TRAPNO.md)

系统软件负责保存任务所需的标量 T、U 和 Tile 数据。各操作的异常说明给出故障时已经提交的效果和重试位置。

## TLSU 访存异常

TLSU 的全局内存地址使用发起上下文的数据地址翻译和权限规则。地址翻译、权限或总线失败进入当前精确数据异常路径；`TRAPARG0` 保存该路径定义的故障虚拟地址。操作页规定完整预检、部分效果、重复地址顺序和目标发布边界。现行 TLSU 操作及其逐项异常合同见[Tile 操作目录](../header/tileblock/intro.md)。

## CUBE 首次使用

0.59.1 Sail 模型 只实现 CUBE 首次使用检查。检查条件是当前上下文位于 ACR2，且 `ECONFIG_ACR1` 的 CUBE 位 33 为 1。检查覆盖当前目录中 `family=CUBE`、`engine=CUBE` 的 12 个矩阵操作，并发生在块头目标预检之后、块状态转换和 Tile 效果开始之前。

触发时 Sail 产生精确的同步指令异常：`TRAPNO.E=1`、`TRAPNO.ARGV=1`、`TRAPNO.TRAPNUM=E_INST (0)`、`TRAPNO.CAUSE=EC_PERM (4)`、`TRAPARG0=1`、`ECSTATE.BI=0`。异常发生在操作数消费、块状态修改、Tile 分配、队列接纳、访存请求和其他架构效果之前；处理完成后可以重试原始 CUBE 块头。

当前规范没有第二类扩展首次使用入口；软件不得把 CUBE 信封中的种类、使能位或参数值推广为其他执行上下文。

## 规范边界

PTO 导入的标量、命令和 Tile 合同定义各操作的合法性、故障优先级和效果原子性。LinxISA 的 Sail 模型给出上述 CUBE 首次使用异常的寄存器值。平台规定上下文分配、调度时的驻留策略和异常服务路由。
""",
    "docs/zh/isa/arch/prgorder.md": """# 程序序与可见性

程序序描述一条执行流中指令的先后关系。块头先登记操作和操作数绑定。块体指令在当前块的约束下读取状态。提交时，按该操作定义的依赖、故障检查和写回顺序产生架构效果。

以矩阵乘累加为例，A、B 提供乘法输入，C 是显式的本地累加源。操作读取 C 的旧值，并把累加结果写入新分配的目标 D。C 和 D 必须是不同的绑定。下一条使用结果的操作读取 D。

跨 PE 的内存可见性还取决于访问作用域、原子操作及同步指令。实现可以并行安排彼此独立的计算，但必须满足各指令规定的可见顺序。
""",
    "docs/zh/isa/arch/bisa.md": """# 块指令与生命周期

Linx 程序以块作为配置、提交和恢复边界。块头建立块类型、控制流参数以及本次操作需要的属性和资源绑定；块体中的标量指令按当前块类型检查适用性；`BSTOP` 或下一条 `BSTART` 形成提交边界。

## 当前块类型

- `BSTART.STD` 建立整型标量块。
- `BSTART.FP` 建立浮点标量块。
- `BSTART.SYS` 建立系统块。
- `BSTART.TEPL` 及其 `BSTART.VEC`、`BSTART.SFU` 规范别名选择 Tile VEC 或 SFU 操作。
- TLSU 和 CUBE 操作由各自的 Tile 操作块头选择。

Tile 块可以先登记 `B.DIM`、`B.DATR`、`B.IOR`、`B.IOT`、`B.IOS` 等配置与绑定。进入块体后，普通标量指令仍保持当前 Tile 块类型，并按该操作的适用条件执行。完整操作在提交边界读取已经登记的块头状态。

## 控制状态

`BPC` 记录当前块起点，`TPC` 指向当前块内的指令。块头中的转移类型决定下一个块地址；提交前产生的异常按当前块的恢复状态处理。具体目标计算和返回地址写回以对应块头指令页为准。
""",
    "docs/zh/isa/arch/branch.md": """# 块间控制流

块头决定当前块完成后的控制流。控制流参数在块头执行时记录，在块提交边界生效。

## 转移类型 {#branch}

- **FALL**：顺延到编码规定的下一块地址。
- **DIRECT**：使用 PC 相对的直接目标。
- **CALL**：选择调用目标。是否写入 `ra` 由具体块头形式决定。
- **COND**：根据块内设置的提交条件选择目标或顺延路径。
- **IND**：从架构寄存器状态读取间接目标。
- **ICALL**：组合间接目标与调用返回状态。
- **RET**：使用已保存的返回状态。

`HL.BSTART.CALL` 分别编码调用目标和返回目标。`L.BSTART.FP/STD CALL` 本身保留 `ra`；需要返回的代码须先用 `SETRET` 或 `C.SETRET` 建立返回地址。每个形式的 PC 基准、立即数字段和对齐要求见对应指令页。
""",
    "docs/zh/isa/arch/execute.md": """# 块指令执行模型

## 建立块

执行 `BSTART` 时，处理器结束上一块并初始化新的块描述符。块头命令在进入块体前登记维度、数据类型、标量寄存器和 Tile 绑定。相同属性被重复设置、绑定数量不合法或资源不可用时，必须在相应架构效果之前报告异常。

## 执行块体

第一条普通标量指令使块进入块体阶段。之后再执行块头配置命令会触发块控制异常，规范明确规定为零参与者的空操作除外。普通标量指令先按当前块类型检查适用性，再读取操作数和产生效果。Tile 操作的完整效果在提交时读取已经闭合的块描述符。

`TPC` 按成功执行的指令长度推进，`BPC` 保持当前块起点。T、U 临时队列和显式目的寄存器的发布顺序由具体指令定义。

## 提交与异常

`BSTOP` 或下一条 `BSTART` 形成提交边界。提交前先完成合法性、资源和地址预检；失败时按具体操作的异常规则保留或撤销效果。成功提交后，控制流使用块头记录的下一块目标继续执行。
""",
    "docs/zh/isa/arch/executemachine.md": """# 块指令执行机制

当前执行机制由块头配置阶段、标量块体阶段和提交阶段组成。块头配置写入当前块描述符；第一条普通标量指令关闭配置阶段；提交阶段执行 Tile 操作、发布结果并选择下一块地址。

配置、块体和提交共享同一个块身份。实现可以并行准备操作数或调度执行资源，但必须保持规范要求的操作数快照、异常先后和结果发布顺序。实现细节不得产生额外的架构寄存器、隐式累加器或软件可见入口。
""",
    "docs/zh/isa/arch/constraints.md": """# LinxISA 0.59.1 架构约束

## 块生命周期

块头配置只能在块体开始前执行。第一条普通标量指令关闭配置阶段；之后出现块头配置命令会触发块控制异常，规范声明为零参与者空操作的形式除外。`BSTOP` 或下一条 `BSTART` 形成提交边界。

Tile 操作的输入、目的、布局、类型、维度和资源绑定必须在第一个架构效果前完成检查。TLSU 和 CUBE 块按各自操作页定义合法性，并通过块头显式绑定 Local 或 Shared Tile。

## 状态与寄存器

- 每个 Tile 结果由一个显式目的产生，可以被零个或多个后续操作读取。
- `reuse` 和最后使用标记控制资源生命周期，不改变数据语义。
- T、U 是标量块内临时队列；Local、Shared Tile 的身份与大小由绑定命令定义。
- 带累加的矩阵操作读取显式 Local 输入 C，并写入显式目的 D。

## 指令合法性

每条指令只能在其发布定义允许的块类型中执行。操作数选择、别名、双目的写回顺序、访存对齐和异常原子性均以对应指令页为准。保留编码和未实现形式必须在读取操作数或产生架构效果前拒绝。
""",
    "docs/zh/isa/arch/exception.md": """# 中断和异常

中断是指令流水线外的异步事件，异常是当前指令检测到的同步事件。两者都通过当前 ACR 的路由状态选择处理入口，并保存恢复所需的块与指令位置。

## 块状态

成功执行的块在提交边界发布结果。异常指令按其定义保留或撤销效果，并把当前 BPC、TPC、BARG 和异常参数保存到发布版系统寄存器目录指定的位置。标量 T、U 或 Tile 数据是否由软件进一步保存，由异常处理环境决定。

## 异常与陷出

处理器在进入服务请求前记录异常号和参数，切换到目标 ACR，并从该 ACR 的异常基址开始执行。恢复时使用已保存的块地址、指令地址和块参数。主动修复路径只适用于规范明确允许接管的异常。
""",
    "docs/zh/isa/exception/acr_switch.md": """# ACR 切换

外部中断、同步异常以及 `ACRE`、`ACRC` 和系统调用块可以改变当前 ACR。切换同时更新异常路由、当前执行状态和后续取指位置。

## ACR_ENTER

`ACRE` 在块提交时请求进入目标 ACR。处理器检查目标关系，从目标上下文恢复 CSTATE、BPC 和按指令选择的 BARG 状态，再从恢复位置继续执行。

## SERVICE_REQUEST

`ACRC`、同步异常和异步中断可以发起服务请求。处理器把当前 CSTATE、BPC、TPC、BARG、异常号和参数保存到目标 ACR 的系统寄存器，随后清理当前块参数并把 BPC 设置为该 ACR 的异常入口。整个架构状态切换作为一个不可分割的过程完成。

浮点标志、异常号、参数和返回所需状态的具体字段以 0.59.1 系统寄存器目录及对应指令页为准。
""",
    "docs/zh/isa/register/common/intro.md": """# 架构状态

## 全局状态

全局状态包括通用寄存器、系统寄存器、程序计数、内存以及 Local、Shared Tile 状态。异常上下文保存恢复所需的块地址、指令地址和块参数。

## 块状态

每个活动块有独立的块描述符，记录块类型、下一块目标、维度、数据属性、标量绑定与 Tile 绑定。标量 T、U 队列提供块内临时结果。Tile 操作使用显式 Local 或 Shared 源和目的；带累加的操作显式读取累加源并写入显式目的。

## 状态提交

指令按各自定义读取源快照并发布结果。块头配置在进入块体前完成，Tile 操作在提交边界读取完整描述符。异常和恢复只使用规范列出的状态，不引入隐藏软件可见状态。
""",
    "docs/zh/isa/blockIntro/tlsu_block/intro.md": """# TLSU 数据搬运块

TLSU 在全局内存与 Tile 寄存器之间执行数据搬运、预取、gather、scatter、掩码访问和索引原子操作。每个操作由发布目录中的 TLSU Tile 选择器和完整块描述符确定。

## 配置与绑定

`BSTART.TLOAD`、`BSTART.TSTORE`、`BSTART.TMOV`、`BSTART.TPREFETCH` 及索引传输块头选择具体操作。`B.DIM` 给出有效形状，`B.DATR` 给出数据属性，`B.IOR` 绑定标量地址参数，`B.IOT` 或 `B.IOS` 绑定 Tile 源和目的。

## 执行边界

操作在产生第一个架构效果前完成块描述符、布局、类型、资源和地址预检。执行掩码未启用的位置不产生地址或内存效果。具体对齐、错误原子性、重复地址顺序和目标发布规则见每个 Tile 操作页。
""",
}


def _obsolete_pattern(names: Iterable[str]) -> re.Pattern[str]:
    # Longest first prevents a shorter family spelling from hiding a suffix.
    alternatives = "|".join(
        re.escape(name) for name in sorted(names, key=len, reverse=True)
    )
    return re.compile(rf"(?<![A-Za-z0-9_.])(?:{alternatives})(?![A-Za-z0-9_.])", re.I)


@lru_cache(maxsize=4)
def _cached_pattern(names: tuple[str, ...]) -> re.Pattern[str]:
    return _obsolete_pattern(names)


def obsolete_mentions(text: str, names: Iterable[str]) -> tuple[str, ...]:
    """Return obsolete mnemonic and programming-model terms visible in text."""
    ordered = tuple(sorted(set(names)))
    hits = {
        match.group(0).upper()
        for match in (_cached_pattern(ordered).finditer(text) if ordered else ())
    }
    hits.update(match.group(0) for match in OBSOLETE_CONCEPT.finditer(text))
    return tuple(sorted(hits))


def _filter_mixed_markdown(text: str, names: Iterable[str]) -> str:
    """Drop conflicting prose, fences, table rows or list items locally."""
    lines = text.splitlines(keepends=True)
    kept: list[str] = []
    index = 0
    while index < len(lines):
        line = lines[index]
        if line.lstrip().startswith("```"):
            end = index + 1
            while end < len(lines) and not lines[end].lstrip().startswith("```"):
                end += 1
            end = min(end + 1, len(lines))
            block = "".join(lines[index:end])
            if not obsolete_mentions(block, names):
                kept.extend(lines[index:end])
            index = end
            continue
        if line.startswith(("|", "- ", "* ", "+ ")):
            if not obsolete_mentions(line, names):
                kept.append(line)
            index += 1
            continue
        if not line.strip() or re.match(r"^#{1,6}\s", line):
            kept.append(line)
            index += 1
            continue
        end = index + 1
        while (
            end < len(lines)
            and lines[end].strip()
            and not re.match(r"^#{1,6}\s", lines[end])
            and not lines[end].startswith(("|", "- ", "* ", "+ ", "```"))
        ):
            end += 1
        block = "".join(lines[index:end])
        if not obsolete_mentions(block, names):
            kept.extend(lines[index:end])
        index = end

    # Remove headings with no remaining body before the next same/higher-level
    # heading. Blank lines are ignored while deciding whether a body remains.
    changed = True
    while changed:
        changed = False
        for index, line in enumerate(kept):
            match = re.match(r"^(#{2,6})\s", line)
            if not match:
                continue
            level = len(match.group(1))
            body = False
            for candidate in kept[index + 1 :]:
                heading = re.match(r"^(#{1,6})\s", candidate)
                if heading and len(heading.group(1)) <= level:
                    break
                if candidate.strip() and not heading:
                    body = True
                    break
            if not body:
                kept.pop(index)
                changed = True
                break
    result = "".join(kept)
    return re.sub(r"\n{3,}", "\n\n", result).strip() + "\n" if result.strip() else ""


def active_markdown(
    path: str, markdown: str, obsolete_names: Iterable[str]
) -> str | None:
    """Return a coherent 0.59.1 article or None for a wholly retired topic."""
    if path in ACTIVE_REPLACEMENTS:
        revised = ACTIVE_REPLACEMENTS[path].strip() + "\n"
    else:
        normalized = "/" + path.replace("\\", "/").lstrip("/")
        if path in OBSOLETE_SOURCE_FILES or any(
            part in normalized for part in OBSOLETE_SOURCE_PARTS
        ):
            return None
        if not obsolete_mentions(markdown, obsolete_names):
            return markdown
        revised = _filter_mixed_markdown(markdown, obsolete_names)
    if not revised or obsolete_mentions(revised, obsolete_names):
        return None
    return revised
