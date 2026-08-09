	.file	"pto_tmatmul_acc.cpp"
	.text
	.globl	pto_tmatmul_acc_i32_8x8         #  -- Begin function pto_tmatmul_acc_i32_8x8
	.p2align	1
	.type	pto_tmatmul_acc_i32_8x8,@function
pto_tmatmul_acc_i32_8x8:                #  @pto_tmatmul_acc_i32_8x8
#  %bb.0:
FENTRY	[ra ~ ra], sp!, 8
#  %bb.1:
C.BSTART.STD
c.movr	zero,	->a3
c.movi	8,	->a4
#  %bb.3:
BSTART.TLOAD	INT32
B.DIM	a4, 0, ->lb0
B.DIM	a4, 0, ->lb1
B.DIM	a4, 0, ->lb2
B.IOR	[a0,a3],[]
B.IOT	last, ->t<4KB>
#  %bb.4:
BSTART.TLOAD	INT32
B.DIM	a4, 0, ->lb0
B.DIM	a4, 0, ->lb1
B.DIM	a4, 0, ->lb2
B.IOR	[a1,a3],[]
B.IOT	last, ->t<4KB>
#  %bb.5:
BSTART.TMATMUL	INT32
C.B.DIMI	8, 	->lb0
C.B.DIMI	8, 	->lb1
C.B.DIMI	8, 	->lb2
B.IOT	t#2.reuse, t#1.reuse, last
#  %bb.8:
BSTART.ACCCVT	INT32
B.IOT	last, ->m<4KB>
#  %bb.6:
BSTART.TMATMUL.ACC	INT32
C.B.DIMI	8, 	->lb0
C.B.DIMI	8, 	->lb1
C.B.DIMI	8, 	->lb2
B.IOT	t#2, t#1, last
#  %bb.9:
BSTART.ACCCVT	INT32
B.IOT	last, ->m<4KB>
#  %bb.7:
BSTART.TSTORE	INT32
B.DIM	a4, 0, ->lb0
B.DIM	a4, 0, ->lb1
B.DIM	a4, 0, ->lb2
B.IOR	[a2,a3],[]
B.IOT	m#1, last
#  %bb.2:
FRET.STK	[ra ~ ra], sp!, 8
.Lfunc_end0:
	.size	pto_tmatmul_acc_i32_8x8, .Lfunc_end0-pto_tmatmul_acc_i32_8x8
                                        #  -- End function
	.ident	"clang version 23.0.0git (https://github.com/LinxISA/llvm-project.git 487db9698c9c748de9afe33aa160c6a52be961ab)"
	.section	".note.GNU-stack","",@progbits
	.addrsig
