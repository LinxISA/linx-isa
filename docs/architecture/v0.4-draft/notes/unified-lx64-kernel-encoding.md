# v0.4 draft note: Unified lx64 kernel encoding (scalar lane + vector lane)

## Context

The strict v0.3 manual currently documents a split between "scalar" instruction families (often 16/32-bit) and "vector" instruction families (`V.*`, 64-bit prefix+main), with additional operand restrictions in vector bodies.

For the rendering/GPGPU kernel-body direction, we assume a different (more GPU-like) execution reality:

- **Scalar-lane and vector-lane instructions are both 64-bit** encodings inside the SIMT kernel body.
- They share **one operand encoding space**: a register field can name one of several domains:
  - scalar temporaries / clockhands (`t`, `u`)
  - vector-argument namespace (`ri*`)
  - predicate register (`p`)
  - tile bases (`TA`, `TB`, `TO`, `TS`, ...)
  - per-lane tile/value registers (`vt`, `vu`, `vm`, `vn`) for lane execution
- A mode bit / opcode variant distinguishes whether an operation is executed in:
  - the **scalar-uniform lane** (`l.*` forms), or
  - the **vector lane** (`v.*` forms)

This enables:
- uniform control-flow and uniform global-memory access via the bridged path in kernel bodies (no BCC scalar memory)
- natural shader lowering with per-lane compute + scalar control + explicit EXEC mask `p`

## TODOs to specify (must be nailed down)
1) The exact **encoding mechanism** that distinguishes `l.*` vs `v.*`.
2) The register-id ranges / numeric encodings for special domains (`ri*`, `p`, `TA/TB/TO/TS`, `vt/vu/vm/vn`).
3) For `.brg` loads/stores: whether `v.*.brg` includes implicit `lc0` addressing while `l.*.brg` does not, or whether both forms exist.

