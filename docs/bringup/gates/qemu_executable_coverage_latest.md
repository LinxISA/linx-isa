# QEMU Executable Coverage Ledger

Generated: `2026-07-15T18:46:30Z`

This ledger counts only per-form evidence bound to golden identity, bytes, test ID,
artifacts, QEMU SHA, a test-specific terminal PASS, and an oracle. Suite exit 0 and stdout alone do not count.

## Evidence Levels

| Level | Availability | Forms | Mnemonics |
| --- | --- | ---: | ---: |
| L2 | `available` | 6 | 6 |
| L3 | `available` | 6 | 6 |

## Admitted Forms

| Form | Suite / Test | Level | Oracle | Bytes |
| --- | --- | --- | --- | --- |
| `c_bstart_16_c4e238a9227a` | `callret / 0x0000140f` | `L3` | `exact_value` | `8400` |
| `c_bstart_std_16_8b40f078c14a` | `callret / 0x0000140d` | `L3` | `exact_value` | `0038` |
| `fentry_32_a47584ec13b6` | `callret / 0x0000140b` | `L3` | `exact_value` | `4100a504` |
| `fret_ra_32_659c886221c1` | `callret / 0x0000140c` | `L3` | `exact_value` | `4120a504` |
| `fret_stk_32_4fe246bd8241` | `callret / 0x0000140b` | `L3` | `exact_value` | `4130a504` |
| `j_32_a303cf05af42` | `callret / 0x00001410` | `L3` | `exact_value` | `37000300` |

## Failed / Rejected Evidence

None.

## Execution Observations

- `callret / 0x0000140b`: status `PASS`, oracle `PASS`, timeout-after-fail `False`, test-contract `valid`, attribution `none`
- `callret / 0x0000140c`: status `PASS`, oracle `PASS`, timeout-after-fail `False`, test-contract `valid`, attribution `none`
- `callret / 0x0000140d`: status `PASS`, oracle `PASS`, timeout-after-fail `False`, test-contract `valid`, attribution `none`
- `callret / 0x0000140f`: status `PASS`, oracle `PASS`, timeout-after-fail `False`, test-contract `valid`, attribution `none`
- `callret / 0x00001410`: status `PASS`, oracle `PASS`, timeout-after-fail `False`, test-contract `valid`, attribution `none`
- `v03_vector_ops / 0x00001321`: status `FAIL`, oracle `FAIL`, timeout-after-fail `True`, failure `0x00001321` expected `0x0000000000000053` actual `0x0000000000000011`, test-contract `invalid`, attribution `test_contract`, note: Historical first-red evidence. The AVS source used invalid VT/VU lifetime and relative-index semantics; the corrected source and authored B.IOR binding now pass 0x1300, 0x1310, and 0x1320.
