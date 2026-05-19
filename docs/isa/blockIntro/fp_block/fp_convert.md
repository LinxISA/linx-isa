# Data format conversion

Data format conversion instructions mainly include three types of operations:

- Conversion between floating point numbers and floating point numbers;
- Convert floating point numbers to signed or unsigned numbers;
- Convert signed or unsigned numbers to floating point numbers.

| Command | Description | Rounding Mode |
|------|--------|---------|
| fcvt | Conversion between floating point numbers | Controlled by CSTATE (FRM), default RNE |
| scvtf | Signed integer conversion to floating point | Controlled by CSTATE (FRM), default RNE |
| ucvtf | Unsigned integer conversion to floating point | Controlled by CSTATE (FRM), default RNE |
| fcvta | Convert floating point to signed/unsigned integer type | Default RNA, rounding away from zero |
| fcvtm | Convert floating point to signed/unsigned integer type | Default RDN, round to negative infinity |
| fcvtn | Convert floating point to signed/unsigned integer type | Default RNE, round to the nearest even number |
| fcvtp | Convert floating point to signed/unsigned integer type | Default RUP, round to positive infinity |
| fcvtz | Convert floating point to signed/unsigned integer type | Default RTZ, rounding toward zero |

The assembly format is as follows:

```asm
    fcvt.{srcT2dstT}  SrcL, ->{t, u, Rd}
    fcvta.{srcT2dstT} SrcL, ->{t, u, Rd}
    fcvtm.{srcT2dstT} SrcL, ->{t, u, Rd}
    fcvtn.{srcT2dstT} SrcL, ->{t, u, Rd}
    fcvtp.{srcT2dstT} SrcL, ->{t, u, Rd}
    fcvtz.{srcT2dstT} SrcL, ->{t, u, Rd}
    scvtf.{srcT2dstT} SrcL, ->{t, u, Rd}
    ucvtf.{srcT2dstT} SrcL, ->{t, u, Rd}
```

Among them: srcT: refers to the input data type, dstT: refers to the data type after format conversion.