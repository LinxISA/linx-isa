# 原子指令

原子指令，也称为原子操作或者是原子性指令，是指在多处理器系统或多线程环境中执行时不会被中断的操作，即操作要么完全执行，要么完全不执行。因为这些环境中可能有多个处理器或线程同时访问共享资源。原子指令可以确保这些操作不会被打断或部分执行，从而避免数据不一致和出现不可预测的结果。一条原子指令往往包含一组操作，这样可以提高指令集的效率、简化编程模型、减少指令流水线的开销、以及提高处理器的吞吐量。

向量原子指令目前主要包含Load.op和Store.op两类指令。

## 指令列表

1.Load.op类原子指令列表如下:

|     微指令    |         汇编格式                          |     描述       |
|--------------|-------------------------------------------|----------------|
| V.LW.ADD | `v.lw.add<.{aq,rl,f,aqrl,aqf,rlf,aqrlf}> [SrcL.ud], SrcR.{T}, ->Dst.{W}` | 原子执行内存加载字·相加      |
| V.LW.AND | `v.lw.and<.{aq,rl,f,aqrl,aqf,rlf,aqrlf}> [SrcL.ud], SrcR.{T}, ->Dst.{W}` | 原子执行内存加载字·相与      |
| V.LW.OR  | `v.lw.or<.{aq,rl,f,aqrl,aqf,rlf,aqrlf}> [SrcL.ud], SrcR.{T}, ->Dst.{W}`  | 原子执行内存加载字·取或      |
| V.LW.XOR | `v.lw.xor<.{aq,rl,f,aqrl,aqf,rlf,aqrlf}> [SrcL.ud], SrcR.{T}, ->Dst.{W}` | 原子执行内存加载字·取异或    |
| V.LW.MAX | `v.lw.max<.{aq,rl,f,aqrl,aqf,rlf,aqrlf}> [SrcL.ud], SrcR.{T}, ->Dst.{W}` | 原子执行内存加载字·取最大值  |
| V.LW.MIN | `v.lw.min<.{aq,rl,f,aqrl,aqf,rlf,aqrlf}> [SrcL.ud], SrcR.{T}, ->Dst.{W}` | 原子执行内存加载字·取最小值  |
| V.LD.ADD | `v.ld.add<.{aq,rl,f,aqrl,aqf,rlf,aqrlf}> [SrcL.ud], SrcR.{T}, ->Dst.{W}` | 原子执行内存加载双字·相加      |
| V.LD.AND | `v.ld.and<.{aq,rl,f,aqrl,aqf,rlf,aqrlf}> [SrcL.ud], SrcR.{T}, ->Dst.{W}` | 原子执行内存加载双字·相与      |
| V.LD.OR  | `v.ld.or<.{aq,rl,f,aqrl,aqf,rlf,aqrlf}> [SrcL.ud], SrcR.{T}, ->Dst.{W}`  | 原子执行内存加载双字·取或      |
| V.LD.XOR | `v.ld.xor<.{aq,rl,f,aqrl,aqf,rlf,aqrlf}> [SrcL.ud], SrcR.{T}, ->Dst.{W}` | 原子执行内存加载双字·取异或    |
| V.LD.MAX | `v.ld.max<.{aq,rl,f,aqrl,aqf,rlf,aqrlf}> [SrcL.ud], SrcR.{T}, ->Dst.{W}` | 原子执行内存加载双字·取最大值  |
| V.LD.MIN | `v.ld.min<.{aq,rl,f,aqrl,aqf,rlf,aqrlf}> [SrcL.ud], SrcR.{T}, ->Dst.{W}` | 原子执行内存加载双字·取最小值  |

<!-- 
![load.op](../../../figs/bitfield/svg/Introduction_64bit/Atomic.svg) 
-->

2.Store.op类原子指令列表如下:

|     微指令    |         汇编格式                          |     描述       |
|--------------|-------------------------------------------|----------------|
| V.SW.ADD | `v.sw.add<.{rl,f,rd,rlf,rdf,rlrd,rlrdf}> [SrcL.ud], SrcR.{T}` | 原子执行存储字·相加      |
| V.SW.AND | `v.sw.and<.{rl,f,rd,rlf,rdf,rlrd,rlrdf}> [SrcL.ud], SrcR.{T}` | 原子执行存储字·相与      |
| V.SW.OR  | `v.sw.or<.{rl,f,rd,rlf,rdf,rlrd,rlrdf}> [SrcL.ud], SrcR.{T}`  | 原子执行存储字·取或      |
| V.SW.XOR | `v.sw.xor<.{rl,f,rd,rlf,rdf,rlrd,rlrdf}> [SrcL.ud], SrcR.{T}` | 原子执行存储字·取异或      |
| V.SW.MAX | `v.sw.max<.{rl,f,rd,rlf,rdf,rlrd,rlrdf}> [SrcL.ud], SrcR.{T}` | 原子执行存储字·取最大值  |
| V.SW.MIN | `v.sw.min<.{rl,f,rd,rlf,rdf,rlrd,rlrdf}> [SrcL.ud], SrcR.{T}` | 原子执行存储字·取最小值  |
| V.SD.ADD | `v.sd.add<.{rl,f,rd,rlf,rdf,rlrd,rlrdf}> [SrcL.ud], SrcR.{T}` | 原子执行存储双字·相加      |
| V.SD.AND | `v.sd.and<.{rl,f,rd,rlf,rdf,rlrd,rlrdf}> [SrcL.ud], SrcR.{T}` | 原子执行存储双字·相与      |
| V.SD.OR  | `v.sd.or<.{rl,f,rd,rlf,rdf,rlrd,rlrdf}> [SrcL.ud], SrcR.{T}`  | 原子执行存储双字·取或      |
| V.SD.XOR | `v.sd.xor<.{rl,f,rd,rlf,rdf,rlrd,rlrdf}> [SrcL.ud], SrcR.{T}` | 原子执行存储双字·取异或      |
| V.SD.MAX | `v.sd.max<.{rl,f,rd,rlf,rdf,rlrd,rlrdf}> [SrcL.ud], SrcR.{T}` | 原子执行存储双字·取最大值  |
| V.SD.MIN | `v.sd.min<.{rl,f,rd,rlf,rdf,rlrd,rlrdf}> [SrcL.ud], SrcR.{T}` | 原子执行存储双字·取最小值  |

## 属性参数

原子指令可以通过".aq"和".rl"两个后缀来添加额外的内存访问顺序限制，以保证内存访问的一致性。aq表示acquire语义，rl表示release语义，具体定义如下:

|   aq  |  rl  |  含义                             |
|-------|--------|-------------------------------------|
|  0  |  0  | 没有顺序限制                        |
|  0  |  1  |该指令的前序所有访问内存的指令的结果必须在该指令执行之前被观察到  |
|  1  |  0  |该指令的后序所有访问内存的指令必须等该指令执行完成后才开始执行    |
|  1  |  1  |该指令的前序所有访问内存的指令的结果必须在该指令执行之前被观察到，其后序所有访问内存的指令必须等该指令执行完成后才开始执行    |

原子指令还可以通过可选属性“.rd”，指示该指令在当前Group的所有lane内访存地址是相同的，执行store reduce的操作。以及使用“.f”标识指示原子操作的内存访问发生在远端Cache。

具体定义如下:

|  rd   |  f | 含义          |
|-------|------|--------------|
|   0   |   0  |  无特殊属性         |
|   0   |   1  |  表示原子操作的内存访问发生在远端 Cache中   |
|   1   |   0  |  在所有lane内SrcL中地址是相同的，执行store reduce的操作  |
|   1   |   1  |  在所有lane内SrcL中地址是相同的，执行store reduce的操作，且表示原子操作的内存访问发生在远端 Cache中  |

## 指令编码

![atomic](../../../figs/bitfield/svg/Introduction_64bit/AtomicOperationVector.svg)
