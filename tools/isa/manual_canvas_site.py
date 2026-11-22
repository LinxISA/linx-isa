"""Publish final reviewed illustrations; keep layout guides in the source bundle."""

from hashlib import sha256
from html import escape
import json
from pathlib import Path


VIEWS = {
    "block-tpc-cmovr": {
        "pages": ["arch-execution.html", "arch-tpc.html", "op-c-movr.html"],
        "alt": "标准块中的寄存器移动：BPC 保持块起点；C.MOVR 将源值送往目标，成功后 TPC 前进 2 字节。",
        "caption": "图中只画成功路径。BSTART 开始一个块，块头命令准备执行状态。16 位 C.MOVR 先读 Reg5 源，再写 Reg5 目标。此时 TPC 已指向下一条指令，BPC 仍指向本块起点。箭头表示架构上的先后关系。",
    },
    "mgather-byte-displacement": {
        "pages": [
            "tile-mgather.html",
            "op-bstart-mgather.html",
            "arch-tlsu-block.html",
        ],
        "alt": "四个字节位移 8、0、8、4 加到基址 0x1000。通过地址预检后，四个目标位置依次取得 3、1、3、2。",
        "caption": "示例使用普通 U32 数据，有效区域包含四个索引位置，省略可选范围描述符。索引位置 0 和 2 都访问 0x1008，所以两处都得到 3。只有所有有效地址的预检均通过，才发布目标 Tile。",
    },
}


def include_canvas(bodies, folder: Path):
    provenance_file = "silicon-canvas-provenance.json"
    provenance = json.loads((folder / provenance_file).read_bytes())
    files = {"figures/" + provenance_file: (folder / provenance_file).read_bytes()}
    figures = []
    for item in provenance["figures"]:
        name = item["name"]
        view = VIEWS[name]
        image = name + ".png"
        review_file = name + ".review.json"
        review_bytes = (folder / review_file).read_bytes()
        review = json.loads(review_bytes)
        image_bytes = (folder / image).read_bytes()
        digest = sha256(image_bytes).hexdigest()
        if (
            digest != review["image_sha256"]
            or review["artifact_id"] != item["artifact_id"]
        ):
            raise ValueError(f"{name}: final image does not match its review")
        names = [item["source"], name + ".silicon-canvas-prompt.txt", review_file]
        for role in ("guide", "export"):
            record = item["assets"][role]
            if (
                sha256((folder / record["path"]).read_bytes()).hexdigest()
                != record["sha256"]
            ):
                raise ValueError(f"{name}: {role} asset digest mismatch")
            names.append(record["path"])
        for asset in names + [image]:
            files["figures/" + asset] = (folder / asset).read_bytes()
        details = (
            f"<details><summary>图源与核对记录</summary><p>"
            f'<a href="figures/{item["source"]}">可编辑的 Silicon Canvas 场景</a> · '
            f'<a href="figures/{review_file}">成图审阅记录</a></p></details>'
        )
        html = (
            f'<figure class="canvas-figure"><img class="canvas-figure-image" src="figures/{image}" '
            f'alt="{escape(view["alt"], quote=True)}" loading="lazy"><figcaption>{escape(view["caption"])}</figcaption>'
            f"{details}</figure>"
        )
        for target in view["pages"]:
            title, body = bodies[target]
            end = "<!-- authored:end --></section>"
            if end not in body:
                raise ValueError(f"{target}: missing expected authored chapter")
            bodies[target] = title, body.replace(end, end + html, 1)
        figures.append(
            {
                "id": item["artifact_id"],
                "name": name,
                "image": "figures/" + image,
                "sha256": digest,
                "pages": view["pages"],
                "source_files": ["figures/" + v for v in names]
                + ["figures/" + provenance_file],
                "accepted_image_sha256": digest,
                "review_decision": review["decision"]["action"],
                "review_file": "figures/" + review_file,
                "review_sha256": sha256(review_bytes).hexdigest(),
            }
        )
    if {f["name"] for f in figures} != set(VIEWS):
        raise ValueError("missing required illustration")
    files["canvas-audit.json"] = json.dumps(
        {"tool": provenance["silicon_canvas"], "figures": figures},
        ensure_ascii=False,
        indent=2,
    ).encode()
    return files
