.text
v056_isa_forms:
    B.DIM sp, 129, ->lb1
    B.IOR [sp,sp,sp],[a0]
    B.IOT [], last ->u<1>

    .4byte 0x08831181
    BSTART.CUBE 3, FP32
    BSTART.FIXP 3, FP32
    TLOAD.NORM <LB0: R2+12, LB1: 13, LB2: R1, FP32, Max> [a1, a2, a3, a7], ->T<64KB>
    .4byte 0x08111181
    .4byte 0x08031181
    .4byte 0x08231181
    .4byte 0x08211181
    BSTART.VPAR VS16
    BSTART.VSEQ VS16
    BSTOP

    C.BSTART.MPAR
    C.BSTART.MSEQ
    C.BSTART.SYS
    C.BSTART.VPAR
    C.BSTART.VSEQ
    C.BSTOP

    c.ssrget 1, ->t
    .4byte 0x07f19181
    .4byte 0x07e19181
    FENTRY [ra ~ ra], sp!, 16
    FRET.STK [ra ~ ra], sp!, 16
    hl.casw.aqrlf [a1], a2, a3, ->a0
    hl.casd.aqrlf [a1], a2, a3, ->a0
