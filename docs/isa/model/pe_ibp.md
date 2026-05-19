# PE Inst_BP

## Function

1. Before sending a microinstruction instruction fetch request to the IFU, branch prediction of the microinstruction needs to be performed first.

![pe_ibp](../../figs/model/model_detail/pe_ibp.svg)

## Data structure

* **inst_bp_mode**
Function: Field used to decide which microinstruction branch prediction to use:
When it is 1, the instruction sequence run out using the function model will be used as the reference for bp, that is, perfect bp.
When it is 0, the bp based on the 1-bit saturation counter is performed, that is, the current jump is determined only based on the last jump of the TPC.
When it is 2, perform bp based on a 2-bit saturation counter.

* **hyperTrace**
Function: Stores the instruction sequence run by the function model, which is used to provide a reference for branch instruction prediction results for pe when bp mode is 1. The method of locating a certain block in the trace is to locate the block's position in the trace based on the distance to the oldest block.
Implementation: For the structure variable of HyperTraceEntry, bpc, isHyper, and instQ are stored, where instQ is the queue actually used to store the instruction sequence.

* **hyperIQ**
Function: records the latest intra-block jump address, used for target address prediction of branch prediction when bp mode is 0.
Implementation: deque

* **instMap**
Function: Stores the target address prediction value of branch prediction, which is used for the target address prediction of branch prediction when bp mode is 2.
Implementation: unordered_map

## Execution process

1. When inst_bp_mode is not equal to 1, call PE::checkBranchInst() to pass tpc and other information to IBP, and the target address prediction value of the branch instruction will be returned to pe through the dst field.
2. Pe will call IBP::predict() and determine the value of inst_bp_mode. If it is 0, it will call IBP::checkBranchInst() and use hyperIQ to perform bp based on a 1-bit saturation counter; if it is 2, it will call IBP::noHistBP () and use instMap to perform bp based on a 1-bit saturation counter;
3. When inst_bp_mode is equal to 1, pe will use hyperTrace for perfect bp.