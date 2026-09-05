    .text
    .globl linx_v0586_mgather_add
    .type linx_v0586_mgather_add,@function
linx_v0586_mgather_add:
    FENTRY [ra ~ ra], sp!, 8
    BSTART.TLOAD U32
    C.B.DIMI 32, ->lb0
    C.B.DIMI 1, ->lb1
    B.IOR [a1, a5]
    B.IOT mask=0001, last, ->t<128B>

    BSTART.TLOAD U32
    C.B.DIMI 32, ->lb0
    C.B.DIMI 1, ->lb1
    B.IOR [a2, a5]
    B.IOT mask=0001, last, ->u<128B>

    BSTART.MGATHER.ADD U32
    C.B.DIMI 32, ->lb0
    C.B.DIMI 1, ->lb1
    B.IOR [a0]
    B.IOT t#1, u#1, mask=0001, last, ->t<128B>

    BSTART.TSTORE U32
    C.B.DIMI 32, ->lb0
    C.B.DIMI 1, ->lb1
    B.IOR [a3, a5]
    B.IOT t#1, mask=0001, last
    FRET.STK [ra ~ ra], sp!, 8
    .size linx_v0586_mgather_add, .-linx_v0586_mgather_add

    .globl linx_v0586_mscatter_popc
    .type linx_v0586_mscatter_popc,@function
linx_v0586_mscatter_popc:
    FENTRY [ra ~ ra], sp!, 8
    BSTART.TLOAD U32
    C.B.DIMI 32, ->lb0
    C.B.DIMI 1, ->lb1
    B.IOR [a1, a2]
    B.IOT mask=0001, last, ->t<128B>

    BSTART.MSCATTER.POPC U32
    C.B.DIMI 32, ->lb0
    C.B.DIMI 1, ->lb1
    B.IOR [a0]
    B.IOT t#1, mask=0001, last
    FRET.STK [ra ~ ra], sp!, 8
    .size linx_v0586_mscatter_popc, .-linx_v0586_mscatter_popc
