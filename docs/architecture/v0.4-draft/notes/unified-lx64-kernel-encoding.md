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

(Exact derivation rule TBD: likely keyed primarily off the destination register class; see open questions below.)

This enables:
- uniform control-flow and uniform global-memory access via the bridged path in kernel bodies (no BCC scalar memory)
- natural shader lowering with per-lane compute + scalar control + explicit EXEC mask `p`

## TODOs to specify (must be nailed down)
1) The exact **derivation rule** for `l.*` vs `v.*` when multiple register classes appear in one instruction.
   - is it determined by destination class?
   - for stores/branches (no dst), is it determined by the data source class?
   - are mixed-class instructions legal, and if so what are the broadcast/merge rules?
2) The register-id ranges / numeric encodings for special domains (`ri*`, `p`, `TA/TB/TO/TS`, `vt/vu/vm/vn`).
3) For `.brg` loads/stores: whether the address formation differs between `v.*.brg` and `l.*.brg` (implicit `lc0` or not), or whether both share the same rules.

