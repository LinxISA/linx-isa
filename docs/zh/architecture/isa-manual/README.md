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

## 0.59.1 离线中文指令手册

从 [0.59.1 正式发行页](https://github.com/LinxISA/linx-isa/releases/tag/v0.59.1) 下载 HTML 压缩包，解压后打开 `index.html`。首页按 ALU、BBD、BRU、LSU 等功能分类；每类都有独立的助记符索引。进入指令页后可直接阅读本仓库中文站原有的说明、示例和原图，另可展开发布版位图和编码表。版本与来源页列出发布提交和目录文件的校验摘要。

在仓库的 `docs/architecture/isa-manual` 目录执行 `make html-reference check-html-reference` 可重新生成并核对。生成器读取正式 tag，并逐项对照 578 个公共形式、705 个 scoped 形式和 216 个 Linx 专有形式。浅克隆需先获取 `v0.59.1` 标签。

生成中文原文页使用仓库现有的 MkDocs 文档依赖。分类与单页的设计依据见[参考站组织结构分析](arm64-reference-organization.md)。

架构状态、执行模型和异常说明同样取自发布标签的中文源文件。系统寄存器表单独列出本版的 100 项定义。22 个无独立原页的条目标为“0.59.1 增补”。从仓库根目录运行 `python3 -m pip install -r docs/architecture/isa-manual/reference/requirements.txt` 即可安装与发布包相同版本的 Markdown 和代码高亮组件。

[独立审阅记录](reader-quality-review.md)列出影响芯片实现的版本差异及修正。
