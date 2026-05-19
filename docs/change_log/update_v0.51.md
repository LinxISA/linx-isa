# 0.51 version update

Update date: June 11, 2025

For the path to the web version of the instruction encoding design document, please see [LinxISA Encoding-0.51](https://dbox.huawei.com/detaildocs?oid=VR:wt.doc.WTDocument:100980339929)

The most important change in version LinxISA0.51 is the introduction of parallel block design and the supplement of the definition of architectural state around the content of parallel blocks.

Parallel block instruction evolved from SIMTblock instruction in version 0.4. In order to avoid patent and intellectual property issues, the SIMT block naming in version 0.51 was changed to **Parallel Block**. On this basis, the design of Tile Register is added to architectural state and the definition of vector instructions is refreshed, so that the parallel block can more efficiently carry out large-scale computing tasks in the fields of artificial intelligence, graphics rendering and high-performance computing.

![ParallelBlock](../figs/isa/version/parblock.png)

## Update Summary

| Classification | Description |
|-------|-------|
| First layer architectural state | Add 32 Tile Registers: <br>1.T#1-T#8<br>U#1-U#8<br>M#1-M#8<br>N#1-N#8 |
| Status within the parallel block | Add 8 scalar registers: T#1-T#4, U#1-U#4 |
| Status within the parallel block | vector registers reduced from 32 to 16: VT#1-VT#4, VU#1-VU#4, VM#1-VM#4, VN#1-VN#4 |
| Parallel block internal status | Loop control register changed to block internal status: LB0-LB2, LC0-LC2 |
| Parallel block internal status | Add mask register: P register |
| Add header instruction | B.DIM, C.B.DIM, C.B.DIMI, B.IOT |
| Recovery block jump instruction encoding | b.eq, b.ne, b.lt, bge, b.ltu, b.geu, jr, j |
| Add two jump instructions | b.z, b.nz |
| scalar register modification | T and U registers modified to non-fixed bit width |
| Added 8 shuffle instructions | shfl.up, shfl.down, shfl.bfly, shfl.idx, shfli.up, shfli.down, shfli.bfly, shfli.idx |
| Modification of ALU class instructions | Restore optional parameters for input (.neg and .not) |
| Instruction input/output | Some instructions add P register input/output |
| Instruction behavior definition | Reduce instruction output behavior redefinition |
| Delete command | loop.get, loop.set |
| Delete system register | LPCB0, LPCE0, LPCB1, LPCE1, LPCB2, LPCE2 |