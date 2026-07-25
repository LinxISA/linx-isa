/* v0.57 TEPL partial-valid binary kernels. */

    .text

    .macro TPART_KERNEL name, op
    .globl \name
    .type \name,@function
\name:
    FENTRY [ra ~ ra], sp!, 8

    BSTART.TLOAD FP32
    C.B.DIMI 4, ->lb0
    C.B.DIMI 3, ->lb1
    C.B.DIMI 4, ->lb2
    B.ARG NORM.normal
    B.IOR [a0],[]
    B.IOT last, ->t<512B>

    BSTART.TLOAD FP32
    C.B.DIMI 2, ->lb0
    C.B.DIMI 2, ->lb1
    C.B.DIMI 4, ->lb2
    B.ARG NORM.normal
    B.IOR [a1],[]
    B.IOT last, ->t<512B>

    BSTART.\op FP32
    C.B.DIMI 4, ->lb0
    C.B.DIMI 3, ->lb1
    C.B.DIMI 4, ->lb2
    B.ARG VV
    B.IOT t#2, t#1, last, ->t<512B>

    BSTART.TSTORE FP32
    C.B.DIMI 4, ->lb0
    C.B.DIMI 32, ->lb1
    C.B.DIMI 4, ->lb2
    B.ARG NORM.normal
    B.IOR [a2],[]
    B.IOT t#1, last, ->t<512B>

    FRET.STK [ra ~ ra], sp!, 8
    .size \name, .-\name
    .endm

    TPART_KERNEL linx_tpartadd_f32, TPARTADD
    TPART_KERNEL linx_tpartmul_f32, TPARTMUL
    TPART_KERNEL linx_tpartmax_f32, TPARTMAX
    TPART_KERNEL linx_tpartmin_f32, TPARTMIN

    .macro PART_ARG_KERNEL name, op
    .globl \name
    .type \name,@function
\name:
    FENTRY [ra ~ ra], sp!, 8

    BSTART.TLOAD FP32
    C.B.DIMI 8, ->lb0
    C.B.DIMI 2, ->lb1
    C.B.DIMI 8, ->lb2
    B.ARG NORM.normal
    B.IOR [a0],[]
    B.IOT last, ->t<512B>

    BSTART.TLOAD FP32
    C.B.DIMI 8, ->lb0
    C.B.DIMI 2, ->lb1
    C.B.DIMI 8, ->lb2
    B.ARG NORM.normal
    B.IOR [a1],[]
    B.IOT last, ->t<512B>

    BSTART.TLOAD UINT32
    C.B.DIMI 8, ->lb0
    C.B.DIMI 2, ->lb1
    C.B.DIMI 8, ->lb2
    B.ARG NORM.normal
    B.IOR [a2],[]
    B.IOT last, ->t<512B>

    BSTART.TLOAD UINT32
    C.B.DIMI 8, ->lb0
    C.B.DIMI 2, ->lb1
    C.B.DIMI 8, ->lb2
    B.ARG NORM.normal
    B.IOR [a3],[]
    B.IOT last, ->t<512B>

    BSTART.\op FP32
    C.B.DIMI 8, ->lb0
    C.B.DIMI 2, ->lb1
    C.B.DIMI 8, ->lb2
    B.ARG VV
    B.IOT t#4, t#3, ->t<512B>
    B.IOT t#2, t#1, last, ->u<512B>

    BSTART.TSTORE FP32
    C.B.DIMI 8, ->lb0
    C.B.DIMI 16, ->lb1
    C.B.DIMI 8, ->lb2
    B.ARG NORM.normal
    B.IOR [a4],[]
    B.IOT t#1, last, ->t<512B>

    BSTART.TSTORE UINT32
    C.B.DIMI 8, ->lb0
    C.B.DIMI 16, ->lb1
    C.B.DIMI 8, ->lb2
    B.ARG NORM.normal
    B.IOR [a5],[]
    B.IOT u#1, last, ->u<512B>

    FRET.STK [ra ~ ra], sp!, 8
    .size \name, .-\name
    .endm

    PART_ARG_KERNEL linx_tpartargmax_f32_u32, TPARTARGMAX
    PART_ARG_KERNEL linx_tpartargmin_f32_u32, TPARTARGMIN

    .section ".note.GNU-stack","",@progbits
