# BFU

Block Fetch Unit (BFU) is a module used to fetch Block Header. It is divided into two parts: ISIDE and BSIDE are used for instruction reading and next address prediction respectively. This chapter mainly introduces the ISIDE part, and the BSIDE part will be introduced separately in the [BP](./bp.md/) chapter.

Different from the traditional RISC instruction set, each instruction in LinxISA has a jump attribute, which means that BFU can default to each block instruction as a jump instruction. This feature enables corresponding simplification of the microarchitecture. At the same time, because the block instruction encoding length is relatively long at 128-bit, the microarchitecture currently only fetches one instruction per clock cycle, so part of the prediction logic can be simplified.

## Block jump type

In order to improve the accuracy of prediction, BFU uses five-level pipeline prediction to handle different jump types. These types include:

| Type | Explanation | Assembly flag |
|---------------|----------|------------|
| Fall Through | Postponement | bnext.fall |
| Direct Jump | Direct jump | bnext.direct |
| CALL | Call jump | bnext.call |
| Conditional Jump | Conditional Jump | bnext.cond |
| Indirect | Indirect jump | bnext.ind |
| Indirect Call | Indirect call | bnext.indcall |
| Return | Return | bnext.ret |
| ECall | exception call | bnext.ecall |
| EReturn | exception return | bnext.eret |

## BFU overall architecture diagram

The picture below shows the work pipeline diagram of BFU.

  ![bpu](../figs/uArch/BFU_TOP.png){ width="800"){ width="800" }

## ISIDE (Instruction Side)
As shown in the figure, BFU is divided into two streams: iside and bside. The Iside part includes L1 ICache, Pre_decode and Static Predictor modules. The functions of each module are as follows:

*ICache
Read the stored data in L1 according to the input physical address. The tag determines whether it is a hit. If it is not a hit, a refill request is sent to L2 to rewrite the data. If it is a hit, the data is read out from the data. After the data is read, the pre_decode module parses to obtain the jump attribute of the block, and the static predictor module parses to obtain the offset from the next block (BNEXT offset) carried by the current header and the size of the current block (BSize), thereby calculating and predicting the BPC of the next block.

* block instruction pre-decode (Pre-decode)
Pre-decoding decodes the 128-bit block instruction obtained from the header cache to obtain jump type, jump offset and other information, and calculates the target address of the direct jump instruction for subsequent branch prediction checkers to determine the correctness of the prediction.

* Static branch predictor (Static Predictor) and branch prediction checker
	After fetching the instruction, the static branch checker will get some accurate information, including the jump type and the address of the direct jump. After getting this information, the prediction check module mainly checks the following errors:

	**Direct/indirect jump instruction prediction does not jump error:** Check for instructions that must jump such as Direct/Indirect/Call/Indirect/Ret. If the prediction unit encounters such a block and predicts that it will not jump, it is regarded as a prediction error.**Target address error:** For jump instructions (such as Direct, Call, Fall Through, Concat) whose target address can be known through the instruction code, if the predicted address does not match the correct address, it is considered a prediction error.
	After an error is found, the branch prediction checker will generate the SP Flush signal, clear the pipeline related signals, and restart fetching and prediction from the correct address.

## BSIDE (Branch Prediction Side)
* uBTB
Provides fast prediction of 0-cycle jump direction, jump target address, and jump attributes.

*RAS
The return address stack RAS is essentially similar to a circular buffer, used to predict and track call (also called push, push on the stack) and return (also called pop, pop out of the stack) instruction pairs, and store return addresses. Each RAS entry has two field segments: backlink and target. The backlink field stores the top of stack pointer TOS corresponding to each execution of the call instruction, and the target field stores the target address (VA) given each time the return instruction is executed. If RAS predicts a call (push) instruction every time, a return address will be stored in RAS; if RAS predicts a return (pop) instruction every time, a return address will be popped out of RAS;

![RAS_FIG](../figs/uArch/RAS_FIG.PNG){ width="800" }

Figure: Schematic diagram of RAS microarchitecture

*GHR
It is used to store the final prediction result of each beat jump instruction (jump/no jump), and predict a new GHR value and IHR value based on the past results, and send them to the TAGE and ITBB modules for hash operation respectively to calculate the folded query sequence number and corresponding to the correct jump.

*TAGE
Used to predict jump directions. There are four prediction tables (numbered 0~3) and one base table. Each entry in each table stores direction predictions for different jumps. Each table is indexed by a different sequence number, where the sequence number is calculated by hashing the global jump history and the PC of the current block. Tables with larger numbers will add longer jump history for hashing, so they are more accurate.

*iBTB
In the F2 stage of the pipeline, if the pre_decode module on the iside side parses and obtains that the jump attribute of the block is an indirect jump type (including indirect jump INDIR and indirect call INDCALL), a more accurate predicted target address will be provided in iBTB.

* PRED predicts internal competition logic
In the F3 stage of the pipeline, the main predictor PRED will produce the final and most accurate prediction information of the entire BFU module. There are three types of prediction information: block jump type, block jump direction, and block jump target address.
For block jump types, the block jump type obtained by the static predictor by parsing header is the most accurate, so the block attributes are directly passed to the main predictor (PRED) module for final prediction.
For the block jump target address, the block jump target address obtained by the static predictor by parsing header can only be trusted under certain circumstances, that is, when the block jump type is FALL, DIRECT, CONCAT, CALL, COND, the correct jump target address can be obtained by parsing header. In other cases, the target address obtained by the static predictor is not trustworthy. If it is the RET type, the result obtained by RAS two beats after the F1 stage prediction is the most credible; if it is the INDIRECT or INDCALL type, the result obtained by iBTB is the most credible; otherwise, the result obtained by uBTB is used.
For the block jump direction, if it is CONDblock type, the prediction result of TAGE is used; if block type is FALL or CONCAT type, it is regarded as not jumping, and the other cases are regarded as jumps.

*BRQ
The branch queue BRQ is essentially similar to a FIFO, which is used to store the real-time running information of the branch predictor and serve as a basis for the update and recovery of the branch predictor when necessary (such as mis-predict, etc.).

![RAS_FIG](../figs/uArch/BRQ_FIG.PNG){ width="800" }Figure BRQ_TOP module architecture block diagram
The data in each entry of BRQ is wide. We need to get different parts of an entry under some different conditions (Rob refreshed/Bru refreshed/BRQ parsed correctly) and roll it over to the next cycle. As shown below, "√" means that the field will be read in this case:| BRQ ENT GRP | BRQ ENT Field | rob_flush | bru_flush | Bru correct resolve | width | start bit | end bit |
| ----------- | ------------- | --------- | --------- | ----------- | ----- | --------- | ------- |
| GHR | GHRQ_RIDX | √ | √ | √ | 8 | 0 | 7 |
| IHR | BASE | √ | √ | √ | 12 | 20 | 27 |
| TAGE | StartPos | | √ | √ | 3 | 8 | |
| TAGE | STR | | √ | √ | 1 | 11 | |
| TAGE | TNT | | √ | √ | 1 | 19 | |
| TAGE | U_b3w0 | | √ | √ | 2 | 21 | |
| TAGE | CTR_b3w0 | | √ | √ | 2 | 23 | |
| TAGE | POS_b3w0 | | √ | √ | 2 | 25 | |
| TAGE | HIT_b3w0 | | √ | √ | 1 | 26 | |
| TAGE | U_b2w0 | | √ | √ | 2 | 28 | |
| TAGE | CTR_b2w0 | | √ | √ | 2 | 30 | |
| TAGE | POS_b2w0 | | √ | √ | 2 | 32 | |
| TAGE | HIT_b2w0 | | √ | √ | 1 | 33 | || TAGE | U_b1w0 | | √ | √ | 2 | 35 | |
| TAGE | CTR_b1w0 | | √ | √ | 2 | 37 | |
| TAGE | POS_b1w0 | | √ | √ | 2 | 39 | |
| TAGE | HIT_b1w0 | | √ | √ | 1 | 40 | |
| TAGE | U_b0w0 | | √ | √ | 2 | 42 | |
| TAGE | CTR_b0w0 | | √ | √ | 2 | 44 | |
| TAGE | POS_b0w0 | | √ | √ | 2 | 46 | |
| TAGE | HIT_b0w0 | | √ | √ | 1 | 47 | |
| RS | TOS | √ | √ | | 6 | 53 | |
| RS | WPTR | √ | √ | | 6 | 59 | |
| IBTB | HIT_BNK | | √ | √ | 2 | 61 | 62 |