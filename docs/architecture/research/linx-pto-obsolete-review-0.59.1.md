# LinxISA v0.59.1 与 PTO 的扩展差异调研

2026-11-24 的调研以 LinxISA `v0.59.1` 和 PTO `v0.59.1.0` 为基线。两者共有 578 个基础编码形式和 705 个作用域封装，Linx 另有 216 个独有形式。119 个 Tile 操作按块头选择，单独计数。[发布对齐记录](../v0.59.1-pto-alignment.md)

调研核对了每个 Linx 独有形式的位宽、固定位掩码和匹配值。216 个形式均落入锁定的 PTO 编码预留范围。PTO 的 50 条预留记录还包含非零 FALL Fixup 载荷、条件分支保留名、TEPL 保留选择子。两侧按预留记录数相减无法得到指令差异数。[PTO 预留表](../../../isa/v0.59/state/extension_encoding_reservations.json)

分离块的去留还涉及 VS8/VS16、lane 谓词、向量寄存器与异常恢复。共享的块维度设置、Tile 绑定和标量 T/U 队列仍有独立的 PTO 定义；例如 `HL.QPUSH`、`HL.QPOP`、`HL.QMT` 属于共同集合。[PTO 命令形式](../../../isa/v0.59/state/pto_command_forms.json)

调研中的 A–I 分组已形成正式架构决策。193 个 obsolete 形式的完整清单、编码预留和其余 23 个形式的处置均以该决策为准。[已采纳的架构决策](../../zh/architecture/linx-two-level-block-obsolescence.md)
