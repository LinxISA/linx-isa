## 背景介绍

在BISA持续推演的过程中我们发现, 适当地将部分Blocks合成1个Hyper Block会产生性能或Codesize收益。而决策：将哪些Blocks合并成Hyper Block 不仅仅依赖于对程序的静态分析, 更多地, 我们需要一些runtime数据来支撑Blocks Hyper化这一决策。为此, 本文将讨论一个BISA的语言扩展：当程序员对应用程序足够了解, 或已通过pref等分析工具知晓了哪块C代码适合归并成一个Hyper Block时, 如何在C源码级给予编译器提示, 最终获取性能或Codesize收益。

**注意**：本文不讨论为什么要引入Hyper Block; 什么场景下使用Hyper Block最优; 能否通过xxx方式将Blocks Hyper化这件事全部交给编译器实现, 做到程序员不感知等问题。只讨论：
**当程序员知道哪块C代码适合归并成一个Hyper Block时, 如何修改C源码给予编译器提示**这个命题。

## 方案描述 (当前pragma方案在0.50上暂未支持)

参考openMP, 采用pragma制导的方式在C源码给予编译器提示。关键字`block { }`表示将花括号指示的域编译成1个Hyper Block, 例如：
```c
int arr[10] = {1,2,3,4,5,6,7,8,9,0};
void test(int n, int a) {
  #pragma linx block
  {
  for (int i = 0; i < n; ++i) {
    arr[i] += a;
  }
  }

  arr[4] -= a;

  #pragma linx block
  {
    if (arr[3] > a)
      arr[3] -= a;
    else
      arr[3] += a;
  }
}
```

## 约束与限制

### 条目1
`#pragma linx block { }`中花括号`{ }`即为C语言中 域/复合语句 的标准语法, 需要满足C语言本身的语法规则：如`{ }`内定义的变量不能被其外部访问。

### 条目2
允许1个函数内存在多个待编译成Hyper Block的域；嵌套的Hyper Block域没有意义, 编译器将会报错；

### 条目3
由于Hyper Block设计本身存在如下限制:

- 顶部单入：Caller不允许跳转至Hyper Block内部的某条指令
- 底部单出：不能在内部跳出Hyper Block

因此, `#pragma linx block { }`不允许:

- 存在类于`goto`的语句, 直接跳转至`block { }`域中的内部
- 存在类于`goto`/`return`的语句, 直接跳转至`block { }`域中的外部
> 注：支持`for/switch`语句中存在`break`。因为本质上这些`break`和语句块的终止指向同一个位置(即语句块的末尾)。
- Hyper Block内部存在Function Call
