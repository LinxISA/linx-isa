# Matrix Multiplication Notes

Matrix multiplication research notes and design tradeoff analyses.

## Contents

- [low-precision-inner-vs-outer-product.md](low-precision-inner-vs-outer-product.md) - 调研低精度矩阵乘中内积式与外积式数据流的电路代价、数据搬运代价与数值精度权衡
- [inner-vs-outer-matmul-architecture-zh.tex](inner-vs-outer-matmul-architecture-zh.tex) - 只比较内积与外积的 LaTeX 论文稿件
- [inner-vs-outer-matmul-architecture-zh.pdf](inner-vs-outer-matmul-architecture-zh.pdf) - 上述论文的 PDF 成稿
- [outercube-isca-style-review-zh.tex](outercube-isca-style-review-zh.tex) - outerCube 电路级分析的 LaTeX 稿件
- [outercube-review-v2.pdf](outercube-review-v2.pdf) - 由上述 LaTeX 生成的 PDF 成稿
- [figures/](figures/) - 论文中使用的 SVG/PDF 示意图资源

## Scope

This directory is for matrix multiplication implementation notes that do not
fit the ISA contract pages or bring-up guides.
