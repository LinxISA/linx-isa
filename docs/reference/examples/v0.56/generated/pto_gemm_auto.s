	.file	"pto_gemm_auto.cpp"
	.text
	.globl	pto_gemm_auto_i32               #  -- Begin function pto_gemm_auto_i32
	.p2align	1
	.type	pto_gemm_auto_i32,@function
pto_gemm_auto_i32:                      #  @pto_gemm_auto_i32
#  %bb.0:
FENTRY	[ra ~ ra], sp!, 16
#  %bb.2:
BSTART	CALL, _ZN3pto4linx9auto_mode15gemm_kernel_i32EPKiS3_Pi, ra=.LBB0_1
.LBB0_1:                                #  Label of block must be emitted
FRET.STK	[ra ~ ra], sp!, 16
.Lfunc_end0:
	.size	pto_gemm_auto_i32, .Lfunc_end0-pto_gemm_auto_i32
                                        #  -- End function
	.section	.text._ZN3pto4linx9auto_mode15gemm_kernel_i32EPKiS3_Pi,"axG",@progbits,_ZN3pto4linx9auto_mode15gemm_kernel_i32EPKiS3_Pi,comdat
	.weak	_ZN3pto4linx9auto_mode15gemm_kernel_i32EPKiS3_Pi #  -- Begin function _ZN3pto4linx9auto_mode15gemm_kernel_i32EPKiS3_Pi
	.p2align	1
	.type	_ZN3pto4linx9auto_mode15gemm_kernel_i32EPKiS3_Pi,@function
_ZN3pto4linx9auto_mode15gemm_kernel_i32EPKiS3_Pi: #  @_ZN3pto4linx9auto_mode15gemm_kernel_i32EPKiS3_Pi
#  %bb.0:
FENTRY	[ra ~ ra], sp!, 16384
#  %bb.1:
BSTART.TMA	TLOAD, INT32
C.B.DIMI	0, 	->lb0
C.B.DIMI	0, 	->lb1
B.ARG	NORM.normal
B.IOR	[a0],[]
B.IOT	[], last	->t<4KB>
#  %bb.3:
C.BSTART.STD
hl.addi	a0, 4096,	->a3
#  %bb.4:
BSTART.TMA	TLOAD, INT32
C.B.DIMI	0, 	->lb0
C.B.DIMI	0, 	->lb1
B.ARG	NORM.normal
B.IOR	[a3],[]
B.IOT	[], last	->t<4KB>
#  %bb.5:
C.BSTART.STD
hl.addi	a0, 8192,	->a3
#  %bb.6:
BSTART.TMA	TLOAD, INT32
C.B.DIMI	0, 	->lb0
C.B.DIMI	0, 	->lb1
B.ARG	NORM.normal
B.IOR	[a3],[]
B.IOT	[], last	->t<4KB>
#  %bb.7:
C.BSTART.STD
hl.addi	sp, 8192,	->a3
#  %bb.8:
BSTART.TMA	TSTORE, INT32
C.B.DIMI	0, 	->lb0
C.B.DIMI	0, 	->lb1
B.ARG	NORM.normal
B.IOR	[a3],[]
B.IOT	[t#1], last	->t<4KB>
#  %bb.9:
C.BSTART.STD
hl.addi	a0, 12288,	->a3
#  %bb.10:
BSTART.TMA	TLOAD, INT32
C.B.DIMI	0, 	->lb0
C.B.DIMI	0, 	->lb1
B.ARG	NORM.normal
B.IOR	[a3],[]
B.IOT	[], last	->t<4KB>
#  %bb.11:
C.BSTART.STD
hl.addi	sp, 4096,	->a3
#  %bb.12:
BSTART.TMA	TSTORE, INT32
C.B.DIMI	0, 	->lb0
C.B.DIMI	0, 	->lb1
B.ARG	NORM.normal
B.IOR	[a3],[]
B.IOT	[t#1], last	->t<4KB>
#  %bb.13:
C.BSTART.STD
hl.addi	a0, 16384,	->a3
#  %bb.14:
BSTART.TMA	TLOAD, INT32
C.B.DIMI	0, 	->lb0
C.B.DIMI	0, 	->lb1
B.ARG	NORM.normal
B.IOR	[a3],[]
B.IOT	[], last	->t<4KB>
#  %bb.15:
C.BSTART.STD
hl.addi	a0, 32768,	->a3
hl.addi	a0, 28672,	->a4
hl.addi	a0, 24576,	->a5
hl.addi	a0, 20480,	->a6
#  %bb.16:
BSTART.TMA	TLOAD, INT32
C.B.DIMI	0, 	->lb0
C.B.DIMI	0, 	->lb1
B.ARG	NORM.normal
B.IOR	[a6],[]
B.IOT	[], last	->t<4KB>
#  %bb.17:
BSTART.TMA	TLOAD, INT32
C.B.DIMI	0, 	->lb0
C.B.DIMI	0, 	->lb1
B.ARG	NORM.normal
B.IOR	[a5],[]
B.IOT	[], last	->t<4KB>
#  %bb.18:
BSTART.TMA	TLOAD, INT32
C.B.DIMI	0, 	->lb0
C.B.DIMI	0, 	->lb1
B.ARG	NORM.normal
B.IOR	[a4],[]
B.IOT	[], last	->t<4KB>
#  %bb.19:
BSTART.TMA	TLOAD, INT32
C.B.DIMI	0, 	->lb0
C.B.DIMI	0, 	->lb1
B.ARG	NORM.normal
B.IOR	[a3],[]
B.IOT	[], last	->u<4KB>
#  %bb.20:
C.BSTART.STD
hl.addi	a1, 28672,	->a3
hl.addi	a1, 24576,	->a4
hl.addi	a1, 20480,	->a5
hl.addi	a1, 16384,	->a6
hl.addi	a1, 12288,	->a7
hl.addi	a1, 8192,	->x0
hl.addi	a1, 4096,	->x1
#  %bb.21:
BSTART.TMA	TLOAD, INT32
C.B.DIMI	0, 	->lb0
C.B.DIMI	0, 	->lb1
B.ARG	NORM.normal
B.IOR	[a1],[]
B.IOT	[], last	->u<4KB>
#  %bb.22:
BSTART.TMA	TLOAD, INT32
C.B.DIMI	0, 	->lb0
C.B.DIMI	0, 	->lb1
B.ARG	NORM.normal
B.IOR	[x1],[]
B.IOT	[], last	->u<4KB>
#  %bb.23:
BSTART.TMA	TLOAD, INT32
C.B.DIMI	0, 	->lb0
C.B.DIMI	0, 	->lb1
B.ARG	NORM.normal
B.IOR	[x0],[]
B.IOT	[], last	->u<4KB>
#  %bb.24:
BSTART.TMA	TLOAD, INT32
C.B.DIMI	0, 	->lb0
C.B.DIMI	0, 	->lb1
B.ARG	NORM.normal
B.IOR	[a7],[]
B.IOT	[], last	->u<4KB>
#  %bb.25:
BSTART.TMA	TLOAD, INT32
C.B.DIMI	0, 	->lb0
C.B.DIMI	0, 	->lb1
B.ARG	NORM.normal
B.IOR	[a6],[]
B.IOT	[], last	->u<4KB>
#  %bb.26:
BSTART.TMA	TLOAD, INT32
C.B.DIMI	0, 	->lb0
C.B.DIMI	0, 	->lb1
B.ARG	NORM.normal
B.IOR	[a5],[]
B.IOT	[], last	->u<4KB>
#  %bb.27:
BSTART.TMA	TLOAD, INT32
C.B.DIMI	0, 	->lb0
C.B.DIMI	0, 	->lb1
B.ARG	NORM.normal
B.IOR	[a4],[]
B.IOT	[], last	->u<4KB>
#  %bb.28:
BSTART.TMA	TLOAD, INT32
C.B.DIMI	0, 	->lb0
C.B.DIMI	0, 	->lb1
B.ARG	NORM.normal
B.IOR	[a3],[]
B.IOT	[], last	->t<4KB>
#  %bb.29:
BSTART.CUBE	MAMULB, INT32
C.B.DIMI	8, 	->lb0
C.B.DIMI	8, 	->lb1
C.B.DIMI	8, 	->lb2
B.IOT	[t#3, u#2], last	->acc<4KB>
#  %bb.65:
BSTART.CUBE	ACCCVT, INT32
B.IOT	[], last	->m<4KB>
#  %bb.30:
BSTART.CUBE	MAMULB, INT32
C.B.DIMI	8, 	->lb0
C.B.DIMI	8, 	->lb1
C.B.DIMI	8, 	->lb2
B.IOT	[t#2, u#3], last	->acc<4KB>
#  %bb.66:
BSTART.CUBE	ACCCVT, INT32
B.IOT	[], last	->m<4KB>
#  %bb.31:
C.BSTART.STD
hl.addi	sp, 8192,	->a3
#  %bb.32:
BSTART.TMA	TLOAD, INT32
C.B.DIMI	0, 	->lb0
C.B.DIMI	0, 	->lb1
B.ARG	NORM.normal
B.IOR	[a3],[]
B.IOT	[], last	->t<4KB>
#  %bb.33:
BSTART.CUBE	MAMULB, INT32
C.B.DIMI	8, 	->lb0
C.B.DIMI	8, 	->lb1
C.B.DIMI	8, 	->lb2
B.IOT	[t#4, u#4], last	->acc<4KB>
#  %bb.67:
BSTART.CUBE	ACCCVT, INT32
B.IOT	[], last	->m<4KB>
#  %bb.34:
C.BSTART.STD
hl.addi	sp, 4096,	->a3
#  %bb.35:
BSTART.TMA	TLOAD, INT32
C.B.DIMI	0, 	->lb0
C.B.DIMI	0, 	->lb1
B.ARG	NORM.normal
B.IOR	[a3],[]
B.IOT	[], last	->t<4KB>
#  %bb.36:
BSTART.CUBE	MAMULB, INT32
C.B.DIMI	8, 	->lb0
C.B.DIMI	8, 	->lb1
C.B.DIMI	8, 	->lb2
B.IOT	[t#4, u#5], last	->acc<4KB>
#  %bb.68:
BSTART.CUBE	ACCCVT, INT32
B.IOT	[], last	->m<4KB>
#  %bb.37:
BSTART.CUBE	MAMULB, INT32
C.B.DIMI	8, 	->lb0
C.B.DIMI	8, 	->lb1
C.B.DIMI	8, 	->lb2
B.IOT	[t#5, u#6], last	->acc<4KB>
#  %bb.69:
BSTART.CUBE	ACCCVT, INT32
B.IOT	[], last	->m<4KB>
#  %bb.38:
BSTART.CUBE	MAMULB, INT32
C.B.DIMI	8, 	->lb0
C.B.DIMI	8, 	->lb1
C.B.DIMI	8, 	->lb2
B.IOT	[t#6, u#7], last	->acc<4KB>
#  %bb.70:
BSTART.CUBE	ACCCVT, INT32
B.IOT	[], last	->m<4KB>
#  %bb.39:
BSTART.CUBE	MAMULB, INT32
C.B.DIMI	8, 	->lb0
C.B.DIMI	8, 	->lb1
C.B.DIMI	8, 	->lb2
B.IOT	[t#7, u#8], last	->acc<4KB>
#  %bb.71:
BSTART.CUBE	ACCCVT, INT32
B.IOT	[], last	->m<4KB>
#  %bb.40:
BSTART.CUBE	MAMULB, INT32
C.B.DIMI	8, 	->lb0
C.B.DIMI	8, 	->lb1
C.B.DIMI	8, 	->lb2
B.IOT	[t#8, u#2], last	->acc<4KB>
#  %bb.72:
BSTART.CUBE	ACCCVT, INT32
B.IOT	[], last	->m<4KB>
#  %bb.41:
BSTART.CUBE	MAMULB, INT32
C.B.DIMI	8, 	->lb0
C.B.DIMI	8, 	->lb1
C.B.DIMI	8, 	->lb2
B.IOT	[u#1, u#3], last	->acc<4KB>
#  %bb.73:
BSTART.CUBE	ACCCVT, INT32
B.IOT	[], last	->n<4KB>
#  %bb.42:
BSTART.CUBE	MAMULB, INT32
C.B.DIMI	8, 	->lb0
C.B.DIMI	8, 	->lb1
C.B.DIMI	8, 	->lb2
B.IOT	[t#3, u#4], last	->acc<4KB>
#  %bb.74:
BSTART.CUBE	ACCCVT, INT32
B.IOT	[], last	->n<4KB>
#  %bb.43:
BSTART.CUBE	MAMULB, INT32
C.B.DIMI	8, 	->lb0
C.B.DIMI	8, 	->lb1
C.B.DIMI	8, 	->lb2
B.IOT	[t#2, t#1], last	->acc<4KB>
#  %bb.75:
BSTART.CUBE	ACCCVT, INT32
B.IOT	[], last	->n<4KB>
#  %bb.44:
BSTART.TMA	TSTORE, INT32
C.B.DIMI	0, 	->lb0
C.B.DIMI	0, 	->lb1
B.ARG	NORM.normal
B.IOR	[a2],[]
B.IOT	[m#1], last	->t<4KB>
#  %bb.45:
C.BSTART.STD
hl.addi	a2, 4096,	->a3
#  %bb.46:
BSTART.TMA	TSTORE, INT32
C.B.DIMI	0, 	->lb0
C.B.DIMI	0, 	->lb1
B.ARG	NORM.normal
B.IOR	[a3],[]
B.IOT	[m#2], last	->t<4KB>
#  %bb.47:
C.BSTART.STD
hl.addi	a2, 8192,	->a3
#  %bb.48:
BSTART.TMA	TSTORE, INT32
C.B.DIMI	0, 	->lb0
C.B.DIMI	0, 	->lb1
B.ARG	NORM.normal
B.IOR	[a3],[]
B.IOT	[m#3], last	->t<4KB>
#  %bb.49:
C.BSTART.STD
hl.addi	a2, 12288,	->a3
#  %bb.50:
BSTART.TMA	TSTORE, INT32
C.B.DIMI	0, 	->lb0
C.B.DIMI	0, 	->lb1
B.ARG	NORM.normal
B.IOR	[a3],[]
B.IOT	[m#4], last	->t<4KB>
#  %bb.51:
C.BSTART.STD
hl.addi	a2, 16384,	->a3
#  %bb.52:
BSTART.TMA	TSTORE, INT32
C.B.DIMI	0, 	->lb0
C.B.DIMI	0, 	->lb1
B.ARG	NORM.normal
B.IOR	[a3],[]
B.IOT	[m#5], last	->t<4KB>
#  %bb.53:
C.BSTART.STD
hl.addi	a2, 20480,	->a3
#  %bb.54:
BSTART.TMA	TSTORE, INT32
C.B.DIMI	0, 	->lb0
C.B.DIMI	0, 	->lb1
B.ARG	NORM.normal
B.IOR	[a3],[]
B.IOT	[m#6], last	->t<4KB>
#  %bb.55:
C.BSTART.STD
hl.addi	a2, 24576,	->a3
#  %bb.56:
BSTART.TMA	TSTORE, INT32
C.B.DIMI	0, 	->lb0
C.B.DIMI	0, 	->lb1
B.ARG	NORM.normal
B.IOR	[a3],[]
B.IOT	[m#7], last	->t<4KB>
#  %bb.57:
C.BSTART.STD
hl.addi	a2, 28672,	->a3
#  %bb.58:
BSTART.TMA	TSTORE, INT32
C.B.DIMI	0, 	->lb0
C.B.DIMI	0, 	->lb1
B.ARG	NORM.normal
B.IOR	[a3],[]
B.IOT	[m#8], last	->t<4KB>
#  %bb.59:
C.BSTART.STD
hl.addi	a2, 32768,	->a3
#  %bb.60:
BSTART.TMA	TSTORE, INT32
C.B.DIMI	0, 	->lb0
C.B.DIMI	0, 	->lb1
B.ARG	NORM.normal
B.IOR	[a3],[]
B.IOT	[n#1], last	->t<4KB>
#  %bb.61:
C.BSTART.STD
hl.addi	a2, 36864,	->a3
#  %bb.62:
BSTART.TMA	TSTORE, INT32
C.B.DIMI	0, 	->lb0
C.B.DIMI	0, 	->lb1
B.ARG	NORM.normal
B.IOR	[a3],[]
B.IOT	[n#2], last	->t<4KB>
#  %bb.63:
C.BSTART.STD
hl.addi	a2, 40960,	->a2
#  %bb.64:
BSTART.TMA	TSTORE, INT32
C.B.DIMI	0, 	->lb0
C.B.DIMI	0, 	->lb1
B.ARG	NORM.normal
B.IOR	[a2],[]
B.IOT	[n#3], last	->t<4KB>
#  %bb.2:
FRET.STK	[ra ~ ra], sp!, 16384
.Lfunc_end1:
	.size	_ZN3pto4linx9auto_mode15gemm_kernel_i32EPKiS3_Pi, .Lfunc_end1-_ZN3pto4linx9auto_mode15gemm_kernel_i32EPKiS3_Pi
                                        #  -- End function
	.ident	"clang version 23.0.0git (git@github.com:zhoubot/llvm-project.git cfc6dd5711dcb22eac664da55e1a011c1a49b548)"
	.section	".note.GNU-stack","",@progbits
	.addrsig
