/* v0.57 TEPL layout and padding kernels. */

    .text

    .macro TFILLPAD_KERNEL name, pad, emit_datr=1
    .globl \name
    .type \name,@function
\name:
    FENTRY [ra ~ ra], sp!, 8

    BSTART.TLOAD FP32
    C.B.DIMI 3, ->lb0
    C.B.DIMI 2, ->lb1
    C.B.DIMI 4, ->lb2
    B.ARG NORM.normal
    B.IOR [a0],[]
    B.IOT last, ->t<512B>

    BSTART.TFILLPAD FP32
    C.B.DIMI 3, ->lb0
    C.B.DIMI 2, ->lb1
    C.B.DIMI 4, ->lb2
    B.ARG VV
    .if \emit_datr
    B.DATR normal, FP32, \pad, cmode0, rmode0
    .endif
    B.IOT t#1, last, ->t<512B>

    BSTART.TSTORE FP32
    C.B.DIMI 4, ->lb0
    C.B.DIMI 32, ->lb1
    C.B.DIMI 4, ->lb2
    B.ARG NORM.normal
    B.IOR [a1],[]
    B.IOT t#1, last, ->t<512B>

    FRET.STK [ra ~ ra], sp!, 8
    .size \name, .-\name
    .endm

    TFILLPAD_KERNEL linx_tfillpad_f32_default, ZERO, 0
    TFILLPAD_KERNEL linx_tfillpad_f32_zero, ZERO
    TFILLPAD_KERNEL linx_tfillpad_f32_max, MAX
    TFILLPAD_KERNEL linx_tfillpad_f32_min, MIN

    .macro TFILLPAD_INT8_KERNEL name, dtype, pad
    .globl \name
    .type \name,@function
\name:
    FENTRY [ra ~ ra], sp!, 8

    BSTART.TLOAD \dtype
    C.B.DIMI 3, ->lb0
    C.B.DIMI 2, ->lb1
    C.B.DIMI 4, ->lb2
    B.ARG NORM.normal
    B.IOR [a0],[]
    B.IOT last, ->t<512B>

    BSTART.TFILLPAD \dtype
    C.B.DIMI 3, ->lb0
    C.B.DIMI 2, ->lb1
    C.B.DIMI 4, ->lb2
    B.ARG VV
    B.DATR normal, \dtype, \pad, cmode0, rmode0
    B.IOT t#1, last, ->t<512B>

    BSTART.TSTORE \dtype
    C.B.DIMI 4, ->lb0
    C.B.DIMI 128, ->lb1
    C.B.DIMI 4, ->lb2
    B.ARG NORM.normal
    B.IOR [a1],[]
    B.IOT t#1, last, ->t<512B>

    FRET.STK [ra ~ ra], sp!, 8
    .size \name, .-\name
    .endm

    TFILLPAD_INT8_KERNEL linx_tfillpad_s8_max, INT8, MAX
    TFILLPAD_INT8_KERNEL linx_tfillpad_s8_min, INT8, MIN
    TFILLPAD_INT8_KERNEL linx_tfillpad_u8_max, UINT8, MAX
    TFILLPAD_INT8_KERNEL linx_tfillpad_u8_min, UINT8, MIN

    .section ".note.GNU-stack","",@progbits
