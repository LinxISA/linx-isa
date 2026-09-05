    .text
    .globl linx_v0586_timg2col
    .type linx_v0586_timg2col,@function
linx_v0586_timg2col:
    FENTRY [ra ~ ra], sp!, 8
    # LLVM 3d79447f does not yet parse BSTART.TIMG2COL. Encode the exact
    # PTO 0.58.6 U32 word (DataType=25, match=0x01c11181) until it does.
    .4byte 0xc9c11181
    B.DATR ND2M16, DTYPE_NONE, Zero
    C.B.DIMI 8, ->lb0
    C.B.DIMI 4, ->lb1
    C.B.DIMI 8, ->lb2
    B.IOR [a0, zero, zero]
    B.IOR [a2, a3, a4]
    B.IOT mask=1111, last, ->m<512B>

    BSTART.TSTORE U32
    B.DATR M162ND, DTYPE_NONE, Null
    C.B.DIMI 8, ->lb0
    C.B.DIMI 4, ->lb1
    B.IOR [a1, a5]
    B.IOT m#1, mask=0001, last
    FRET.STK [ra ~ ra], sp!, 8
    .size linx_v0586_timg2col, .-linx_v0586_timg2col
