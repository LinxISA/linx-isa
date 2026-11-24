"""Current LinxISA v0.59.1 datatype pages derived from the locked PTO format set."""

from __future__ import annotations

from dataclasses import dataclass
from html import escape
import json
from pathlib import Path
import re
from typing import Any


TILE_TYPES_SOURCE = "asl/arch/data-types/tile-data-types.asl"
MATRIX_SOURCE = "asl/tile/model/legality/matrix-functions.asl"
HIF_SCALE_SOURCE = "asl/arch/data-types/formats/hif4-scale.asl"
FORMAT_ROOT = "asl/arch/data-types/formats"


@dataclass(frozen=True)
class FloatingFormat:
    code: int
    name: str
    source: str
    carrier_bits: int
    lane_bits: int
    lanes: int
    sign_bits: int
    sign_bit: int
    exponent_bits: int
    fraction_bits: int
    bias: int | None
    low_zero: int = 0
    high_zero: int = 0
    zero: bool = True
    signed_zero: bool = True
    subnormal: bool = True
    infinity: bool = False
    quiet_nan: bool = False
    signaling_nan: bool = False
    exponent_bits_min: int | None = None
    fraction_bits_min: int | None = None


FLOATING = {
    item.name: item
    for item in (
        FloatingFormat(
            0,
            "FP64",
            "fp64.asl",
            64,
            64,
            1,
            1,
            63,
            11,
            52,
            1023,
            infinity=True,
            quiet_nan=True,
            signaling_nan=True,
        ),
        FloatingFormat(
            1,
            "FP32",
            "fp32.asl",
            32,
            32,
            1,
            1,
            31,
            8,
            23,
            127,
            infinity=True,
            quiet_nan=True,
            signaling_nan=True,
        ),
        FloatingFormat(
            2,
            "TF32",
            "tf32.asl",
            32,
            32,
            1,
            1,
            31,
            8,
            10,
            127,
            low_zero=13,
            infinity=True,
            quiet_nan=True,
            signaling_nan=True,
        ),
        FloatingFormat(
            3,
            "HF32",
            "hf32.asl",
            32,
            32,
            1,
            1,
            31,
            8,
            11,
            127,
            low_zero=12,
            infinity=True,
            quiet_nan=True,
            signaling_nan=True,
        ),
        FloatingFormat(
            4,
            "FP16",
            "fp16.asl",
            16,
            16,
            1,
            1,
            15,
            5,
            10,
            15,
            infinity=True,
            quiet_nan=True,
            signaling_nan=True,
        ),
        FloatingFormat(
            5,
            "BF16",
            "bf16.asl",
            16,
            16,
            1,
            1,
            15,
            8,
            7,
            127,
            infinity=True,
            quiet_nan=True,
            signaling_nan=True,
        ),
        FloatingFormat(
            6,
            "HiF8",
            "hif8.asl",
            8,
            8,
            1,
            1,
            7,
            4,
            3,
            None,
            signed_zero=False,
            infinity=True,
            quiet_nan=True,
            exponent_bits_min=0,
            fraction_bits_min=1,
        ),
        FloatingFormat(7, "E4M3", "e4m3.asl", 8, 8, 1, 1, 7, 4, 3, 7, quiet_nan=True),
        FloatingFormat(
            8,
            "E5M2",
            "e5m2.asl",
            8,
            8,
            1,
            1,
            7,
            5,
            2,
            15,
            infinity=True,
            quiet_nan=True,
            signaling_nan=True,
        ),
        FloatingFormat(9, "E3M2", "e3m2.asl", 8, 6, 1, 1, 5, 3, 2, 3, high_zero=2),
        FloatingFormat(10, "E2M3", "e2m3.asl", 8, 6, 1, 1, 5, 2, 3, 1, high_zero=2),
        FloatingFormat(11, "E2M1X2", "e2m1x2.asl", 8, 4, 2, 1, 3, 2, 1, 1),
        FloatingFormat(
            12, "E1M2X2", "e1m2x2.asl", 8, 4, 2, 1, 3, 0, 3, None, subnormal=False
        ),
        FloatingFormat(
            13,
            "E8M0",
            "e8m0.asl",
            8,
            8,
            1,
            0,
            0,
            8,
            0,
            127,
            zero=False,
            signed_zero=False,
            subnormal=False,
            quiet_nan=True,
        ),
        FloatingFormat(
            14, "HiF4X2", "hif4x2.asl", 8, 4, 2, 1, 3, 1, 2, 1, subnormal=False
        ),
        FloatingFormat(
            15,
            "E6M2",
            "e6m2.asl",
            8,
            8,
            1,
            0,
            0,
            6,
            2,
            48,
            zero=False,
            signed_zero=False,
            subnormal=False,
            quiet_nan=True,
        ),
        FloatingFormat(
            21,
            "RCPE6M2",
            "rcpe6m2.asl",
            8,
            8,
            1,
            0,
            0,
            6,
            2,
            48,
            zero=False,
            signed_zero=False,
            subnormal=False,
            quiet_nan=True,
        ),
    )
}

INTEGERS = {
    "S64": (16, 64, True),
    "S32": (17, 32, True),
    "S16": (18, 16, True),
    "S8": (19, 8, True),
    "S4X2": (20, 4, True),
    "U64": (24, 64, False),
    "U32": (25, 32, False),
    "U16": (26, 16, False),
    "U8": (27, 8, False),
    "U4X2": (28, 4, False),
}

MATRIX_MX = {"FP16", "BF16", "E4M3", "E5M2", "E2M1X2", "E1M2X2", "HiF4X2"}
MATRIX_E8M0 = {"E4M3", "E5M2", "E2M1X2", "E1M2X2"}


def _asset(name: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    return f"figures/datatypes/{slug}.svg"


_COLORS = ("#315b7d", "#2d7a72", "#a15d28", "#7057a3", "#7c3f62", "#536b37")


def _ranges(widths: list[int], total: int) -> list[str]:
    high = total - 1
    result = []
    for width in widths:
        low = high - width + 1
        result.append(str(high) if high == low else f"{high}:{low}")
        high = low - 1
    if high != -1:
        raise ValueError("datatype diagram fields do not cover the carrier")
    return result


def _floating_fields(item: FloatingFormat) -> list[tuple[str, int]]:
    if item.name == "HiF8":
        return [("S", 1), ("D/E/M 动态区", 7)]
    if item.name == "E1M2X2":
        return [("lane1 S", 1), ("lane1 M", 3), ("lane0 S", 1), ("lane0 M", 3)]
    if item.lanes == 2:
        lane = [("S", 1), ("E", item.exponent_bits), ("F", item.fraction_bits)]
        return [(f"lane1 {name}", width) for name, width in lane] + [
            (f"lane0 {name}", width) for name, width in lane
        ]
    fields: list[tuple[str, int]] = []
    if item.high_zero:
        fields.append(("必须为 0", item.high_zero))
    if item.sign_bits:
        fields.append(("S", item.sign_bits))
    if item.exponent_bits:
        fields.append(("E", item.exponent_bits))
    if item.fraction_bits:
        fields.append(("F", item.fraction_bits))
    if item.low_zero:
        fields.append(("必须为 0", item.low_zero))
    return fields


def _integer_fields(name: str) -> tuple[int, list[tuple[str, int]]]:
    _, bits, signed = INTEGERS[name]
    if name.endswith("X2"):
        lane = [("S", 1), ("数值", bits - 1)] if signed else [("数值", bits)]
        return 8, [(f"lane1 {label}", width) for label, width in lane] + [
            (f"lane0 {label}", width) for label, width in lane
        ]
    return bits, ([("S", 1), ("数值", bits - 1)] if signed else [("数值", bits)])


def _svg(
    name: str, total: int, fields: list[tuple[str, int]], description: str
) -> bytes:
    ranges = _ranges([width for _, width in fields], total)
    width, height, left, top, bar_width, bar_height = 1120, 260, 40, 54, 1040, 72
    x = left
    shapes = []
    legend = []
    for index, ((label, bits), bit_range) in enumerate(
        zip(fields, ranges, strict=True)
    ):
        field_width = bar_width * bits / total
        color = _COLORS[index % len(_COLORS)]
        shapes.append(
            f'<rect x="{x:.2f}" y="{top}" width="{field_width:.2f}" height="{bar_height}" fill="{color}" stroke="#f5f7fa" stroke-width="2"/>'
        )
        if field_width >= 48:
            shapes.append(
                f'<text x="{x + field_width / 2:.2f}" y="{top + 42}" text-anchor="middle" class="field">{escape(label)}</text>'
            )
        column_x = 46 + (index % 4) * 268
        row_y = 166 + (index // 4) * 31
        legend.append(
            f'<rect x="{column_x}" y="{row_y - 15}" width="18" height="18" rx="3" fill="{color}"/>'
            f'<text x="{column_x + 27}" y="{row_y}" class="legend">[{bit_range}] {escape(label)} · {bits} 位</text>'
        )
        x += field_width
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">
<title id="title">{escape(name)} 位域</title>
<desc id="desc">{escape(description)}；载体共 {total} 位，位段从高位到低位排列。</desc>
<style>.title{{font:600 24px system-ui,sans-serif;fill:#17212b}}.field{{font:600 15px system-ui,sans-serif;fill:white}}.legend{{font:15px system-ui,sans-serif;fill:#263746}}.bits{{font:13px ui-monospace,monospace;fill:#516270}}</style>
<rect width="1120" height="260" fill="#f7f9fc" rx="12"/>
<text x="40" y="33" class="title">{escape(name)} · {total} 位载体</text>
<text x="40" y="145" class="bits">bit {total - 1}</text><text x="1080" y="145" text-anchor="end" class="bits">bit 0</text>
{"".join(shapes)}{"".join(legend)}</svg>'''
    return svg.encode()


def _datatype_svg(name: str) -> bytes:
    if name in FLOATING:
        item = FLOATING[name]
        description = _layout(item)
        return _svg(name, item.carrier_bits, _floating_fields(item), description)
    total, fields = _integer_fields(name)
    return _svg(name, total, fields, f"{name} 整数载体")


def _hif_scale_svg() -> bytes:
    return _svg(
        "HiF4_SCALE",
        32,
        [("E1_16", 16), ("E1_8", 8), ("E6M2", 8)],
        "U32 分层缩放字：16 个四元素指数、8 个八元素指数和一个 E6M2 基础值",
    )


def _applicability(name: str) -> str:
    if name in {"FP16", "BF16"}:
        return "Matrix-MX 可把它作为主输入，并且该侧不绑定缩放 Tile。"
    if name in MATRIX_E8M0:
        return (
            "Matrix-MX 可把它作为主输入；每侧按 K 维每 32 个元素绑定一个 E8M0 缩放值。"
        )
    if name == "HiF4X2":
        return "在矩阵运算中，HiF4X2 用作 Matrix-MX 主输入；每侧按 K 维每 64 个元素绑定一个 U32 HiF4 缩放字。"
    if name == "E8M0":
        return (
            "Matrix-MX 使用 E8M0 作为 E4M3、E5M2、E2M1X2、E1M2X2 的每 32 元素缩放载体。"
        )
    return "该编码是已分配的 Tile DataType。具体操作是否接受它，仍由对应操作页的类型规则决定。Matrix-MX 不接受该类型作为主输入。"


def _specials(item: FloatingFormat) -> str:
    values = []
    if item.zero:
        values.append("零" if not item.signed_zero else "正零和负零")
    if item.subnormal:
        values.append("次正规数")
    if item.infinity:
        values.append("正负无穷")
    if item.quiet_nan:
        values.append("安静 NaN")
    if item.signaling_nan:
        values.append("信号 NaN")
    return "、".join(values) if values else "不定义零、次正规数、无穷或 NaN"


def _layout(item: FloatingFormat) -> str:
    if item.name == "HiF8":
        return "1 位符号；点域决定 0–4 位指数和 1–3 位尾数。不同点域共享一个 8 位载体。"
    if item.name == "E1M2X2":
        return "一个 8 位载体保存两个 4 位 lane；每个 lane 为 1 位符号和 3 位幅值，没有独立指数域。"
    if item.lanes == 2:
        return f"一个 8 位载体保存两个 4 位 lane；每个 lane 为 1 位符号、{item.exponent_bits} 位指数、{item.fraction_bits} 位尾数。"
    if item.sign_bits:
        layout = f"1 位符号、{item.exponent_bits} 位指数、{item.fraction_bits} 位尾数"
    else:
        layout = f"{item.exponent_bits} 位指数、{item.fraction_bits} 位尾数，无符号位"
    if item.high_zero:
        layout += f"；8 位载体的最高 {item.high_zero} 位必须为零"
    if item.low_zero:
        layout += f"；32 位载体的最低 {item.low_zero} 位必须为零"
    return layout + "。"


def _format_rule(item: FloatingFormat) -> str:
    if item.name == "HiF8":
        return "点域 0000 表示 denormal，0001 表示 D0；001、01、10、11 分别选择 1、2、3、4 位指数，并留下 3、3、2、1 位尾数。"
    if item.name == "E8M0":
        return (
            "编码 0x00 至 0xFE 表示 2^(E−127)；0xFF 表示安静 NaN。该格式没有零或无穷。"
        )
    if item.name == "E6M2":
        return "编码 0x00 至 0xFE 表示 (1+M/4)×2^(E−48)；0xFF 表示安静 NaN。该格式没有零或无穷。"
    if item.name == "RCPE6M2":
        return "编码 0x00 至 0xFE 表示对应 E6M2 有限值的倒数；0xFF 表示安静 NaN。"
    if item.name == "E1M2X2":
        return "每个 lane 的三位幅值 M 表示 M/4，符号位独立；+0 与 −0 都有编码。"
    if item.name == "E2M1X2":
        return "每个 lane 使用偏置 1 的两位指数和一位尾数，支持有符号零与次正规数，不定义无穷或 NaN。"
    if item.name == "HiF4X2":
        return "每个 lane 使用偏置 1 的一位指数和两位尾数，支持有符号零，不定义次正规数、无穷或 NaN。"
    if item.name == "E4M3":
        return "该格式不定义无穷或信号 NaN；指数和尾数全一的模式表示安静 NaN。"
    return ""


def _format_page(item: FloatingFormat) -> str:
    image = f'<figure><img src="{escape(_asset(item.name), quote=True)}" alt="{escape(item.name)} 位域图"></figure>'
    bias = "—" if item.bias is None else str(item.bias)
    return (
        f'<section class="datatype-definition" data-datatype="{item.name}" data-code="{item.code}">'
        f"<p><code>{item.name}</code> 的 5 位 DataType 编码为 <code>{item.code}</code>。"
        f"载体宽度 {item.carrier_bits} 位，每个数值 lane 宽度 {item.lane_bits} 位，"
        f"每个载体包含 {item.lanes} 个 lane。</p>"
        f"<p>{_layout(item)}</p>{image}"
        + (f"<p>{_format_rule(item)}</p>" if _format_rule(item) else "")
        + '<div class="table-scroll"><table><thead><tr><th>指数偏置</th><th>已定义的特殊值类别</th></tr></thead>'
        f"<tbody><tr><td>{bias}</td><td>{_specials(item)}</td></tr></tbody></table></div>"
        f"<h2>适用性</h2><p>{_applicability(item.name)}</p>"
        "<p>格式在 DataType 字段中已分配，不等于所有指令都接受该格式。标量 FSU 使用自己的类型字段，其适用范围应查对应标量指令页。</p>"
        "</section>"
    )


def _integer_page(name: str) -> str:
    code, bits, signed = INTEGERS[name]
    packed = name.endswith("X2")
    if signed:
        low, high = -(1 << (bits - 1)), (1 << (bits - 1)) - 1
    else:
        low, high = 0, (1 << bits) - 1
    storage = (
        f"一个 8 位载体保存两个 {bits} 位 lane。"
        if packed
        else f"一个载体保存一个 {bits} 位整数。"
    )
    return (
        f'<section class="datatype-definition" data-datatype="{name}" data-code="{code}">'
        f"<p><code>{name}</code> 的 5 位 DataType 编码为 <code>{code}</code>。{storage}</p>"
        f'<figure><img src="{escape(_asset(name), quote=True)}" alt="{escape(name)} 位域图"></figure>'
        f"<p>每个 lane 的数值范围为 <code>[{low}, {high}]</code>。"
        + ("最高位是二进制补码符号位。" if signed else "所有位均构成无符号数值。")
        + "</p><h2>适用性</h2><p>该编码是已分配的 Tile DataType。具体操作是否接受它，由对应操作页定义；不能从位宽本身推断操作合法性。</p></section>"
    )


def _hif_scale_page() -> str:
    return (
        '<section class="datatype-definition" data-datatype="HiF4_SCALE">'
        "<p>HiF4 Matrix-MX 的缩放载体是一个普通 <code>U32</code> Tile 元素，不占用新的 DataType 编码。"
        "其低 8 位是 E6M2 基础值，位 15:8 保存 8 个 E1_8 指数增量，位 31:16 保存 16 个 E1_16 指数增量。</p>"
        f'<figure><img src="{escape(_asset("HiF4_SCALE"), quote=True)}" alt="HiF4 U32 缩放字位域图"></figure>'
        "<p>一个缩放字对应 64 个逻辑 HiF4 lane。lane q 使用 E1_8[q/8] 与 E1_16[q/4]，"
        "最终缩放值为 E6M2 × 2^(E1_8 + E1_16)。E6M2 的 0xFF 表示安静 NaN；其他编码按偏置 48 和 2 位尾数解释。</p>"
        "</section>"
    )


def _mx_page(name: str) -> str:
    if name == "MXFP4":
        carriers = "E2M1X2 或 E1M2X2"
    else:
        carriers = "E4M3 或 E5M2"
    return (
        f'<section class="datatype-definition" data-datatype="{name}">'
        f"<p><code>{name}</code> 是 Matrix-MX 的组合用法，不是一个独立的 5 位 DataType 编码。"
        f"主输入使用 {carriers}，并沿 K 维每 32 个元素绑定一个 E8M0 缩放值。</p>"
        "<p>主输入 Tile 与缩放 Tile 是两个独立操作数；缩放值不会嵌入主输入载体。"
        "每一侧是否需要缩放由该侧 DataType 独立决定。</p></section>"
    )


def _intro() -> str:
    rows = "".join(
        f"<tr><td><code>{code}</code></td><td><code>{name}</code></td></tr>"
        for code, name in sorted(
            [(item.code, item.name) for item in FLOATING.values()]
            + [(value[0], name) for name, value in INTEGERS.items()]
        )
    )
    return (
        "<p>DataType 是 5 位编码。本版分配 27 个值；22、23、29、30、31 保留，必须在产生架构效果前拒绝。</p>"
        '<div class="table-scroll"><table><thead><tr><th>编码</th><th>Tile DataType</th></tr></thead>'
        f"<tbody>{rows}</tbody></table></div>"
        "<p>本目录分别说明数值格式和存储载体。一个格式被分配编码，不表示所有 Tile 操作、标量 FSU 或 Matrix-MX 都接受它。"
        "每条操作的类型集合以对应操作页为准。</p>"
    )


def datatype_pages() -> dict[str, tuple[str, str]]:
    pages: dict[str, tuple[str, str]] = {
        "arch-datatype-intro.html": ("数据类型", _intro())
    }
    direct_routes = {
        "BF16": "bf16",
        "FP16": "fp16",
        "FP32": "fp32",
        "FP64": "fp64",
        "TF32": "tf32",
        "HF32": "hf32",
        "HiF8": "hif8",
        "E8M0": "mx-scale",
        "HiF4X2": "hif4",
        "E6M2": "e6m2",
        "RCPE6M2": "rcpe6m2",
    }
    for name, slug in direct_routes.items():
        pages[f"arch-datatype-{slug}.html"] = (name, _format_page(FLOATING[name]))
    pages["arch-datatype-fp8.html"] = (
        "FP8（E4M3 / E5M2）",
        _format_page(FLOATING["E4M3"]) + _format_page(FLOATING["E5M2"]),
    )
    pages["arch-datatype-fp6.html"] = (
        "FP6（E3M2 / E2M3）",
        _format_page(FLOATING["E3M2"]) + _format_page(FLOATING["E2M3"]),
    )
    pages["arch-datatype-fp4.html"] = (
        "FP4 打包格式",
        _format_page(FLOATING["E2M1X2"]) + _format_page(FLOATING["E1M2X2"]),
    )
    integer_routes = {
        "S64": "int64",
        "S32": "int32",
        "S16": "int16",
        "S8": "int8",
        "S4X2": "int4",
        "U64": "uint64",
        "U32": "uint32",
        "U16": "uint16",
        "U8": "uint8",
        "U4X2": "uint4",
    }
    for name, slug in integer_routes.items():
        pages[f"arch-datatype-{slug}.html"] = (name, _integer_page(name))
    pages["arch-datatype-hif-scale.html"] = ("HiF4 U32 缩放字", _hif_scale_page())
    pages["arch-datatype-mxfp4.html"] = ("MXFP4 组合", _mx_page("MXFP4"))
    pages["arch-datatype-mxfp8.html"] = ("MXFP8 组合", _mx_page("MXFP8"))
    return pages


def datatype_index() -> tuple[str, str]:
    pages = datatype_pages()
    entries = "".join(
        f'<li><a href="{route}">{escape(title)}</a></li>'
        for route, (title, _) in sorted(pages.items())
        if route != "arch-datatype-intro.html"
    )
    return (
        "数据类型",
        '<p>按编码格式和组合缩放方案查阅。具体操作适用性仍以操作页为准。</p><ul class="chapter-index">'
        + entries
        + "</ul>",
    )


def datatype_assets() -> dict[str, bytes]:
    assets = {_asset(name): _datatype_svg(name) for name in (*FLOATING, *INTEGERS)}
    assets[_asset("HiF4_SCALE")] = _hif_scale_svg()
    return dict(sorted(assets.items()))


def _metadata(path: Path) -> dict[str, Any]:
    first = path.read_text().splitlines()[0]
    return json.loads(first.split(": ", 1)[1])


def validate_datatype_authority(pto_root: Path) -> list[str]:
    errors: list[str] = []
    domain = _metadata(pto_root / TILE_TYPES_SOURCE)["field_domains"][0]
    assigned = {item["meaning"]: item["value"] for item in domain["assigned"]}
    wanted = {item.name: item.code for item in FLOATING.values()} | {
        name: value[0] for name, value in INTEGERS.items()
    }
    if assigned != wanted:
        errors.append("Tile DataType assigned code set differs")
    if domain["reserved"] != [22, 23, 29, 30, 31]:
        errors.append("Tile DataType reserved code set differs")
    for item in FLOATING.values():
        source = (pto_root / FORMAT_ROOT / item.source).read_text()
        expected = {
            "carrier_bits": item.carrier_bits,
            "lane_bits": item.lane_bits,
            "lanes_per_carrier": item.lanes,
            "sign_bits": item.sign_bits,
            "sign_bit": item.sign_bit,
            "exponent_bits_min": item.exponent_bits_min
            if item.exponent_bits_min is not None
            else item.exponent_bits,
            "exponent_bits_max": item.exponent_bits,
            "fraction_bits_min": item.fraction_bits_min
            if item.fraction_bits_min is not None
            else item.fraction_bits,
            "fraction_bits_max": item.fraction_bits,
            "required_low_zero_bits": item.low_zero,
            "required_high_zero_bits": item.high_zero,
        }
        for field, value in expected.items():
            if not re.search(rf"\b{field}\s*=\s*{value}\b", source):
                errors.append(f"{item.name}: {field} differs")
        bias_available = item.bias is not None
        if (
            f"exponent_bias_available = {'TRUE' if bias_available else 'FALSE'}"
            not in source
        ):
            errors.append(f"{item.name}: exponent bias availability differs")
        if bias_available and not re.search(
            rf"\bexponent_bias\s*=\s*{item.bias}\b", source
        ):
            errors.append(f"{item.name}: exponent bias differs")
        boolean_fields = {
            "has_zero": item.zero,
            "has_signed_zero": item.signed_zero,
            "has_subnormal": item.subnormal,
            "has_infinity": item.infinity,
            "has_quiet_nan": item.quiet_nan,
            "has_signaling_nan": item.signaling_nan,
        }
        for field, value in boolean_fields.items():
            literal = f"{field} = {'TRUE' if value else 'FALSE'}"
            if literal not in source:
                errors.append(f"{item.name}: {field} differs")
    matrix = (pto_root / MATRIX_SOURCE).read_text()
    function = matrix.split("pure func TileMXInputTypeSupported", 1)[1].split(
        "end;", 1
    )[0]
    actual_matrix_types = set(re.findall(r"TileDataType_([A-Za-z0-9]+)", function))
    if actual_matrix_types != MATRIX_MX:
        errors.append("Matrix-MX input type set differs")
    for literal in (
        "if data_type == TileDataType_HiF4X2 then return 64",
        "if data_type == TileDataType_HiF4X2 then return TileDataType_U32",
        "return TileDataType_E8M0",
    ):
        if literal not in matrix:
            errors.append(f"Matrix-MX scaling rule missing: {literal}")
    hif = (pto_root / HIF_SCALE_SOURCE).read_text()
    for literal in ("scale_word[7:0]", "8 + (q DIVRM 8)", "16 + (q DIVRM 4)"):
        if literal not in hif:
            errors.append(f"HiF4 scale rule missing: {literal}")
    return errors


__all__ = [
    "datatype_assets",
    "datatype_index",
    "datatype_pages",
    "validate_datatype_authority",
]
