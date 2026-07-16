	.text
	.align 2

	.globl atomic_lr_w_nonzero_srczero
	.type atomic_lr_w_nonzero_srczero,@function
atomic_lr_w_nonzero_srczero:
	C.BSTART.STD RET
	# LR.W RegDst=a0, SrcL=a0, SrcZero=31.
	.4byte 0x21f1010b
	c.setc.tgt ra
	C.BSTOP
	.size atomic_lr_w_nonzero_srczero, .-atomic_lr_w_nonzero_srczero

	.globl atomic_lr_d_nonzero_srczero
	.type atomic_lr_d_nonzero_srczero,@function
atomic_lr_d_nonzero_srczero:
	C.BSTART.STD RET
	# LR.D RegDst=a0, SrcL=a0, SrcZero=17.
	.4byte 0x3111010b
	c.setc.tgt ra
	C.BSTOP
	.size atomic_lr_d_nonzero_srczero, .-atomic_lr_d_nonzero_srczero
