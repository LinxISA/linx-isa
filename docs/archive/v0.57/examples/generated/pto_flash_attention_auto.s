	.file	"pto_flash_attention_auto.cpp"
	.text
	.globl	pto_flash_attention_auto_i32    #  -- Begin function pto_flash_attention_auto_i32
	.p2align	1
	.type	pto_flash_attention_auto_i32,@function
pto_flash_attention_auto_i32:           #  @pto_flash_attention_auto_i32
#  %bb.0:
FENTRY	[ra ~ ra], sp!, 8
#  %bb.1:
C.BSTART.STD
c.movr	zero,	->a4
c.movi	8,	->a5
#  %bb.3:
BSTART.TLOAD	INT32
B.DIM	a5, 0, ->lb0
B.DIM	a5, 0, ->lb1
B.DIM	a5, 0, ->lb2
B.IOR	[a0,a4],[]
B.IOT	last, ->t<4KB>
#  %bb.4:
C.BSTART.STD
hl.addi	a0, 4096,	->a6
#  %bb.5:
BSTART.TLOAD	INT32
B.DIM	a5, 0, ->lb0
B.DIM	a5, 0, ->lb1
B.DIM	a5, 0, ->lb2
B.IOR	[a6,a4],[]
B.IOT	last, ->t<4KB>
#  %bb.6:
C.BSTART.STD
hl.addi	a0, 8192,	->a6
#  %bb.7:
BSTART.TLOAD	INT32
B.DIM	a5, 0, ->lb0
B.DIM	a5, 0, ->lb1
B.DIM	a5, 0, ->lb2
B.IOR	[a6,a4],[]
B.IOT	last, ->t<4KB>
#  %bb.8:
C.BSTART.STD
hl.addi	a0, 12288,	->a6
#  %bb.9:
BSTART.TLOAD	INT32
B.DIM	a5, 0, ->lb0
B.DIM	a5, 0, ->lb1
B.DIM	a5, 0, ->lb2
B.IOR	[a6,a4],[]
B.IOT	last, ->t<4KB>
#  %bb.10:
C.BSTART.STD
hl.addi	a0, 16384,	->a0
#  %bb.11:
BSTART.TLOAD	INT32
B.DIM	a5, 0, ->lb0
B.DIM	a5, 0, ->lb1
B.DIM	a5, 0, ->lb2
B.IOR	[a0,a4],[]
B.IOT	last, ->t<4KB>
#  %bb.12:
C.BSTART.STD
hl.addi	a1, 16384,	->a0
hl.addi	a1, 12288,	->a6
hl.addi	a1, 8192,	->a7
hl.addi	a1, 4096,	->x0
#  %bb.13:
BSTART.TLOAD	INT32
B.DIM	a5, 0, ->lb0
B.DIM	a5, 0, ->lb1
B.DIM	a5, 0, ->lb2
B.IOR	[a1,a4],[]
B.IOT	last, ->t<4KB>
#  %bb.14:
BSTART.TLOAD	INT32
B.DIM	a5, 0, ->lb0
B.DIM	a5, 0, ->lb1
B.DIM	a5, 0, ->lb2
B.IOR	[x0,a4],[]
B.IOT	last, ->t<4KB>
#  %bb.15:
BSTART.TLOAD	INT32
B.DIM	a5, 0, ->lb0
B.DIM	a5, 0, ->lb1
B.DIM	a5, 0, ->lb2
B.IOR	[a7,a4],[]
B.IOT	last, ->t<4KB>
#  %bb.16:
BSTART.TLOAD	INT32
B.DIM	a5, 0, ->lb0
B.DIM	a5, 0, ->lb1
B.DIM	a5, 0, ->lb2
B.IOR	[a6,a4],[]
B.IOT	last, ->u<4KB>
#  %bb.17:
BSTART.TLOAD	INT32
B.DIM	a5, 0, ->lb0
B.DIM	a5, 0, ->lb1
B.DIM	a5, 0, ->lb2
B.IOR	[a0,a4],[]
B.IOT	last, ->u<4KB>
#  %bb.18:
C.BSTART.STD
hl.addi	a2, 12288,	->a0
hl.addi	a2, 8192,	->a1
hl.addi	a2, 4096,	->a6
#  %bb.19:
BSTART.TLOAD	INT32
B.DIM	a5, 0, ->lb0
B.DIM	a5, 0, ->lb1
B.DIM	a5, 0, ->lb2
B.IOR	[a2,a4],[]
B.IOT	last, ->u<4KB>
#  %bb.20:
BSTART.TLOAD	INT32
B.DIM	a5, 0, ->lb0
B.DIM	a5, 0, ->lb1
B.DIM	a5, 0, ->lb2
B.IOR	[a6,a4],[]
B.IOT	last, ->u<4KB>
#  %bb.21:
BSTART.TLOAD	INT32
B.DIM	a5, 0, ->lb0
B.DIM	a5, 0, ->lb1
B.DIM	a5, 0, ->lb2
B.IOR	[a1,a4],[]
B.IOT	last, ->u<4KB>
#  %bb.22:
BSTART.TLOAD	INT32
B.DIM	a5, 0, ->lb0
B.DIM	a5, 0, ->lb1
B.DIM	a5, 0, ->lb2
B.IOR	[a0,a4],[]
B.IOT	last, ->u<4KB>
#  %bb.23:
BSTART.TMATMUL	INT32
C.B.DIMI	8, 	->lb0
C.B.DIMI	8, 	->lb1
C.B.DIMI	8, 	->lb2
B.IOT	t#8.reuse, t#3, last
#  %bb.58:
BSTART.ACCCVT	INT32
B.IOT	last, ->m<4KB>
#  %bb.24:
BSTART.TMATMUL	INT32
C.B.DIMI	8, 	->lb0
C.B.DIMI	8, 	->lb1
C.B.DIMI	8, 	->lb2
B.IOT	t#6.reuse, t#2.reuse, last
#  %bb.59:
BSTART.ACCCVT	INT32
B.IOT	last, ->m<4KB>
#  %bb.25:
BSTART.TMATMUL	INT32
C.B.DIMI	8, 	->lb0
C.B.DIMI	8, 	->lb1
C.B.DIMI	8, 	->lb2
B.IOT	t#5.reuse, t#1.reuse, last
#  %bb.60:
BSTART.ACCCVT	INT32
B.IOT	last, ->m<4KB>
#  %bb.26:
BSTART.TMATMUL	INT32
C.B.DIMI	8, 	->lb0
C.B.DIMI	8, 	->lb1
C.B.DIMI	8, 	->lb2
B.IOT	t#4.reuse, u#6.reuse, last
#  %bb.61:
BSTART.ACCCVT	INT32
B.IOT	last, ->m<4KB>
#  %bb.27:
BSTART.TMATMUL	INT32
C.B.DIMI	8, 	->lb0
C.B.DIMI	8, 	->lb1
C.B.DIMI	8, 	->lb2
B.IOT	t#3, u#5.reuse, last
#  %bb.62:
BSTART.ACCCVT	INT32
B.IOT	last, ->m<4KB>
#  %bb.28:
BSTART.TMATMUL	INT32
C.B.DIMI	8, 	->lb0
C.B.DIMI	8, 	->lb1
C.B.DIMI	8, 	->lb2
B.IOT	t#6, t#2, last
#  %bb.63:
BSTART.ACCCVT	INT32
B.IOT	last, ->m<4KB>
#  %bb.29:
BSTART.TMATMUL	INT32
C.B.DIMI	8, 	->lb0
C.B.DIMI	8, 	->lb1
C.B.DIMI	8, 	->lb2
B.IOT	t#4, t#1, last
#  %bb.64:
BSTART.ACCCVT	INT32
B.IOT	last, ->m<4KB>
#  %bb.30:
BSTART.TMATMUL	INT32
C.B.DIMI	8, 	->lb0
C.B.DIMI	8, 	->lb1
C.B.DIMI	8, 	->lb2
B.IOT	t#2, u#6, last
#  %bb.65:
BSTART.ACCCVT	INT32
B.IOT	last, ->m<4KB>
#  %bb.31:
BSTART.TMATMUL	INT32
C.B.DIMI	8, 	->lb0
C.B.DIMI	8, 	->lb1
C.B.DIMI	8, 	->lb2
B.IOT	t#1, u#5, last
#  %bb.66:
BSTART.ACCCVT	INT32
B.IOT	last, ->n<4KB>
#  %bb.32:
BSTART.TMATMUL	INT32
C.B.DIMI	8, 	->lb0
C.B.DIMI	8, 	->lb1
C.B.DIMI	8, 	->lb2
B.IOT	m#8, u#4.reuse, last
#  %bb.67:
BSTART.ACCCVT	INT32
B.IOT	last, ->m<4KB>
#  %bb.33:
BSTART.TMATMUL	INT32
C.B.DIMI	8, 	->lb0
C.B.DIMI	8, 	->lb1
C.B.DIMI	8, 	->lb2
B.IOT	m#8, u#3.reuse, last
#  %bb.68:
BSTART.ACCCVT	INT32
B.IOT	last, ->m<4KB>
#  %bb.34:
BSTART.TMATMUL	INT32
C.B.DIMI	8, 	->lb0
C.B.DIMI	8, 	->lb1
C.B.DIMI	8, 	->lb2
B.IOT	m#8, u#2.reuse, last
#  %bb.69:
BSTART.ACCCVT	INT32
B.IOT	last, ->m<4KB>
#  %bb.35:
BSTART.TMATMUL	INT32
C.B.DIMI	8, 	->lb0
C.B.DIMI	8, 	->lb1
C.B.DIMI	8, 	->lb2
B.IOT	m#8, u#1.reuse, last
#  %bb.70:
BSTART.ACCCVT	INT32
B.IOT	last, ->m<4KB>
#  %bb.36:
BSTART.TMATMUL	INT32
C.B.DIMI	8, 	->lb0
C.B.DIMI	8, 	->lb1
C.B.DIMI	8, 	->lb2
B.IOT	m#8, u#4.reuse, last
#  %bb.71:
BSTART.ACCCVT	INT32
B.IOT	last, ->m<4KB>
#  %bb.37:
BSTART.TMATMUL	INT32
C.B.DIMI	8, 	->lb0
C.B.DIMI	8, 	->lb1
C.B.DIMI	8, 	->lb2
B.IOT	m#8, u#3, last
#  %bb.72:
BSTART.ACCCVT	INT32
B.IOT	last, ->m<4KB>
#  %bb.38:
BSTART.TMATMUL	INT32
C.B.DIMI	8, 	->lb0
C.B.DIMI	8, 	->lb1
C.B.DIMI	8, 	->lb2
B.IOT	m#8, u#2, last
#  %bb.73:
BSTART.ACCCVT	INT32
B.IOT	last, ->m<4KB>
#  %bb.39:
BSTART.TMATMUL	INT32
C.B.DIMI	8, 	->lb0
C.B.DIMI	8, 	->lb1
C.B.DIMI	8, 	->lb2
B.IOT	m#8, u#1, last
#  %bb.74:
BSTART.ACCCVT	INT32
B.IOT	last, ->m<4KB>
#  %bb.40:
BSTART.TMATMUL	INT32
C.B.DIMI	8, 	->lb0
C.B.DIMI	8, 	->lb1
C.B.DIMI	8, 	->lb2
B.IOT	n#1, u#1, last
#  %bb.75:
BSTART.ACCCVT	INT32
B.IOT	last, ->n<4KB>
#  %bb.41:
BSTART.TSTORE	INT32
B.DIM	a5, 0, ->lb0
B.DIM	a5, 0, ->lb1
B.DIM	a5, 0, ->lb2
B.IOR	[a3,a4],[]
B.IOT	m#8, last
#  %bb.42:
C.BSTART.STD
hl.addi	a3, 4096,	->a0
#  %bb.43:
BSTART.TSTORE	INT32
B.DIM	a5, 0, ->lb0
B.DIM	a5, 0, ->lb1
B.DIM	a5, 0, ->lb2
B.IOR	[a0,a4],[]
B.IOT	m#7, last
#  %bb.44:
C.BSTART.STD
hl.addi	a3, 8192,	->a0
#  %bb.45:
BSTART.TSTORE	INT32
B.DIM	a5, 0, ->lb0
B.DIM	a5, 0, ->lb1
B.DIM	a5, 0, ->lb2
B.IOR	[a0,a4],[]
B.IOT	m#6, last
#  %bb.46:
C.BSTART.STD
hl.addi	a3, 12288,	->a0
#  %bb.47:
BSTART.TSTORE	INT32
B.DIM	a5, 0, ->lb0
B.DIM	a5, 0, ->lb1
B.DIM	a5, 0, ->lb2
B.IOR	[a0,a4],[]
B.IOT	m#5, last
#  %bb.48:
C.BSTART.STD
hl.addi	a3, 16384,	->a0
#  %bb.49:
BSTART.TSTORE	INT32
B.DIM	a5, 0, ->lb0
B.DIM	a5, 0, ->lb1
B.DIM	a5, 0, ->lb2
B.IOR	[a0,a4],[]
B.IOT	m#4, last
#  %bb.50:
C.BSTART.STD
hl.addi	a3, 20480,	->a0
#  %bb.51:
BSTART.TSTORE	INT32
B.DIM	a5, 0, ->lb0
B.DIM	a5, 0, ->lb1
B.DIM	a5, 0, ->lb2
B.IOR	[a0,a4],[]
B.IOT	m#3, last
#  %bb.52:
C.BSTART.STD
hl.addi	a3, 24576,	->a0
#  %bb.53:
BSTART.TSTORE	INT32
B.DIM	a5, 0, ->lb0
B.DIM	a5, 0, ->lb1
B.DIM	a5, 0, ->lb2
B.IOR	[a0,a4],[]
B.IOT	m#2, last
#  %bb.54:
C.BSTART.STD
hl.addi	a3, 28672,	->a0
#  %bb.55:
BSTART.TSTORE	INT32
B.DIM	a5, 0, ->lb0
B.DIM	a5, 0, ->lb1
B.DIM	a5, 0, ->lb2
B.IOR	[a0,a4],[]
B.IOT	m#1, last
#  %bb.56:
C.BSTART.STD
hl.addi	a3, 32768,	->a0
#  %bb.57:
BSTART.TSTORE	INT32
B.DIM	a5, 0, ->lb0
B.DIM	a5, 0, ->lb1
B.DIM	a5, 0, ->lb2
B.IOR	[a0,a4],[]
B.IOT	n#1, last
#  %bb.2:
FRET.STK	[ra ~ ra], sp!, 8
.Lfunc_end0:
	.size	pto_flash_attention_auto_i32, .Lfunc_end0-pto_flash_attention_auto_i32
                                        #  -- End function
	.ident	"clang version 23.0.0git (https://github.com/LinxISA/llvm-project.git 487db9698c9c748de9afe33aa160c6a52be961ab)"
	.section	".note.GNU-stack","",@progbits
	.addrsig
