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
For the block jump direction, if it is CONDblock type, the prediction result of TAGE is used; if block type is of FALL, CALL, CONCAT type, it is regarded as not jumping, and the other cases are regarded as jumps.

*BRQ
The branch queue BRQ is essentially similar to a FIFO, which is used to store the real-time running information of the branch predictor and serve as a basis for the update and recovery of the branch predictor when necessary (such as mis-predict, etc.).

![RAS_FIG](../figs/uArch/BRQ_FIG.PNG){ width="800" }

 Figure BRQ_TOP module architecture block diagram
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