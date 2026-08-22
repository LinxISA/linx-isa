    .text
    .globl linx_v0583_tlsu_copy
    .type linx_v0583_tlsu_copy,@function
linx_v0583_tlsu_copy:
    FENTRY [ra ~ ra], sp!, 8
    BSTART.TLOAD S32
    C.B.DIMI 32, ->lb0
    C.B.DIMI 32, ->lb1
    B.IOR [a0, a2]
    B.IOT mask=0001, last, ->t<4KB>

    BSTART.TSTORE S32
    C.B.DIMI 32, ->lb0
    C.B.DIMI 32, ->lb1
    B.IOR [a1, a2]
    B.IOT t#1, mask=0001, last
    FRET.STK [ra ~ ra], sp!, 8
    .size linx_v0583_tlsu_copy, .-linx_v0583_tlsu_copy
