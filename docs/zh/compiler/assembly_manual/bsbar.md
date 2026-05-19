# 内存写入投机屏障伪指令：**BSBAR**

内存写投机屏障BSBAR(Block Store Speculation Barrier)的指令定义和微架构行为详见：[指令手册/控制块/BSBAR](https://openx.huawei.com/mkdocs/project/1410/blockisa-doc/docs/site/docs/isa/inst/BSBAR/)

汇编上，`b.sbar.<oow> <N>`是一条位于块头汇编伪指令序列中的**伪指令**(块头汇编描述见：[编程手册/汇编指令/块头/综述](https://openx.huawei.com/mkdocs/project/1410/blockisa-doc/docs/site/docs/compiler/assembly_manual/block_header/))。例如：
```Linx
...
.section .text
label:
  bstart label.start
  b.sbar 1
  bget a0, a1
  bstop label.end
.section .text.body
label.start:
  sdi a0, [a1, 0]
label.end:
...
```

----------------------

以下是`b.sbar <N>`书写方式，此时块内store **顺序提交**：

| 块内**运行时**的store个数  | 汇编表示  |
| ------------ | ------------ |
| N = 0  | 方式1：`b.sbar 0`；方式2：缺省。**注**：2种表达方式等价  |
| N = [1, 63]  | `b.sbar N`  |
| N = [64, +∞)  | `b.sbar `  |
| N 的值不确定  | `b.sbar `  |

以下是`b.sbar.oow <N>`书写方式，此时块内store **乱序提交**：

| 块内**运行时**的store个数  | 汇编表示  |
| ------------ | ------------ |
| N = 0  | `b.sbar.oow 0` |
| N = [1, 63]  | `b.sbar.oow N`  |
| N = [64, +∞)  | `b.sbar.oow `  |
| N 的值不确定  | `b.sbar.oow `  |

