# QEMU Executable Coverage Ledger

Generated: `2026-08-02T12:51:46Z`

This ledger counts only per-form evidence bound to golden identity, bytes, test ID,
artifacts, QEMU SHA, a test-specific terminal PASS, and an oracle. Suite exit 0 and stdout alone do not count.

## Evidence Levels

| Level | Availability | Forms | Mnemonics |
| --- | --- | ---: | ---: |
| L2 | `available` | 60 | 60 |
| L3 | `available` | 60 | 60 |

## Admitted Forms

| Form | Suite / Test | Level | Oracle | Bytes |
| --- | --- | --- | --- | --- |
| `add_32_d04202886d0a` | `executable_scalar / 0x00002501` | `L3` | `exact_value` | `05814106` |
| `and_32_b6a903a3ec94` | `executable_scalar / 0x00002503` | `L3` | `exact_value` | `05a14106` |
| `c_bstart_16_c4e238a9227a` | `callret / 0x0000140f` | `L3` | `exact_value` | `8400` |
| `c_bstart_std_16_8b40f078c14a` | `callret / 0x0000140d` | `L3` | `exact_value` | `0038` |
| `cmp_eq_32_6af7c8f41300` | `executable_integer / 0x00002609` | `L3` | `exact_value` | `45813106` |
| `cmp_ge_32_d88e3a1cfff4` | `executable_integer / 0x0000260d` | `L3` | `exact_value` | `45d14106` |
| `cmp_geu_32_0c002dc415ef` | `executable_integer / 0x0000260e` | `L3` | `exact_value` | `45f14106` |
| `cmp_lt_32_c0b8cc320f12` | `executable_integer / 0x0000260b` | `L3` | `exact_value` | `45c14106` |
| `cmp_ltu_32_4377481baebc` | `executable_integer / 0x0000260c` | `L3` | `exact_value` | `45e14106` |
| `cmp_ne_32_fc47fbb1a0de` | `executable_integer / 0x0000260a` | `L3` | `exact_value` | `45913206` |
| `csel_32_ba77cbad3c99` | `executable_integer / 0x0000260f` | `L3` | `exact_value` | `f7015216` |
| `div_32_a6efe85f8662` | `executable_integer / 0x00002605` | `L3` | `exact_value` | `57814100` |
| `divu_32_cfbc0d1760e4` | `executable_integer / 0x00002606` | `L3` | `exact_value` | `57914100` |
| `fentry_32_a47584ec13b6` | `callret / 0x0000140b` | `L3` | `exact_value` | `4100a504` |
| `fret_ra_32_659c886221c1` | `callret / 0x0000140c` | `L3` | `exact_value` | `4120a504` |
| `fret_stk_32_4fe246bd8241` | `callret / 0x0000140b` | `L3` | `exact_value` | `4130a504` |
| `hl_ldip_48_60afa6423d39` | `executable_memory / 0x0000220c` | `L3` | `architectural_state` | `1e2819320200` |
| `hl_lwui_po_48_09a75b628dc4` | `executable_memory / 0x00002201` | `L3` | `architectural_state` | `3e1819611100` |
| `hl_lwui_pr_48_32de19a508f0` | `executable_memory / 0x00002202` | `L3` | `architectural_state` | `2e1819611100` |
| `hl_lwui_upo_48_33260eb06a2c` | `executable_memory / 0x00002203` | `L3` | `architectural_state` | `3e1829614100` |
| `hl_lwui_upr_48_998a98c46469` | `executable_memory / 0x00002204` | `L3` | `architectural_state` | `2e1829614100` |
| `hl_lwuip_48_2a5d6d8f3b70` | `executable_memory / 0x00002209` | `L3` | `architectural_state` | `1e2099e10100` |
| `hl_sdip_48_6d622cf167ca` | `executable_memory / 0x0000220d` | `L3` | `architectural_state` | `de0059305100` |
| `hl_swi_po_48_66a80d0fa7f5` | `executable_memory / 0x00002205` | `L3` | `architectural_state` | `3e2859204102` |
| `hl_swi_pr_48_68b9003e0421` | `executable_memory / 0x00002206` | `L3` | `architectural_state` | `2e2059a02102` |
| `hl_swi_upo_48_243d3c38cd1a` | `executable_memory / 0x00002207` | `L3` | `architectural_state` | `3e2059e02108` |
| `hl_swi_upr_48_15c2fb96aab0` | `executable_memory / 0x00002208` | `L3` | `architectural_state` | `2e2859604108` |
| `hl_swip_48_e2fca8cde001` | `executable_memory / 0x0000220a` | `L3` | `architectural_state` | `9e0059a04200` |
| `hl_swip_u_48_e2dc917c8505` | `executable_memory / 0x0000220b` | `L3` | `architectural_state` | `9e0059e04210` |
| `j_32_a303cf05af42` | `callret / 0x00001410` | `L3` | `exact_value` | `37000300` |
| `l_bstart_std_64_37e84068ce61` | `callret / 0x00001411` | `L3` | `exact_value` | `0f06000001200000` |
| `lb_32_b718aa88e28f` | `executable_scalar / 0x00002509` | `L3` | `exact_value` | `09814106` |
| `lbu_32_a9a58ab4ea22` | `executable_integer / 0x00002601` | `L3` | `exact_value` | `09c14106` |
| `ld_32_7c48838bc4e6` | `executable_scalar / 0x0000250c` | `L3` | `exact_value` | `09b14106` |
| `lh_32_d0f04d7d7696` | `executable_scalar / 0x0000250a` | `L3` | `exact_value` | `09914106` |
| `lhu_32_730caf67ecd1` | `executable_integer / 0x00002602` | `L3` | `exact_value` | `09d14106` |
| `lr_d_32_84d21a553dc1` | `atomic / 0x00007163` | `L3` | `exact_value` | `0b011131` |
| `lr_w_32_efecc735bb75` | `atomic / 0x00007162` | `L3` | `exact_value` | `0b01f121` |
| `lw_32_3a77ffafcb34` | `executable_scalar / 0x0000250b` | `L3` | `exact_value` | `09a14106` |
| `lwu_32_678935925636` | `executable_integer / 0x00002603` | `L3` | `exact_value` | `09e14106` |
| `mul_32_9f2affd8efb8` | `executable_integer / 0x00002604` | `L3` | `exact_value` | `47814100` |
| `or_32_a7fb80e78831` | `executable_scalar / 0x00002504` | `L3` | `exact_value` | `05b14106` |
| `rem_32_0abbd6a3b865` | `executable_integer / 0x00002607` | `L3` | `exact_value` | `57c14100` |
| `remu_32_d7a5d1ebbbf5` | `executable_integer / 0x00002608` | `L3` | `exact_value` | `57d14100` |
| `sb_32_43c106ae3749` | `executable_scalar / 0x0000250d` | `L3` | `architectural_state` | `4900411e` |
| `sd_32_9dbc40328653` | `executable_scalar / 0x00002510` | `L3` | `architectural_state` | `4930521e` |
| `sh_32_bc7d4a7dea28` | `executable_scalar / 0x0000250e` | `L3` | `architectural_state` | `4910411e` |
| `sll_32_a100b8961e21` | `executable_scalar / 0x00002506` | `L3` | `exact_value` | `05f14100` |
| `sra_32_ba03eea6386b` | `executable_scalar / 0x00002508` | `L3` | `exact_value` | `05e14100` |
| `srl_32_5cfca42c59f3` | `executable_scalar / 0x00002507` | `L3` | `exact_value` | `05d14100` |
| `sub_32_af383d4a2b42` | `executable_scalar / 0x00002502` | `L3` | `exact_value` | `05914106` |
| `sw_32_28ad317b1b41` | `executable_scalar / 0x0000250f` | `L3` | `architectural_state` | `49205216` |
| `v_add_64_394294cc5946` | `v057_vector_ops / 0x00001370` | `L3` | `exact_value` | `7f02520005801000` |
| `v_cmp_lt_64_3ef2162a77ba` | `v057_vector_ops / 0x00001320` | `L3` | `exact_value` | `7f82110045401000` |
| `v_fadd_64_c5c08b2ac830` | `v057_vector_ops / 0x00001374` | `L3` | `exact_value` | `7f0212004b802000` |
| `v_fmul_64_3e2b1576cbfe` | `v057_vector_ops / 0x00001375` | `L3` | `exact_value` | `7f0212004ba03000` |
| `v_lw_brg_64_6163b7a621fc` | `v057_vector_ops / 0x00001372` | `L3` | `exact_value` | `7fa2000009200000` |
| `v_sub_64_3c88cf0158f8` | `v057_vector_ops / 0x00001371` | `L3` | `exact_value` | `7f02520005101100` |
| `v_sw_brg_64_d78368c708bd` | `v057_vector_ops / 0x00001373` | `L3` | `exact_value` | `7fa0002049200108` |
| `xor_32_33510860c585` | `executable_scalar / 0x00002505` | `L3` | `exact_value` | `05c14106` |

## Failed / Rejected Evidence

None.

## Execution Observations

- `callret / 0x0000140b`: status `PASS`, oracle `PASS`, timeout-after-fail `False`, test-contract `valid`, attribution `none`
- `callret / 0x0000140c`: status `PASS`, oracle `PASS`, timeout-after-fail `False`, test-contract `valid`, attribution `none`
- `callret / 0x0000140d`: status `PASS`, oracle `PASS`, timeout-after-fail `False`, test-contract `valid`, attribution `none`
- `callret / 0x0000140f`: status `PASS`, oracle `PASS`, timeout-after-fail `False`, test-contract `valid`, attribution `none`
- `callret / 0x00001410`: status `PASS`, oracle `PASS`, timeout-after-fail `False`, test-contract `valid`, attribution `none`
- `callret / 0x00001411`: status `PASS`, oracle `PASS`, timeout-after-fail `False`, test-contract `valid`, attribution `none`
- `executable_memory / 0x00002201`: status `PASS`, oracle `PASS`, timeout-after-fail `False`, test-contract `valid`, attribution `none`
- `executable_memory / 0x00002202`: status `PASS`, oracle `PASS`, timeout-after-fail `False`, test-contract `valid`, attribution `none`
- `executable_scalar / 0x00002501`: status `PASS`, oracle `PASS`, timeout-after-fail `False`, test-contract `valid`, attribution `none`
- `executable_scalar / 0x00002502`: status `PASS`, oracle `PASS`, timeout-after-fail `False`, test-contract `valid`, attribution `none`
- `executable_scalar / 0x00002503`: status `PASS`, oracle `PASS`, timeout-after-fail `False`, test-contract `valid`, attribution `none`
- `executable_scalar / 0x00002504`: status `PASS`, oracle `PASS`, timeout-after-fail `False`, test-contract `valid`, attribution `none`
- `executable_scalar / 0x00002505`: status `PASS`, oracle `PASS`, timeout-after-fail `False`, test-contract `valid`, attribution `none`
- `executable_scalar / 0x00002506`: status `PASS`, oracle `PASS`, timeout-after-fail `False`, test-contract `valid`, attribution `none`
- `executable_scalar / 0x00002507`: status `PASS`, oracle `PASS`, timeout-after-fail `False`, test-contract `valid`, attribution `none`
- `executable_scalar / 0x00002508`: status `PASS`, oracle `PASS`, timeout-after-fail `False`, test-contract `valid`, attribution `none`
- `executable_scalar / 0x00002509`: status `PASS`, oracle `PASS`, timeout-after-fail `False`, test-contract `valid`, attribution `none`
- `executable_scalar / 0x0000250a`: status `PASS`, oracle `PASS`, timeout-after-fail `False`, test-contract `valid`, attribution `none`
- `executable_scalar / 0x0000250b`: status `PASS`, oracle `PASS`, timeout-after-fail `False`, test-contract `valid`, attribution `none`
- `executable_scalar / 0x0000250c`: status `PASS`, oracle `PASS`, timeout-after-fail `False`, test-contract `valid`, attribution `none`
- `executable_scalar / 0x0000250d`: status `PASS`, oracle `PASS`, timeout-after-fail `False`, test-contract `valid`, attribution `none`
- `executable_scalar / 0x0000250e`: status `PASS`, oracle `PASS`, timeout-after-fail `False`, test-contract `valid`, attribution `none`
- `executable_scalar / 0x0000250f`: status `PASS`, oracle `PASS`, timeout-after-fail `False`, test-contract `valid`, attribution `none`
- `executable_scalar / 0x00002510`: status `PASS`, oracle `PASS`, timeout-after-fail `False`, test-contract `valid`, attribution `none`
- `executable_memory / 0x00002203`: status `PASS`, oracle `PASS`, timeout-after-fail `False`, test-contract `valid`, attribution `none`
- `executable_memory / 0x00002204`: status `PASS`, oracle `PASS`, timeout-after-fail `False`, test-contract `valid`, attribution `none`
- `executable_memory / 0x00002205`: status `PASS`, oracle `PASS`, timeout-after-fail `False`, test-contract `valid`, attribution `none`
- `executable_memory / 0x00002206`: status `PASS`, oracle `PASS`, timeout-after-fail `False`, test-contract `valid`, attribution `none`
- `executable_memory / 0x00002207`: status `PASS`, oracle `PASS`, timeout-after-fail `False`, test-contract `valid`, attribution `none`
- `executable_memory / 0x00002208`: status `PASS`, oracle `PASS`, timeout-after-fail `False`, test-contract `valid`, attribution `none`
- `executable_memory / 0x00002209`: status `PASS`, oracle `PASS`, timeout-after-fail `False`, test-contract `valid`, attribution `none`
- `executable_memory / 0x0000220a`: status `PASS`, oracle `PASS`, timeout-after-fail `False`, test-contract `valid`, attribution `none`
- `executable_memory / 0x0000220b`: status `PASS`, oracle `PASS`, timeout-after-fail `False`, test-contract `valid`, attribution `none`
- `executable_memory / 0x0000220c`: status `PASS`, oracle `PASS`, timeout-after-fail `False`, test-contract `valid`, attribution `none`
- `executable_memory / 0x0000220d`: status `PASS`, oracle `PASS`, timeout-after-fail `False`, test-contract `valid`, attribution `none`
- `executable_integer / 0x00002601`: status `PASS`, oracle `PASS`, timeout-after-fail `False`, test-contract `valid`, attribution `none`
- `executable_integer / 0x00002602`: status `PASS`, oracle `PASS`, timeout-after-fail `False`, test-contract `valid`, attribution `none`
- `executable_integer / 0x00002603`: status `PASS`, oracle `PASS`, timeout-after-fail `False`, test-contract `valid`, attribution `none`
- `executable_integer / 0x00002604`: status `PASS`, oracle `PASS`, timeout-after-fail `False`, test-contract `valid`, attribution `none`
- `executable_integer / 0x00002605`: status `PASS`, oracle `PASS`, timeout-after-fail `False`, test-contract `valid`, attribution `none`
- `executable_integer / 0x00002606`: status `PASS`, oracle `PASS`, timeout-after-fail `False`, test-contract `valid`, attribution `none`
- `executable_integer / 0x00002607`: status `PASS`, oracle `PASS`, timeout-after-fail `False`, test-contract `valid`, attribution `none`
- `executable_integer / 0x00002608`: status `PASS`, oracle `PASS`, timeout-after-fail `False`, test-contract `valid`, attribution `none`
- `executable_integer / 0x00002609`: status `PASS`, oracle `PASS`, timeout-after-fail `False`, test-contract `valid`, attribution `none`
- `executable_integer / 0x0000260a`: status `PASS`, oracle `PASS`, timeout-after-fail `False`, test-contract `valid`, attribution `none`
- `executable_integer / 0x0000260b`: status `PASS`, oracle `PASS`, timeout-after-fail `False`, test-contract `valid`, attribution `none`
- `executable_integer / 0x0000260c`: status `PASS`, oracle `PASS`, timeout-after-fail `False`, test-contract `valid`, attribution `none`
- `executable_integer / 0x0000260d`: status `PASS`, oracle `PASS`, timeout-after-fail `False`, test-contract `valid`, attribution `none`
- `executable_integer / 0x0000260e`: status `PASS`, oracle `PASS`, timeout-after-fail `False`, test-contract `valid`, attribution `none`
- `executable_integer / 0x0000260f`: status `PASS`, oracle `PASS`, timeout-after-fail `False`, test-contract `valid`, attribution `none`
- `v057_vector_ops / 0x00001372`: status `PASS`, oracle `PASS`, timeout-after-fail `False`, test-contract `valid`, attribution `none`
- `v057_vector_ops / 0x00001370`: status `PASS`, oracle `PASS`, timeout-after-fail `False`, test-contract `valid`, attribution `none`
- `v057_vector_ops / 0x00001373`: status `PASS`, oracle `PASS`, timeout-after-fail `False`, test-contract `valid`, attribution `none`
- `v057_vector_ops / 0x00001371`: status `PASS`, oracle `PASS`, timeout-after-fail `False`, test-contract `valid`, attribution `none`
- `v057_vector_ops / 0x00001374`: status `PASS`, oracle `PASS`, timeout-after-fail `False`, test-contract `valid`, attribution `none`
- `v057_vector_ops / 0x00001375`: status `PASS`, oracle `PASS`, timeout-after-fail `False`, test-contract `valid`, attribution `none`
- `v057_vector_ops / 0x00001320`: status `PASS`, oracle `PASS`, timeout-after-fail `False`, test-contract `valid`, attribution `none`
- `atomic / 0x00007162`: status `PASS`, oracle `PASS`, timeout-after-fail `False`, test-contract `valid`, attribution `none`
- `atomic / 0x00007163`: status `PASS`, oracle `PASS`, timeout-after-fail `False`, test-contract `valid`, attribution `none`
- `v057_vector_ops / 0x00001321`: status `FAIL`, oracle `FAIL`, timeout-after-fail `True`, failure `0x00001321` expected `0x0000000000000053` actual `0x0000000000000011`, test-contract `invalid`, attribution `test_contract`, note: Historical first-red evidence. The AVS source used invalid VT/VU lifetime and relative-index semantics; the corrected source and authored B.IOR binding now pass 0x1300, 0x1310, and 0x1320.
