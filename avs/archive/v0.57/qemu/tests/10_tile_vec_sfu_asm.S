/* PTO ISA VEC/SFU execution through the unchanged TEPL binary carrier. */

    .text

/* Rejected dtype profiles. The ACR0 trap handler resumes at the TSTORE below,
 * which must observe the original source as the queue head. */

    .macro SFU_REJECT_USER name, resume, op, dtype
    .globl \name
    .type \name,@function
\name:
    FENTRY [ra ~ ra], sp!, 8

    ssrget 0x0033, ->a0
    BSTART.TLOAD \dtype
    B.DATR normal, \dtype, ZERO, cmode0, rmode0
    B.IOR [a0],[]
    B.IOT last, ->t<2KB>

    BSTART.\op \dtype
    B.IOT t#1, last, ->t<2KB>

    .globl \resume
\resume:
    ssrget 0x0034, ->a0
    BSTART.TSTORE \dtype
    B.DATR normal, \dtype, ZERO, cmode0, rmode0
    B.IOR [a0],[]
    B.IOT t#1, last, ->t<2KB>

    FRET.STK [ra ~ ra], sp!, 8
    .size \name, .-\name
    .endm

    SFU_REJECT_USER linx_sfu_reject_texp_fp16_user, \
                    linx_sfu_reject_texp_fp16_resume, TEXP, FP16
    SFU_REJECT_USER linx_sfu_reject_tlog_bf16_user, \
                    linx_sfu_reject_tlog_bf16_resume, TLOG, BF16

    .globl linx_sfu_reject_acr0_trap_handler
    .type linx_sfu_reject_acr0_trap_handler,@function
linx_sfu_reject_acr0_trap_handler:
    C.BSTART
    ssrget 0x0f02, ->a0
    ssrset a0, 0x0036
    addi zero, 0, ->a1
    ssrset a1, 0x0f00
    ssrget 0x0035, ->a0
    ssrset a0, 0x0f41
    ssrset a0, 0x0f43
    acre 0
    .size linx_sfu_reject_acr0_trap_handler, \
          .-linx_sfu_reject_acr0_trap_handler

/* PTO ISA SFU row/column broadcast and expand-arithmetic kernels. */


    .macro LOAD_FP32 reg, cols, rows, stride
    BSTART.TLOAD FP32
    C.B.DIMI \cols, ->lb0
    C.B.DIMI \rows, ->lb1
    C.B.DIMI \stride, ->lb2
    B.DATR normal, FP32, ZERO, cmode0, rmode0
    B.IOR [\reg],[]
    B.IOT last, ->t<4KB>
    .endm

    .macro STORE_FP32 reg
    BSTART.TSTORE FP32
    C.B.DIMI 8, ->lb0
    C.B.DIMI 4, ->lb1
    C.B.DIMI 8, ->lb2
    B.DATR normal, FP32, ZERO, cmode0, rmode0
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

/* PTO ISA SFU layout and padding kernels. */


    .macro TFILLPAD_KERNEL name, pad, emit_datr=1
    .globl \name
    .type \name,@function
\name:
    FENTRY [ra ~ ra], sp!, 8

    BSTART.TLOAD FP32
    C.B.DIMI 3, ->lb0
    C.B.DIMI 2, ->lb1
    C.B.DIMI 4, ->lb2
    B.DATR normal, FP32, ZERO, cmode0, rmode0
    B.IOR [a0],[]
    B.IOT last, ->t<512B>

    BSTART.TFILLPAD FP32
    C.B.DIMI 3, ->lb0
    C.B.DIMI 2, ->lb1
    C.B.DIMI 4, ->lb2
    .if \emit_datr
    B.DATR normal, FP32, \pad, cmode0, rmode0
    .endif
    B.IOT t#1, last, ->t<512B>

    BSTART.TSTORE FP32
    C.B.DIMI 4, ->lb0
    C.B.DIMI 32, ->lb1
    C.B.DIMI 4, ->lb2
    B.DATR normal, FP32, ZERO, cmode0, rmode0
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
    B.DATR normal, \dtype, ZERO, cmode0, rmode0
    B.IOR [a0],[]
    B.IOT last, ->t<512B>

    BSTART.TFILLPAD \dtype
    C.B.DIMI 3, ->lb0
    C.B.DIMI 2, ->lb1
    C.B.DIMI 4, ->lb2
    B.DATR normal, \dtype, \pad, cmode0, rmode0
    B.IOT t#1, last, ->t<512B>

    BSTART.TSTORE \dtype
    C.B.DIMI 4, ->lb0
    C.B.DIMI 128, ->lb1
    C.B.DIMI 4, ->lb2
    B.DATR normal, \dtype, ZERO, cmode0, rmode0
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
    B.DATR normal, FP32, ZERO, cmode0, rmode0
    B.IOR [a0],[]
    B.IOT last, ->t<512B>
    BSTART.TRESHAPE INT16
    C.B.DIMI 8, ->lb0
    C.B.DIMI 32, ->lb1
    C.B.DIMI 8, ->lb2
    B.IOT t#1, last, ->t<512B>
    BSTART.TSTORE INT16
    C.B.DIMI 8, ->lb0
    C.B.DIMI 32, ->lb1
    C.B.DIMI 8, ->lb2
    B.DATR normal, INT16, ZERO, cmode0, rmode0
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
    B.DATR normal, FP32, ZERO, cmode0, rmode0
    B.IOR [a0],[]
    B.IOT last, ->t<512B>
    BSTART.TLOAD FP32
    C.B.DIMI 2, ->lb0
    C.B.DIMI 2, ->lb1
    C.B.DIMI 4, ->lb2
    B.DATR normal, FP32, ZERO, cmode0, rmode0
    B.IOR [a1],[]
    B.IOT last, ->t<512B>
    BSTART.TCONCAT FP32
    C.B.DIMI 5, ->lb0
    C.B.DIMI 2, ->lb1
    C.B.DIMI 8, ->lb2
    B.IOT t#2, t#1, last, ->t<512B>
    BSTART.TSTORE FP32
    C.B.DIMI 8, ->lb0
    C.B.DIMI 16, ->lb1
    C.B.DIMI 8, ->lb2
    B.DATR normal, FP32, ZERO, cmode0, rmode0
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
    B.DATR normal, UINT8, ZERO, cmode0, rmode0
    B.IOR [a0],[]
    B.IOT last, ->t<512B>
    BSTART.TLOAD UINT32
    C.B.DIMI 8, ->lb0
    B.DATR normal, UINT32, ZERO, cmode0, rmode0
    B.IOR [a1],[]
    B.IOT last, ->t<512B>
    BSTART.TGATHERB UINT8
    C.B.DIMI 8, ->lb0
    B.IOT t#2, t#1, last, ->t<512B>
    BSTART.TSTORE UINT8
    C.B.DIMI 512, ->lb0
    B.DATR normal, UINT8, ZERO, cmode0, rmode0
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
    B.IOR [a0],[a1]
    B.IOT last, ->t<512B>
    BSTART.TSTORE INT32
    C.B.DIMI 128, ->lb0
    B.DATR normal, INT32, ZERO, cmode0, rmode0
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
    B.IOR [a0],[a1]
    B.IOT last, ->t<512B>
    BSTART.TSTORE INT32
    C.B.DIMI 4, ->lb0
    C.B.DIMI 32, ->lb1
    C.B.DIMI 4, ->lb2
    B.DATR normal, INT32, ZERO, cmode0, rmode0
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
    B.DATR normal, FP32, ZERO, cmode0, rmode0
    B.IOR [a0],[]
    B.IOT last, ->t<512B>
    BSTART.TEXTRACT FP32
    C.B.DIMI 3, ->lb0
    C.B.DIMI 2, ->lb1
    C.B.DIMI 4, ->lb2
    B.IOR [a1],[a2]
    B.IOT t#1, last, ->t<512B>
    BSTART.TSTORE FP32
    C.B.DIMI 4, ->lb0
    C.B.DIMI 32, ->lb1
    C.B.DIMI 4, ->lb2
    B.DATR normal, FP32, ZERO, cmode0, rmode0
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
    B.DATR normal, INT8, ZERO, cmode0, rmode0
    B.IOR [a0],[]
    B.IOT last, ->t<512B>
    BSTART.TLOAD FP32
    C.B.DIMI 1, ->lb0
    C.B.DIMI 3, ->lb1
    C.B.DIMI 1, ->lb2
    B.DATR normal, FP32, ZERO, cmode0, rmode0
    B.IOR [a1],[]
    B.IOT last, ->t<512B>
    BSTART.TLOAD FP32
    C.B.DIMI 1, ->lb0
    C.B.DIMI 3, ->lb1
    C.B.DIMI 1, ->lb2
    B.DATR normal, FP32, ZERO, cmode0, rmode0
    B.IOR [a2],[]
    B.IOT last, ->t<512B>
    BSTART.TDEQUANT FP32
    C.B.DIMI 4, ->lb0
    C.B.DIMI 3, ->lb1
    C.B.DIMI 4, ->lb2
    B.DATR normal, INT8, ZERO, cmode0, rmode0
    B.IOT t#3, t#2
    B.IOT t#1, last, ->t<512B>
    BSTART.TSTORE FP32
    C.B.DIMI 4, ->lb0
    C.B.DIMI 32, ->lb1
    C.B.DIMI 4, ->lb2
    B.DATR normal, FP32, ZERO, cmode0, rmode0
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
    B.DATR normal, INT32, ZERO, cmode0, rmode0
    B.IOR [a0],[]
    B.IOT last, ->t<512B>

    BSTART.TLOAD INT32
    C.B.DIMI 8, ->lb0
    C.B.DIMI 2, ->lb1
    C.B.DIMI 8, ->lb2
    B.DATR normal, INT32, ZERO, cmode0, rmode0
    B.IOR [a1],[]
    B.IOT last, ->t<512B>

    BSTART.\op INT32
    C.B.DIMI 8, ->lb0
    C.B.DIMI 2, ->lb1
    C.B.DIMI 8, ->lb2
    B.IOT t#1, t#2, ->t<512B>
    B.IOT last, ->t<512B>

    /* Descriptor order is dst1, dst0; dst0 is therefore the newest T. */
    BSTART.TSTORE INT32
    C.B.DIMI 8, ->lb0
    C.B.DIMI 16, ->lb1
    C.B.DIMI 8, ->lb2
    B.DATR normal, INT32, ZERO, cmode0, rmode0
    B.IOR [a2],[]
    B.IOT t#1, last, ->t<512B>

    BSTART.TSTORE INT32
    C.B.DIMI 8, ->lb0
    C.B.DIMI 16, ->lb1
    C.B.DIMI 8, ->lb2
    B.DATR normal, INT32, ZERO, cmode0, rmode0
    B.IOR [a3],[]
    B.IOT t#1, last, ->t<512B>

    FRET.STK [ra ~ ra], sp!, 8
    .size \name, .-\name
    .endm

    INTERLEAVE_KERNEL linx_tinterleave_s32, TINTERLEAVE
    INTERLEAVE_KERNEL linx_tdeinterleave_s32, TDEINTERLEAVE

/* PTO ISA SFU partial-valid binary kernels. */


    .macro TPART_KERNEL name, op
    .globl \name
    .type \name,@function
\name:
    FENTRY [ra ~ ra], sp!, 8

    BSTART.TLOAD FP32
    C.B.DIMI 4, ->lb0
    C.B.DIMI 3, ->lb1
    C.B.DIMI 4, ->lb2
    B.DATR normal, FP32, ZERO, cmode0, rmode0
    B.IOR [a0],[]
    B.IOT last, ->t<512B>

    BSTART.TLOAD FP32
    C.B.DIMI 2, ->lb0
    C.B.DIMI 2, ->lb1
    C.B.DIMI 4, ->lb2
    B.DATR normal, FP32, ZERO, cmode0, rmode0
    B.IOR [a1],[]
    B.IOT last, ->t<512B>

    BSTART.\op FP32
    C.B.DIMI 4, ->lb0
    C.B.DIMI 3, ->lb1
    C.B.DIMI 4, ->lb2
    B.IOT t#2, t#1, last, ->t<512B>

    BSTART.TSTORE FP32
    C.B.DIMI 4, ->lb0
    C.B.DIMI 32, ->lb1
    C.B.DIMI 4, ->lb2
    B.DATR normal, FP32, ZERO, cmode0, rmode0
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
    B.DATR normal, FP32, ZERO, cmode0, rmode0
    B.IOR [a0],[]
    B.IOT last, ->t<512B>

    BSTART.TLOAD FP32
    C.B.DIMI 8, ->lb0
    C.B.DIMI 2, ->lb1
    C.B.DIMI 8, ->lb2
    B.DATR normal, FP32, ZERO, cmode0, rmode0
    B.IOR [a1],[]
    B.IOT last, ->t<512B>

    BSTART.TLOAD UINT32
    C.B.DIMI 8, ->lb0
    C.B.DIMI 2, ->lb1
    C.B.DIMI 8, ->lb2
    B.DATR normal, UINT32, ZERO, cmode0, rmode0
    B.IOR [a2],[]
    B.IOT last, ->t<512B>

    BSTART.TLOAD UINT32
    C.B.DIMI 8, ->lb0
    C.B.DIMI 2, ->lb1
    C.B.DIMI 8, ->lb2
    B.DATR normal, UINT32, ZERO, cmode0, rmode0
    B.IOR [a3],[]
    B.IOT last, ->t<512B>

    BSTART.\op FP32
    C.B.DIMI 8, ->lb0
    C.B.DIMI 2, ->lb1
    C.B.DIMI 8, ->lb2
    B.IOT t#4, t#3, ->t<512B>
    B.IOT t#2, t#1, last, ->u<512B>

    BSTART.TSTORE FP32
    C.B.DIMI 8, ->lb0
    C.B.DIMI 16, ->lb1
    C.B.DIMI 8, ->lb2
    B.DATR normal, FP32, ZERO, cmode0, rmode0
    B.IOR [a4],[]
    B.IOT t#1, last, ->t<512B>

    BSTART.TSTORE UINT32
    C.B.DIMI 8, ->lb0
    C.B.DIMI 16, ->lb1
    C.B.DIMI 8, ->lb2
    B.DATR normal, UINT32, ZERO, cmode0, rmode0
    B.IOR [a5],[]
    B.IOT u#1, last, ->u<512B>

    FRET.STK [ra ~ ra], sp!, 8
    .size \name, .-\name
    .endm

    PART_ARG_KERNEL linx_tpartargmax_f32_u32, TPARTARGMAX
    PART_ARG_KERNEL linx_tpartargmin_f32_u32, TPARTARGMIN

/* PTO ISA TCMP mode carriers. The generic TEPL builtin does not expose
 * B.DATR.CMode, so these focused kernels provide L2/L3 coverage for all six
 * architectural comparison modes without changing the compiler API. */


    .macro TCMP_KERNEL name, dtype, cmode
    .globl \name
    .type \name,@function
\name:
    FENTRY [ra ~ ra], sp!, 8

    BSTART.TLOAD \dtype
    C.B.DIMI 32, ->lb0
    C.B.DIMI 32, ->lb1
    C.B.DIMI 32, ->lb2
    B.DATR normal, \dtype, ZERO, cmode0, rmode0
    B.IOR [a0],[]
    B.IOT last, ->t<4KB>

    BSTART.TLOAD \dtype
    C.B.DIMI 32, ->lb0
    C.B.DIMI 32, ->lb1
    C.B.DIMI 32, ->lb2
    B.DATR normal, \dtype, ZERO, cmode0, rmode0
    B.IOR [a1],[]
    B.IOT last, ->t<4KB>

    BSTART.TCMP \dtype
    C.B.DIMI 31, ->lb0
    C.B.DIMI 32, ->lb1
    C.B.DIMI 32, ->lb2
    B.DATR normal, \dtype, ZERO, cmode\cmode, rmode0
    B.IOT t#2, t#1, last, ->t<4KB>

    BSTART.TSTORE UINT32
    C.B.DIMI 32, ->lb0
    C.B.DIMI 32, ->lb1
    C.B.DIMI 32, ->lb2
    B.DATR normal, UINT32, ZERO, cmode0, rmode0
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
    B.DATR normal, \dtype, ZERO, cmode0, rmode0
    B.IOR [a0],[]
    B.IOT last, ->t<4KB>

    BSTART.TCMPS \dtype
    C.B.DIMI 31, ->lb0
    C.B.DIMI 32, ->lb1
    C.B.DIMI 32, ->lb2
    B.DATR normal, \dtype, ZERO, cmode\cmode, rmode0
    B.IOR [a1],[]
    B.IOT t#1, last, ->t<4KB>

    BSTART.TSTORE UINT32
    C.B.DIMI 32, ->lb0
    C.B.DIMI 32, ->lb1
    C.B.DIMI 32, ->lb2
    B.DATR normal, UINT32, ZERO, cmode0, rmode0
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

/* Exact-value carriers for signed narrow VEC arithmetic. */


    .macro TILE_BINARY name, opcode, dtype, footprint
    .globl \name
    .type \name,@function
\name:
    FENTRY [ra ~ ra], sp!, 8

    BSTART.TLOAD \dtype
    C.B.DIMI 32, ->lb0
    C.B.DIMI 32, ->lb1
    C.B.DIMI 32, ->lb2
    B.DATR normal, \dtype, ZERO, cmode0, rmode0
    B.IOR [a0],[]
    B.IOT last, ->t<\footprint>

    BSTART.TLOAD \dtype
    C.B.DIMI 32, ->lb0
    C.B.DIMI 32, ->lb1
    C.B.DIMI 32, ->lb2
    B.DATR normal, \dtype, ZERO, cmode0, rmode0
    B.IOR [a1],[]
    B.IOT last, ->t<\footprint>

    BSTART.\opcode \dtype
    C.B.DIMI 32, ->lb0
    C.B.DIMI 32, ->lb1
    C.B.DIMI 32, ->lb2
    B.IOT t#2, t#1, last, ->t<\footprint>

    BSTART.TSTORE \dtype
    C.B.DIMI 32, ->lb0
    C.B.DIMI 32, ->lb1
    C.B.DIMI 32, ->lb2
    B.DATR normal, \dtype, ZERO, cmode0, rmode0
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
    B.DATR normal, \dtype, ZERO, cmode0, rmode0
    B.IOR [a0],[]
    B.IOT last, ->t<\footprint>

    BSTART.\opcode \dtype
    C.B.DIMI 32, ->lb0
    C.B.DIMI 32, ->lb1
    C.B.DIMI 32, ->lb2
    B.IOT t#1, last, ->t<\footprint>

    BSTART.TSTORE \dtype
    C.B.DIMI 32, ->lb0
    C.B.DIMI 32, ->lb1
    C.B.DIMI 32, ->lb2
    B.DATR normal, \dtype, ZERO, cmode0, rmode0
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

    .macro TILE_CONVERT name, src_dtype, src_footprint, dst_dtype, dst_footprint
    .globl \name
    .type \name,@function
\name:
    FENTRY [ra ~ ra], sp!, 8

    BSTART.TLOAD \src_dtype
    C.B.DIMI 32, ->lb0
    C.B.DIMI 32, ->lb1
    C.B.DIMI 32, ->lb2
    B.DATR normal, \src_dtype, ZERO, cmode0, rmode0
    B.IOR [a0],[]
    B.IOT last, ->t<\src_footprint>

    BSTART.TCVT \dst_dtype
    C.B.DIMI 32, ->lb0
    C.B.DIMI 32, ->lb1
    C.B.DIMI 32, ->lb2
    B.IOT t#1, last, ->t<\dst_footprint>

    BSTART.TSTORE \dst_dtype
    C.B.DIMI 32, ->lb0
    C.B.DIMI 32, ->lb1
    C.B.DIMI 32, ->lb2
    B.DATR normal, \dst_dtype, ZERO, cmode0, rmode0
    B.IOR [a1],[]
    B.IOT t#1, last, ->t<\dst_footprint>

    FRET.STK [ra ~ ra], sp!, 8
    .size \name, .-\name
    .endm

    TILE_CONVERT linx_tcvt_f32_f16, FP32, 4KB, FP16, 2KB
    TILE_CONVERT linx_tcvt_bf16_f32, BF16, 2KB, FP32, 4KB

    TILE_BINARY linx_trem_s32, TREM, INT32, 4KB

    .globl linx_trems_s32
    .type linx_trems_s32,@function
linx_trems_s32:
    FENTRY [ra ~ ra], sp!, 8

    BSTART.TLOAD INT32
    C.B.DIMI 32, ->lb0
    C.B.DIMI 32, ->lb1
    C.B.DIMI 32, ->lb2
    B.DATR normal, INT32, ZERO, cmode0, rmode0
    B.IOR [a0],[]
    B.IOT last, ->t<4KB>

    BSTART.TREMS INT32
    C.B.DIMI 32, ->lb0
    C.B.DIMI 32, ->lb1
    C.B.DIMI 32, ->lb2
    B.IOR [a1],[]
    B.IOT t#1, last, ->t<4KB>

    BSTART.TSTORE INT32
    C.B.DIMI 32, ->lb0
    C.B.DIMI 32, ->lb1
    C.B.DIMI 32, ->lb2
    B.DATR normal, INT32, ZERO, cmode0, rmode0
    B.IOR [a2],[]
    B.IOT t#1, last, ->t<4KB>

    FRET.STK [ra ~ ra], sp!, 8
    .size linx_trems_s32, .-linx_trems_s32

/* PTO ISA SFU product and index-reduction kernels. */


    .macro REDUCE_KERNEL name, op, src_dtype, dst_dtype, dst_cols, dst_rows, dst_stride
    .globl \name
    .type \name,@function
\name:
    FENTRY [ra ~ ra], sp!, 8

    BSTART.TLOAD \src_dtype
    C.B.DIMI 8, ->lb0
    C.B.DIMI 8, ->lb1
    C.B.DIMI 8, ->lb2
    B.DATR normal, \src_dtype, ZERO, cmode0, rmode0
    B.IOR [a0],[]
    B.IOT last, ->t<4KB>

    BSTART.\op \src_dtype
    C.B.DIMI 8, ->lb0
    C.B.DIMI 8, ->lb1
    C.B.DIMI 8, ->lb2
    B.IOT t#1, last, ->t<4KB>

    BSTART.TSTORE \dst_dtype
    C.B.DIMI \dst_cols, ->lb0
    C.B.DIMI \dst_rows, ->lb1
    C.B.DIMI \dst_stride, ->lb2
    B.DATR normal, \dst_dtype, ZERO, cmode0, rmode0
    B.IOR [a1],[]
    B.IOT t#1, last, ->t<4KB>

    FRET.STK [ra ~ ra], sp!, 8
    .size \name, .-\name
    .endm

    REDUCE_KERNEL linx_trowprod_s32, TROWPROD, INT32, INT32, 1, 8, 1
    REDUCE_KERNEL linx_tcolprod_s32, TCOLPROD, INT32, INT32, 8, 1, 8
    REDUCE_KERNEL linx_trowargmax_f32, TROWARGMAX, FP32, UINT32, 1, 8, 1
    REDUCE_KERNEL linx_trowargmin_f32, TROWARGMIN, FP32, UINT32, 1, 8, 1
    REDUCE_KERNEL linx_tcolargmax_f32, TCOLARGMAX, FP32, UINT32, 8, 1, 8
    REDUCE_KERNEL linx_tcolargmin_f32, TCOLARGMIN, FP32, UINT32, 8, 1, 8

/* PTO ISA VEC packed-predicate selection kernels. */


    .globl linx_tsel_s32
    .type linx_tsel_s32,@function
linx_tsel_s32:
    FENTRY [ra ~ ra], sp!, 8

    BSTART.TLOAD UINT32
    C.B.DIMI 2, ->lb0
    C.B.DIMI 16, ->lb1
    C.B.DIMI 2, ->lb2
    B.DATR normal, UINT32, ZERO, cmode0, rmode0
    B.IOR [a0],[]
    B.IOT last, ->t<4KB>

    BSTART.TLOAD INT32
    C.B.DIMI 64, ->lb0
    C.B.DIMI 16, ->lb1
    C.B.DIMI 64, ->lb2
    B.DATR normal, INT32, ZERO, cmode0, rmode0
    B.IOR [a1],[]
    B.IOT last, ->t<4KB>

    BSTART.TLOAD INT32
    C.B.DIMI 64, ->lb0
    C.B.DIMI 16, ->lb1
    C.B.DIMI 64, ->lb2
    B.DATR normal, INT32, ZERO, cmode0, rmode0
    B.IOR [a2],[]
    B.IOT last, ->t<4KB>

    BSTART.TSEL INT32
    C.B.DIMI 64, ->lb0
    C.B.DIMI 16, ->lb1
    C.B.DIMI 64, ->lb2
    B.IOT t#3, t#2
    B.IOT t#1, last, ->t<4KB>

    BSTART.TSTORE INT32
    C.B.DIMI 64, ->lb0
    C.B.DIMI 16, ->lb1
    C.B.DIMI 64, ->lb2
    B.DATR normal, INT32, ZERO, cmode0, rmode0
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
    B.DATR normal, UINT32, ZERO, cmode0, rmode0
    B.IOR [a0],[]
    B.IOT last, ->t<4KB>

    BSTART.TLOAD INT32
    C.B.DIMI 64, ->lb0
    C.B.DIMI 16, ->lb1
    C.B.DIMI 64, ->lb2
    B.DATR normal, INT32, ZERO, cmode0, rmode0
    B.IOR [a1],[]
    B.IOT last, ->t<4KB>

    BSTART.TSELS INT32
    C.B.DIMI 64, ->lb0
    C.B.DIMI 16, ->lb1
    C.B.DIMI 64, ->lb2
    B.IOR [a2],[]
    B.IOT t#2, t#1, last, ->t<4KB>

    BSTART.TSTORE INT32
    C.B.DIMI 64, ->lb0
    C.B.DIMI 16, ->lb1
    C.B.DIMI 64, ->lb2
    B.DATR normal, INT32, ZERO, cmode0, rmode0
    B.IOR [a3],[]
    B.IOT t#1, last, ->t<4KB>

    FRET.STK [ra ~ ra], sp!, 8
    .size linx_tsels_s32, .-linx_tsels_s32

/* Rectangular Tile shape metadata carrier. */


    .globl linx_tadd_rect_s32
    .type linx_tadd_rect_s32,@function
linx_tadd_rect_s32:
    FENTRY [ra ~ ra], sp!, 8

    BSTART.TLOAD INT32
    C.B.DIMI 3, ->lb0
    C.B.DIMI 2, ->lb1
    C.B.DIMI 4, ->lb2
    B.DATR normal, INT32, ZERO, cmode0, rmode0
    B.IOR [a0],[]
    B.IOT last, ->t<4KB>

    BSTART.TLOAD INT32
    C.B.DIMI 3, ->lb0
    C.B.DIMI 2, ->lb1
    C.B.DIMI 4, ->lb2
    B.DATR normal, INT32, ZERO, cmode0, rmode0
    B.IOR [a1],[]
    B.IOT last, ->t<4KB>

    BSTART.TADD INT32
    C.B.DIMI 3, ->lb0
    C.B.DIMI 2, ->lb1
    C.B.DIMI 4, ->lb2
    B.IOT t#2, t#1, last, ->t<4KB>

    BSTART.TSTORE INT32
    C.B.DIMI 3, ->lb0
    C.B.DIMI 2, ->lb1
    C.B.DIMI 4, ->lb2
    B.DATR normal, INT32, ZERO, cmode0, rmode0
    B.IOR [a2],[]
    B.IOT t#1, last, ->t<4KB>

    FRET.STK [ra ~ ra], sp!, 8
    .size linx_tadd_rect_s32, .-linx_tadd_rect_s32


    .section ".note.GNU-stack","",@progbits
