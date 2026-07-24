/* Exact-value carriers for signed narrow TEPL arithmetic. */

    .text

    .macro TILE_BINARY name, opcode, dtype, footprint
    .globl \name
    .type \name,@function
\name:
    FENTRY [ra ~ ra], sp!, 8

    BSTART.TLOAD \dtype
    C.B.DIMI 32, ->lb0
    C.B.DIMI 32, ->lb1
    C.B.DIMI 32, ->lb2
    B.ARG NORM.normal
    B.IOR [a0],[]
    B.IOT last, ->t<\footprint>

    BSTART.TLOAD \dtype
    C.B.DIMI 32, ->lb0
    C.B.DIMI 32, ->lb1
    C.B.DIMI 32, ->lb2
    B.ARG NORM.normal
    B.IOR [a1],[]
    B.IOT last, ->t<\footprint>

    BSTART.\opcode \dtype
    C.B.DIMI 32, ->lb0
    C.B.DIMI 32, ->lb1
    C.B.DIMI 32, ->lb2
    B.ARG VV
    B.IOT t#2, t#1, last, ->t<\footprint>

    BSTART.TSTORE \dtype
    C.B.DIMI 32, ->lb0
    C.B.DIMI 32, ->lb1
    C.B.DIMI 32, ->lb2
    B.ARG NORM.normal
    B.IOR [a2],[]
    B.IOT t#1, last, ->t<\footprint>

    FRET.STK [ra ~ ra], sp!, 8
    .size \name, .-\name
    .endm

    .macro TILE_UNARY name, opcode, dtype, footprint
    .globl \name
    .type \name,@function
\name:
    FENTRY [ra ~ ra], sp!, 8

    BSTART.TLOAD \dtype
    C.B.DIMI 32, ->lb0
    C.B.DIMI 32, ->lb1
    C.B.DIMI 32, ->lb2
    B.ARG NORM.normal
    B.IOR [a0],[]
    B.IOT last, ->t<\footprint>

    BSTART.\opcode \dtype
    C.B.DIMI 32, ->lb0
    C.B.DIMI 32, ->lb1
    C.B.DIMI 32, ->lb2
    B.ARG VV
    B.IOT t#1, last, ->t<\footprint>

    BSTART.TSTORE \dtype
    C.B.DIMI 32, ->lb0
    C.B.DIMI 32, ->lb1
    C.B.DIMI 32, ->lb2
    B.ARG NORM.normal
    B.IOR [a1],[]
    B.IOT t#1, last, ->t<\footprint>

    FRET.STK [ra ~ ra], sp!, 8
    .size \name, .-\name
    .endm

    TILE_BINARY linx_tmax_s8, TMAX, INT8, 1KB
    TILE_BINARY linx_tshr_s8, TSHR, INT8, 1KB
    TILE_UNARY linx_tabs_s8, TABS, INT8, 1KB
    TILE_UNARY linx_tneg_s16, TNEG, INT16, 2KB
    TILE_BINARY linx_tdiv_s16, TDIV, INT16, 2KB
    TILE_BINARY linx_tadd_f16, TADD, FP16, 2KB
    TILE_BINARY linx_tmul_bf16, TMUL, BF16, 2KB

    TILE_BINARY linx_trem_s32, TREM, INT32, 4KB

    .globl linx_trems_s32
    .type linx_trems_s32,@function
linx_trems_s32:
    FENTRY [ra ~ ra], sp!, 8

    BSTART.TLOAD INT32
    C.B.DIMI 32, ->lb0
    C.B.DIMI 32, ->lb1
    C.B.DIMI 32, ->lb2
    B.ARG NORM.normal
    B.IOR [a0],[]
    B.IOT last, ->t<4KB>

    BSTART.TREMS INT32
    C.B.DIMI 32, ->lb0
    C.B.DIMI 32, ->lb1
    C.B.DIMI 32, ->lb2
    B.ARG VS
    B.IOR [a1],[]
    B.IOT t#1, last, ->t<4KB>

    BSTART.TSTORE INT32
    C.B.DIMI 32, ->lb0
    C.B.DIMI 32, ->lb1
    C.B.DIMI 32, ->lb2
    B.ARG NORM.normal
    B.IOR [a2],[]
    B.IOT t#1, last, ->t<4KB>

    FRET.STK [ra ~ ra], sp!, 8
    .size linx_trems_s32, .-linx_trems_s32

    .section ".note.GNU-stack","",@progbits
