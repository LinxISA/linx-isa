# 第 2 阶段：ISA 规范集成

事实来源：`isa/v0.56/**`（编译为`isa/v0.56/linxisa-v0.56.json`）

支持上下文：
- `isa/README.md`
- `isa/generated/codecs/`（生成的解码/编码工件）

## 规则

编译器、仿真器和 RTL 行为必须源自同一目录，或根据同一目录进行检查。

## 再生

```bash
python3 tools/isa/build_golden.py --profile v0.56 --pretty
python3 tools/isa/validate_spec.py --spec isa/v0.56/linxisa-v0.56.json
```