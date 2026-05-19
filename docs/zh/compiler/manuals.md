# Introduction

本文档主要介绍异构模式下Block ISA作为device设备，将任务offload至Block ISA的编译、运行方式。

# 源码修改

- **将需要卸载至Block ISA model运对于行的函数标记linx_kernel attribute**
- 目前对于kernel函数的**限制**：
    1. kernel函数的参数类型非浮点类型
    2. kernel函数的参数/返回值类型长度不超过64bit
    3. kernel函数及其被调用函数中不能调用系统库函数
    4. kernel函数及其被调用函数中不能使用间接调用（函数指针）方式

```c
#include <stdio.h>

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

以上述源码为例，若我们希望将`foo`函数卸载至Block ISA设备运行，则在`foo`函数添加`linx_kernel`和`noinline`attribute。

# Host编译

host编译器在编译kernel函数时，将在kernel函数中插入Block ISA模型的接口以及runtime。以X86作为host设备，当运行至kernel函数时，将从host切换至Block ISA model运行。runtime用以获取kernel函数中调用的函数及使用的全局变量信息。host侧的编译方式如下： 

- clone构建LLVM编译器：

  ```shell
  git clone -b dev_host_compilation ssh://git@codehub-dg-y.huawei.com:2222/linx/ISA-Codesign/BlockISA/linx-llvm.git
  ```

- clone构建Block ISA model仓：

  ```shell
  git clone -b master ssh://git@codehub-dg-y.huawei.com:2222/Graphflow/BlockISA.git
  ```

- 使用以上LLVM编译器编译host代码，并链接Block ISA的模型动态库: 

  ```shell
  clang xxx.c -o a.out -L ${model_path}/BlockISA/lib -lfunc_model -lruntime -L/usr/lib64 -lelf -O2 -flinx-instrument
  ```

- 如果编译过程提示以下warning：

  ```shell
  warning: private global variable xxx is used in kernel function.
  ```

- 以上warning产生，是因为kernel函数中存在常量字符串。目前Block ISA有gcc和llvm两条工具链，两条工具链对常量字符串的命名可能不同。若llvm编译器将常量字符串定义为全局变量，命名为a.str; 而gcc编译器可能会将这个该字符串定义为b.str。在后面处理全局变量时，host和device两侧就无法将这个全
  局变量对应起来。如果host和device的都使用llvm编译器，可以忽略该warning；如果host使用llvm编译器，device使用gcc编译器，则需要在源码中把该字符串定义为全局变量使用。 


# Host 运行

host侧编译链接通过之后，需要在host侧运行，以获取kernel函数执行期间调用函数及全局变量地址信息，runtime将会记录以上信息。执行host可执行文件后，将在执行目录下生成`linx_runtime_info.json`文件，其中记录了host执行期间kernel函数调用的函数以及使用的全局变量信息。以上述示例为例，先通过配置环境变量(表示host可执行文件完全运行在host machine），再运行可执行文件：

```shell
export BISA_MODEL_RUN=0
./a.out
```

运行结束后，将在执行目录下生成`linx_runtime_info.json`文件。

# Device编译  

Device（Block ISA）侧的编译过程，与普通编译过程的差异在于：在编译出Block ISA的可重定位文件(.o)后，需要使用工具根据host runtime信息，对应地修改Block ISA可重定位文件中全局变量的地址。因此，Device侧的编译过程为：  

## 编译

使用Block ISA llvm编译器将源码编译为 .o 文件:  

```shell
${compiler_path}/bin/clang a.c b.c -O2 -c --target=linx64 -march=linx64im -mabi=lp64 -fno-jump-tables
```

使用Block ISA gcc编译器将源码编译为`.o`文件：

```shell
${compiler_path}/linx64-unknown-elf/bin/linx64-unknown-elf-gcc -O2 a.c b.c -fno-section-anchors -c -mcmodel=medlow
```

## 全局变量地址调整

使用工具将Block ISA可重定位文件中全局变量的地址修改为host可执行文件中对应全局变量的地址。工具在`BlockISA/scripts/reloc_globals`目录下：  

```shell
${model_path}/BlockISA/scripts/reloc_globals/reloc_globals --runtime linx_runtime_info.json --device a.o b.o --debug
```

选项说明：

`--runtime`指定了host侧输入的runtime信息

`--device`指定了device侧的可重定位文件，可以指定1-n个device侧输入文件
`--debug`输出中间调试信息
`--help`输出帮助信息

若Block ISA可重定位文件中使用了全局变量， `reloc_globals`将全局变量替换为host可执行文件中全局变量的地址，写回至原可重定位文件；若没有使用全局变量则不做修改。

此外，异构模式下，Device侧只有kernel函数相关的代码（kernel函数及被kernel函数调用的函数）运行在Block ISA模型上，其它非kernel函数相关的代码，实际上并不会被模型执行。因此，在处理以上device侧输入.o文件时，若.o中存在未定义的符号，工具会通过runtime信息判断未定义的符号，若未定义的符号在host侧runtime信息中不存在，则生成一个未定义符号的定义；若未定义符号在host侧runtime信息中被使用，则进行报错，提示需要该符号的定义。

## 链接

通过gcc编译器将以上修改后的可重定位文件链接为Block ISA的可执行文件：

```shell
${compiler_path}/linx64-unknown-elf/bin/linx64-unknown-elf-gcc -O2 a.o b.o -o bisa_kernel.o
```

通过llvm编译器将以上修改后的可重定位文件链接为Block ISA的可执行文件：

```shell
${compiler_path}/bin/clang -O2 a.o b.o -o bisa_kernel.o --target=linx64 -march=linx64im -mabi=lp64
```

## 运行

执行host侧的可执行文件，执行至kernel函数时，BlockISA模型将读取BlockISA的可执行文件并执行kernel函数，除了kernel函数，其余代码运行在host上。

```shell
# 设置kernel函数运行在Block ISA模型上
unset BISA_MODEL_RUN
./a.out
```

# Python依赖库（非必须）

**以下说明只有当调试`reloc_globals`工具或者使用源码运行时需要关注**
Block ISA重定位文件中全局变量地址调整的工具，使用python3和[LIEF](https://lief-project.github.io/)开发，其中LIEF用于读写二进制文件。
`reloc_globals.py`源码位于`BlockISA/scripts/reloc_globals`目录下

- 安装LIEF：

``` shell
git clone https://github.com/lief-project/LIEF.git
cd LIEF
python3 setup.py install
```

> 需修改一处bug

- 运行`reloc_globals.py`

```
python3 ${model_path}/BlockISA/scripts/reloc_globals/reloc_globals.py --host a.out --device a.o b.o --debug
```
