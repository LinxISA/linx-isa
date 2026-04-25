	.text

	.globl callret_tpl_fret_stk_slot_redirect
	.type callret_tpl_fret_stk_slot_redirect,@function
callret_tpl_fret_stk_slot_redirect:
	# FENTRY [ra ~ ra], sp!, 16
	.4byte 0x04a50041
	c.movr ra, ->a1
	addtpc .Lcallret_tpl_fret_stk_redirect, ->a2
	addi a2, .Lcallret_tpl_fret_stk_redirect, ->a2
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
	addtpc .Lcallret_tpl_fret_ra_redirect, ->a2
	addi a2, .Lcallret_tpl_fret_ra_redirect, ->a2
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
	j .Lcallret_tpl_ret_error_trailer_bad
	C.BSTOP
.Lcallret_tpl_ret_error_trailer_bad:
	addi zero, 85, ->a0
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
