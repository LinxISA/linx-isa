"""Functional-unit indexes from the release catalog's uop_big_kind."""

from collections import Counter
from html import escape

# Display name, frozen catalog key, description and index filename.
CATEGORIES = (
    ("ALU", "ALU", "整数运算", "整数加减、逻辑、移位、位域及寄存器数据移动。"),
    ("BBD", "BBD", "块边界", "标记块边界并携带块控制信息的形式。"),
    ("BRU", "BRU", "分支与比较", "比较、跳转、返回地址及提交条件。"),
    ("LSU", "AGU", "访存", "加载、存储和预取。目录将这些形式归入 AGU。"),
    ("AMO", "AMO", "原子访存", "原子读改写、保留加载和条件存储。"),
    ("CMD", "CMD", "块命令", "指令块的操作选择、属性设置与操作数绑定。"),
    ("FSU", "FSU", "标量浮点", "标量浮点运算、比较及数值转换。"),
    ("SYS", "SYS", "系统指令", "系统寄存器、维护操作和系统控制。"),
    ("VEC", "VEC", "向量指令", "向量指令体中的运算、访存与跨通道操作。"),
)
BY_KEY = {key: (name, title) for name, key, title, _ in CATEGORIES}


def cat_file(key):
    return "class-" + BY_KEY[key][0].lower() + ".html"


def category_links(prefix=""):
    return "".join(
        f'<a href="{prefix}{cat_file(key)}">{name}</a>'
        for name, key, _, _ in CATEGORIES
    )


def index_pages(rows, entries, alpha_index, tile_count):
    counts = Counter(row["uop_big_kind"] for row in rows)
    if set(counts) != set(BY_KEY):
        raise ValueError("functional class mapping differs from the release catalog")
    by_name = {e[0]: e for e in entries}
    table = []
    result = {}
    for name, key, label, description in CATEGORIES:
        mnemonics = sorted({r["mnemonic"] for r in rows if r["uop_big_kind"] == key})
        url = cat_file(key)
        intro = f"<p>{escape(description)} 本类收录 {len(mnemonics)} 个目录助记符、{counts[key]} 个编码形式。</p>"
        result[url] = (
            f"{name} · {label}助记符索引",
            alpha_index([by_name[m] for m in mnemonics], intro, "搜索本类助记符"),
        )
        table.append(
            f'<tr><th><a href="{url}">{name} · {label}</a></th><td>{description}</td>'
            f"<td>{len(mnemonics)}</td><td>{counts[key]}</td></tr>"
        )
    result["index.html"] = (
        "指令分类",
        "<p>先选择指令类型，再按字母查找助记符。已知指令名称可以直接查"
        '<a href="mnemonics.html">全部助记符</a>；已知机器字可以查<a href="encoding.html">编码索引</a>。</p>'
        '<div class="table-scroll"><table class="lookup categories"><thead><tr><th>类型</th><th>内容</th>'
        "<th>助记符</th><th>编码形式</th></tr></thead><tbody>"
        + "".join(table)
        + f'</tbody></table></div><p><a href="tile.html">Tile 操作索引</a>另列 {tile_count} 个由块命令选择的操作，'
        "可按 VEC、SFU、TLSU 和 CUBE 引擎查阅。</p>",
    )
    return result
