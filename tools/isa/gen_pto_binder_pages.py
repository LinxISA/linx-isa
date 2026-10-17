#!/usr/bin/env python3
"""Generate binder references from the pinned PTO owning ASL contracts."""

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def pages():
    profile = ROOT / "isa/v0.58"
    lock = json.loads((profile / "pto-scalar-proposal.lock.json").read_text())
    owners = json.loads((profile / "state/pto_binder_contracts.json").read_text())["instructions"]
    forms = json.loads((profile / "state/pto_command_forms.json").read_text())["forms"]
    for name in ("B.IOT", "B.IOS"):
        records = [form for form in forms if form["mnemonic"] == name]
        syntax = [part.strip() for form in records for part in form["asm"].split(" | ")]
        url = f"https://github.com/PTO-ISA/pto-spec/blob/{lock['source']['commit']}/{owners[name]['source']}"
        for chinese in (False, True):
            lines = [f"# {name}", "", f"{'唯一规范来源' if chinese else 'Sole normative source'}: [PTO-SPEC golden]({url}).", "",
                     "## 汇编形式" if chinese else "## Assembly forms", "", "```asm", *syntax, "```", "",
                     "## 编码" if chinese else "## Encodings", "", "| PTO form | mask | match | fields |", "| --- | --- | --- | --- |"]
            for record in records:
                part = record["encoding"][0]
                fields = "; ".join(f"{field['name']}=" + ",".join(
                    f"{piece['instruction_lsb'] + piece['width'] - 1}:{piece['instruction_lsb']}"
                    for piece in field["pieces"]) for field in record["fields"])
                lines.append(f"| `{record['form_id']}` | `{part['mask']}` | `{part['match']}` | {fields} |")
            if chinese:
                lines += ["", "## 语义边界", "",
                    "显式 `.reuse` 保留所选源的数据；省略 `.reuse` 表示最后一次使用，在成功且未被取消的块完成时消耗对应的数据容量。旧编码的规范打印形式包含 `.reuse`。",
                    "Local 源按参与 PE 消耗数据容量；Shared 源消耗完整 Core 范围的数据容量。寄存器代次身份和描述符保留。",
                    "`PEMode=000` 在位置、重复、分配、描述符及内存检查前为严格无副作用路径。其他 PEMode 的四 PE mask 由 golden 公共译码器定义。",
                    "B.IOT 的终止位 L 与源最后使用标记是不同维度。每个源的 `.reuse` 独立编码。B.IOS 使用绝对 Shared 名称 S0..S63。",
                    "纯源 `SizeCode=0` 不分配目的。Local 目的使用 1..10，每 PE 为 128 B..64 KiB；Shared 目的使用 1..12，完整 Core 对象为 128 B..256 KiB。其余大小码保留。",
                    "完整合法性、异常和状态转换以以上 PTO owning ASL 为准；本页编码表直接生成自同一 golden。",
                    "", "## 模型支持", "", "新增 LAST/LL/LR/RL 形式尚未在 Linx Sail 子集中实现；模型在产生效果前拒绝。编码存在不等于执行支持。"]
            else:
                for field in ("defaults", "legality", "state_effects", "memory_effects", "ordering", "exceptions"):
                    lines += ["", "## " + field.replace("_", " ").capitalize(), ""]
                    lines += ["- " + rule for rule in owners[name]["contract"].get(field, [])]
                lines += ["", "## Model support", "", "New LAST/LL/LR/RL forms are not implemented by the Linx Sail subset and reject before effects. Encoding presence does not establish execution support."]
            path = ROOT / ("docs/zh/isa/header" if chinese else "docs/isa/header") / f"{name}.md"
            yield path, "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    for path, text in pages():
        if args.check:
            if path.read_text() != text:
                raise SystemExit(f"stale PTO binder reference: {path}")
        else:
            path.write_text(text)
    print("OK: bilingual binder references match PTO golden")


if __name__ == "__main__":
    main()
