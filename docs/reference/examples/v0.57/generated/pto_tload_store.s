	.file	"pto_tload_store.cpp"
	.text
	.globl	pto_tload_store_i32             #  -- Begin function pto_tload_store_i32
	.p2align	1
	.type	pto_tload_store_i32,@function
pto_tload_store_i32:                    #  @pto_tload_store_i32
#  %bb.0:
FENTRY	[ra ~ ra], sp!, 8
#  %bb.1:
C.BSTART.STD
c.movr	zero,	->a2
addi	zero, 32,	->a3
#  %bb.3:
BSTART.TLOAD	INT32
B.DIM	a3, 0, ->lb0
B.DIM	a3, 0, ->lb1
B.DIM	a3, 0, ->lb2
B.IOR	[a0,a2],[]
B.IOT	last, ->t<4KB>
#  %bb.4:
BSTART.TSTORE	INT32
B.DIM	a3, 0, ->lb0
B.DIM	a3, 0, ->lb1
B.DIM	a3, 0, ->lb2
B.IOR	[a1,a2],[]
B.IOT	t#1, last
#  %bb.2:
FRET.STK	[ra ~ ra], sp!, 8
.Lfunc_end0:
	.size	pto_tload_store_i32, .Lfunc_end0-pto_tload_store_i32
                                        #  -- End function
	.ident	"clang version 23.0.0git (https://github.com/LinxISA/llvm-project.git 487db9698c9c748de9afe33aa160c6a52be961ab)"
	.section	".note.GNU-stack","",@progbits
	.addrsig
