# QEMU Executable Coverage Ledger

Generated: `2026-07-25T08:31:15Z`

This ledger counts only per-form evidence bound to golden identity, bytes, test ID,
artifacts, QEMU SHA, a test-specific terminal PASS, and an oracle. Suite exit 0 and stdout alone do not count.

## Evidence Levels

| Level | Availability | Forms | Mnemonics |
| --- | --- | ---: | ---: |
| L2 | `available` | 4 | 4 |
| L3 | `available` | 4 | 4 |

## Admitted Forms

| Form | Suite / Test | Level | Oracle | Bytes |
| --- | --- | --- | --- | --- |
| `hl_bfi_48_8adfd476aacc` | `executable_maddw_bfi_mi / 0x00002902` | `L3` | `exact_value` | `ce4c4da14100` |
| `hl_miadd_48_ec5127b6dfd6` | `executable_maddw_bfi_mi / 0x00002903` | `L3` | `exact_value` | `6ea84d814142` |
| `hl_misub_48_e9e4c7b23479` | `executable_maddw_bfi_mi / 0x00002904` | `L3` | `exact_value` | `6ea84d914142` |
| `maddw_32_9f922b15e674` | `executable_maddw_bfi_mi / 0x00002901` | `L3` | `exact_value` | `47f15120` |

## Failed / Rejected Evidence

None.

## Execution Observations

- `executable_maddw_bfi_mi / 0x00002901`: status `PASS`, oracle `PASS`, timeout-after-fail `False`, test-contract `valid`, attribution `none`
- `executable_maddw_bfi_mi / 0x00002902`: status `PASS`, oracle `PASS`, timeout-after-fail `False`, test-contract `valid`, attribution `none`
- `executable_maddw_bfi_mi / 0x00002903`: status `PASS`, oracle `PASS`, timeout-after-fail `False`, test-contract `valid`, attribution `none`
- `executable_maddw_bfi_mi / 0x00002904`: status `PASS`, oracle `PASS`, timeout-after-fail `False`, test-contract `valid`, attribution `none`
