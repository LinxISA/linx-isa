/* v0.57 TEPL two-source interleave/de-interleave execution carriers. */

    .text

    .macro INTERLEAVE_KERNEL name, op
    .globl \name
    .type \name,@function
\name:
    FENTRY [ra ~ ra], sp!, 8

    BSTART.TLOAD INT32
    C.B.DIMI 8, ->lb0
    C.B.DIMI 2, ->lb1
    C.B.DIMI 8, ->lb2
    B.ARG NORM.normal
    B.IOR [a0],[]
    B.IOT last, ->t<512B>

    BSTART.TLOAD INT32
    C.B.DIMI 8, ->lb0
    C.B.DIMI 2, ->lb1
    C.B.DIMI 8, ->lb2
    B.ARG NORM.normal
    B.IOR [a1],[]
    B.IOT last, ->t<512B>

    BSTART.\op INT32
    C.B.DIMI 8, ->lb0
    C.B.DIMI 2, ->lb1
    C.B.DIMI 8, ->lb2
    B.ARG VV
    B.IOT t#1, t#2, ->t<512B>
    B.IOT last, ->t<512B>

    /* Descriptor order is dst1, dst0; dst0 is therefore the newest T. */
    BSTART.TSTORE INT32
    C.B.DIMI 8, ->lb0
    C.B.DIMI 16, ->lb1
    C.B.DIMI 8, ->lb2
    B.ARG NORM.normal
    B.IOR [a2],[]
    B.IOT t#1, last, ->t<512B>

    BSTART.TSTORE INT32
    C.B.DIMI 8, ->lb0
    C.B.DIMI 16, ->lb1
    C.B.DIMI 8, ->lb2
    B.ARG NORM.normal
    B.IOR [a3],[]
    B.IOT t#1, last, ->t<512B>

    FRET.STK [ra ~ ra], sp!, 8
    .size \name, .-\name
    .endm

    INTERLEAVE_KERNEL linx_tinterleave_s32, TINTERLEAVE
    INTERLEAVE_KERNEL linx_tdeinterleave_s32, TDEINTERLEAVE

    .section ".note.GNU-stack","",@progbits
