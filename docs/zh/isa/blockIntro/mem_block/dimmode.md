# 分组模式

在当前版本中，Tile 块体采用三级嵌套迭代结构：`lc2 → lc1 → lc0`，对应的总迭代为 `lb2 × lb1 × lb0`。执行单元以 Group 为调度粒度，且每个 Group 的 laneNum 固定为 64。基于上述设计，块指令块体的分组方式存在多种可选方案；当前版本支持 **降维模式** 和 **多维模式** 两种分组模式。

## 降维模式

**降维模式（Reduce Dimension，RD）** 就是将三层迭代（lc2, lc1, lc0）线性化铺平为一维序列，按每64次迭代（对应一个Group的laneNum）打包分配到Group顺序执行，直到完成。

特点：

- 最大化铺平，便于均匀分配与吞吐。
- 不保留原三维结构的边界或邻接关系。

图示如下：

![reducedim](../../../figs/isa/arch/reducedim.png){ width="1200" }

## 多维模式

**多维模式（Multi Dimension, MD）** 是以最内层 lc0 为分组粒度，同一Group内不得包含不同的 lc0 值；在固定 lc0 下展开外层维度 的一种分组模式。

特点：

- 保留内层维度（lc0）的边界与隔离，适合对数据/资源在 lc0 维度需要严格分域或依赖的场景。
- 相对 RD 更强调维度结构一致性。

多维模式下，如果最内层循环上限 lb0 小于 Group.lanenum，那么每一次的最内层循环可以分配到同一个Group内执行。图示如下：

![multidim](../../../figs/isa/arch/multidim.png){ width="1200" }

如果最内层循环上限 lb0 大于 Group.lanenum，那么每一次的最内层循环需要按序分配到不同Group执行。图示如下：

![multidim](../../../figs/isa/arch/multidim1.png){ width="1200" }

多维模型下，必须保证：

- 同一个Group内LC0的值必须是连续递增的；
- 同一个Group内LC1的值必须保持不变；
- 同一个Group内LC2的值必须保持不变；

该模型下，一个Tile块拆分出来的Group的数量计算公式为：
```c++
if (LB0 % 64 > 0) 
    innerNum = LB0 / 64 +1;
else
    innerNum = LB0 / 64;
GroupNumber = LB2 * LB1 * innerNum;
```

多维模式更适合于地址连续load/store的使用场景，保证在一个Group内lc0是连续递增的。

## 注意事项

如果块指令块头中没有明确指定采用 “降维模式” 还是 “多维模式”，则 **默认采用多维模式** 实现。

## 总结

软件或程序员可根据实际场景在两种分组模式间选择：若追求最大化吞吐与均匀分配，采用降维模式；若需保留 lc0 维度的边与依赖一致性，采用多维模式（例如Group内地址连续的load/store指令的使用）。
