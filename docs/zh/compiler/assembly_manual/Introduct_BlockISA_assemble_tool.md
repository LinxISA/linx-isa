# 汇编链接工具介绍

LLVM内置汇编器是LLVM工具组件中的一员，功能为将汇编文件转换为二进制对象文件。关于clang的使用，可以参见：[https://clang.llvm.org/](https://clang.llvm.org/)

灵犀指令集汇编器通过使能Linx-LLVM的内置汇编器实现的，支持LLVM内置汇编器的通用功能, 因此在接下来的描述中，将重点说明在Linx指令集上的使用方式。

## 使用灵犀指令集汇编器

可以直接使用clang工具对灵犀指令集汇编文件进行汇编。

```
clang --target=linx64v5-linux-musl -c tmp.S -o tmp.o
```

当所有的源文件都已经已经汇编完成成为二进制目标文件时（后缀为.o的文件）， 可以使用GNU的链接器来生成最终的可执行文件（默认为ELF格式）。
```
clang --target=linx64v5-linux-musl  tmp.o -o tmp.out
```

