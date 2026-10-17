# v0.58 Atomic op5 Re-encoding + Store-op / MCOPY / DMA.FREE Extension

> Current scope: DMA.FREE.S/L and MCOPY.DS/DL retain their encodings only and are NOT IMPLEMENTED. The resource semantics described below are historical proposal text, not the active contract.

This change re-encodes the atomic main class onto a unified five-bit op5
field, adds ten Linx-only non-vector scalar forms to the v0.58 profile, and
completes the 32-bit CAS documentation surface.

## Motivation

- The store-op atomic family (SW.*/SD.*) had no subtract operation.
- No byte/halfword store-op atomic forms existed because the atomic
  `14..12` sub-class space is fully allocated.
- The far flag at bit 27 was never implemented by any model
  (the Sail model parses and discards it), making it a safely reusable bit.
- `DMA` needed explicit resource-release variants, and `MCOPY` needed
  access-mode variants that report completion status.

## Encoding: unified op5 = 31..27

The atomic main class (`6..4=000, 3..1=101, 0=1`) now reads `31..27` as one
field:

- **b30..27 = operation/size code** — b27 (formerly far) is absorbed as the
  code's least-significant bit, keeping the sequential numbering:
  operations `0000`=ADD, `0001`=AND, `0010`=OR, `0011`=XOR, `0100`=SMAX,
  `0101`=SMIN, `0110`=UMAX, `0111`=UMIN, `1000`=SUB (new); LR/SC/SWAP size
  codes `0000`=B, `0001`=H, `0010`=W, `0011`=D;
- **b31 = flag bit** — size override for the store-op forms (SW/SD slots),
  relocated far flag for LR/SC/SWAP and the load-op forms (LW.*/LD.*).

Consequences:

- the `.f`/`.rlf` suffixes are removed from the sixteen SW.*/SD.* forms;
- LR/SC/SWAP/LW/LD keep `.f`, with far now decoding from bit 31;
- the forty-four existing far-bearing/store-op atomic forms are re-encoded
  with the code shifted one bit down (`new_match = (old_code << 27) | low`),
  acceptable because far was never implemented and the far=1 code points
  were dead;
- their `pto_scalar_forms.json` mirror entries were updated in lockstep
  (masks, matches, far field piece moved from lsb 27 to lsb 31) so the exact
  PTO identity match stays green.

## New instructions

| Mnemonic | 31..27 | 14..12 | mask | match |
|---|---|---|---|---|
| SW.SUB  | 0_1000 | 011 | 0xfc007fff | 0x4000300b |
| SD.SUB  | 0_1000 | 101 | 0xfc007fff | 0x4000500b |
| SB.ADD  | 1_0000 | 011 | 0xfc007fff | 0x8000300b |
| SB.SUB  | 1_1000 | 011 | 0xfc007fff | 0xc000300b |
| SH.ADD  | 1_0000 | 101 | 0xfc007fff | 0x8000500b |
| SH.SUB  | 1_1000 | 101 | 0xfc007fff | 0xc000500b |
| DMA.FREE.S | 31..25=0000010 | 111 | 0xfff07fff | 0x0400700b |
| DMA.FREE.L | 31..25=0000011 | 111 | 0xfff07fff | 0x0600700b |
| MCOPY.DS | 26..25=01 | 001 | 0x0600707f | 0x02001031 |
| MCOPY.DL | 26..25=11 | 001 | 0x0600707f | 0x06001031 |

Re-encoded existing forms (mask/match), SW slot (14..12=011):

| Mnemonic | old match | new match | op5 |
|---|---|---|---|
| SW.ADD  | 0x0000300b | 0x0000300b | 00000 |
| SW.AND  | 0x1000300b | 0x0800300b | 00001 |
| SW.OR   | 0x2000300b | 0x1000300b | 00010 |
| SW.XOR  | 0x3000300b | 0x1800300b | 00011 |
| SW.SMAX | 0x4000300b | 0x2000300b | 00100 |
| SW.SMIN | 0x5000300b | 0x2800300b | 00101 |
| SW.UMAX | 0x6000300b | 0x3000300b | 00110 |
| SW.UMIN | 0x7000300b | 0x3800300b | 00111 |

SD slot (14..12=101) follows the same pattern with base 0x500b; LW/LD/LR/SC/
SWAP use mask 0x7800707f-family values with far at b31 (for example LW.SMAX
0x2000200b, LR.H 0x0800000b, SWAPH 0x0800600b).

Notes:

- `MCOPY.DS`/`MCOPY.DL` share the `RegSrc0/1/2` layout with `MCOPY` and add a
  `RegDst` return that carries the L2SPM replica address; `26..25` distinguishes
  `00`=MCOPY, `01`=DS (Store mode), `11`=DL (Load mode).
- `DMA.FREE.S`/`DMA.FREE.L` release the L2SPM resources designated by the
  address in `SrcL`, in Store / Load mode respectively.
- CAS keeps its own layout (`31..27=SrcD`, no far flag) and is unchanged.

## Governance amendments

- `tools/isa/check_pto_v058_manifest.py` freezes the exact ten-form
  Linx-only extension set (the non-vector delta check now expects
  184 V.* forms + 4 vector headers + 10 extension forms).
- `docs/architecture/v0.58-architecture-contract.md` records the amendment.
- The PTO catalog lock is unchanged: no new PTO forms are claimed; the ten
  forms are Linx-only pending PTO adoption.

## Documentation completion: 32-bit CASB/CASH/CASW/CASD

The 32-bit compare-and-swap forms have been part of the v0.58 spec since the
v0.57 alignment (PR #139 encoding design), but the Chinese site never
published them. This change completes that surface without touching the ISA
layer (they are PTO-aligned forms with existing uop classifications and
generated English pages):

- new Chinese instruction pages `docs/zh/isa/inst/misa_s/CAS{B,H,W,D}.md`
  plus English stubs;
- new bitfield JSON+SVG diagrams in both the English and Chinese figure
  trees;
- the previously commented-out compare-and-swap section of
  `atomic.md` is restored in both languages, now noting that the 32-bit
  forms carry no `.f` suffix (HL.CAS\* covers remote access);
- `instlist.md` gains the 32-bit CAS row in both languages;
- `mkdocs.zh.yml` navigation lists CASB/CASH/CASW/CASD between SWAPD and
  HL.CASB.

## Files changed

- `isa/v0.58/opcodes/lx_32.opc` — 44 atomic entries re-encoded onto op5,
  16 store-op asm suffixes trimmed, 10 added
- `isa/v0.58/state/pto_scalar_forms.json` — 44 mirrored forms updated
- `isa/v0.58/uop_classification_v0.58/AMO/{AMO,DMA}.json`,
  `CMD/BLOCK_SPLIT.json` — classifications for the new forms
- `isa/v0.58/linxisa-v0.58.json` — regenerated (766 -> 776 instructions)
- `isa/generated/codecs/linxisa32.decode`, `linxisa_opcodes.c` — regenerated
- `docs/isa/wavedrom/`, isa-manual generated encodings/fragments/tables,
  `docs/isa/instructions|groups|index` — regenerated
- `docs/figs/bitfield/json|svg` (+ zh mirror) — 50 atomic diagrams updated
  or added (code/far field positions swapped, op5 values corrected)
- Chinese manual pages: 22 store-op pages updated, 10 extension pages and
  4 CAS pages added; English stubs added; `atomic.md`/`instlist.md` updated
  in both languages
- `mkdocs.zh.yml` — navigation for the new pages
- `tools/isa/test_v058_storeop_ext.py` — spec-level contract test
- `tools/isa/check_pto_v058_manifest.py` — extension whitelist

## Follow-up work (requires submodule bumps)

- LLVM: assembler/disassembler/codegen for the ten mnemonics, the `.f`-less
  store-op suffix set, and the re-encoded atomic decodes; then add
  `avs/compiler/linx-llvm/tests/asm/42_v058_storeop_ext_forms.s` and a
  negative test for the removed `sw.add.f` suffix.
- QEMU: decode/execute for the new forms and the op5 layout; `far=1`
  store-op-era words must not decode through legacy paths.
- Sail model: regenerate decode, move far to b31, drop the unused store-op
  far parameter.
