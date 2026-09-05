/*
 * LinxISA QEMU Test Suite - Main Runner
 * 
 * This file includes all test suites and provides a main entry point
 * that runs all tests sequentially.
 */

#include "linx_test.h"

/* Compile-time suite selection (1 = enabled, 0 = disabled) */
#ifndef LINX_TEST_ENABLE_ARITHMETIC
#define LINX_TEST_ENABLE_ARITHMETIC 1
#endif
#ifndef LINX_TEST_ENABLE_BITWISE
#define LINX_TEST_ENABLE_BITWISE 1
#endif
#ifndef LINX_TEST_ENABLE_LOADSTORE
#define LINX_TEST_ENABLE_LOADSTORE 1
#endif
#ifndef LINX_TEST_ENABLE_BRANCH
#define LINX_TEST_ENABLE_BRANCH 1
#endif
#ifndef LINX_TEST_ENABLE_MOVE
#define LINX_TEST_ENABLE_MOVE 1
#endif
#ifndef LINX_TEST_ENABLE_FLOAT
#define LINX_TEST_ENABLE_FLOAT 1
#endif
#ifndef LINX_TEST_ENABLE_ATOMIC
#define LINX_TEST_ENABLE_ATOMIC 1
#endif
#ifndef LINX_TEST_ENABLE_JUMPTABLE
#define LINX_TEST_ENABLE_JUMPTABLE 1
#endif
#ifndef LINX_TEST_ENABLE_VARARGS
#define LINX_TEST_ENABLE_VARARGS 1
#endif
#ifndef LINX_TEST_ENABLE_SYSTEM
#define LINX_TEST_ENABLE_SYSTEM 1
#endif
#ifndef LINX_TEST_ENABLE_CALLRET
#define LINX_TEST_ENABLE_CALLRET 0
#endif
#ifndef LINX_TEST_ENABLE_SIMT_AUTOVEC
#define LINX_TEST_ENABLE_SIMT_AUTOVEC 0
#endif
#ifndef LINX_TEST_ENABLE_RUNTIME
#define LINX_TEST_ENABLE_RUNTIME 0
#endif
#ifndef LINX_TEST_ENABLE_HL_CMP
#define LINX_TEST_ENABLE_HL_CMP 0
#endif
#ifndef LINX_TEST_ENABLE_SETC_IMM
#define LINX_TEST_ENABLE_SETC_IMM 0
#endif
#ifndef LINX_TEST_ENABLE_MADDW_BFI_MI
#define LINX_TEST_ENABLE_MADDW_BFI_MI 0
#endif
#ifndef LINX_TEST_ENABLE_TILE_V0586_GM_ATOM_RED
#define LINX_TEST_ENABLE_TILE_V0586_GM_ATOM_RED 0
#endif
#ifndef LINX_TEST_ENABLE_TILE_V0586_TIMG2COL
#define LINX_TEST_ENABLE_TILE_V0586_TIMG2COL 0
#endif
#ifndef LINX_TEST_ENABLE_TILE_V0583_TLSU
#define LINX_TEST_ENABLE_TILE_V0583_TLSU 0
#endif
#ifndef LINX_TEST_ENABLE_TILE_V0583_VEC
#define LINX_TEST_ENABLE_TILE_V0583_VEC 0
#endif
#ifndef LINX_TEST_ENABLE_TILE_V0583_SFU
#define LINX_TEST_ENABLE_TILE_V0583_SFU 0
#endif
#ifndef LINX_TEST_ENABLE_TILE_V0583_CUBE
#define LINX_TEST_ENABLE_TILE_V0583_CUBE 0
#endif

/* Forward declarations for test suite functions */
#if LINX_TEST_ENABLE_ARITHMETIC
void run_arithmetic_tests(void);
#endif
#if LINX_TEST_ENABLE_BITWISE
void run_bitwise_tests(void);
#endif
#if LINX_TEST_ENABLE_LOADSTORE
void run_loadstore_tests(void);
#endif
#if LINX_TEST_ENABLE_BRANCH
void run_branch_tests(void);
#endif
#if LINX_TEST_ENABLE_MOVE
void run_move_tests(void);
#endif
#if LINX_TEST_ENABLE_FLOAT
void run_float_tests(void);
#endif
#if LINX_TEST_ENABLE_ATOMIC
void run_atomic_tests(void);
#endif
#if LINX_TEST_ENABLE_JUMPTABLE
void run_jumptable_tests(void);
#endif
#if LINX_TEST_ENABLE_VARARGS
void run_varargs_tests(void);
#endif
#if LINX_TEST_ENABLE_SYSTEM
void run_system_tests(void);
#endif
#if LINX_TEST_ENABLE_CALLRET
void run_callret_tests(void);
#endif
#if LINX_TEST_ENABLE_SIMT_AUTOVEC
void run_simt_autovec_tests(void);
#endif
#if LINX_TEST_ENABLE_RUNTIME
void run_freestanding_runtime_tests(void);
#endif
#if LINX_TEST_ENABLE_HL_CMP
void run_hl_cmp_tests(void);
#endif
#if LINX_TEST_ENABLE_SETC_IMM
void run_setc_imm_tests(void);
#endif
#if LINX_TEST_ENABLE_MADDW_BFI_MI
void run_maddw_bfi_mi_tests(void);
#endif
#if LINX_TEST_ENABLE_TILE_V0586_GM_ATOM_RED
void run_tile_v0586_gm_atom_red_tests(void);
#endif
#if LINX_TEST_ENABLE_TILE_V0586_TIMG2COL
void run_tile_v0586_timg2col_tests(void);
#endif
#if LINX_TEST_ENABLE_TILE_V0583_TLSU
void run_tile_v0583_tlsu_tests(void);
#endif
#if LINX_TEST_ENABLE_TILE_V0583_VEC
void run_tile_v0583_vec_tests(void);
#endif
#if LINX_TEST_ENABLE_TILE_V0583_SFU
void run_tile_v0583_sfu_tests(void);
#endif
#if LINX_TEST_ENABLE_TILE_V0583_CUBE
void run_tile_v0583_cube_tests(void);
#endif

/*
 * Main entry point
 */
void _start(void) {
#if !LINX_TEST_QUIET
    uart_puts("Linx QEMU tests\r\n");
#endif
    
    /* Run all test suites */
#if LINX_TEST_ENABLE_ARITHMETIC
    run_arithmetic_tests();
#endif
#if LINX_TEST_ENABLE_BITWISE
    run_bitwise_tests();
#endif
#if LINX_TEST_ENABLE_LOADSTORE
    run_loadstore_tests();
#endif
#if LINX_TEST_ENABLE_BRANCH
    run_branch_tests();
#endif
#if LINX_TEST_ENABLE_MOVE
    run_move_tests();
#endif
#if LINX_TEST_ENABLE_FLOAT
    run_float_tests();
#endif
#if LINX_TEST_ENABLE_ATOMIC
    run_atomic_tests();
#endif
#if LINX_TEST_ENABLE_JUMPTABLE
    run_jumptable_tests();
#endif
#if LINX_TEST_ENABLE_VARARGS
    run_varargs_tests();
#endif
#if LINX_TEST_ENABLE_CALLRET
    run_callret_tests();
#endif
#if LINX_TEST_ENABLE_SIMT_AUTOVEC
    run_simt_autovec_tests();
#endif
#if LINX_TEST_ENABLE_RUNTIME
    run_freestanding_runtime_tests();
#endif
#if LINX_TEST_ENABLE_HL_CMP
    run_hl_cmp_tests();
#endif
#if LINX_TEST_ENABLE_SETC_IMM
    run_setc_imm_tests();
#endif
#if LINX_TEST_ENABLE_MADDW_BFI_MI
    run_maddw_bfi_mi_tests();
#endif
#if LINX_TEST_ENABLE_TILE_V0586_GM_ATOM_RED
    run_tile_v0586_gm_atom_red_tests();
#endif
#if LINX_TEST_ENABLE_TILE_V0586_TIMG2COL
    run_tile_v0586_timg2col_tests();
#endif
#if LINX_TEST_ENABLE_TILE_V0583_TLSU
    run_tile_v0583_tlsu_tests();
#endif
#if LINX_TEST_ENABLE_TILE_V0583_VEC
    run_tile_v0583_vec_tests();
#endif
#if LINX_TEST_ENABLE_TILE_V0583_SFU
    run_tile_v0583_sfu_tests();
#endif
#if LINX_TEST_ENABLE_TILE_V0583_CUBE
    run_tile_v0583_cube_tests();
#endif
#if LINX_TEST_ENABLE_SYSTEM
    /* This suite exits through its final trap continuation; keep it last. */
    run_system_tests();
#endif
    
    /* Print final summary */
#if !LINX_TEST_QUIET
    uart_puts("\r\n");
    uart_puts("=================================================\r\n");
    uart_puts("              TEST SUITE COMPLETE                \r\n");
    uart_puts("=================================================\r\n");
    uart_puts("\r\n");
    uart_puts("All tests completed successfully!\r\n");
    uart_puts("\r\n");
    uart_puts("Note: Check UART output for individual test results.\r\n");
    uart_puts("      Each test suite prints PASS for each test.\r\n");
    uart_puts("\r\n");
#else
    /* Quiet runs still need one bounded completion oracle. */
    uart_putc('L'); uart_putc('I'); uart_putc('N'); uart_putc('X');
    uart_putc(' '); uart_putc('T'); uart_putc('E'); uart_putc('S');
    uart_putc('T'); uart_putc('S'); uart_putc(' '); uart_putc('P');
    uart_putc('A'); uart_putc('S'); uart_putc('S');
    uart_putc('\r'); uart_putc('\n');
#endif
    
    linx_test_exit(0);
}
