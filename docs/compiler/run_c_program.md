# Run C program on CPU simulation model

This article is mainly used to introduce how to run a C language program on the Linx Instruction Set Architecture CPU simulation model.

## **Basic Concept**

The core of running the CPU model is to complete the compilation of both the simulation model and the C language program. The CPU simulation model includes gfsim and gfrun.

- **gfsim**: Actual CPU simulation model, clock-accurate model, named `model`.  
- **gfrun**: Regarding the verification model of the running results, actually run the program and determine whether the results are correct or not. It is named `emulator`.  

Linx Instruction Set Architecture Clock Accurate Model (GFSim) is a C++-based model with no dependencies on other libraries.  
This model is used to study the performance and design space exploration of Linx Instruction Set Architecture-based CPUs.  
This model is portable and can be transplanted to other components in `Gem5` or `HASim` for full system evaluation.  

## **Compile simulation model**

### **Download BlockISA code**

First open your Linux server, enter your personal working directory, and create a folder to store the BlockISA code.  

- You can execute the following commands:

```
    cd ${PATH/}
    ls
    mkdir blockisa
```

Then go to the folder directory you just created (blockisa/) and download the BlockISA code.  

- You can execute the following commands:

```
    cd blockisa/
    git clone ssh://git@codehub-dg-y.huawei.com:2222/Graphflow/BlockISA.git
```

Note: The download path is located at the `克隆/下载` location in the upper right corner of BlockISA's CodeHub.  

If you are downloading for the first time, an error will be reported at this step. This is because you have not configured the server key.  

- First you need to generate/obtain your personal secret key (public key and private key), execute the following command:

```
    ssh-keygen
```

After entering the command, you will be prompted to enter the file storing the secret key and the password. You can enter them all and use the default values.  
Example:

> energizing public/private rsa key pair.
> Enter file in which to save the key (~/.ssh/id_rsa): <--enter
> Enter passphrase (empty for no passphrase): <--enter
> Enter same passphrase again: <--enter

At this point you should have obtained the public and private keys, which are stored in the `~/.ssh/id_rsa.pub` and `~/.ssh/id_rsa` files by default.
View the generated public key and select and copy the contents.

```
    cat ~/.ssh/id_rsa.pub
```

Then configure the server secret key and execute in sequence:

> Enter CodeHub->Avatar in the upper right corner->Settings->SSH public key->Add SSH public key->Fill in the "ssh-rsa XXX" content->Confirm.

At this point you have configured the server key and execute the following command to download it normally.

```
    git clone ssh://git@codehub-dg-y.huawei.com:2222/Graphflow/BlockISA.git
```

### **Build simulation model**

Although the BlockISA code has been downloaded, the model cannot be run directly. It needs to be compiled to build the executable programs of `gfsim` and `gfrun`.
Here you can use the CMake tool to perform relevant configurations and generate makefile files, and perform compilation through the make command.

!!! note "note"
    
    Here you need to enter the same level directory as BlockISA.

Execute the following commands in sequence:

```
    cd BlockISA
    mkdir build
    cd build
    cmake ..
    make -j
```
After successful compilation, the executable programs of `gfsim` and `gfrun` will be generated in the /BlockISA/bin/ directory.
At the same time, the compilation of the model is completed here, and then continue to compile the C program that needs to be run.

## **Compile c program**

In order to match the instructions of BlockISA, the BlockISA compiler needs to be used to compile the c program.

### **Download gcc compiler**- Get the latest GCC compiler: [GCC compiler download path](http://10.175.104.61:8888/other/bisa_share/toolchain/BlockISA/GCC/Used-by-LLVM/).

Then create a file outside the blockISA directory, upload linx64-linux-gnu.tar and decompress it.

- You can execute the following commands:

```
    mkdir ctest
    cd ctest/
    tar -xf linx64-linux-gnu.tar.gz
```

### **Compile and link c program**

c file takes the following main.c content as an example:

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

At the same time, a start.s file needs to be compiled and linked, and its acquisition path is: [start.s file download path] (https://codehub-y.huawei.com/Graphflow/BlockISA/files?ref=master&filePath=test%2Fstart.s&isFile=true).
Next you can start compiling the file and linking it into an executable program (ELF file).

1. Compile the main.c file

```
    ./linx64-linux-gnu/bin/linx64-linux-gnu-gcc -c O2 main.c -o main.o
```

2. Compile the start.s file

```
    ./linx64-linux-gnu/bin/linx64-linux-gnu-gcc -c start.s -o start.o
```

3. Link

```
    ./linx64-linux-gnu/bin/linx64-linux-gnu-gcc main.o start.o -nostartfiles -static -o main.elf
```

## **Run program**

First copy the binary file to the BlockISA first-level directory

```
    cp  ${PATH}/blockisa/ctest/main.elf  ${PATH}/blockisa/BlockISA/
```

Specifically, copy the "linked binary file" to the "BlockISA first-level directory".

### **Run gfrun**

After copying, we can run gfrun to verify the model test.

* Verify model running executable program command:

```
    /bin/gfrun -f main.elf
```

* Printing `trace` mode can be enabled by adding the `-t 1` parameter:

```
    /bin/gfrun -f main.elf -t 1
```

### Run gfsim

At this time, if you run gfsim directly, it will not work, and some pre-order configuration is required.

!!! note "note"

    Here you need to deploy it every time you restart the server.

**Step one: Setup environment path**

After entering the BlockISA directory, enter the following commands:

```
    export LD_LIBRARY_PATH=${/path/to/BlockISA}/model/soc/lib
```

**Step 2: Set Soc parameters (Use default SOC parameters)**

The relevant parameters of SoC are in the `soc/parameter` file, and these parameters need to be linked.
Continue to enter the next command:

```
    ln -s ${/path/to/BlockISA}/model/soc/parameter/ ./parameter
```

**Step 3: Create a log folder (BlockISA first-level directory)**

Because the SOC stores log information into the log folder. Therefore, you need to create a log folder in the running directory.

```
    mkdir log
```

Then you need to recompile here. After entering the build directory (BlockISA/build), enter:

```
    cmake ..
    make –j
```

After completing the two compilations, you can run gfsim normally.

- **Run gfsim**

Return to the parent directory of the build and run the c program through gfsim to compile the linked executable file.  
Execute the following command:

```
    cd ..
    ./bin/gfsim -f main.elf
```

- **Output Trace information**

If you want to view the trace information of model execution, you can add the following parameters to the run command to enable trace mode.

- **-t 1** (trace mode 1): Output simple trace information of all stages of the model.
- **-t 2** (trace mode 2): Output tracking information during the model submission phase.
- **-t 3** (trace mode three): Output detailed tracking information for all stages of the model.

To enable tracking mode one, execute the following command:

```
    ./bin/gfsim -f main.elf –t 1
```

Example of output information in tracking mode one:

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

To enable tracking mode two, execute the following command:

```
    ./bin/gfsim -f main.elf –t 2
```

Trace Mode 2 dumps the BROB status timeline for each cycle.

![image](../figs/intro/gfsim-t2.png){ width="800" }

Tracking mode 2 output content format description:- **Symbol -**: The block is currently in an idle state (including the instruction fetch/rename/stay phase in `Block Control Core (BCC)`)
- **Symbol +**: The block is in the state of being distributed into a `PE`.
- **Symbol \***: The block is in the state of being executed in `PE` (including being submitted by PE)
- **Symbol r**: The block is in a stopped state due to reading a register (caused by inter-block register dependencies)
- **Symbol m**: The block is in a stalled state due to access to memory
- **Symbol num**: Number of block instruction executed
- **Symbol →**: The block is forwarding collection data

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

To enable tracking mode three, execute the following command:

```
    ./bin/gfsim -f main.elf –t 3
```

Example of output information of tracking mode three:

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

* You can also add the `-s core.soc_enable=true` parameter to run the model with a full system SOC:

```
    /bin/gfsim -f main.elf -s core.soc_enable=true
```