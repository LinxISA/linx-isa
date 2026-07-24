/* v0.57 TCMP mode carriers. The generic TEPL builtin does not expose
 * B.DATR.CMode, so these focused kernels provide L2/L3 coverage for all six
 * architectural comparison modes without changing the compiler API. */

    .text

    .macro TCMP_KERNEL name, dtype, cmode
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
    B.IOT last, ->t<4KB>

    BSTART.TLOAD \dtype
    C.B.DIMI 32, ->lb0
    C.B.DIMI 32, ->lb1
    C.B.DIMI 32, ->lb2
    B.ARG NORM.normal
    B.IOR [a1],[]
    B.IOT last, ->t<4KB>

    BSTART.TCMP \dtype
    C.B.DIMI 31, ->lb0
    C.B.DIMI 32, ->lb1
    C.B.DIMI 32, ->lb2
    B.ARG VV
    B.DATR normal, \dtype, ZERO, cmode\cmode, rmode0
    B.IOT t#2, t#1, last, ->t<4KB>

    BSTART.TSTORE UINT32
    C.B.DIMI 32, ->lb0
    C.B.DIMI 32, ->lb1
    C.B.DIMI 32, ->lb2
    B.ARG NORM.normal
    B.IOR [a2],[]
    B.IOT t#1, last, ->t<4KB>

    FRET.STK [ra ~ ra], sp!, 8
    .size \name, .-\name
    .endm

    .macro TCMPS_KERNEL name, dtype, cmode
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
    B.IOT last, ->t<4KB>

    BSTART.TCMPS \dtype
    C.B.DIMI 31, ->lb0
    C.B.DIMI 32, ->lb1
    C.B.DIMI 32, ->lb2
    B.ARG VS
    B.DATR normal, \dtype, ZERO, cmode\cmode, rmode0
    B.IOR [a1],[]
    B.IOT t#1, last, ->t<4KB>

    BSTART.TSTORE UINT32
    C.B.DIMI 32, ->lb0
    C.B.DIMI 32, ->lb1
    C.B.DIMI 32, ->lb2
    B.ARG NORM.normal
    B.IOR [a2],[]
    B.IOT t#1, last, ->t<4KB>

    FRET.STK [ra ~ ra], sp!, 8
    .size \name, .-\name
    .endm

    TCMP_KERNEL linx_tcmp_s32_eq, INT32, 0
    TCMP_KERNEL linx_tcmp_s32_ne, INT32, 1
    TCMP_KERNEL linx_tcmp_s32_lt, INT32, 2
    TCMP_KERNEL linx_tcmp_s32_le, INT32, 3
    TCMP_KERNEL linx_tcmp_s32_gt, INT32, 4
    TCMP_KERNEL linx_tcmp_s32_ge, INT32, 5

    TCMP_KERNEL linx_tcmp_u32_lt, UINT32, 2
    TCMP_KERNEL linx_tcmp_s16_lt, INT16, 2
    TCMP_KERNEL linx_tcmp_u16_lt, UINT16, 2
    TCMP_KERNEL linx_tcmp_s8_lt, INT8, 2
    TCMP_KERNEL linx_tcmp_u8_lt, UINT8, 2
    TCMP_KERNEL linx_tcmp_f32_ne, FP32, 1
    TCMP_KERNEL linx_tcmp_f32_ge, FP32, 5
    TCMP_KERNEL linx_tcmp_f16_lt, FP16, 2

    TCMPS_KERNEL linx_tcmps_s32_lt, INT32, 2

    .section ".note.GNU-stack","",@progbits
