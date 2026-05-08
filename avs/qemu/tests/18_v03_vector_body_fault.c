#include "linx_test.h"
#include <stdint.h>

/*
 * Dedicated negative regression for in-body branch containment.
 *
 * This suite intentionally uses a no-return trap/exit chain, so keep it as a
 * standalone lane rather than folding it into the normal v0.56 vector smoke.
 */

enum {
    SSR_CONT_EXIT = 0x0035,
    SSR_LAST_TRAPNO = 0x0036,
    SSR_LAST_TRAPARG0 = 0x0037,
    SSR_LAST_EBARG_TPC = 0x0038,
    SSR_LAST_ECSTATE = 0x0039,

    SSR_ECSTATE_ACR0 = 0x0F00,
    SSR_EVBASE_ACR0 = 0x0F01,
    SSR_EBARG_BPC_CUR_ACR0 = 0x0F41,

    SSR_ECSTATE_ACR1 = 0x1F00,
    SSR_EVBASE_ACR1 = 0x1F01,
    SSR_TRAPNO_ACR1 = 0x1F02,
    SSR_TRAPARG0_ACR1 = 0x1F03,
    SSR_ETEMP0_ACR1 = 0x1F06,
    SSR_EBARG_BPC_CUR_ACR1 = 0x1F41,
    SSR_EBARG_TPC_ACR1 = 0x1F43,
};

enum {
    TESTID_V03_BODY_BFETCH = 0x1280,
};

#define CSTATE_ACR_MASK 0xFull
#define CSTATE_BI_BIT (1ull << 62)

static inline uint64_t trapno_is_async(uint64_t trapno) { return (trapno >> 63) & 1ull; }
static inline uint64_t trapno_has_argv(uint64_t trapno) { return (trapno >> 62) & 1ull; }
static inline uint64_t trapno_cause(uint64_t trapno) { return (trapno >> 24) & 0xFFFFFFull; }
static inline uint64_t trapno_trapnum(uint64_t trapno) { return trapno & 0x3Full; }

static inline uint64_t ssrget_uimm(uint32_t ssrid)
{
    uint64_t out;
    __asm__ volatile("ssrget %1, ->%0" : "=r"(out) : "i"(ssrid) : "memory");
    return out;
}

static inline void ssrset_uimm(uint32_t ssrid, uint64_t value)
{
    __asm__ volatile("ssrset %0, %1" : : "r"(value), "i"(ssrid) : "memory");
}

static inline void hl_ssrset_uimm24(uint32_t ssrid, uint64_t value)
{
    __asm__ volatile("hl.ssrset %0, %1" : : "r"(value), "i"(ssrid) : "memory");
}

extern void linx_v03_body_fault_user(void);
extern void linx_v03_body_fault_resume_to_exit(void);
extern void linx_v03_body_fault_acr0_exit_handler(void);
extern void linx_v03_body_fault_acr1_record_trap_handler(void);
extern void __linx_v03_escape_body_branch(void);
extern void __linx_v03_escape_body_end(void);

__attribute__((noreturn)) static void linx_after_v03_body_bfetch_exit(void);

__asm__(
    ".p2align 3\n"
    ".globl __linx_v03_escape_body\n"
    ".globl __linx_v03_escape_body_branch\n"
    ".globl __linx_v03_escape_body_end\n"
    "__linx_v03_escape_body:\n"
    "  v.cmp.ltui lc0.ud, 1, ->p\n"
    "__linx_v03_escape_body_branch:\n"
    "  b.nz 3\n"
    "  C.BSTOP\n"
    "__linx_v03_escape_body_end:\n");

__asm__(
    ".globl linx_v03_body_fault_user\n"
    "linx_v03_body_fault_user:\n"
    "  C.BSTART\n"
    "  BSTART.MSEQ 0\n"
    "  B.TEXT __linx_v03_escape_body\n"
    "  C.B.DIMI 1, ->lb0\n"
    "  C.BSTART\n"
    "  ebreak 0\n");

__asm__(
    ".globl linx_v03_body_fault_resume_to_exit\n"
    "linx_v03_body_fault_resume_to_exit:\n"
    "  C.BSTART\n"
    "  acrc 0\n"
    "  C.BSTOP\n");

__asm__(
    ".globl linx_v03_body_fault_acr0_exit_handler\n"
    "linx_v03_body_fault_acr0_exit_handler:\n"
    "  C.BSTART\n"
    "  addi zero, 0, ->a1\n"
    "  ssrset a1, 0x0f00\n"
    "  ssrget 0x0035, ->a0\n"
    "  ssrset a0, 0x0f41\n"
    "  ssrset a0, 0x0f43\n"
    "  acre 0\n");

__asm__(
    ".globl linx_v03_body_fault_acr1_record_trap_handler\n"
    "linx_v03_body_fault_acr1_record_trap_handler:\n"
    "  C.BSTART\n"
    "  hl.ssrget 0x1f02, ->a0\n"
    "  hl.ssrget 0x1f03, ->a1\n"
    "  hl.ssrget 0x1f43, ->a2\n"
    "  hl.ssrget 0x1f00, ->a4\n"
    "  ssrset a0, 0x0036\n"
    "  ssrset a1, 0x0037\n"
    "  ssrset a2, 0x0038\n"
    "  ssrset a4, 0x0039\n"
    "  hl.ssrget 0x1f06, ->a3\n"
    "  hl.ssrset a3, 0x1f41\n"
    "  hl.ssrset a3, 0x1f43\n"
    "  acre 0\n");

void run_v03_vector_body_fault_tests(void)
{
    test_start(TESTID_V03_BODY_BFETCH);
    uart_puts("v0.56 in-body branch escape traps E_BLOCK(EC_BFETCH) ... ");

    ssrset_uimm(SSR_LAST_TRAPNO, 0);
    ssrset_uimm(SSR_LAST_TRAPARG0, 0);
    ssrset_uimm(SSR_LAST_EBARG_TPC, 0);
    ssrset_uimm(SSR_LAST_ECSTATE, 0);
    hl_ssrset_uimm24(SSR_ETEMP0_ACR1,
                     (uint64_t)(uintptr_t)&linx_v03_body_fault_resume_to_exit);
    ssrset_uimm(SSR_CONT_EXIT,
                (uint64_t)(uintptr_t)&linx_after_v03_body_bfetch_exit);
    hl_ssrset_uimm24(SSR_EVBASE_ACR1,
                     (uint64_t)(uintptr_t)&linx_v03_body_fault_acr1_record_trap_handler);
    ssrset_uimm(SSR_EVBASE_ACR0,
                (uint64_t)(uintptr_t)&linx_v03_body_fault_acr0_exit_handler);
    ssrset_uimm(SSR_ECSTATE_ACR0, 2);
    ssrset_uimm(SSR_EBARG_BPC_CUR_ACR0,
                (uint64_t)(uintptr_t)&linx_v03_body_fault_user);
    __asm__ volatile("acre 0" : : : "memory");
    __builtin_unreachable();
}

__attribute__((noreturn)) static void linx_after_v03_body_bfetch_exit(void)
{
    const uint64_t trapno = ssrget_uimm(SSR_LAST_TRAPNO);
    const uint64_t traparg0 = ssrget_uimm(SSR_LAST_TRAPARG0);
    const uint64_t ebarg_tpc = ssrget_uimm(SSR_LAST_EBARG_TPC);
    const uint64_t ecstate = ssrget_uimm(SSR_LAST_ECSTATE);
    const uint64_t expected_target =
        (uint64_t)(uintptr_t)&__linx_v03_escape_body_end;
    const uint64_t expected_resume_tpc =
        (uint64_t)(uintptr_t)&__linx_v03_escape_body_branch;

    TEST_EQ64(trapno_is_async(trapno), 0, TESTID_V03_BODY_BFETCH + 1);
    TEST_EQ64(trapno_has_argv(trapno), 1, TESTID_V03_BODY_BFETCH + 2);
    TEST_EQ64(trapno_trapnum(trapno), 5, TESTID_V03_BODY_BFETCH + 3);
    TEST_EQ64(trapno_cause(trapno), 0x300, TESTID_V03_BODY_BFETCH + 4);
    TEST_EQ64(traparg0, expected_target, TESTID_V03_BODY_BFETCH + 5);
    TEST_EQ64(ebarg_tpc, expected_resume_tpc, TESTID_V03_BODY_BFETCH + 6);
    TEST_EQ64(ecstate & CSTATE_ACR_MASK, 2, TESTID_V03_BODY_BFETCH + 7);
    TEST_EQ64((ecstate & CSTATE_BI_BIT) != 0, 1, TESTID_V03_BODY_BFETCH + 8);

    test_pass();
    uart_puts("\r\n");
    uart_puts("=================================================\r\n");
    uart_puts("              TEST SUITE COMPLETE                \r\n");
    uart_puts("=================================================\r\n");
    uart_puts("\r\n");
    uart_puts("All tests completed successfully!\r\n");
    uart_puts("\r\n");
    uart_puts("*** REGRESSION PASSED ***\r\n");
    EXIT_CODE = 0;
    while (1) {
    }
}
