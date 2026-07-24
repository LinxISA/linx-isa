/* Rectangular Tile shape metadata carrier. */

    .text

    .globl linx_tadd_rect_s32
    .type linx_tadd_rect_s32,@function
linx_tadd_rect_s32:
    FENTRY [ra ~ ra], sp!, 8

    BSTART.TLOAD INT32
    C.B.DIMI 3, ->lb0
    C.B.DIMI 2, ->lb1
    C.B.DIMI 4, ->lb2
    B.ARG NORM.normal
    B.IOR [a0],[]
    B.IOT last, ->t<4KB>

    BSTART.TLOAD INT32
    C.B.DIMI 3, ->lb0
    C.B.DIMI 2, ->lb1
    C.B.DIMI 4, ->lb2
    B.ARG NORM.normal
    B.IOR [a1],[]
    B.IOT last, ->t<4KB>

    BSTART.TADD INT32
    C.B.DIMI 3, ->lb0
    C.B.DIMI 2, ->lb1
    C.B.DIMI 4, ->lb2
    B.ARG VV
    B.IOT t#2, t#1, last, ->t<4KB>

    BSTART.TSTORE INT32
    C.B.DIMI 3, ->lb0
    C.B.DIMI 2, ->lb1
    C.B.DIMI 4, ->lb2
    B.ARG NORM.normal
    B.IOR [a2],[]
    B.IOT t#1, last, ->t<4KB>

    FRET.STK [ra ~ ra], sp!, 8
    .size linx_tadd_rect_s32, .-linx_tadd_rect_s32

    .section ".note.GNU-stack","",@progbits
