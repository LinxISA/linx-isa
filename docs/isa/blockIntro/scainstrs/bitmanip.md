# bit operation instructions

Bit manipulation instructions include F-type instructions used to intercept or set bits.

| Microinstructions | Assembly format | Description |
|---------------|---------------|----------------------------------------|
| BXU | bxu SrcL, M, N, ->{t,u,Rd} | Continuously intercept the `N` bits starting from the `M` bit of the source operand without sign extension |
| BXS | bxs SrcL, M, N, ->{t,u,Rd} | Continuously intercept the `N` bits starting from the `M` bit of the source operand and sign extend |
| BIC | bic SrcL, M, N, ->{t,u,Rd} | Set the consecutive `N` bits starting from the `M` bit of the source operand to 0 |
| BIS | bis SrcL, M, N, ->{t,u,Rd} | Set the consecutive `N` bits starting from the `M` bit of the source operand to 1 |
| CTZ | ctz SrcL, M, N, ->{t,u,Rd} | Count the number of 0s after the first 1 in the `N` bit of the source operand starting from the `M` bit |
| CLZ | clz SrcL, M, N, ->{t,u,Rd} | Count the number of 0s starting from the `M` bit of the source operand before the first 1 in the `N` bit |
| BCNT | bcnt SrcL, M, N, ->{t,u,Rd} | Count the number of consecutive `N` bits starting from the `M` bit of the source operand that are 1 |
| REV | rev SrcL, M, N, ->{t,u,Rd} | Flip in units of `N` bits within the range of `M` bits of the source operand |

The encoding format is as follows:

![BitOperation](../../../figs/bitfield/svg/Introduction_32bit/BitOperation.svg)