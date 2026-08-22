    .text
    .globl linx_v0583_vec_add
    .type linx_v0583_vec_add,@function
linx_v0583_vec_add:
    FENTRY [ra ~ ra], sp!, 8
    BSTART.TLOAD FP32
    C.B.DIMI 32, ->lb0
    C.B.DIMI 32, ->lb1
    B.IOR [a0, a3]
    B.IOT mask=0001, last, ->t<4KB>

    BSTART.TLOAD FP32
    C.B.DIMI 32, ->lb0
    C.B.DIMI 32, ->lb1
    B.IOR [a1, a3]
    B.IOT mask=0001, last, ->t<4KB>

    BSTART.VEC TADD, FP32
    C.B.DIMI 32, ->lb0
    C.B.DIMI 32, ->lb1
    B.IOT t#2, t#1, mask=0001, last, ->t<4KB>

    BSTART.TSTORE FP32
    C.B.DIMI 32, ->lb0
    C.B.DIMI 32, ->lb1
    B.IOR [a2, a3]
    B.IOT t#1, mask=0001, last
    FRET.STK [ra ~ ra], sp!, 8
    .size linx_v0583_vec_add, .-linx_v0583_vec_add
