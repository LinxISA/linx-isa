# Decode and Dispatch Model Mapping

The architectural backend input is a D1 group containing up to four fixed
64-bit instructions read from the Instruction Buffer.

1. D1 performs full opcode, operand, immediate, exception, and split/fuse
   decode.
2. D2 calculates complete BROB/ROB, rename, IQ, and memory-order demand and
   resolves block-boundary ownership.
3. D3 atomically accepts the complete group or changes no allocation state.
4. Dispatch routes admitted uops to their execution-class issue structures.

Model identifiers such as `bfu_be_q`, `MachineHeader`, or
`decodeBlockHeader()` describe current executable-model organization only.
They are useful for behavior comparison but are not architectural IFU-to-OOO
interfaces and do not define a separate block-header decode path.
