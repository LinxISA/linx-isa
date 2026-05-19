# BIFU

## 功能

1. 分支预测。依据BPC预测当前块的跳转类型、方向和目的地址。
2. 取块头。跟据BPC从I-Cache中取指，并进行预解码，得到跳转类型和下一个块的地址，以便在此取指阶段进行分支预测的初步检查并作出最终预测。

## 实现

![BIFU](../../figs/model/model_detail/BIFU.svg)

### 压入最旧的失败预测到resolveQ【*be_bfu_rslv_q.write(oldestMispred.mhdr);*】

### 取指流水线【1】——F1阶段
    进行跳转方向和下一个BPC的预测。【*BFU::runF1()*】

### 取指流水线【2】——F2/Ft阶段
    从Cache中取指。【*BFU::runF2() => bhc.fetch(fb); => getHeader(fb, n);*】

### 取指流水线【3】——F3阶段
    作出最终的分支预测。【*BFU::runF3() => sp.predict(fb); // 预解码 doMainPrediction(fb); // 作出一个最终的分支预测*】； 
 
    将指令送到解码模块。【*BFU::pipeMove() => brq.push(pipe[F3].fb); => bfu->deliverHeader(fb->mhdr[pos]); => intf.bfu_be_q->write(h);*】

## 备注

BFU内部流水线往后移动【*BFU::pipeMove()*】
