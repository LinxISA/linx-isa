# PE_IFU

## Function

1. Responsible for receiving and processing header control information from BCC
2. Analyze header control information, perform branch prediction, etc. to generate instruction fetch requests
3. According to the instruction fetch request, fetch data from ICache and generate a microinstruction bundle and send it to the PE_Decode stage

![pe_ifu](../../figs/model/model_detail/pe_ifu.svg)

## Detailed introduction

The top of the red dotted line is ISide (Instruction Fetch Side), and the bottom is BSide (Branch Predict Side)

### Running water:

- F0: The process in which OPE receives PE Control information and Flush information from BCC and generates FetchReq. Hyper blocks or blocks that require a Bend instruction to indicate the end need to be predicted by Bsiede, but not vice versa.
- F1: The process of querying ICache, TLB and uBTB
- F2: Access ICache to get data; or handle CacheMiss
- F3: Pre-decoding determines whether the End instruction and branch instruction (and type) are included, and performs total branch prediction arbitration. and insert BRQ and InstBuffer
- F4/D1: Decode instructions, check masks, etc.
- D2: Command rename
- BCC: Block Control Core, responsible for header processing and scheduling.

### IFU composition

- fetchControlQ: Cache the header control information received by OPE

#### 1.ISide:

- RAHQ: Run Ahead Fetch Requesets Queue, the instruction fetch request queue generated after header control information parsing
- ICache: cache instruction data
- Pre-Decode: Decode instructions and parse out branch types, etc.
- SP: Static Branch Predictor (Static Predictor) checks the instruction prediction information. If the previously predicted branch type/address is wrong, a Flush is generated; if the End instruction is detected, a Flush is also generated and the header control information of the next block is processed.
- InstBuffer: Instruction cache, which stores a set of microinstructions (bundle) fetched in each cycle.
- Decoder: decode instructions and check related masks

#### 2.BSide:

- uBTB: Provides a 0-cycle prediction, including branch type/direction/address, etc.
- iBTB: predict indirect branch instructions
- GHR: Global history register, used to store the final prediction result of each beat jump instruction (jump/no jump)
- BIM: Provide a direction prediction when all tables in TAGE have no hit
- DP: Direct Predictor, predicts the result of a direct jump instruction
- MP: Main Predictor, used to arbitrate all predictions to obtain the final prediction result type/direction/address, etc.
- BRQ: Branch Inst Queue, which stores the real-time running information of the branch predictor and serves as a basis for updating and restoring the branch predictor when necessary (such as mis-predict, etc.)