    .text
    .globl linx_v0583_cube_matmul
    .type linx_v0583_cube_matmul,@function
linx_v0583_cube_matmul:
    FENTRY [ra ~ ra], sp!, 8
    BSTART.TLOAD S32
    B.DATR ND2M16, DTYPE_NONE, Null
    C.B.DIMI 4, ->lb0
    C.B.DIMI 4, ->lb1
    B.IOR [a0, a3]
    B.IOT mask=0001, last, ->m<128B>

    BSTART.TLOAD S32
    B.DATR ND2N8, DTYPE_NONE, Null
    C.B.DIMI 4, ->lb0
    C.B.DIMI 4, ->lb1
    B.IOR [a1, a3]
    B.IOT mask=0001, last, ->n<128B>

    BSTART.TMATMUL S32
    B.FPATR 0, 0, 0, 0, 0, 0, 0, 0, 0
    C.B.DIMI 4, ->lb0
    C.B.DIMI 4, ->lb1
    C.B.DIMI 4, ->lb2
    B.IOT m#1, n#1, mask=0001, last, ->m<128B>

    BSTART.TSTORE S32
    B.DATR M162ND, DTYPE_NONE, Null
    C.B.DIMI 4, ->lb0
    C.B.DIMI 4, ->lb1
    B.IOR [a2, a3]
    B.IOT m#1, mask=0001, last
    FRET.STK [ra ~ ra], sp!, 8
    .size linx_v0583_cube_matmul, .-linx_v0583_cube_matmul
