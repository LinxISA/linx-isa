# Code Template 
Code Template (CT) 是为 灵犀指令集 中定义的模板块与特定指令而定制的微指令生成器。目前定义下，其主要承担以下任务：
- **微指令模板**
	- MSGBuffer 请求传递
	- MSGBuffer 回复传递

- **块指令模板**
	- **B.MCOPY**: 以字节粒度将目标内存指定大小拷贝至目标地址
	- **B.MSET**: 将目标内存赋值成指定的数值(字节)
	- **B.MPUSH**: 将指定寄存器列表连续写入目标内存地址，并更新寄存器指针
	- **B.MPOP**: 从目标内存地址连续读取数据写入目的寄存器列表中，并更新寄存器指针
	- **F.ENTRY**: 将指定寄存器列表连续写入目标内存地址
	- **F.EXIT**: 从目标内存地址连续读取数据写入目的寄存器列表中，并使用ra寄存器更新CARG.TGT
	- **F.RET**: 从目标内存地址连续读取数据写入目的寄存器列表中，并使用RegRet寄存器更新CARG.TGT

- **异常模板**
	- 异常上下文保存
	- 异常上下文恢复

- **Call块模板**
	- 自动保存返回地址

## Code Template 自定义指令

目前 Code Template 中生成的指令大部分都是已在 灵犀指令集 中定义的微指令。同时，我们也在其中定义了一些与微架构相关的指令：


- **Clear LSMAP**: 清空本块在Local Smap中的所有映射关系，使得之后对GPR的访问都指向Global寄存器。
- **Set RA**: 计算出CALL类型块的返回地址，并将其存入 Global R1 寄存器

## Code Template 实现

注：此章只描述 Code Template 的实现，具体每个功能的代码生成与硬件配合不在此章体现。

Code Template将通过状态机实现。状态机通过特定的事件触发进入对应的模板状态，接管前端取指单元并产生相应微指令。在指令生成完毕后，Code Template 将把指令源头交还给前端。至此，Code Template 完成了一次代码生成工作。

**Code Template 状态**：

- **Idle**      ：初始态，Code Template 空闲，并可接收特定事件请求
- **Setup  [x]**: 准备态，Code Template 已收到生成请求，但还未到生成指令的正确时机，等待目标事件发生并接管前端。
- **CodeGen[x]**: 生成态，Code Template 接管前端并生成一系列指令，结束时跳转回初始态

需要注意的是Setup与CodeGen是一组状态集合，其中每一个细分场景都对应一组独立的Setup & CodeGen状态机(不同场景由[x]标识)。同时，Idle态跳往不同场景的条件也是不同的，以下列出了所有状态的跳转条件:

- **模板块场景**：
	- Idle    -> Setup  : Block Control Core前端 (BDecode) 解析到模板块
	- Setup   -> CodeGen: 模板块所需寄存器或参数准备完成，且上一个块将要解析完毕
	- CodeGen -> Idle   : 指令生成完毕

- **异常场景**: 
	- Idle    -> Setup  : 当前最老块的最老指令上报异常，且类型为Debug或可恢复异常
	- Setup   -> CodeGen: 当前异常Flush完成时
	- CodeGen -> Idle   : 指令生成完毕

- **Setc.msg 微指令场景**：
	- Idle    -> Setup  : 当 PE 前端（Decode）解析到 setc.msg 微指令
	- Setup   -> CodeGen: 所需参数准备完成，当前块解析到最后一条指令
	- CodeGen -> Idle   : 指令生成完毕

- **Call块场景**：
	- Idle    -> Setup  : Block Control Core前端 (BDecode) 解析到 Call 块
	- Setup   -> CodeGen: 上一个块将要解析完毕
	- CodeGen -> Idle   : 指令生成完毕
