.text
v0585_isa_forms:
    B.CATR trap, atomic, aqrl, far, dr
    B.DATR ND2NZ.normal, FP16, Max, cmode5, rmode6, sat, canonicalize
    B.FPATR 1, 2, 3, 1, 0, 1, 1, 1, 1, 1
    B.IOT t#1, mask=1111, last, ->u<1KB>
    BSTART.TEPL 0, 1, FP16
    BSTART.SFU TPERMUTE, FP16
    BSTART.SFU TSORT, FP16
    BSTART.CALL .Lcall_target, .Lcall_return, ->ra
    BSTART.ICALL .Licall_return, ->ra
    FENTRY [ra ~ ra], sp!, 16
    FRET.STK [ra ~ ra], sp!, 16
    L.BSTOP

.Lcall_target:
    C.BSTOP
.Lcall_return:
    C.BSTOP
.Licall_return:
    C.BSTOP
