/* v0.57 CUBE execution carriers. */

    .text
/* v0.57 CUBE TMATMUL.BIAS execution carrier. */


    .globl linx_tmatmul_bias_s32
    .type linx_tmatmul_bias_s32,@function
linx_tmatmul_bias_s32:
    FENTRY [ra ~ ra], sp!, 8

    BSTART.TLOAD INT32
    C.B.DIMI 8, ->lb0
    C.B.DIMI 8, ->lb1
    C.B.DIMI 8, ->lb2
    B.ARG NORM.normal
    B.IOR [a0],[]
    B.IOT last, ->t<512B>

    BSTART.TLOAD INT32
    C.B.DIMI 8, ->lb0
    C.B.DIMI 8, ->lb1
    C.B.DIMI 8, ->lb2
    B.ARG NORM.normal
    B.IOR [a1],[]
    B.IOT last, ->t<512B>

    BSTART.TLOAD INT32
    C.B.DIMI 8, ->lb0
    C.B.DIMI 1, ->lb1
    C.B.DIMI 8, ->lb2
    B.ARG NORM.normal
    B.IOR [a2],[]
    B.IOT last, ->t<512B>

    BSTART.TMATMUL.BIAS INT32
    C.B.DIMI 8, ->lb0
    C.B.DIMI 8, ->lb1
    C.B.DIMI 8, ->lb2
    B.IOT t#3, t#2
    B.IOT t#1, last, ->acc<512B>

    BSTART.ACCCVT INT32
    B.IOT last, ->m<512B>

    BSTART.TSTORE INT32
    C.B.DIMI 8, ->lb0
    C.B.DIMI 16, ->lb1
    C.B.DIMI 8, ->lb2
    B.ARG NORM.normal
    B.IOR [a3],[]
    B.IOT m#1, last, ->m<512B>

    FRET.STK [ra ~ ra], sp!, 8
    .size linx_tmatmul_bias_s32, .-linx_tmatmul_bias_s32

/* v0.57 CUBE TGEMV and TGEMV.ACC execution carrier. */


    .globl linx_tgemv_s32
    .type linx_tgemv_s32,@function
linx_tgemv_s32:
    FENTRY [ra ~ ra], sp!, 8

    BSTART.TLOAD INT32
    C.B.DIMI 8, ->lb0
    C.B.DIMI 8, ->lb1
    C.B.DIMI 8, ->lb2
    B.ARG NORM.normal
    B.IOR [a0],[]
    B.IOT last, ->t<512B>

    BSTART.TLOAD INT32
    C.B.DIMI 8, ->lb0
    C.B.DIMI 8, ->lb1
    C.B.DIMI 8, ->lb2
    B.ARG NORM.normal
    B.IOR [a1],[]
    B.IOT last, ->t<512B>

    BSTART.TGEMV INT32
    C.B.DIMI 8, ->lb0
    C.B.DIMI 1, ->lb1
    C.B.DIMI 8, ->lb2
    B.IOT t#2, t#1, last, ->acc<512B>

    BSTART.ACCCVT INT32
    B.IOT last, ->m<512B>

    BSTART.TSTORE INT32
    C.B.DIMI 8, ->lb0
    C.B.DIMI 16, ->lb1
    C.B.DIMI 8, ->lb2
    B.ARG NORM.normal
    B.IOR [a2],[]
    B.IOT m#1, last, ->m<512B>

    FRET.STK [ra ~ ra], sp!, 8
    .size linx_tgemv_s32, .-linx_tgemv_s32

    .globl linx_tgemv_acc_s32
    .type linx_tgemv_acc_s32,@function
linx_tgemv_acc_s32:
    FENTRY [ra ~ ra], sp!, 8

    BSTART.TLOAD INT32
    C.B.DIMI 8, ->lb0
    C.B.DIMI 8, ->lb1
    C.B.DIMI 8, ->lb2
    B.ARG NORM.normal
    B.IOR [a0],[]
    B.IOT last, ->t<512B>

    BSTART.TLOAD INT32
    C.B.DIMI 8, ->lb0
    C.B.DIMI 8, ->lb1
    C.B.DIMI 8, ->lb2
    B.ARG NORM.normal
    B.IOR [a1],[]
    B.IOT last, ->t<512B>

    BSTART.TGEMV INT32
    C.B.DIMI 8, ->lb0
    C.B.DIMI 1, ->lb1
    C.B.DIMI 8, ->lb2
    B.IOT t#2.reuse, t#1.reuse, last, ->acc<512B>

    BSTART.ACCCVT INT32
    B.IOT last, ->m<512B>

    BSTART.TGEMV.ACC INT32
    C.B.DIMI 8, ->lb0
    C.B.DIMI 1, ->lb1
    C.B.DIMI 8, ->lb2
    B.IOT t#2, t#1, last, ->acc<512B>

    BSTART.ACCCVT INT32
    B.IOT last, ->m<512B>

    BSTART.TSTORE INT32
    C.B.DIMI 8, ->lb0
    C.B.DIMI 16, ->lb1
    C.B.DIMI 8, ->lb2
    B.ARG NORM.normal
    B.IOR [a2],[]
    B.IOT m#1, last, ->m<512B>

    FRET.STK [ra ~ ra], sp!, 8
    .size linx_tgemv_acc_s32, .-linx_tgemv_acc_s32


    .section ".note.GNU-stack","",@progbits
