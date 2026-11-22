# Silicon Canvas 手册图

本目录的 `*.silicon-canvas.json` 是可编辑场景，`*.silicon-canvas-prompt.txt`
与 `*.silicon-canvas-guide.png` 是 Silicon Canvas 编译结果，`*.png` 是宿主
Image Gen 生成并进入 Silicon Canvas 审图回路的生产位图。结构底稿仅用于约束生成，
不能替代最终位图。

## 固定工具与重现

工具固定为 [du-du-wang/silicon-canvas](https://github.com/du-du-wang/silicon-canvas)
提交 `7b590daf2217acc5a95d5c40d289d56d91a9fbfc`、版本 `0.7.0`。
`silicon-canvas-provenance.json` 记录实际入口脚本和已安装包源树摘要；构建器会核对
checkout 提交、clean 状态、入口和 42 个包文件的逐字节等价性，核验失败时停止。

```sh
git clone https://github.com/du-du-wang/silicon-canvas /path/to/silicon-canvas
git -C /path/to/silicon-canvas checkout 7b590daf2217acc5a95d5c40d289d56d91a9fbfc
python3 -m venv /path/to/silicon-canvas-venv
/path/to/silicon-canvas-venv/bin/pip install /path/to/silicon-canvas

/path/to/silicon-canvas-venv/bin/python tools/isa/build_manual_canvas_figures.py \
  --mcp /path/to/silicon-canvas-venv/bin/silicon-canvas-mcp \
  --tool-root /path/to/silicon-canvas \
  --artifacts /path/to/private-artifacts \
  --output docs/architecture/isa-manual/reference/figures \
  docs/architecture/isa-manual/reference/figures/mgather-byte-displacement.silicon-canvas.json \
  docs/architecture/isa-manual/reference/figures/block-tpc-cmovr.silicon-canvas.json
```

随后把每个逐字提示词和对应 `target_structure` guide 一起交给宿主 Image Gen。
对生产位图调用 `review_manual_canvas_figure.py`，在独立 image-only 上下文完成返回的
冷读任务，再用 `submit_manual_canvas_review.py` 提交。工具以 `accept` 结束时核对获准图的摘要；以 `stop` 结束时，保留工具指定的最佳尝试。后一种情况还须核对最佳图片的摘要、该次技术核对记录、独立审阅意见和保留的版面限制。


## 正文引用建议

- `mgather-byte-displacement.png`：放在 MGATHER 指令页或 Tile 不规则访存章节。
  建议替代文本：`MGATHER 以 BaseGPR 加四个字节位移形成地址，预检全部通过后读取 GM，成功时一次发布 Local DstTile，故障时不发布目标。`
- `block-tpc-cmovr.png`：放在 block 执行／程序计数器章节，并在 C.MOVR 指令页交叉引用。
  建议替代文本：`BSTART 打开 block，C.MOVR 将完整 XLEN 值从 Reg5 源原样发布到 Reg5 目标；TPC 前进 2 字节而 BPC 保持 block 起点，提交边界清除头部状态。`

图中说明性流程来自固定 LinxISA `v0.59.1` 与 PTO 提交
`a89a53d48f5708328be609fe2e6296ac8bdb4bc2`，不替代规范 ASL。
