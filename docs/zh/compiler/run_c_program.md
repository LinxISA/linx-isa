# CPU仿真模型上运行C程序

本篇主要用来介绍如何在灵犀指令集架构的CPU仿真模型上面跑一段C语言程序。

## **基本概念**

运行CPU模型的核心是完成对仿真模型和C语言程序双方的编译工作，其中CPU仿真模型包括gfsim和gfrun。

- **gfsim**：实际的CPU仿真模型，时钟精确模型，命名为 `model`。  
- **gfrun**：关于运行结果的校验模型，实际运行该程序，判断结果正误，命名为 `emulator`。  

灵犀指令集架构 时钟精确模型(GFSim)是一个基于C++的模型，与其他库没有依赖关系。  
该模型用于研究基于灵犀指令集架构的CPU的性能和设计空间探索。  
此模型是可移植的，可以移植到 `Gem5` 或 `HASim` 中的其他组件，用于整个系统评估。  

## **编译仿真模型**

### **下载BlockISA代码**

首先打开你的Linux服务器，进入到个人的工作目录下，创建存放BlockISA代码的文件夹。  

- 可以执行以下命令:

```
    cd ${PATH/}
    ls
    mkdir blockisa
```

然后进入到刚刚创建的文件夹目录(blockisa/)，下载BlockISA代码。  

- 可以执行以下命令:

```
    cd blockisa/
    git clone ssh://git@codehub-dg-y.huawei.com:2222/Graphflow/BlockISA.git
```

注：下载路径位于BlockISA的CodeHub-右上角 `克隆/下载` 位置。  

如果你是首次下载，到这一步会报错，这是因为你没有配置服务器秘钥。  

- 首先需要生成/获取个人的秘钥（公钥和私钥），执行以下命令:

```
    ssh-keygen
```

输入命令后会提示你输入存放秘钥的文件以及密语，可以全部enter，使用默认值。  
示例：

> enerating public/private rsa key pair.  
> Enter file in which to save the key (~/.ssh/id_rsa):  <--enter  
> Enter passphrase (empty for no passphrase):  <--enter  
> Enter same passphrase again:  <--enter  

此时你应该已经获得了公钥和私钥，默认存放在 `~/.ssh/id_rsa.pub` 和 `~/.ssh/id_rsa` 文件内。
查看生成的公钥，并将该内容全选复制。

```
    cat ~/.ssh/id_rsa.pub
```

然后配置服务器秘钥，依次执行：  

> 进入CodeHub->右上角头像->设置->SSH公钥->添加SSH公钥->将"ssh-rsa XXX"内容填入->确认。

此时你已经配置好服务器秘钥，执行下列命令，可以正常下载。

```
    git clone ssh://git@codehub-dg-y.huawei.com:2222/Graphflow/BlockISA.git
```

### **构建仿真模型**

尽管已经下载好BlockISA的代码，但是还不能直接跑模型，需要通过编译来构建`gfsim`和`gfrun`的可执行程序。
这里可以使用CMake工具来进行相关配置以及生成makefile文件，并通过make命令执行编译。

!!! note "注意"
    
    这里需要进入BlockISA同一级目录。

依次执行以下命令：

```
    cd BlockISA
    mkdir build
    cd build
    cmake ..
    make -j
```
编译成功后，会在/BlockISA/bin/目录下生成`gfsim`和`gfrun`的可执行程序。
同时到这里模型的编译就完成了，接下来继续编译需要运行的c程序。

## **编译c程序**

为了和BlockISA的指令匹配，需要用到BlockISA的编译器来编译c程序。

### **下载gcc编译器**

- 获取最新的GCC编译器：[GCC编译器下载路径](http://10.175.104.61:8888/other/bisa_share/toolchain/BlockISA/GCC/Used-by-LLVM/)。  

然后在blockISA的目录外部建立一个文件，上传linx64-linux-gnu.tar并解压。

- 可以执行以下命令：

```
    mkdir ctest
    cd ctest/
    tar -xf linx64-linux-gnu.tar.gz
```

### **编译链接c程序**

c文件以下面的main.c内容为例：

```
    int main()
    {
        int a, b, c;
        a = 1;
        b = 2;
        c = a + b;
        return 0;
    }
```

同时需要编译链接一个start.s文件，其获取路径为：[start.s文件下载路径](https://codehub-y.huawei.com/Graphflow/BlockISA/files?ref=master&filePath=test%2Fstart.s&isFile=true)。
下面你就可以开始编译文件并链接成可执行程序（ELF文件）。

1、编译main.c文件

```
    ./linx64-linux-gnu/bin/linx64-linux-gnu-gcc -c O2 main.c -o main.o
```

2、编译start.s文件

```
    ./linx64-linux-gnu/bin/linx64-linux-gnu-gcc -c start.s -o start.o
```

3、链接

```
    ./linx64-linux-gnu/bin/linx64-linux-gnu-gcc main.o start.o -nostartfiles -static -o main.elf
```

## **运行程序**

首先把二进制文件复制到BlockISA一级目录

```
    cp  ${PATH}/blockisa/ctest/main.elf  ${PATH}/blockisa/BlockISA/
```

具体而言，就是将 “链接后二进制文件” 拷贝到 “BlockISA的一级目录”。

### **运行gfrun**

复制之后，我们可以运行gfrun，进行校验模型测试。

* 校验模型跑可执行程序命令:

```
    /bin/gfrun -f main.elf
```

* 可以通过添加`-t 1`参数来启用打印`trace`模式:

```
    /bin/gfrun -f main.elf -t 1
```

### 运行gfsim

此时如果直接运行gfsim是无法运行的，需要进行一些前序配置。

!!! note "注意"

    这里每次重启服务器都需要部署一遍。

**第一步：设置环境路径（Setup environment path）**

进入BlockISA目录后，输入下列指令：

```
    export LD_LIBRARY_PATH=${/path/to/BlockISA}/model/soc/lib
```

**第二步：设置Soc参数（Use default SOC parameters）**

SoC的相关参数在 `soc/parameter` 文件内，需要对于这些参数进行链接。
继续输入下条指令：

```
    ln -s ${/path/to/BlockISA}/model/soc/parameter/ ./parameter
```

**第三步：建立日志文件夹（BlockISA一级目录）**

因为 SOC 会将日志信息存储到日志文件夹中。因此，你需要在运行目录下创建一个日志文件夹。

```
    mkdir log
```

然后这里要重新编译一下，进入build目录（BlockISA/build）之后，输入:

```
    cmake ..
    make –j
```

完成两项编译之后就可以正常运行gfsim了。

- **运行gfsim**

返回到build的上级目录，通过 gfsim 运行c程序编译链接后的可执行文件。  
执行以下命令：

```
    cd ..
    ./bin/gfsim -f main.elf
```

- **输出Trace信息**

如果你想查看模型执行的trace信息，可以在运行命令中添加如下参数来启用跟踪模式。

- **-t 1**(trace 模式一)：输出模型所有阶段的简单跟踪信息。
- **-t 2**(trace 模式二)：输出模型提交阶段的跟踪信息。
- **-t 3**(trace 模式三)：输出模型所有阶段的详细跟踪信息。

启用跟踪模式一，执行以下命令：

```
    ./bin/gfsim -f main.elf –t 1
```

跟踪模式一输出信息示例：

```
Cycle 44:
[IFU0           Stage]: prefetch tag: 0x13f40 icache miss and send request packet
[BCC  Decode    Stage]: BSeq 1: Block COND Size 196 GET( R1 R2 R3 R4 R8 ) SET( R2 R3 R11 ) BTEXT 0x13fb2 (CONCAT)
[IFU1           Stage]: received prefetch tpc: 0x13fb2 size: c4
[IFU1           Stage]: The tag: 0x13f80 enters the prefetch queue.
[IFU1           Stage]: The tag: 0x13fc0 enters the prefetch queue.
[IFU1           Stage]: The tag: 0x14000 enters the prefetch queue.
[IFU1           Stage]: The tag: 0x14040 enters the prefetch queue.
[IFU1           Stage]: The tag: 0x14080 enters the prefetch queue.
[IFU1           Stage]: The tag: 0x140c0 enters the prefetch queue.
[IFU1           Stage]: The tag: 0x14100 enters the prefetch queue.
[BCC  Decode    Stage]: set IFU prefetch queue tpc: 0x13fb2 size: c4
[BCC  Issue Stage]: current Lane Count after enqueue:  57 197 0 0
[BCC  Decode    Stage]: BSeq 2: Block DIRECT Size 0 BTEXT 0x1413a
[BCC  Decode    Stage]: set IFU prefetch queue tpc: 0x1413a size: 0
[BCC  Issue Stage]: current Lane Count after enqueue:  57 197 1 0
[BCC  Rename    Stage]: Get B0-R1-P1 B0-R2-P2 B0-R3-P3 B0-R8-P8 B0-End | x-> finish Get rename Block:0, continue
[BCC  Rename    Stage]: Set B0-R3-P16 B0-R4-P17 B0-End | x-> finish Set rename Block:0, continue
[BCC  Rename    Stage]: Get | x-> get nothing, skip
[BCC  Rename    Stage]: Set | x-> set nothing, skip

```

启用跟踪模式二，执行以下命令：

```
    ./bin/gfsim -f main.elf –t 2
```

跟踪模式2转储每个周期的BROB状态时间线。

![image](../figs/intro/gfsim-t2.png){ width="800" }

跟踪模式2输出内容格式说明：

- **Symbol -**: 该块目前是处于空闲的状态 (包括在`Block Control Core (BCC)`中取指/重命名/停留的阶段)
- **Symbol +**: 该块处于被分发到一个`PE`中的状态。
- **Symbol \***: 该块处于在`PE`中执行的状态 (包括被PE提交)
- **Symbol r**: 该块处于由于读取寄存器而停止的状态 (是由与块间寄存器依赖关系引起)
- **Symbol m**: 该块处于由于访问存储器而停止的状态
- **Symbol num**: 执行的块指令数
- **Symbol →**: 该块正在转发集合数据

```
GFSim start executing at BPC 0x105e0
Cycle 1 ---------------------------------------------------------------- IPC 0
Cycle 2 ---------------------------------------------------------------- IPC 0
Cycle 3 ---------------------------------------------------------------- IPC 0
Cycle 4 ---------------------------------------------------------------- IPC 0
Cycle 5 ---------------------------------------------------------------- IPC 0
Cycle 6 ---------------------------------------------------------------- IPC 0
Cycle 7 +--------------------------------------------------------------- IPC 0
Cycle 8 ++-------------------------------------------------------------- IPC 0
Cycle 9 ++-------------------------------------------------------------- IPC 0
Cycle 10 +++------------------------------------------------------------- IPC 0
Cycle 11 ++++------------------------------------------------------------ IPC 0
Cycle 12 +++++----------------------------------------------------------- IPC 0
Cycle 13 ++++++---------------------------------------------------------- IPC 0
Cycle 14 +++++++--------------------------------------------------------- IPC 0
Cycle 15 *++r++++-------------------------------------------------------- IPC 1
Cycle 16 **+rr++++------------------------------------------------------- IPC 3
Cycle 17 **+rrr++++------------------------------------------------------ IPC 4
Cycle 18 m**rrrr++++----------------------------------------------------- IPC 4
Cycle 19 m+rrrrrr++-+---------------------------------------------------- IPC 0
Cycle 20 m*rrrrrrr+-+---------------------------------------------------- IPC 4
Cycle 21 m*rrrrrrrr*++--------------------------------------------------- IPC 8
Cycle 22 +*rrrrrrrr*+++-------------------------------------------------- IPC 6
Cycle 23 +*rrrrrrrr*r+++------------------------------------------------- IPC 5
Cycle 24 +-rrrrrrrr-r++++------------------------------------------------ IPC 2
Cycle 25 *-rrrrrrrr-r+++++----------------------------------------------- IPC 6
Cycle 26 +-+rrrrrrr-r+r++++---------------------------------------------- IPC 4
Cycle 27 --*rrrrrrr-r+rr++++--------------------------------------------- IPC 4
Cycle 28 --*rrrrrrr-r+rrr++++-------------------------------------------- IPC 4
Cycle 29 --*rrrrrrr-r*rrrr++++------------------------------------------- IPC 6
Cycle 30 --*rrrrrrr-+*rrrrr++-+------------------------------------------ IPC 6
Cycle 31 --**rrrrrr-+*rrrrrr+-++----------------------------------------- IPC 4
Cycle 32 --++rrrrrr-**rrrrrrr*+++---------------------------------------- IPC 5
Cycle 33 --+*rrrrrr--*rrrrrrr*++++--------------------------------------- IPC 5
Cycle 34 --+*rrrrrr--*rrrrrrr*r++++-------------------------------------- IPC 7
Cycle 35 --+*rrrrrr--*rrrrrrr-r+++++------------------------------------- IPC 4
Cycle 36 --+*rrrrrr---rrrrrrr-r+r++++------------------------------------ IPC 5
Cycle 37 --++rrrrrr---*rrrrrr-r+rr++++----------------------------------- IPC 6
Cycle 38 --++rrrrrr---+rrrrrr-r+rrr++++---------------------------------- IPC 6
Cycle 39 --*rrrrrrr---+rrrrrr-r*rrrr++++--------------------------------- IPC 4
Cycle 40 --*r+rrrrr---*rrrrrr-r*rrrrr++-+-------------------------------- IPC 6
Cycle 41 ---r+rrrrr---*rrrrrr-+*rrrrrr+-++------------------------------- IPC 6
Cycle 42 ---r*rrrrr---*rrrrrr-++rrrrrrr*+++------------------------------ IPC 6
Cycle 43 ---r*rrrrr---*rrrrrr-*+rrrrrrr*++++----------------------------- IPC 9
Cycle 44 ---+*rrrrr---*rrrrrr--*rrrrrrr*r++++---------------------------- IPC 9
Cycle 45 ---+*rrrrr---+rrrrrr--+rrrrrrr-r+++++--------------------------- IPC 5
Cycle 46 ---*+rrrrr---*rrrrrr--*rrrrrrr-r+r+++--------------------------- IPC 7
Cycle 47 ----*rrrrr---*rrrrrr--+rrrrrrr-r+rr++--------------------------- IPC 5
Cycle 48 -----rrrrr---+rrrrrr--*+rrrrrr-r+rrr+--------------------------- IPC 6
Cycle 49 -----*rrrr---+rrrrrr--++rrrrrr-r*rrrr--------------------------- IPC 6
Cycle 50 -----*rrrr---*rrrrrr--++rrrrrr-r*rrrr--------------------------- IPC 5
Cycle 51 -----*rrrr---+rrrrrr--*+rrrrrr-+*rrrr--------------------------- IPC 5
Cycle 52 -----*rrrr---*rrrrrr--+*rrrrrr-+*rrrr--------------------------- IPC 6
Cycle 53 -----*rrrr---+rrrrrr--+*rrrrrr-*+rrrr--------------------------- IPC 5
Cycle 54 -----*rrrr----rrrrrr--**rrrrrr--+rrrr--------------------------- IPC 10
Cycle 55 -----*rrrr----+rrrrr---+rrrrrr--+rrrr--------------------------- IPC 3
Cycle 56 -----+rrrr----*rrrrr---*rrrrrr--*rrrr--------------------------- IPC 5
Cycle 57 ------rrrr----*rrrrr---+rrrrrr--r+rrr--------------------------- IPC 6
Cycle 58 ------*rrr----*rrrrr---+rrrrrr--r+rrr--------------------------- IPC 7
Cycle 59 ------*rrr----*rrrrr---*rrrrrr--r*rrr+-------------------------- IPC 7
Cycle 60 ------*rrr----*rrrrr---rrrrrrr--r*rrr++------------------------- IPC 6
Cycle 61 ------*rrr----*rrrrr---rrrrrrr--r*rrr+++------------------------ IPC 4
Cycle 62 ------*rrr----*rrrrr---rrrrrrr--r*rrr++++----------------------- IPC 5
Cycle 63 ------*rrr----+rrrrr---*rrrrrr--r+rrrr++-+---------------------- IPC 5
Cycle 64 ------*rrr-----+rrrr---+rrrrrr--r+rrrrr+-+---------------------- IPC 1
Cycle 65 ------+rrr-----*rrrr---*rrrrrr--r+rrrrrr*+---------------------- IPC 4
Cycle 66 -------rrr-----*rrrr---*rrrrrr--r*rrrrrr*++--------------------- IPC 9
Cycle 67 -------*rr-----*rrrr---*+rrrrr--rrrrrrrr*r++-------------------- IPC 4
Cycle 68 -------*rr-----*rrrr---*+rrrrr--rrrrrrrr-r+++------------------- IPC 6
Cycle 69 -------*rr-----*rrrr---++rrrrr--rrrrrrrr-r++++------------------ IPC 8
Cycle 70 -------*rr-----*rrrr----+rrrrr--r++rrrrr-r++++------------------ IPC 6
Cycle 71 -------*rr-----*rrrr----*rrrrr--r+*rrrrr-r+r++------------------ IPC 6
Cycle 72 -------*rr-----+rrrr----*rrrrr--r**rrrrr-r+rr+------------------ IPC 8
Cycle 73 -------*rr------+rrr----*rrrrr--r**rrrrr-r+rrr------------------ IPC 6
Cycle 74 -------+rr------+rrr----*rrrrr--r+*rrrrr-+*rrr------------------ IPC 8
Cycle 75 --------rr------*rrr----+rrrrr--r+*rrrrr-+*rrr------------------ IPC 7
Cycle 76 --------*r------*rrr----*rrrrr--r+*rrrrr-**rrr------------------ IPC 8
Cycle 77 --------*r------*rrr----*rrrrr--r++rrrrr--*rrr------------------ IPC 8
Cycle 78 --------*r------*rrr----*+rrrr--r*+rrrrr--*rrr------------------ IPC 9
Cycle 79 --------*r------*rrr----*+rrrr--r++rrrrr--*rrr+----------------- IPC 8
Cycle 80 --------*r------*rrr----**rrrr--r++rrrrr---rrr++---------------- IPC 4
Cycle 81 --------*r------*rrr----+*rrrr--r*+rrrrr---rrr++---------------- IPC 8
Cycle 82 --------*r------*+rr-----*rrrr--r++rrrrr---*rr++---------------- IPC 6
Cycle 83 --------+r------++rr-----*rrrr--rr+rrrrr---+rrr+---------------- IPC 4
Cycle 84 ---------r-------*rr-----rrrrr--r++rrrrr---*rrrr---------------- IPC 6
Cycle 85 ---------*-------*rr-----rrrrr--r+*rrrrr---*rrrr---------------- IPC 8
Cycle 86 ---------*m------*rr-----+rrrr--r*rrrrrr---*rrrr---------------- IPC 6
Cycle 87 ---------*m------*rr-----++rrr--r-rrrrrr---*rrrr---------------- IPC 7
Cycle 88 ---------*m------*rr-----*+rrr--r-rrrrrr---*rrrr---------------- IPC 8
Cycle 89 ---------**------*rr-----**rrr--r-r+rrrr---+rrrr---------------- IPC 6
Cycle 90 ---------**------*rr-----**rrr--r-r+rrrr---rrrrr---------------- IPC 10
Cycle 91 ---------**------*rr-----**rrr--r-+*rrrr---r*rrr---------------- IPC 8
Cycle 92 ---------+*------+rr-----+*rrr--r-+*rrrr---++rrr---------------- IPC 6
Cycle 93 ------------------+r------rrrr--r-**rrrr---++rrr---------------- IPC 5
Cycle 94 ------------------*r------rrrr--r-**rrrr---**rrr---------------- IPC 7
Cycle 95 ------------------*r------+rrr--r-*rrrrr----*rrr---------------- IPC 6
Cycle 96 ------------------*r------++rr--r-*rrrrr----*rrr---------------- IPC 4
Cycle 97 ------------------*r------*+rr--r-+rrrrr----*rrr+--------------- IPC 6
Cycle 98 ------------------*r------*+rr--r--r+rrr----*rrr++-------------- IPC 5
Cycle 99 ------------------*r------*+rr--r--r+rrr----*rrr+++------------- IPC 5
Cycle 100 ------------------*r------+*rr--r--+*rrr----*rrr++-+------------ IPC 6
Cycle 101 ------------------+r------**rr--r--+*rrr----++rrr+-++----------- IPC 4
Cycle 102 -------------------+------+*rr--r--**rrr-----+rrrr*+++---------- IPC 4
Cycle 103 -------------------*-------+rr--r--**rrr-----*rrrr*++++--------- IPC 7
Cycle 104 -------------------*-------*rr--r--*rrrr-----*rrrr*r++++-------- IPC 6
Cycle 105 -------------------*-------rrr--r--+rrrr-----*rrrr-r+++++------- IPC 3
Cycle 106 -------------------*-------rrr--r--*rrrr-----*rrrr-r+r++++------ IPC 9
Cycle 107 -------------------*-------+rr--r--+r+rr-----*rrrr-r+rr++++----- IPC 7
Cycle 108 -------------------*m------++r--r---r+rr-----*rrrr-r+rrr+++----- IPC 5
Cycle 109 -------------------*m------*+r--r---r*rr-----+rrrr-r*rrrr++----- IPC 9
Cycle 110 -------------------+m------**r--r---+*rr-----++rrr-r*rrrrr+----- IPC 7
Cycle 111 --------------------*------**r--r---+*rr-----++rrr-r*rrrrrr----- IPC 7
Cycle 112 --------------------*------*+r--r---**rr-----+*rrr-+*rrrrrr----- IPC 9
Cycle 113 --------------------*------++r--r---*rrr-----**rrr-+*rrrrrr----- IPC 8
Cycle 114 --------------------*-------+r--r---*rrr-----+*rrr-*-rrrrrr----- IPC 6
Cycle 115 ----------------------------*r--r---*rrr------*rrr---*rrrrr+---- IPC 9
Cycle 116 ----------------------------*r--r---+r+r------rrrr---+rrrrr++--- IPC 4
Cycle 117 ----------------------------*r--r----r+r------rrrr---*rrrrr+++-- IPC 7
Cycle 118 ----------------------------*r--r----r*r------rrrr---*rrrrr+++-- IPC 9
Cycle 119 --------------------*-------*r--r----+*r------r+rr---*rrrrrr++-- IPC 9
Cycle 120 --------------------*-------*r--r----+*r------++rr---*rrrrrr++-- IPC 9
Cycle 121 --------------------*-------+r--r----**r------+*rr---*rrrrrr+r-- IPC 8
Cycle 122 ----------------------------*r--r----*rr------**rr---+rrrrrr+r-- IPC 6
Cycle 123 ----------------------------+r--r----*rr------**rr----rrrrrr+r-- IPC 5
Cycle 124 -----------------------------r--r----*rr------**rr----*rrrrr+r-- IPC 8
Cycle 125 -----------------------------+--r----+r+------*rrr----+rrrrr+r-- IPC 3
Cycle 126 --------------------*--------*--r-----r+------+rrr----*rrrrr-r-- IPC 4
Cycle 127 --------------------*--------*--r-----r*-------rrr----*rrrrr-r-- IPC 7
Cycle 128 --------------------*--------*--r-----+*-------r+r----*rrrrr-r-- IPC 7
Cycle 129 -----------------------------*--r-----+*-------++r----*rrrrr-r-- IPC 6
Cycle 130 --------------------m--------*--r-----+*-------+*r----*rrrrr-r-- IPC 8
Cycle 131 --------------------m--------*m-r-----+r-------**r----+rrrrr-r-- IPC 4
Cycle 132 --------------------m--------*m-r-----+r-------**r-----rrrrr-r-- IPC 5
Cycle 133 --------------------*--------+m-r-----*r-------**r-----*rrrr-r-- IPC 6
Cycle 134 --------------------*---------*-r-----*r-------*rr-----+rrrr-r-- IPC 6
Cycle 135 --------------------*---------*-+-----*r-------+rr-----*rrrr-r-- IPC 4
Cycle 136 ------------------------------*-+-----*r--------rr-----*rrrr*r-- IPC 6
Cycle 137 ------------------------------*-*-----+r--------r+-----*rrrr*r-- IPC 6
Cycle 138 --------------------------------+------r--------++-----*rrrr*r-- IPC 4
Cycle 139 ---------------------------------------r--------+*-----*rrrr*r-- IPC 5
Cycle 140 ---------------------------------------+--------**-----+rrrr*r-- IPC 3
Cycle 141 ---------------------------------------+--------**------rrrr-r-- IPC 3
Cycle 142 ---------------------------------------*--------**------*rrr-r-- IPC 5
Cycle 143 ---------------------------------------*--------*r------+rrr-r+- IPC 3
Cycle 144 ---------------------------------------*m-------+r------*rrr-r++ IPC 3

```

启用跟踪模式三，执行以下命令：

```
    ./bin/gfsim -f main.elf –t 3
```

跟踪模式三的输出信息示例：

```
Cycle 93:
[OPE0 Fetch     Stage]: Received fetch data at: 0x13fa2 mask 16 data 2239 467 5400 28 2083 467 4101 82b  (Block 0)
[OPE1 Fetch     Stage]: Received fetch data at: 0x14002 mask 16 data 2367 e001 9300 48 4761 2771 230 e001  (Block 1)
[BCC  Rename    Stage]: Get | x-> get nothing, skip
[BCC  Rename    Stage]: Set | x-> set nothing, skip
BROB size 26
        B0 BPC 0x12c58 executing in PE0<- oldest
        B1 BPC 0x12c68 executing in PE1
        B2 BPC 0x12c78 completed
        B3 BPC 0x12c48 executing in PE3
        B4 BPC 0x12c50 executing in PE2
        B5 BPC 0x12cb8 executing in PE3
        B6 BPC 0x12cc0 completed
        B7 BPC 0x12c80 executing in PE2
        B8 BPC 0x12c90 executing in PE3
        B9 BPC 0x12ca0 executing in PE0
        B10 BPC 0x12cb0 completed
        B11 BPC 0x12ce0 dispatched to PE2 for execution
        B12 BPC 0x12ce8 dispatched to PE2 for execution
        B13 BPC 0x12cf0 dispatched to PE1 for execution
        B14 BPC 0x12cf8 completed
        B15 BPC 0x12d00 completed
        B16 BPC 0x12d08 dispatched to PE2 for execution
        B17 BPC 0x12d10 completed
        B18 BPC 0x12d18 dispatched to PE1 for execution
        B19 BPC 0x12d28 dispatched to PE2 for execution
        B20 BPC 0x12d30 dispatched to PE2 for execution
        B21 BPC 0x12d48 dispatched to PE2 for execution
        B22 BPC 0x12d58 dispatched to PE3 for execution
        B23 BPC 0x12d68 completed
        B24 BPC 0x12d38 dispatched to PE0 for execution
        B25 BPC 0x12d40 dispatched to PE0 for execution
        B26 BPC 0x0
        B27 BPC 0x0

```

* 你也可以添加 `-s core.soc_enable=true` 参数，运行带有全系统SOC的模型:

```
    /bin/gfsim -f main.elf -s core.soc_enable=true
```
