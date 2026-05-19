# 灵犀指令集架构 手册 (AsciiDoc)

此目录包含 **灵犀指令集架构 (灵犀 ISA)** 的实时 v0.56.2 ISA 手册，以
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

- 当前发行说明：`docs/releases/v0.56.2.md`
- 最新发布页面：https://github.com/灵犀指令集/linx-isa/releases/latest

## 重新生成生成的部分

该手册包括从规范规范生成的 AsciiDoc：
- `isa/v0.56/linxisa-v0.56.json`

再生：

```bash
make gen
```

注意：`build/` 被 gitignored；本地构建输出不会提交到存储库。