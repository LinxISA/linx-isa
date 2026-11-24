# 灵犀指令集架构 手册 (AsciiDoc)

此目录包含 **灵犀指令集架构 (灵犀 ISA)** 的实时 v0.58 ISA 手册，以
**AsciiDoc** 并使用以下方式构建为 **PDF**
`asciidoctor-pdf`（通过 Bundler）。

内容特定于 灵犀 的设计（块结构控制流、`BSTART/BSTOP`、ClockHands 临时变量、
模板指令（如 `FENTRY` 等）。

该文档网站还发布了更广泛的 Markdown 手册层次结构，源自
最新导入的手册树。更广泛的等级制度是主要公众
导航界面，但是这本英文 AsciiDoc 手册仍然是规范的
架构可见行为的英文手册源。

相关发布的镜像：

- `docs/background/`
- `docs/compiler/`
- `docs/isa/`
- `docs/zh/`（中国镜子）

## 构建

从这个目录：

```bash
make pdf
```

输出：
- `build/linxisa-isa-manual.pdf`

## 发布工件

- 当前发行说明：`docs/zh/releases/v0.58.3.md`
- 最新发布页面：https://github.com/灵犀指令集/linx-isa/releases/latest

## 重新生成生成的部分

该手册包括从规范规范生成的 AsciiDoc：
- `isa/v0.58/linxisa-v0.58.json`（当前规范权威）

再生：

```bash
make gen
```

注意：`build/` 被 gitignored；本地构建输出不会提交到存储库。

## 0.59.2 离线 HTML 手册

解压后打开 `index.html`，从八个功能分类、助记符或编码索引查找指令。本版收录 1,306 个编码形式和 119 个 Tile 操作。四个只预留编码的形式在正文中单独标注。系统寄存器表按发布目录列出 100 项寄存器的读写、复位及副作用。类型页区分存储载体、数值格式和具体操作允许的输入。构建检查同时覆盖页面、折叠资料和离线附件。[下载中文 HTML 手册](https://github.com/LinxISA/linx-isa/releases/download/v0.59.2/linxisa-0.59.2-html.zip)

在本目录运行 `make html-reference check-html-reference` 可重建和核验。检出环境需要 v0.59.2 发布标签和 v0.59.1 的原始中文资料标签。Markdown 依赖列在 `reference/requirements.txt` 中。
