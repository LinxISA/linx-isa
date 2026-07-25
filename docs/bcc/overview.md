# LinxCore Block-Control Frontend

The LinxCore frontend fetches a normal instruction stream and preserves
architectural block boundaries expressed by `BSTART` and `BSTOP`.

Its IFU is split into:

- [I-SIDE and overall IFU](./bifu.md), which owns the I-F0..I-F4 fetch
  pipeline and Instruction Buffer production;
- [B-SIDE](./bp.md), which owns the decoupled B-F0..B-F4 prediction pipeline.

I-SIDE and B-SIDE exchange explicitly identified request, prediction,
training, and redirect messages; they do not advance in lockstep. D1 reads
four fixed 64-bit instructions from
the Instruction Buffer and hands decoded groups to OOO resource preparation.

Downstream block tracking, rename, scheduling, execution, BROB/ROB retirement,
and recovery remain separate owners and must not be folded into IFU prediction
or predecode.
