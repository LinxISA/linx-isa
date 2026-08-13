    .text
    .globl linx_v058_tlsu_copy
    .type linx_v058_tlsu_copy,@function
linx_v058_tlsu_copy:
    FENTRY [ra ~ ra], sp!, 8
    BSTART.TLOAD FP32
    C.B.DIMI 32, ->lb0
    C.B.DIMI 32, ->lb1
    B.IOR [a0, a2]
    B.IOT mask=1111, last, ->t<4KB>

    BSTART.TSTORE FP32
    C.B.DIMI 32, ->lb0
    C.B.DIMI 32, ->lb1
    B.IOR [a1, a2]
    B.IOT t#1, mask=1111, last
    FRET.STK [ra ~ ra], sp!, 8
    .size linx_v058_tlsu_copy, .-linx_v058_tlsu_copy
