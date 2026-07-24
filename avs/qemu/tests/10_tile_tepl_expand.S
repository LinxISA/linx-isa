/* v0.57 TEPL row/column broadcast and expand-arithmetic kernels. */

    .text

    .macro LOAD_FP32 reg, cols, rows, stride
    BSTART.TLOAD FP32
    C.B.DIMI \cols, ->lb0
    C.B.DIMI \rows, ->lb1
    C.B.DIMI \stride, ->lb2
    B.ARG NORM.normal
    B.IOR [\reg],[]
    B.IOT last, ->t<4KB>
    .endm

    .macro STORE_FP32 reg
    BSTART.TSTORE FP32
    C.B.DIMI 8, ->lb0
    C.B.DIMI 4, ->lb1
    C.B.DIMI 8, ->lb2
    B.ARG NORM.normal
    B.IOR [\reg],[]
    B.IOT t#1, last, ->t<4KB>
    .endm

    .macro EXPAND_BINARY name, op, vec_cols, vec_rows, vec_stride
    .globl \name
    .type \name,@function
\name:
    FENTRY [ra ~ ra], sp!, 8
    LOAD_FP32 a0, 8, 4, 8
    LOAD_FP32 a1, \vec_cols, \vec_rows, \vec_stride

    BSTART.\op FP32
    C.B.DIMI 8, ->lb0
    C.B.DIMI 4, ->lb1
    C.B.DIMI 8, ->lb2
    B.ARG VV
    B.IOT t#2, t#1, last, ->t<4KB>

    STORE_FP32 a2
    FRET.STK [ra ~ ra], sp!, 8
    .size \name, .-\name
    .endm

    .macro EXPAND_PURE name, op, vec_cols, vec_rows, vec_stride
    .globl \name
    .type \name,@function
\name:
    FENTRY [ra ~ ra], sp!, 8
    LOAD_FP32 a0, \vec_cols, \vec_rows, \vec_stride

    BSTART.\op FP32
    C.B.DIMI 8, ->lb0
    C.B.DIMI 4, ->lb1
    C.B.DIMI 8, ->lb2
    B.ARG VV
    B.IOT t#1, last, ->t<4KB>

    STORE_FP32 a1
    FRET.STK [ra ~ ra], sp!, 8
    .size \name, .-\name
    .endm

    EXPAND_PURE linx_trowexpand_f32, TROWEXPAND, 1, 4, 1
    EXPAND_PURE linx_tcolexpand_f32, TCOLEXPAND, 8, 1, 8

    EXPAND_BINARY linx_trowexpandadd_f32, TROWEXPANDADD, 1, 4, 1
    EXPAND_BINARY linx_trowexpandsub_f32, TROWEXPANDSUB, 1, 4, 1
    EXPAND_BINARY linx_trowexpandmul_f32, TROWEXPANDMUL, 1, 4, 1
    EXPAND_BINARY linx_trowexpanddiv_f32, TROWEXPANDDIV, 1, 4, 1
    EXPAND_BINARY linx_trowexpandmax_f32, TROWEXPANDMAX, 1, 4, 1
    EXPAND_BINARY linx_trowexpandmin_f32, TROWEXPANDMIN, 1, 4, 1
    EXPAND_BINARY linx_trowexpandexpdif_f32, TROWEXPANDEXPDIF, 1, 4, 1

    EXPAND_BINARY linx_tcolexpandadd_f32, TCOLEXPANDADD, 8, 1, 8
    EXPAND_BINARY linx_tcolexpandsub_f32, TCOLEXPANDSUB, 8, 1, 8
    EXPAND_BINARY linx_tcolexpandmul_f32, TCOLEXPANDMUL, 8, 1, 8
    EXPAND_BINARY linx_tcolexpanddiv_f32, TCOLEXPANDDIV, 8, 1, 8
    EXPAND_BINARY linx_tcolexpandmax_f32, TCOLEXPANDMAX, 8, 1, 8
    EXPAND_BINARY linx_tcolexpandmin_f32, TCOLEXPANDMIN, 8, 1, 8
    EXPAND_BINARY linx_tcolexpandexpdif_f32, TCOLEXPANDEXPDIF, 8, 1, 8

    .section ".note.GNU-stack","",@progbits
