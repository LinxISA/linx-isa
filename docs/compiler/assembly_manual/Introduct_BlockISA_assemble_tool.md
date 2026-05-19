# Introduction to assembly link tools

The LLVM built-in assembler is a member of the LLVM tool component and its function is to convert assembly files into binary object files. Regarding the use of clang, please see: [https://clang.llvm.org/](https://clang.llvm.org/)

The LinxISA assembler is implemented by enabling the built-in assembler of Linx-LLVM and supports the common functions of the LLVM built-in assembler. Therefore, in the following description, the use of the Linx instruction set will be focused on.

## Use LinxISA assembler

You can directly use the clang tool to assemble the LinxISA assembly file.

```
clang --target=linx64v5-linux-musl -c tmp.S -o tmp.o
```

When all source files have been assembled into binary object files (files with a .o suffix), the GNU linker can be used to generate the final executable file (default is ELF format).
```
clang --target=linx64v5-linux-musl  tmp.o -o tmp.out
```