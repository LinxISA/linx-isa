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
#ifndef LINX_TEST_ENABLE_TILE
#define LINX_TEST_ENABLE_TILE 0
#endif
#ifndef LINX_TEST_ENABLE_SYSTEM
#define LINX_TEST_ENABLE_SYSTEM 1
#endif
#ifndef LINX_TEST_ENABLE_V03_VECTOR
#define LINX_TEST_ENABLE_V03_VECTOR 0
#endif
#ifndef LINX_TEST_ENABLE_V03_VECTOR_OPS
#define LINX_TEST_ENABLE_V03_VECTOR_OPS 0
#endif
#ifndef LINX_TEST_ENABLE_V03_VECTOR_BODY_FAULT
#define LINX_TEST_ENABLE_V03_VECTOR_BODY_FAULT 0
#endif
#ifndef LINX_TEST_ENABLE_CALLRET
#define LINX_TEST_ENABLE_CALLRET 0
#endif
#ifndef LINX_TEST_ENABLE_PTO_PARITY
#define LINX_TEST_ENABLE_PTO_PARITY 0
#endif
#ifndef LINX_TEST_ENABLE_SIMT_AUTOVEC
#define LINX_TEST_ENABLE_SIMT_AUTOVEC 0
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
#if LINX_TEST_ENABLE_TILE
void run_tile_tests(void);
#endif
#if LINX_TEST_ENABLE_SYSTEM
void run_system_tests(void);
#endif
#if LINX_TEST_ENABLE_V03_VECTOR
void run_v03_vector_tile_tests(void);
#endif
#if LINX_TEST_ENABLE_V03_VECTOR_OPS
void run_v03_vector_ops_matrix_tests(void);
#endif
#if LINX_TEST_ENABLE_V03_VECTOR_BODY_FAULT
void run_v03_vector_body_fault_tests(void);
#endif
#if LINX_TEST_ENABLE_CALLRET
void run_callret_tests(void);
#endif
#if LINX_TEST_ENABLE_PTO_PARITY
void run_pto_parity_tests(void);
#endif
#if LINX_TEST_ENABLE_SIMT_AUTOVEC
void run_simt_autovec_tests(void);
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
#if LINX_TEST_ENABLE_TILE
    run_tile_tests();
#endif
#if LINX_TEST_ENABLE_SYSTEM
    run_system_tests();
#endif
#if LINX_TEST_ENABLE_V03_VECTOR
    run_v03_vector_tile_tests();
#endif
#if LINX_TEST_ENABLE_V03_VECTOR_OPS
    run_v03_vector_ops_matrix_tests();
#endif
#if LINX_TEST_ENABLE_V03_VECTOR_BODY_FAULT
    run_v03_vector_body_fault_tests();
#endif
#if LINX_TEST_ENABLE_CALLRET
    run_callret_tests();
#endif
#if LINX_TEST_ENABLE_PTO_PARITY
    run_pto_parity_tests();
#endif
#if LINX_TEST_ENABLE_SIMT_AUTOVEC
    run_simt_autovec_tests();
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
#endif
    
    linx_test_exit(0);
}
