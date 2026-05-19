# Register dynamic usage frequency

Instruction set version when statistical data: v0.31
Update date: November 22, 2023

The statistical registers include: block-private registers R1-R15, global register R0 and intra-block T registers t#1 to t#8.

## Register usage frequency chart

Register R0-R7 | Frequency of use | Register R8-R15 | Frequency of use | Register t#1-T#8 | Frequency of use
------------|----------|-------------|----------|--------------|----------
r0 | 1.13% | r8 | 1.91% | t#1 | 34.75%
r1 | 5.98% | r9 | 2.16% | t#2 | 9.74%
r2 | 6.33% | r10 | 1.39% | t#3 | 3.17%
r3 | 4.61% | r11 | 2.62% | t#4 | 1.31%
r4 | 5.08% | r12 | 3.26% | t#5 | 0.66%
r5 | 2.71% | r13 | 3.67% | t#6 | 0.52%
r6 | 2.61% | r14 | 1.53% | t#7 | 0.45%
r7 | 2.05% | r15 | 1.32% | t#8 | 1.04%

```plotly
{"file_path": "docs/figs/bitfield/json/Summarize/dynamic_execution_register.json"}
```