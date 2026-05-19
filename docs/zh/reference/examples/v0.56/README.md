# 灵犀指令集 组装示例包 (v0.56)

灵犀指令集 v0.56 的规范公共汇编示例。

## 布局

- `curated/`：审查了手工策划的示例。
- `scratch-legacy/`：选定的迁移的暂存程序集（公共允许列表）。
- `generated/`：从 PTO 示例生成的确定性输出。
- `legacy-reference/`：移动历史参考示例。
- `index.yaml`：带有出处和生成命令的清单。

## 规范示例

```asm
BSTART.TMA   TLOAD, FP16
B.ARG        ND2ZN.normal, FP16, Null
B.IOT       [], last ->t<4KB>
B.IOR        [x2,a6],[]
C.B.DIMI     64, ->lb0
C.B.DIMI     64, ->lb1
C.B.DIMI     64, ->lb2
```

来源：`docs/reference/examples/v0.56/curated/linxisa-v0.56-normalized.asm`