# BCC / LinxCoreModel Mapping

LinxCoreModel is an executable behavioral reference, not the owner of
architectural stage names.

For the IFU:

- map cacheline-fetch mechanisms to I-SIDE;
- map predictor algorithms to the decoupled B-SIDE engine;
- map I-SIDE to I-F0..I-F4 and B-SIDE to B-F0..B-F4;
- preserve their independent backpressure and non-lockstep progress;
- map model BFU sequencing to the B-stage responsibilities and provider rank;
- feed four fixed 64-bit Instruction Buffer entries into D1 full decode.

Downstream decode, rename, issue, BROB/ROB, LSU, execution, and recovery retain
their documented owners.

- [View IFU model mapping](./BIFU.md)
- [View Decode](./BCTRL.md)
- [View BROB](./BROB.md)
