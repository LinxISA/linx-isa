/* v0.57 TEPL packed-predicate selection kernels. */

    .text

    .globl linx_tsel_s32
    .type linx_tsel_s32,@function
linx_tsel_s32:
    FENTRY [ra ~ ra], sp!, 8

    BSTART.TLOAD UINT32
    C.B.DIMI 2, ->lb0
    C.B.DIMI 16, ->lb1
    C.B.DIMI 2, ->lb2
    B.ARG NORM.normal
    B.IOR [a0],[]
    B.IOT last, ->t<4KB>

    BSTART.TLOAD INT32
    C.B.DIMI 64, ->lb0
    C.B.DIMI 16, ->lb1
    C.B.DIMI 64, ->lb2
    B.ARG NORM.normal
    B.IOR [a1],[]
    B.IOT last, ->t<4KB>

    BSTART.TLOAD INT32
    C.B.DIMI 64, ->lb0
    C.B.DIMI 16, ->lb1
    C.B.DIMI 64, ->lb2
    B.ARG NORM.normal
    B.IOR [a2],[]
    B.IOT last, ->t<4KB>

    BSTART.TSEL INT32
    C.B.DIMI 64, ->lb0
    C.B.DIMI 16, ->lb1
    C.B.DIMI 64, ->lb2
    B.ARG VV
    B.IOT t#3, t#2
    B.IOT t#1, last, ->t<4KB>

    BSTART.TSTORE INT32
    C.B.DIMI 64, ->lb0
    C.B.DIMI 16, ->lb1
    C.B.DIMI 64, ->lb2
    B.ARG NORM.normal
    B.IOR [a3],[]
    B.IOT t#1, last, ->t<4KB>

    FRET.STK [ra ~ ra], sp!, 8
    .size linx_tsel_s32, .-linx_tsel_s32

    .globl linx_tsels_s32
    .type linx_tsels_s32,@function
linx_tsels_s32:
    FENTRY [ra ~ ra], sp!, 8

    BSTART.TLOAD UINT32
    C.B.DIMI 2, ->lb0
    C.B.DIMI 16, ->lb1
    C.B.DIMI 2, ->lb2
    B.ARG NORM.normal
    B.IOR [a0],[]
    B.IOT last, ->t<4KB>

    BSTART.TLOAD INT32
    C.B.DIMI 64, ->lb0
    C.B.DIMI 16, ->lb1
    C.B.DIMI 64, ->lb2
    B.ARG NORM.normal
    B.IOR [a1],[]
    B.IOT last, ->t<4KB>

    BSTART.TSELS INT32
    C.B.DIMI 64, ->lb0
    C.B.DIMI 16, ->lb1
    C.B.DIMI 64, ->lb2
    B.ARG VS
    B.IOR [a2],[]
    B.IOT t#2, t#1, last, ->t<4KB>

    BSTART.TSTORE INT32
    C.B.DIMI 64, ->lb0
    C.B.DIMI 16, ->lb1
    C.B.DIMI 64, ->lb2
    B.ARG NORM.normal
    B.IOR [a3],[]
    B.IOT t#1, last, ->t<4KB>

    FRET.STK [ra ~ ra], sp!, 8
    .size linx_tsels_s32, .-linx_tsels_s32

    .section ".note.GNU-stack","",@progbits
