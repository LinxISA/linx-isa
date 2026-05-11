    .text
v056_isa_forms:
    B.ARG NORM.normal
    B.ARG ND2ZN.normal, FP16, Null
    B.HINT {BR.likely, TEMP.warm, 129}
    B.DIM sp, 129, ->lb1
    B.IOR [sp,sp,sp],[a0]
    B.IOT [], last ->u<1>

    BSTART.ACCCVT FP32
    BSTART.CUBE 3, FP32
    BSTART.FIXP 3, FP32
    BSTART.TLOAD FP32
    BSTART.TMATMUL FP32
    BSTART.TMATMUL.ACC FP32
    BSTART.TMOV FP32
    BSTART.TSTORE FP32
    BSTART.VPAR VS16
    BSTART.VSEQ VS16
    BSTOP

    C.BSTART.MPAR
    C.BSTART.MSEQ
    C.BSTART.SYS
    C.BSTART.VPAR
    C.BSTART.VSEQ
    C.BSTOP

    c.ssrget GP, ->t
    ERCOV [sp, sp, sp]
    ESAVE [sp, sp, sp]
    FENTRY [sp ~ sp], sp!, 128
    FRET.STK [sp ~ sp], sp!, 128
    hl.casw.aqrlf [a1, 0], a2, a3, ->a0
    hl.casd.aqrlf [a1, 0], a2, a3, ->a0
