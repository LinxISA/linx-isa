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
- The execution domain is **derived from register class usage** (no dedicated mode bit):
  - operations targeting/using per-lane tile/value registers (`vt/vu/vm/vn`) are treated as **vector-lane** execution (`v.*`)
  - operations targeting/using scalar/group resources (`t/u/ri/p/TA/TB/TO/TS/...`) are treated as **scalar-uniform lane** execution (`l.*`)

Chosen derivation rule: **any-operand rule**
- If any operand (src or dst) names a per-lane register (`vt/vu/vm/vn`), the instruction is treated as **vector-lane** execution (`v.*`).
- Otherwise it is treated as **scalar-uniform lane** execution (`l.*`).


This enables:
- uniform control-flow and uniform global-memory access via the bridged path in kernel bodies (no BCC scalar memory)
- natural shader lowering with per-lane compute + scalar control + explicit EXEC mask `p`

## Chosen mixed-class semantics (initial)

Given the any-operand rule:
- In a `v.*` instruction, any scalar/group-domain source operand (`t/u/ri/p/TA/TB/TO/TS/...`) is **broadcast** to all active lanes.
- Per-lane operands (`vt/vu/vm/vn`) remain lane-specific.

## Remaining TODOs
1) When a `v.*` instruction targets a scalar destination (if allowed), what does it mean (illegal? lane0? reduction?)
2) The register-id ranges / numeric encodings for special domains (`ri*`, `p`, `TA/TB/TO/TS`, `vt/vu/vm/vn`).
3) For `.brg` loads/stores: whether the address formation differs between `v.*.brg` and `l.*.brg` (implicit `lc0` or not), or whether both share the same rules.

