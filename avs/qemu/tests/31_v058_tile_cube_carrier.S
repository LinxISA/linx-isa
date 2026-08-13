    .text
    .globl linx_v058_cube_matmul
    .type linx_v058_cube_matmul,@function
linx_v058_cube_matmul:
    FENTRY [ra ~ ra], sp!, 8
    BSTART.TLOAD S32
    C.B.DIMI 4, ->lb0
    C.B.DIMI 4, ->lb1
    B.IOR [a0, a3]
    B.IOT mask=1111, last, ->t<4KB>

    BSTART.TLOAD S32
    C.B.DIMI 4, ->lb0
    C.B.DIMI 4, ->lb1
    B.IOR [a1, a3]
    B.IOT mask=1111, last, ->t<4KB>

    BSTART.TMATMUL S32
    C.B.DIMI 4, ->lb0
    C.B.DIMI 4, ->lb1
    C.B.DIMI 4, ->lb2
    B.IOT t#2, t#1, mask=1111, last, ->m<128B>

    BSTART.TSTORE S32
    C.B.DIMI 4, ->lb0
    C.B.DIMI 4, ->lb1
    B.IOR [a2, a3]
    B.IOT m#1, mask=1111, last
    FRET.STK [ra ~ ra], sp!, 8
    .size linx_v058_cube_matmul, .-linx_v058_cube_matmul
