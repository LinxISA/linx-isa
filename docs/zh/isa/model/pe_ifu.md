# PE_IFU

## 功能

1. 负责接收并处理来自BCC的块头控制信息
2. 解析块头控制信息、进行分支预测等产生取指令请求
3. 根据取指令请求，从ICache 取数据，并生成微指令bundle 发往PE_Decode阶段

![pe_ifu](../../figs/model/model_detail/pe_ifu.svg)

## 详细介绍

红色虚线上方为ISide(Instruction Fetch Side)，下方为BSide(Branch Predict Side)

### 流水：

- F0：OPE 从BCC 接收PE Control信息以及Flush信息，并生成FetchReq的过程。Hyper块或需要Bend指令表示结束的块需要经过BSiede预测，反之不需要。
- F1：查询ICache、TLB以及uBTB的过程
- F2：访问ICache 拿到数据；或处理CacheMiss
- F3：预解码判断是否包含End指令和分支指令(及类型)，进行总分支预测仲裁。并插入BRQ和InstBuffer
- F4/D1：解码指令，检查掩码等
- D2：指令重命名
- BCC：块控制核(Block Control Core)，负责块头处理和调度。

### IFU 组成

- fetchControlQ：缓存OPE 收到的块头控制信息

#### 1.ISide:

- RAHQ：取指请求队列(Run Ahead Fetch Requesets Queue)，块头控制信息解析后生成的取指令请求队列
- ICache：缓存指令数据
- Pre-Decode：对指令进行解码，解析出分支类型等。
- SP：静态分支预测器(Static Predictor)，对指令预测信息进行检查，如果之前预测的分支类型/地址错误，产生Flush；如果检测到End指令同样产生Flush，开始处理下一个块的块头控制信息。
- InstBuffer：指令缓存，存储每周期取到的一组微指令(bundle).
- Decoder：解码指令并且检查相关掩码

#### 2.BSide:

- uBTB：提供一个0-cycle的预测，包括分支类型/方向/地址等
- iBTB：预测间接分支指令
- GHR：全局历史寄存器，记录用于存储每拍跳转指令最后的预测结果(跳转/不跳转)
- BIM：在TAGE的所有表都没有hit的时候，提供一个方向预测
- DP：Direct Predictor，预测直接跳转指令的结果
- MP：主分支预测(Main Predictor)，用于仲裁所有预测得到最终预测结果类型/方向/地址等
- BRQ：分支指令队列(Branch Inst Queue)，存储分支预测器的实时运行信息，并在必要时(例如mis-predict等)作为依据，用于分支预测器的更新和恢复
