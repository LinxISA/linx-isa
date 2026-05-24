.text
v056_isa_forms:
    B.ARG NORM.normal
    B.DIM sp, 129, ->lb1
    B.IOR [sp,sp,sp],[a0]
    BSTART.ACCCVT FP32
    BSTART.CUBE 3, FP32
    BSTART.FIXP 3, FP32
    BSTART.TLOAD FP32
    BSTART.TSTORE FP32
    BSTART.TMATMUL FP16
    BSTART.TMATMUL.ACC FP16
    BSTART.TMOV FP32
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
    ERCOV [a0, a1, a2]
    ESAVE [a0, a1, a2]
    FENTRY [ra ~ ra], sp!, 16
    FRET.STK [ra ~ ra], sp!, 16
    hl.casw.aqrlf [a1], a2, a3, ->a0
    hl.casd.aqrlf [a1], a2, a3, ->a0
