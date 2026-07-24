/* v0.57 TEPL product and index-reduction kernels. */

    .text

    .macro REDUCE_KERNEL name, op, src_dtype, dst_dtype, dst_cols, dst_rows, dst_stride
    .globl \name
    .type \name,@function
\name:
    FENTRY [ra ~ ra], sp!, 8

    BSTART.TLOAD \src_dtype
    C.B.DIMI 8, ->lb0
    C.B.DIMI 8, ->lb1
    C.B.DIMI 8, ->lb2
    B.ARG NORM.normal
    B.IOR [a0],[]
    B.IOT last, ->t<4KB>

    BSTART.\op \src_dtype
    C.B.DIMI 8, ->lb0
    C.B.DIMI 8, ->lb1
    C.B.DIMI 8, ->lb2
    B.ARG VV
    B.IOT t#1, last, ->t<4KB>

    BSTART.TSTORE \dst_dtype
    C.B.DIMI \dst_cols, ->lb0
    C.B.DIMI \dst_rows, ->lb1
    C.B.DIMI \dst_stride, ->lb2
    B.ARG NORM.normal
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

    .section ".note.GNU-stack","",@progbits
