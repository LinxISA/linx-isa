# QEMU Executable Coverage Ledger

Generated: `2026-07-15T17:15:51Z`

This ledger counts only per-form evidence bound to golden identity, bytes, test ID,
artifacts, QEMU SHA, a test-specific terminal PASS, and an oracle. Suite exit 0 and stdout alone do not count.

## Evidence Levels

| Level | Availability | Forms | Mnemonics |
| --- | --- | ---: | ---: |
| L2 | `available` | 3 | 3 |
| L3 | `available` | 3 | 3 |

## Admitted Forms

| Form | Suite / Test | Level | Oracle | Bytes |
| --- | --- | --- | --- | --- |
| `fentry_32_a47584ec13b6` | `callret / 0x0000140b` | `L3` | `exact_value` | `4100a504` |
| `fret_ra_32_659c886221c1` | `callret / 0x0000140c` | `L3` | `exact_value` | `4120a504` |
| `fret_stk_32_4fe246bd8241` | `callret / 0x0000140b` | `L3` | `exact_value` | `4130a504` |

## Failed / Rejected Evidence

None.

## Execution Observations

- `callret / 0x0000140b`: status `PASS`, oracle `PASS`, timeout-after-fail `False`, test-contract `valid`, attribution `none`
- `callret / 0x0000140c`: status `PASS`, oracle `PASS`, timeout-after-fail `False`, test-contract `valid`, attribution `none`
- `v03_vector_ops / 0x00001321`: status `FAIL`, oracle `FAIL`, timeout-after-fail `True`, failure `0x00001321` expected `0x0000000000000053` actual `0x0000000000000011`, test-contract `invalid`, attribution `test_contract`, note: Historical first-red evidence. The AVS source used invalid VT/VU lifetime and relative-index semantics; the corrected source and authored B.IOR binding now pass 0x1300, 0x1310, and 0x1320.
