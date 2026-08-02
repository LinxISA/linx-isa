	.text

	.globl callret_tpl_fret_stk_slot_redirect
	.type callret_tpl_fret_stk_slot_redirect,@function
callret_tpl_fret_stk_slot_redirect:
	# FENTRY [ra ~ ra], sp!, 16
	.4byte 0x04a50041
	c.movr ra, ->a1
	addtpc %tpcrel_hi(.Lcallret_tpl_fret_stk_redirect), ->a2
	addi a2, %tpcrel_lo(.Lcallret_tpl_fret_stk_redirect), ->a2
	sdi a2, [sp, 8]
	addi zero, 17, ->a0
	# FRET.STK [ra ~ ra], sp!, 16
	.4byte 0x04a53041
.Lcallret_tpl_fret_stk_redirect:
	C.BSTART.STD RET
	addi zero, 34, ->a0
	c.setc.tgt a1
	C.BSTOP
	.size callret_tpl_fret_stk_slot_redirect, .-callret_tpl_fret_stk_slot_redirect

	.globl callret_tpl_fret_ra_slot_redirect
	.type callret_tpl_fret_ra_slot_redirect,@function
callret_tpl_fret_ra_slot_redirect:
	# FENTRY [ra ~ ra], sp!, 16
	.4byte 0x04a50041
	c.movr ra, ->a1
	addtpc %tpcrel_hi(.Lcallret_tpl_fret_ra_redirect), ->a2
	addi a2, %tpcrel_lo(.Lcallret_tpl_fret_ra_redirect), ->a2
	sdi a2, [sp, 8]
	addi zero, 51, ->a0
	# FRET.RA [ra ~ ra], sp!, 16
	.4byte 0x04a52041
.Lcallret_tpl_fret_ra_redirect:
	C.BSTART.STD RET
	addi zero, 68, ->a0
	c.setc.tgt a1
	C.BSTOP
	.size callret_tpl_fret_ra_slot_redirect, .-callret_tpl_fret_ra_slot_redirect

	.globl callret_tpl_ret_error_trailer_success
	.type callret_tpl_ret_error_trailer_success,@function
callret_tpl_ret_error_trailer_success:
	C.BSTART.STD RET
	C.BSTOP
.Lcallret_tpl_ret_error_trailer_bad:
	C.BSTART.STD RET
	addi zero, 85, ->a0
	c.setc.tgt ra
	C.BSTOP
	.size callret_tpl_ret_error_trailer_success, .-callret_tpl_ret_error_trailer_success

	.globl callret_tpl_cond_ret_error_trailer_taken
	.type callret_tpl_cond_ret_error_trailer_taken,@function
callret_tpl_cond_ret_error_trailer_taken:
	C.BSTART COND, .Lcallret_tpl_cond_ret_error_jump
	setc.eq zero, zero
	C.BSTART.STD RET
.Lcallret_tpl_cond_ret_error_jump:
	j .Lcallret_tpl_cond_ret_error_handler
	C.BSTOP
.Lcallret_tpl_cond_ret_error_handler:
	C.BSTART.STD RET
	addi zero, 102, ->a0
	c.setc.tgt ra
	C.BSTOP
	.size callret_tpl_cond_ret_error_trailer_taken, .-callret_tpl_cond_ret_error_trailer_taken

	.globl callret_tpl_c_bstart_cond_taken
	.type callret_tpl_c_bstart_cond_taken,@function
callret_tpl_c_bstart_cond_taken:
	C.BSTART COND, .Lcallret_tpl_c_bstart_cond_taken_target
	setc.eq zero, zero
	C.BSTART.STD RET
	addi zero, 225, ->a0
	c.setc.tgt ra
	C.BSTOP
.Lcallret_tpl_c_bstart_cond_taken_target:
	C.BSTART.STD RET
	addi zero, 102, ->a0
	c.setc.tgt ra
	C.BSTOP
	.size callret_tpl_c_bstart_cond_taken, .-callret_tpl_c_bstart_cond_taken

	.globl callret_tpl_c_bstart_cond_not_taken
	.type callret_tpl_c_bstart_cond_not_taken,@function
callret_tpl_c_bstart_cond_not_taken:
	C.BSTART COND, .Lcallret_tpl_c_bstart_cond_not_taken_target
	setc.ne zero, zero
	C.BSTART.STD RET
	addi zero, 85, ->a0
	c.setc.tgt ra
	C.BSTOP
.Lcallret_tpl_c_bstart_cond_not_taken_target:
	C.BSTART.STD RET
	addi zero, 226, ->a0
	c.setc.tgt ra
	C.BSTOP
	.size callret_tpl_c_bstart_cond_not_taken, .-callret_tpl_c_bstart_cond_not_taken

	.globl callret_tpl_j_skip_poison
	.type callret_tpl_j_skip_poison,@function
callret_tpl_j_skip_poison:
	# FENTRY makes J the first instruction of the next translation block.
	# Each observable path reaches its own frame-balanced FRET.STK return.
	.4byte 0x04a50041
	j .Lcallret_tpl_j_handler
	addi zero, 85, ->a0
	.4byte 0x04a53041
.Lcallret_tpl_j_handler:
	C.BSTART DIRECT, .Lcallret_tpl_j_handler_return
	addi zero, 119, ->a0
.Lcallret_tpl_j_handler_return:
	.4byte 0x04a53041
	.size callret_tpl_j_skip_poison, .-callret_tpl_j_skip_poison

	.globl callret_tpl_l_bstart_direct_positive
	.type callret_tpl_l_bstart_direct_positive,@function
callret_tpl_l_bstart_direct_positive:
	# Keep the target close: the canonical decoder treats this displacement as
	# low25 halfwords, while the reversed decoder interprets it as high bits.
	L.BSTART.STD DIRECT, .Lcallret_tpl_l_bstart_direct_positive_target
	addi zero, 68, ->a0
	C.BSTOP
.Lcallret_tpl_l_bstart_direct_positive_fallthrough:
	C.BSTART.STD RET
	addi zero, 85, ->a0
	c.setc.tgt ra
	C.BSTOP
.Lcallret_tpl_l_bstart_direct_positive_target:
	C.BSTART.STD RET
	addi zero, 119, ->a0
	c.setc.tgt ra
	C.BSTOP
	.size callret_tpl_l_bstart_direct_positive, .-callret_tpl_l_bstart_direct_positive

.Lcallret_tpl_l_bstart_direct_negative_target:
	C.BSTART.STD RET
	addi zero, 136, ->a0
	c.setc.tgt ra
	C.BSTOP

	.globl callret_tpl_l_bstart_direct_negative
	.type callret_tpl_l_bstart_direct_negative,@function
callret_tpl_l_bstart_direct_negative:
	L.BSTART.STD DIRECT, .Lcallret_tpl_l_bstart_direct_negative_target
	addi zero, 102, ->a0
	C.BSTOP
	C.BSTART.STD RET
	addi zero, 153, ->a0
	c.setc.tgt ra
	C.BSTOP
	.size callret_tpl_l_bstart_direct_negative, .-callret_tpl_l_bstart_direct_negative
