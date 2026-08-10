# Archived v0.57 PTO Tile QEMU tests

This directory preserves the former `tile`, `pto_parity`, and
`deepseek_tilekernels` QEMU sources for historical investigation only. They
depend on the retired `LinxISA/PTO-Kernel` API and catalog and are not part of
the v0.58 AVS runner, CI, coverage, or conformance evidence.

The v0.58 component topology uses:

- `tools/Linx-TileOP-API` for the Linx Tile API;
- `workloads/pto_kernels` for PTO kernels and the nested SuperNPU corpus;
- VEC, TLSU, CUBE, and SFU as the four semantic engines, with TEPL retained
  only as the unchanged VEC/SFU encoding carrier.

Fresh v0.58 runtime AVS work is tracked by
[LinxISA/linx-isa#169](https://github.com/LinxISA/linx-isa/issues/169). Do not
copy these archived sources back into an active test path.
