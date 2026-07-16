# V03 vector executable-coverage diagnostic

This tranche attempted to add seven existing vector forms to the audited QEMU
L2/L3 ledger without weakening the exact-PC or literal-oracle requirements.
The canonical executable-coverage manifest and latest reports remain unchanged
at 51 admitted forms and zero rejected forms.

| Run | Result | Purpose |
| --- | --- | --- |
| `r1` | timeout | Initial bounded probe. |
| `r2` | pass | Baseline suite run before dedicated literal oracle packets. |
| `r3` | pass | All nine required test IDs and seven literal summaries passed; admission was rejected because the body symbols had empty ELF ranges and most target PCs were not present in the trace. |
| `r4` | timeout | Body symbols had valid `.type`/`.size` metadata, but whole-program `-singlestep` did not complete within 180 seconds. |
| `r5` | pass | Current source regression run with valid symbol ranges and all nine required test IDs. |

All runs used QEMU commit
`2856230890045899f074c18bcb2c2e37bbd09a0c`. The next coverage attempt should
capture the seven target PCs with a bounded, target-scoped trace rather than
single-stepping the full suite. Reporter policy must remain unchanged.
