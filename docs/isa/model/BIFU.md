# BIFU

## Function

1. Branch prediction. Predict the jump type, direction and destination address of the current block based on BPC.
2. Take header. Fetch the instruction from the I-Cache according to the BPC and perform pre-decoding to obtain the jump type and the address of the next block, so that a preliminary check of branch prediction and final prediction can be made during this instruction fetching stage.

## Implementation

![BIFU](../../figs/model/model_detail/BIFU.svg)

### Push the oldest failed prediction to resolveQ [*be_bfu_rslv_q.write(oldestMipred.mhdr);*]

### Fetching pipeline [1]——F1 stage
    Predict the jump direction and next BPC. 【*BFU::runF1()*】

### Fetch pipeline [2]——F2/Ft stage
    Get instructions from Cache. 【*BFU::runF2() => bhc.fetch(fb); => getHeader(fb, n);*】

### Fetching pipeline [3]——F3 stage
    Make final branch predictions. [*BFU::runF3() => sp.predict(fb); // Predecoding doMainPrediction(fb); // Make a final branch prediction*];
 
    Send instructions to the decoding module. 【*BFU::pipeMove() => brq.push(pipe[F3].fb); => bfu->deliverHeader(fb->mhdr[pos]); => intf.bfu_be_q->write(h);*】

## Remarks

BFU internal pipeline moves backward [*BFU::pipeMove()*]