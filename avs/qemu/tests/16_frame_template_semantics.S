#ifndef CASE
#define CASE 1
#endif

	.text
	.globl _start
	.type _start,@function

	.macro UARTC value
	lui 0, ->t
	addi t#1, \value, ->t
	c.swi t#1, [u#1, 0]
	.endm

	.macro FRET_RA_PRE_MARKER
	UARTC 76
	UARTC 73
	UARTC 78
	UARTC 88
	UARTC 95
	UARTC 70
	UARTC 82
	UARTC 69
	UARTC 84
	UARTC 95
	UARTC 82
	UARTC 65
	UARTC 95
	UARTC 80
	UARTC 82
	UARTC 69
	UARTC 95
	UARTC 84
	UARTC 65
	UARTC 82
	UARTC 71
	UARTC 69
	UARTC 84
	UARTC 32
	UARTC 99
	UARTC 97
	UARTC 115
	UARTC 101
	UARTC 61
	UARTC 52
	UARTC 10
	.endm

	.macro FRET_RA_RESTORED_MARKER
	UARTC 76
	UARTC 73
	UARTC 78
	UARTC 88
	UARTC 95
	UARTC 70
	UARTC 82
	UARTC 69
	UARTC 84
	UARTC 95
	UARTC 82
	UARTC 65
	UARTC 95
	UARTC 82
	UARTC 69
	UARTC 83
	UARTC 84
	UARTC 79
	UARTC 82
	UARTC 69
	UARTC 68
	UARTC 95
	UARTC 84
	UARTC 65
	UARTC 82
	UARTC 71
	UARTC 69
	UARTC 84
	UARTC 32
	UARTC 99
	UARTC 97
	UARTC 115
	UARTC 101
	UARTC 61
	UARTC 52
	UARTC 10
	.endm

	.macro FRET_STK_RETAINED_MARKER
	UARTC 76
	UARTC 73
	UARTC 78
	UARTC 88
	UARTC 95
	UARTC 70
	UARTC 82
	UARTC 69
	UARTC 84
	UARTC 95
	UARTC 83
	UARTC 84
	UARTC 75
	UARTC 95
	UARTC 82
	UARTC 69
	UARTC 84
	UARTC 65
	UARTC 73
	UARTC 78
	UARTC 69
	UARTC 68
	UARTC 95
	UARTC 84
	UARTC 65
	UARTC 82
	UARTC 71
	UARTC 69
	UARTC 84
	UARTC 32
	UARTC 99
	UARTC 97
	UARTC 115
	UARTC 101
	UARTC 61
	UARTC 53
	UARTC 10
	.endm

_start:
#if CASE == 1
	/* raw mapping checked by llvm-objdump: [ra ~ ra], sp!, 16 entry/exit */
	.word 0x04a50041
	.word 0x04a51041
#elif CASE == 2
	/* raw mapping checked by llvm-mc: [x2 ~ ra], sp!, 88 entry/exit */
	.word 0x16ab0041
	.word 0x16ab1041
#elif CASE == 3
	/* raw mapping checked by llvm-objdump: [r2 ~ r23], sp!, 176 entry/exit */
	.word 0x2d710041
	.word 0x2d711041
#elif CASE == 4
	/* raw mapping checked by llvm-mc: FRET.RA [ra ~ ra], sp!, 16 */
	BSTART.STD
	addtpc %tpcrel_hi(fret_ra_pre_restore_target), ->a2
	addi a2, %tpcrel_lo(fret_ra_pre_restore_target), ->a2
	c.movr a2, ->ra
	addtpc %tpcrel_hi(fret_ra_restored_target), ->a2
	addi a2, %tpcrel_lo(fret_ra_restored_target), ->a2
	sdi a2, [sp, 8]
	BSTOP
	.word 0x04a52041
#elif CASE == 5
	/* raw mapping checked by llvm-mc: FRET.STK [ra ~ ra], sp!, 16 */
	.word 0x04a50041
	addtpc %tpcrel_hi(fret_stk_retained_target), ->a2
	addi a2, %tpcrel_lo(fret_stk_retained_target), ->a2
	sdi a2, [sp, 8]
	.word 0x04a53041
#else
	j fail
#endif
	j pass

fret_ra_pre_restore_target:
	C.BSTART.STD RET
	lui 65536, ->u
	FRET_RA_PRE_MARKER
	c.setc.tgt ra
	C.BSTOP

fret_ra_restored_target:
	BSTART.STD
	lui 65536, ->u
	FRET_RA_RESTORED_MARKER
	BSTOP
	j pass

fret_stk_retained_target:
	BSTART.STD
	lui 65536, ->u
	FRET_STK_RETAINED_MARKER
	BSTOP
	j pass

pass:
	BSTART.STD
	lui 65536, ->u
	UARTC 76
	UARTC 73
	UARTC 78
	UARTC 88
	UARTC 95
	UARTC 70
	UARTC 82
	UARTC 65
	UARTC 77
	UARTC 69
	UARTC 95
	UARTC 84
	UARTC 69
	UARTC 77
	UARTC 80
	UARTC 76
	UARTC 65
	UARTC 84
	UARTC 69
	UARTC 32
	UARTC 99
	UARTC 97
	UARTC 115
	UARTC 101
	UARTC 61
#if CASE == 1
	UARTC 49
#elif CASE == 2
	UARTC 50
#elif CASE == 3
	UARTC 51
#elif CASE == 4
	UARTC 52
#elif CASE == 5
	UARTC 53
#endif
	UARTC 32
	UARTC 115
	UARTC 116
	UARTC 97
	UARTC 116
	UARTC 117
	UARTC 115
	UARTC 61
	UARTC 80
	UARTC 65
	UARTC 83
	UARTC 83
	UARTC 32
	UARTC 102
	UARTC 105
	UARTC 110
	UARTC 105
	UARTC 115
	UARTC 104
	UARTC 101
	UARTC 114
	UARTC 95
	UARTC 97
	UARTC 100
	UARTC 100
	UARTC 114
	UARTC 61
	UARTC 48
	UARTC 120
	UARTC 49
	UARTC 48
	UARTC 48
	UARTC 48
	UARTC 57
	UARTC 48
	UARTC 48
	UARTC 48
	UARTC 32
	UARTC 102
	UARTC 105
	UARTC 110
	UARTC 105
	UARTC 115
	UARTC 104
	UARTC 101
	UARTC 114
	UARTC 95
	UARTC 118
	UARTC 97
	UARTC 108
	UARTC 117
	UARTC 101
	UARTC 61
	UARTC 48
	UARTC 120
	UARTC 48
	UARTC 48
	UARTC 48
	UARTC 48
	UARTC 53
	UARTC 53
	UARTC 53
	UARTC 53
	UARTC 10
	BSTOP
	BSTART.STD
	lui 65545, ->u
	lui 5, ->t
	addi t#1, 1365, ->t
	c.swi t#1, [u#1, 0]
	BSTOP
	j sink

sink:
	BSTART.STD
	BSTOP
	j sink

fail:
	BSTART.STD
	lui 65545, ->u
	lui 19, ->t
	addi t#1, 819, ->t
	c.swi t#1, [u#1, 0]
	BSTOP
	j fail
