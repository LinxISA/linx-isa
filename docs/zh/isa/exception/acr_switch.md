# ACR切换

一个灵犀逻辑核(LxLC)的ACR状态可以被如下事件改变：

1. 灵犀逻辑核(LxLC)外部中断。
2. 灵犀逻辑核(LxLC)内部执行异常。
3. [acre](../inst/misa_s/ACRE.md)指令所在块提交。
4. [acrc](../inst/misa_s/ACRC.md)指令所在块提交。
5. [系统调用块](../blockIntro/xb_block/intro.md)的准备和提交

这种改变通常同时会引起程序执行序列的变化。这种综合变化可以分成两类：

* 一层（指令）级别切换
  * `ACR_ENTER`。这主要用于管理软件把灵犀逻辑核(LxLC)控制权主动交给被管理的软件。`acre`指令所在块提交属于这种类别。
  * `SERVICE_REQUEST`。这主要用于被管理的软件把灵犀逻辑核(LxLC)的控制权还给管理软件。灵犀逻辑核(LxLC)外部中断，内部执行异常，或者`acrc`指令所在块提交属于这种类别。
* 二层（指令）级别切换
  * `系统调用块`，系统调用块在调用的时候切换到目标ACR，并在提交阶段结束后恢复到切换前的ACR。

## ACR_ENTER

ACR_ENTER通过`acre`指令请求，并在块提交的时候激发。

对于一次从ACRn发起的ACR_ENTER，其具体过程为：

1. 灵犀逻辑核(LxLC)的ACR状态切换到系统寄存器[ECSTATE_ACRn](../register/ssr/ECSTATE.md).ACR。目标ACR必须和当前ACRn可比，并且 ACRn p>= ECSTATE_ACRn.ACR。否则这个步骤本身触发E_INST(EC_PARAM)异常。
2. 用`SSR:ECSTATE_ACRn`的内容恢复当前`SSR:CSTATE`的状态（即，使后者的有效域的内容和前者完全一致）。
3. 用`SSR:EBPC_ACRn`恢复BPC的内容，并调度BPC所在的块执行。
4. 根据`ACRE.RRA`参数，选择是否用`SSR:EBARG_ACRn`的内容恢复`BARG`。
5. 如果`SSR:EBARG`中记录的块类型是STD、SYS或FP，用`SSR:ETPC_ACRn`的内容恢复TPC执行；

## SERVICE_REQUEST

SERVICE_REQUEST可以被三种事件驱动：

1. 通过调用`acrc`指令由软件主动激发。
2. 灵犀逻辑核(LxLC)在执行流水线上遇到同步异常。
3. 灵犀逻辑核(LxLC)在执行流线上检测到异步中断。

`acrc`和异常都是同步的，称为`SYNC_SERVICE_REQUEST`。中断是异步的，称为`ASYNC_SERVICE_REQUEST`。

`SYNC_SERVICE_REQUEST`和`ASYNC_SERVICE_REQUEST`在本文中统称`陷阱`，进入`陷阱`的过程，称为`陷入`。

当发生陷入的时候，引起陷入的原因通过参数`陷入代号`（`Trap Number`，或者`Trap No`）和`陷入原因代号`表示。这两个参数的具体定义，

* 对于中断，请具体参考每个`Xproxy`的定义。
* 对于异常，请参考`s_exception_trap_no`。

如果一个异常的陷入代号为t，原因代号为c，本文会把该异常简单表述为“t(c)”的异常。

部分陷阱包含更多的信息说明原因，这些参数称为`陷入参数`（`TrapArgs`），由每个具体的陷阱具体决定。

发生陷入的时候，陷入代号和原因代号保存在SSR:[TRAPNO_ACRn](../register/ssr/TRAPNO.md)中，陷入参数保存在SSR:[TRAPARG0_ACRn](../register/ssr/TRAPARG0.md)中。

SERVICE_REQUEST总是从某个指令位置激发的，这个位置由BPC和TPC共同定义。这个BPC和TPC共同指定的信息称为这个SERVICE_REQUEST的`陷阱源指令`，或者简称`源指令`。

需要注意的是：并非所有的异常都会触发SERVICE_REQUEST流程，如果异常发生在未被接管的`主动修复块`中，该异常按主动修复块的定义处理。

### <span id="SR_Process">SERVICE_REQUEST流程</span>

对于任意从ACRn到ACRm的SERVICE_REQUEST，其具体行为为，

* 如果是浮点运算产生的相关异常，设置CSTATE.flags中的对应标志位。
* 当前`SSR:CSTATE`保存到`SSR:ECSTATE_ACRm`。如果触发指令是块头指令，设置SSR:ECSTATE_ACRm.BI为0，否则设置为1；；
*	异常块的BPC保存至`SSR:EBPC_ACRm`;
*	异常块的BARG内容保存到`SSR:EBARG_ACRm`，设置`EBARG_ACRm.BlockType`为触发块类型。
*	如果异常块是STD、SYS或FP块，保存触发异常指令的TPC到`SSR:ETPC`； 
*	如果异常块是MPAR、MSEQ、VPAR或VSEQ块，保存触发异常的GroupID至`EBARG.GroupID`字段。
* CSTATE.I设置为0；    # 中断使能位
* CSTATE.ACR位置为m；
* BARG复位到初值；
* BPC设置为EVBASE_ACRm；
* 对于SYNC_SERVICE_REQUEST，
  * TRAPNO_ACRm.E置1；
  * 根据陷入代号和参数，设置`SSR:TRAPNO_ACRm`和`SSR:TRAPARG0_ACRm`。
* 对于ASYNC_SERVICE_REQUEST，
  * TRAPNO_ACRm.E置0；
  * 根据中断类型设置`SSR:TRAPNO_ACRm`和`SSR:TRAPARG0_ACRm`。具体取值参考对应的`Xproxy`定义。

以上行为在灵犀逻辑核(LxLC)内部一次完成，中间不会有其他改变灵犀逻辑核(LxLC)状态的行为介入。

<!-- 
需要特别指出的是：如果在ACRn中的管理软件处理SERVICE_REQUEST的时候，触发第二次`SERVICE_REQUEST`，而该次`SERVICE_REQUEST`的目标ACR仍是ACRn，那么系统寄存器[EBSTATEP](../register/ssr/EBSTATEP.md)指向的`EBSTATE` 会被覆盖，未保存的内容将永远丢失，软件需要通过针对性的设计规避这个问题。
 -->

## BSTATE和EBSTATE

一个`块执行单元`的内部状态称为`BSTATE`，不同`块执行单元`可能使用不同格式的`BSTATE`。

!!! note "注意!"

    请注意：CSTATE不是BSTATE的一部分，它是第一层架构的状态。

而**EBSTATE (Exception Block State)** 是用于保存和恢复状态的存储空间。这个空间的实现根据块类型的不同可能不同。

### **STD、SYS、FP块**

对于 STD、SYS、FP 类型的块指令，其用于标量运算或系统级控制，块内状态相对简单。其 EBSTATE 由系统寄存器与内存共同实现。

当触发异常或中断时，硬件需将 BSTATE 的相关内容保存至系统寄存器，具体为：

- 将 BARG.BPC 写入 **SSR:EBPC**；
- 将 BARG.BPCN 写入 **SSR:EBPCN**；
- 将 BARG 的其余字段写入 **SSR:EBARG**；
- 将 TPC 写入 **SSR:ETPC**。

在异常恢复时，硬件需将上述系统寄存器内容加载回对应的块内寄存器，保证块指令从异常触发点正确继续执行。

BSTATE 中其他 T/U 等标量寄存器是否保存至内存及是否恢复，由操作系统自行决定。

### **VPAR、VSEQ、MPAR、MSEQ块**

对于 VPAR、VSEQ、MPAR、MSEQ 等类型的块指令而言，块内状态相对复杂，并且需要非常大的空间来保存EBSTATE。其 EBSTATE 由系统寄存器与Tile寄存器共同实现。

当触发异常或中断时，硬件需将 BSTATE 的相关内容保存至系统寄存器，具体为：

- 将 BARG.BPC 写入 **SSR:EBPC**；
- 将 BARG.BPCN 写入 **SSR:EBPCN**；
- 将 BARG 的其余字段写入 **SSR:EBARG**；
- 将 触发异常的Group的ID记录在 **SSR:EBARG**。

在异常恢复时，硬件需将上述系统寄存器内容加载回对应的块内寄存器，保证块指令从异常触发点正确继续执行。

BSTATE 中其他寄存器状态是否保存至Tile寄存器或内存及是否恢复，由操作系统自行决定。其中包括：

- 可以通过调用 TSTORE 指令将所有或某一类Tile寄存器保存至内存；
- 可以通过调用 ESAVE 模版块保存Group的TPC和LPR至Tile寄存器; 
- 可以通过调用 TSTORE 指令将ESAVE输出的Tile寄存器内容保存至内存。

如果`块执行单元`在执行中被`SERVICE_REQUEST`打断，而它的`BSTATE`已经改变且未提交，则这个`BSTATE`的状态称为`脏`（`dirty`）的，反之，它的状态称为`干净`（`clean`）
的。

如果某个块在执行中被`SERVICE_REQUEST`打断，而对应的`BSTATE`状态是脏的，该`BSTATE`的内容会被保存在`EBSTATEP`指定的`EBSTATE`中，同时，`SSR:CSTATE`.ebv域设置为1。反之，如果某个块在执行中被`SERVICE_REQUEST`打断，而对应的`BSTATE`状态是干净的，`EBSTATEP`指定的`EBSTATE`维持不变，同时，`SSR:CSTATE`.ebv域设置为0。

<!-- 
.. cnote::

  调度软件，比如操作系统，可以通过保存和恢复脏的上下文恢复被打断的块的执行。如
  果仅仅是进行保存和恢复，它可以忽略EBSTATE的具体格式，仅保存EBSTATE的内容或者
  EBSTATEP指针进行上下文保存。但如果这些调度软件，或者相应的调试软件需要解释或
  者修改其中的内容，则需要深入解释EBSTATE每个域的具体含义。

  `SSR:CSTATE`.ebv的值在被`SERVICE_REQUEST`流程设置后，如果没有
  其他主动修改行为，它会维持不变，并在下一次`SERVICE_REQUEST`中被保存到
  `SSR:ECSTATE_ACRm`。所以调度软件需要根据是否需要用EBSTATE的内容恢复
  以前的执行，在恢复上下文的时候更新`SSR:ECSTATE_ACRm`.ebv的值。
 -->

## 系统调用块ACR切换

系统调用块用于快速（一个块之内）完成对高特权级ACR软件的服务请求。

系统调用块的调用通过`XB`发起调用，基于调用时的ACR进行特权级检查后，当前ACR直接切换为所指定的目标ACR。此后的系统调用块的准备阶段，执行和提交阶段皆以目标ACR特权级执行，在提交完成后，该指令自动重新切换回`XB`执行时的ACR。

本文把`XB`调用时的ACR称为该系统调用块的`调用者ACR`，而准备、执行和提交阶段使用的ACR称为该系统调用块的`被调用方ACR`。

上述过程不影响EBSTATE的内容。如果在系统调用块的准备，执行和提交阶段发生中断或者异常，或者执行阶段执行`acrc`，按SERVICE_REQUEST流程执行。

这种情况下，EBSTATE中保存块的内部状态和调用者BPC的地址，通过该状态调用ACR_ENTER恢复块的运行时，首先恢复到该系统调用块的被调用方ACR，然后完成块的未完成指令（包括提交隐式指令），再恢复到该系统调用块的调用者ACR。
