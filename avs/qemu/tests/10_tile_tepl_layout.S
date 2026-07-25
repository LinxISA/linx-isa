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

    .globl linx_treshape_bytes
    .type linx_treshape_bytes,@function
linx_treshape_bytes:
    FENTRY [ra ~ ra], sp!, 8
    BSTART.TLOAD FP32
    C.B.DIMI 4, ->lb0
    C.B.DIMI 32, ->lb1
    C.B.DIMI 4, ->lb2
    B.ARG NORM.normal
    B.IOR [a0],[]
    B.IOT last, ->t<512B>
    BSTART.TRESHAPE INT16
    C.B.DIMI 8, ->lb0
    C.B.DIMI 32, ->lb1
    C.B.DIMI 8, ->lb2
    B.ARG VV
    B.IOT t#1, last, ->t<512B>
    BSTART.TSTORE INT16
    C.B.DIMI 8, ->lb0
    C.B.DIMI 32, ->lb1
    C.B.DIMI 8, ->lb2
    B.ARG NORM.normal
    B.IOR [a1],[]
    B.IOT t#1, last, ->t<512B>
    FRET.STK [ra ~ ra], sp!, 8
    .size linx_treshape_bytes, .-linx_treshape_bytes

    .globl linx_tconcat_f32
    .type linx_tconcat_f32,@function
linx_tconcat_f32:
    FENTRY [ra ~ ra], sp!, 8
    BSTART.TLOAD FP32
    C.B.DIMI 3, ->lb0
    C.B.DIMI 2, ->lb1
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
    BSTART.TCONCAT FP32
    C.B.DIMI 5, ->lb0
    C.B.DIMI 2, ->lb1
    C.B.DIMI 8, ->lb2
    B.ARG VV
    B.IOT t#2, t#1, last, ->t<512B>
    BSTART.TSTORE FP32
    C.B.DIMI 8, ->lb0
    C.B.DIMI 16, ->lb1
    C.B.DIMI 8, ->lb2
    B.ARG NORM.normal
    B.IOR [a2],[]
    B.IOT t#1, last, ->t<512B>
    FRET.STK [ra ~ ra], sp!, 8
    .size linx_tconcat_f32, .-linx_tconcat_f32

    .globl linx_tgatherb_u8
    .type linx_tgatherb_u8,@function
linx_tgatherb_u8:
    FENTRY [ra ~ ra], sp!, 8
    BSTART.TLOAD UINT8
    C.B.DIMI 512, ->lb0
    B.ARG NORM.normal
    B.IOR [a0],[]
    B.IOT last, ->t<512B>
    BSTART.TLOAD UINT32
    C.B.DIMI 8, ->lb0
    B.ARG NORM.normal
    B.IOR [a1],[]
    B.IOT last, ->t<512B>
    BSTART.TGATHERB UINT8
    C.B.DIMI 8, ->lb0
    B.ARG VV
    B.IOT t#2, t#1, last, ->t<512B>
    BSTART.TSTORE UINT8
    C.B.DIMI 512, ->lb0
    B.ARG NORM.normal
    B.IOR [a2],[]
    B.IOT t#1, last, ->t<512B>
    FRET.STK [ra ~ ra], sp!, 8
    .size linx_tgatherb_u8, .-linx_tgatherb_u8

    .globl linx_tci_s32
    .type linx_tci_s32,@function
linx_tci_s32:
    FENTRY [ra ~ ra], sp!, 8
    BSTART.TCI INT32
    C.B.DIMI 8, ->lb0
    B.ARG VS
    B.IOR [a0],[a1]
    B.IOT last, ->t<512B>
    BSTART.TSTORE INT32
    C.B.DIMI 128, ->lb0
    B.ARG NORM.normal
    B.IOR [a2],[]
    B.IOT t#1, last, ->t<512B>
    FRET.STK [ra ~ ra], sp!, 8
    .size linx_tci_s32, .-linx_tci_s32

    .globl linx_ttri_s32
    .type linx_ttri_s32,@function
linx_ttri_s32:
    FENTRY [ra ~ ra], sp!, 8
    BSTART.TTRI INT32
    C.B.DIMI 4, ->lb0
    C.B.DIMI 4, ->lb1
    C.B.DIMI 4, ->lb2
    B.ARG VS
    B.IOR [a0],[a1]
    B.IOT last, ->t<512B>
    BSTART.TSTORE INT32
    C.B.DIMI 4, ->lb0
    C.B.DIMI 32, ->lb1
    C.B.DIMI 4, ->lb2
    B.ARG NORM.normal
    B.IOR [a2],[]
    B.IOT t#1, last, ->t<512B>
    FRET.STK [ra ~ ra], sp!, 8
    .size linx_ttri_s32, .-linx_ttri_s32

    .globl linx_textract_f32
    .type linx_textract_f32,@function
linx_textract_f32:
    FENTRY [ra ~ ra], sp!, 8
    BSTART.TLOAD FP32
    C.B.DIMI 8, ->lb0
    C.B.DIMI 4, ->lb1
    C.B.DIMI 8, ->lb2
    B.ARG NORM.normal
    B.IOR [a0],[]
    B.IOT last, ->t<512B>
    BSTART.TEXTRACT FP32
    C.B.DIMI 3, ->lb0
    C.B.DIMI 2, ->lb1
    C.B.DIMI 4, ->lb2
    B.ARG VS
    B.IOR [a1],[a2]
    B.IOT t#1, last, ->t<512B>
    BSTART.TSTORE FP32
    C.B.DIMI 4, ->lb0
    C.B.DIMI 32, ->lb1
    C.B.DIMI 4, ->lb2
    B.ARG NORM.normal
    B.IOR [a3],[]
    B.IOT t#1, last, ->t<512B>
    FRET.STK [ra ~ ra], sp!, 8
    .size linx_textract_f32, .-linx_textract_f32

    .globl linx_tdequant_s8_f32
    .type linx_tdequant_s8_f32,@function
linx_tdequant_s8_f32:
    FENTRY [ra ~ ra], sp!, 8
    BSTART.TLOAD INT8
    C.B.DIMI 4, ->lb0
    C.B.DIMI 3, ->lb1
    C.B.DIMI 4, ->lb2
    B.ARG NORM.normal
    B.IOR [a0],[]
    B.IOT last, ->t<512B>
    BSTART.TLOAD FP32
    C.B.DIMI 1, ->lb0
    C.B.DIMI 3, ->lb1
    C.B.DIMI 1, ->lb2
    B.ARG NORM.normal
    B.IOR [a1],[]
    B.IOT last, ->t<512B>
    BSTART.TLOAD FP32
    C.B.DIMI 1, ->lb0
    C.B.DIMI 3, ->lb1
    C.B.DIMI 1, ->lb2
    B.ARG NORM.normal
    B.IOR [a2],[]
    B.IOT last, ->t<512B>
    BSTART.TDEQUANT FP32
    C.B.DIMI 4, ->lb0
    C.B.DIMI 3, ->lb1
    C.B.DIMI 4, ->lb2
    B.ARG VV
    B.DATR normal, INT8, ZERO, cmode0, rmode0
    B.IOT t#3, t#2
    B.IOT t#1, last, ->t<512B>
    BSTART.TSTORE FP32
    C.B.DIMI 4, ->lb0
    C.B.DIMI 32, ->lb1
    C.B.DIMI 4, ->lb2
    B.ARG NORM.normal
    B.IOR [a3],[]
    B.IOT t#1, last, ->t<512B>
    FRET.STK [ra ~ ra], sp!, 8
    .size linx_tdequant_s8_f32, .-linx_tdequant_s8_f32

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
