	.text
	.align 2

	.globl atomic_lr_w_nonzero_srczero
	.type atomic_lr_w_nonzero_srczero,@function
atomic_lr_w_nonzero_srczero:
	C.BSTART.STD RET
	# LR.W RegDst=a0, SrcL=a0, SrcZero=31.
	.4byte 0x11f1010b
	c.setc.tgt ra
	C.BSTOP
	.size atomic_lr_w_nonzero_srczero, .-atomic_lr_w_nonzero_srczero

	.globl atomic_lr_w_signext
	.type atomic_lr_w_signext,@function
atomic_lr_w_signext:
	C.BSTART.STD RET
	# LR.W RegDst=a0, SrcL=a0, SrcZero=31.
	.4byte 0x11f1010b
	c.setc.tgt ra
	C.BSTOP
	.size atomic_lr_w_signext, .-atomic_lr_w_signext

	.globl atomic_lr_d_nonzero_srczero
	.type atomic_lr_d_nonzero_srczero,@function
atomic_lr_d_nonzero_srczero:
	C.BSTART.STD RET
	# LR.D RegDst=a0, SrcL=a0, SrcZero=17.
	.4byte 0x1911010b
	c.setc.tgt ra
	C.BSTOP
	.size atomic_lr_d_nonzero_srczero, .-atomic_lr_d_nonzero_srczero

	.globl atomic_sw_sub
	.type atomic_sw_sub,@function
atomic_sw_sub:
	C.BSTART.STD RET
	.4byte 0x4031300b	/* SW.SUB [a0], a1 */
	c.setc.tgt ra
	C.BSTOP
	.size atomic_sw_sub, .-atomic_sw_sub

	.globl atomic_sd_sub
	.type atomic_sd_sub,@function
atomic_sd_sub:
	C.BSTART.STD RET
	.4byte 0x4031500b	/* SD.SUB [a0], a1 */
	c.setc.tgt ra
	C.BSTOP
	.size atomic_sd_sub, .-atomic_sd_sub

	.globl atomic_sb_add
	.type atomic_sb_add,@function
atomic_sb_add:
	C.BSTART.STD RET
	.4byte 0x8031300b	/* SB.ADD [a0], a1 */
	c.setc.tgt ra
	C.BSTOP
	.size atomic_sb_add, .-atomic_sb_add

	.globl atomic_sb_sub
	.type atomic_sb_sub,@function
atomic_sb_sub:
	C.BSTART.STD RET
	.4byte 0xc031300b	/* SB.SUB [a0], a1 */
	c.setc.tgt ra
	C.BSTOP
	.size atomic_sb_sub, .-atomic_sb_sub

	.globl atomic_sh_add
	.type atomic_sh_add,@function
atomic_sh_add:
	C.BSTART.STD RET
	.4byte 0x8031500b	/* SH.ADD [a0], a1 */
	c.setc.tgt ra
	C.BSTOP
	.size atomic_sh_add, .-atomic_sh_add

	.globl atomic_sh_sub
	.type atomic_sh_sub,@function
atomic_sh_sub:
	C.BSTART.STD RET
	.4byte 0xc031500b	/* SH.SUB [a0], a1 */
	c.setc.tgt ra
	C.BSTOP
	.size atomic_sh_sub, .-atomic_sh_sub

	.globl atomic_dma_free_s
	.type atomic_dma_free_s,@function
atomic_dma_free_s:
	C.BSTART.STD RET
	.4byte 0x0401700b	/* DMA.FREE.S [a0] */
	c.setc.tgt ra
	C.BSTOP
	.size atomic_dma_free_s, .-atomic_dma_free_s

	.globl atomic_dma_free_l
	.type atomic_dma_free_l,@function
atomic_dma_free_l:
	C.BSTART.STD RET
	.4byte 0x0601700b	/* DMA.FREE.L [a0] */
	c.setc.tgt ra
	C.BSTOP
	.size atomic_dma_free_l, .-atomic_dma_free_l

	.globl atomic_mcopy_ds
	.type atomic_mcopy_ds,@function
atomic_mcopy_ds:
	C.BSTART.STD RET
	.4byte 0x22311131	/* MCOPY.DS -> a0, [a0, a1, a2] */
	c.setc.tgt ra
	C.BSTOP
	.size atomic_mcopy_ds, .-atomic_mcopy_ds

	.globl atomic_mcopy_dl
	.type atomic_mcopy_dl,@function
atomic_mcopy_dl:
	C.BSTART.STD RET
	.4byte 0x26311131	/* MCOPY.DL -> a0, [a0, a1, a2] */
	c.setc.tgt ra
	C.BSTOP
	.size atomic_mcopy_dl, .-atomic_mcopy_dl
