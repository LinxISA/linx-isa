# Introduction

This document mainly introduces the compilation and operation methods of Block ISA as a device in heterogeneous mode and offloading tasks to Block ISA.

# Source code modification

- **The function mark linx_kernel attribute that needs to be offloaded to the Block ISA model runtime**
- Current **restrictions** on kernel functions:
    1. The parameter type of the kernel function is not a floating point type
    2. The parameter/return value type length of the kernel function does not exceed 64 bits
    3. System library functions cannot be called in the kernel function and its called functions.
    4. Indirect calls (function pointers) cannot be used in kernel functions and their called functions.

```c
# include <stdio.h>

int arr[10] = {1, 2, 3, 4, 5, 6, 7, 8, 9, 10};
int brr[10] = {10, 9, 8, 7, 6, 5, 4, 3, 2, 1};

int __attribute__((linx_kernel, noinline)) foo(int n) {
  int i, x, y;
  int sum = 0;

  for (i = 0; i < n; i++) {
    x = arr[i];
    y = brr[i];
    if (x > y) {
      sum = sum + x - 1;
    } else {
      sum = y + 1;
    }
  }
  return sum;
}

int main() {

  int succ = 1;

  int res = foo(10);

  printf("%d\n", res);

  if (res != 42) {
    succ = 0;
  }

  if (succ)
    printf("Test PASSED\n");
  else
    printf("Test FAILED\n");

  return 0;
}
```

Taking the above source code as an example, if we want to offload the `foo` function to the Block ISA device for operation, add the `linx_kernel` and `noinline`attributes to the `foo` function.

# Host compilation

When the host compiler compiles the kernel function, it will insert the interface and runtime of the Block ISA model into the kernel function. Using X86 as the host device, when running the kernel function, it will switch from the host to the Block ISA model. The runtime is used to obtain information about the functions called in the kernel function and the global variables used. The compilation method on the host side is as follows:

- clone build LLVM compiler:

  ```shell
  git clone -b dev_host_compilation ssh://git@codehub-dg-y.huawei.com:2222/linx/ISA-Codesign/BlockISA/linx-llvm.git
  ```

- Clone build Block ISA model warehouse:

  ```shell
  git clone -b master ssh://git@codehub-dg-y.huawei.com:2222/Graphflow/BlockISA.git
  ```

- Use the above LLVM compiler to compile the host code and link the model dynamic library of Block ISA:

  ```shell
  clang xxx.c -o a.out -L ${model_path}/BlockISA/lib -lfunc_model -lruntime -L/usr/lib64 -lelf -O2 -flinx-instrument
  ```

- If the compilation process prompts the following warning:

  ```shell
  warning: private global variable xxx is used in kernel function.
  ```

- The above warning occurs because there is a constant string in the kernel function. Currently, Block ISA has two tool chains: gcc and llvm. The two tool chains may name constant strings differently. If the llvm compiler defines a constant string as a global variable, name it a.str; and the gcc compiler may define this string as b.str. When dealing with global variables later, the host and device sides will not be able to
  Local variables correspond to each other. If both host and device use the llvm compiler, you can ignore this warning; if the host uses the llvm compiler and the device uses the gcc compiler, you need to define the string as a global variable in the source code. 


# Host run

After the host side compiles and links, it needs to be run on the host side to obtain the function and global variable address information called during the execution of the kernel function. The runtime will record the above information. After executing the host executable file, the `linx_runtime_info.json` file will be generated in the execution directory, which records the functions called by the kernel function during host execution and the global variable information used. Taking the above example as an example, first configure the environment variables (indicating that the host executable file runs completely on the host machine), and then run the executable file:

```shell
export BISA_MODEL_RUN=0
./a.out
```

After the operation is completed, the `linx_runtime_info.json` file will be generated in the execution directory.

# Device compilation

The difference between the compilation process on the Device (Block ISA) side and the ordinary compilation process is that after compiling the relocatable file (.o) of the Block ISA, you need to use tools to correspondingly modify the addresses of global variables in the relocatable file of the Block ISA based on the host runtime information. Therefore, the compilation process on the Device side is:

## Compile

Use the Block ISA llvm compiler to compile the source code into an .o file:

```shell
${compiler_path}/bin/clang a.c b.c -O2 -c --target=linx64 -march=linx64im -mabi=lp64 -fno-jump-tables
```

Use the Block ISA gcc compiler to compile the source code into a `.o` file:

```shell
${compiler_path}/linx64-unknown-elf/bin/linx64-unknown-elf-gcc -O2 a.c b.c -fno-section-anchors -c -mcmodel=medlow
```

## Global variable address adjustmentUse tools to change the address of the global variable in the Block ISA relocatable file to the address of the corresponding global variable in the host executable file. The tool is in the `BlockISA/scripts/reloc_globals` directory:

```shell
${model_path}/BlockISA/scripts/reloc_globals/reloc_globals --runtime linx_runtime_info.json --device a.o b.o --debug
```

Option description:

`--runtime` specifies the runtime information entered on the host side

`--device` specifies the relocatable file on the device side, and can specify 1-n device-side input files.
`--debug` outputs intermediate debugging information
`--help` outputs help information

If a global variable is used in the Block ISA relocatable file, `reloc_globals` will replace the global variable with the address of the global variable in the host executable file and write it back to the original relocatable file; if the global variable is not used, no modification will be made.

In addition, in heterogeneous mode, only the kernel function-related code on the Device side (kernel function and functions called by the kernel function) runs on the Block ISA model. Other non-kernel function-related code will not actually be executed by the model. Therefore, when processing the above input .o file on the device side, if there is an undefined symbol in the .o, the tool will determine the undefined symbol through the runtime information. If the undefined symbol does not exist in the host side runtime information, a definition of the undefined symbol will be generated; if the undefined symbol is used in the host side runtime information, an error will be reported, prompting that the definition of the symbol is required.

## Link

Link the above modified relocatable file into the executable file of Block ISA through the gcc compiler:

```shell
${compiler_path}/linx64-unknown-elf/bin/linx64-unknown-elf-gcc -O2 a.o b.o -o bisa_kernel.o
```

Link the above modified relocatable file into the executable file of Block ISA through the llvm compiler:

```shell
${compiler_path}/bin/clang -O2 a.o b.o -o bisa_kernel.o --target=linx64 -march=linx64im -mabi=lp64
```

## Run

Execute the executable file on the host side. When the kernel function is executed, the BlockISA model will read the BlockISA executable file and execute the kernel function. Except for the kernel function, the rest of the code runs on the host.

```shell
# 设置kernel函数运行在Block ISA模型上
unset BISA_MODEL_RUN
./a.out
```

# Python dependent libraries (not required)

**The following instructions only need attention when debugging the `reloc_globals` tool or running it with source code**
Block ISA relocation file global variable address adjustment tool, developed using python3 and [LIEF] (https://lief-project.github.io/), where LIEF is used to read and write binary files.
The `reloc_globals.py` source code is located in the `BlockISA/scripts/reloc_globals` directory

- Install LIEF:

``` shell
git clone https://github.com/lief-project/LIEF.git
cd LIEF
python3 setup.py install
```

> A bug needs to be fixed

- Run `reloc_globals.py`

```
python3 ${model_path}/BlockISA/scripts/reloc_globals/reloc_globals.py --host a.out --device a.o b.o --debug
```