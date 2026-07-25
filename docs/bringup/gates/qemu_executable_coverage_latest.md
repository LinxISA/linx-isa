# QEMU Executable Coverage Ledger

Generated: `2026-07-25T08:30:24Z`

This ledger counts only per-form evidence bound to golden identity, bytes, test ID,
artifacts, QEMU SHA, a test-specific terminal PASS, and an oracle. Suite exit 0 and stdout alone do not count.

## Evidence Levels

| Level | Availability | Forms | Mnemonics |
| --- | --- | ---: | ---: |
| L2 | `available` | 14 | 14 |
| L3 | `available` | 14 | 14 |

## Admitted Forms

| Form | Suite / Test | Level | Oracle | Bytes |
| --- | --- | --- | --- | --- |
| `hl_bfi_48_8adfd476aacc` | `executable_maddw_bfi_mi / 0x00002902` | `L3` | `exact_value` | `ce4c4da14100` |
| `hl_miadd_48_ec5127b6dfd6` | `executable_maddw_bfi_mi / 0x00002903` | `L3` | `exact_value` | `6ea84d814142` |
| `hl_misub_48_e9e4c7b23479` | `executable_maddw_bfi_mi / 0x00002904` | `L3` | `exact_value` | `6ea84d914142` |
| `hl_setc_andi_48_f27796612fb3` | `executable_setc_imm / 0x00002803` | `L3` | `exact_value` | `2e01f5225134` |
| `hl_setc_eqi_48_0fe891fb0890` | `executable_setc_imm / 0x00002804` | `L3` | `exact_value` | `2e01f5025134` |
| `hl_setc_gei_48_9563d6395d06` | `executable_setc_imm / 0x00002805` | `L3` | `exact_value` | `defef552b1cb` |
| `hl_setc_geui_48_2390319baf54` | `executable_setc_imm / 0x00002806` | `L3` | `exact_value` | `2e01f5725134` |
| `hl_setc_lti_48_ad4ffebe877c` | `executable_setc_imm / 0x00002807` | `L3` | `exact_value` | `defef542b1cb` |
| `hl_setc_ltui_48_cb7a12ba6ead` | `executable_setc_imm / 0x00002808` | `L3` | `exact_value` | `2e01f5625134` |
| `hl_setc_nei_48_f0bcf6586274` | `executable_setc_imm / 0x00002809` | `L3` | `exact_value` | `defef512b1cb` |
| `hl_setc_ori_48_137bce8aeb04` | `executable_setc_imm / 0x0000280a` | `L3` | `exact_value` | `2e01f5325134` |
| `maddw_32_9f922b15e674` | `executable_maddw_bfi_mi / 0x00002901` | `L3` | `exact_value` | `47f15120` |
| `setc_andi_32_32fe61c0559b` | `executable_setc_imm / 0x00002801` | `L3` | `exact_value` | `75261100` |
| `setc_ori_32_183dc15fad54` | `executable_setc_imm / 0x00002802` | `L3` | `exact_value` | `75361100` |

## Failed / Rejected Evidence

None.

## Execution Observations

- `executable_setc_imm / 0x00002801`: status `PASS`, oracle `PASS`, timeout-after-fail `False`, test-contract `valid`, attribution `none`
- `executable_setc_imm / 0x00002802`: status `PASS`, oracle `PASS`, timeout-after-fail `False`, test-contract `valid`, attribution `none`
- `executable_setc_imm / 0x00002803`: status `PASS`, oracle `PASS`, timeout-after-fail `False`, test-contract `valid`, attribution `none`
- `executable_setc_imm / 0x00002804`: status `PASS`, oracle `PASS`, timeout-after-fail `False`, test-contract `valid`, attribution `none`
- `executable_setc_imm / 0x00002805`: status `PASS`, oracle `PASS`, timeout-after-fail `False`, test-contract `valid`, attribution `none`
- `executable_setc_imm / 0x00002806`: status `PASS`, oracle `PASS`, timeout-after-fail `False`, test-contract `valid`, attribution `none`
- `executable_setc_imm / 0x00002807`: status `PASS`, oracle `PASS`, timeout-after-fail `False`, test-contract `valid`, attribution `none`
- `executable_setc_imm / 0x00002808`: status `PASS`, oracle `PASS`, timeout-after-fail `False`, test-contract `valid`, attribution `none`
- `executable_setc_imm / 0x00002809`: status `PASS`, oracle `PASS`, timeout-after-fail `False`, test-contract `valid`, attribution `none`
- `executable_setc_imm / 0x0000280a`: status `PASS`, oracle `PASS`, timeout-after-fail `False`, test-contract `valid`, attribution `none`
- `executable_maddw_bfi_mi / 0x00002901`: status `PASS`, oracle `PASS`, timeout-after-fail `False`, test-contract `valid`, attribution `none`
- `executable_maddw_bfi_mi / 0x00002902`: status `PASS`, oracle `PASS`, timeout-after-fail `False`, test-contract `valid`, attribution `none`
- `executable_maddw_bfi_mi / 0x00002903`: status `PASS`, oracle `PASS`, timeout-after-fail `False`, test-contract `valid`, attribution `none`
- `executable_maddw_bfi_mi / 0x00002904`: status `PASS`, oracle `PASS`, timeout-after-fail `False`, test-contract `valid`, attribution `none`
