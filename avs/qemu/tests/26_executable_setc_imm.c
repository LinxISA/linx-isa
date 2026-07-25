/* Dedicated executable evidence for SETC immediate commit-argument forms. */

#include "linx_test.h"

#include <stdint.h>

#define TRUE_PATH 0x29u
#define FALSE_PATH 0x16u

#define DEFINE_SETC_IMM_BRANCH(NAME, ASM_OP, TRUE_IMM, FALSE_IMM, TRUE_LHS, FALSE_LHS) \
    __attribute__((noinline, optnone)) uint64_t executable_setc_imm_##NAME(void) { \
        const uint64_t true_lhs = (TRUE_LHS);                                  \
        const uint64_t false_lhs = (FALSE_LHS);                                \
        uint64_t true_result;                                                  \
        uint64_t false_result;                                                 \
        __asm__ volatile(                                                      \
            "  C.BSTART\n"                                                     \
            "  " ASM_OP " %1, " TRUE_IMM "\n"                                \
            "  C.BSTART DIRECT, 1f\n"                                         \
            "  C.BSTART COND, 2f\n"                                           \
            "1:\n"                                                            \
            "  C.BSTART\n"                                                     \
            "  addi zero, 22, ->%0\n"                                         \
            "  C.BSTART DIRECT, 3f\n"                                         \
            "2:\n"                                                            \
            "  C.BSTART\n"                                                     \
            "  addi zero, 41, ->%0\n"                                         \
            "3:\n"                                                            \
            "  C.BSTART\n"                                                     \
            : "=&r"(true_result)                                               \
            : "r"(true_lhs)                                                    \
            : "memory");                                                       \
        __asm__ volatile(                                                      \
            "  C.BSTART\n"                                                     \
            "  " ASM_OP " %1, " FALSE_IMM "\n"                               \
            "  C.BSTART DIRECT, 1f\n"                                         \
            "  C.BSTART COND, 2f\n"                                           \
            "1:\n"                                                            \
            "  C.BSTART\n"                                                     \
            "  addi zero, 22, ->%0\n"                                         \
            "  C.BSTART DIRECT, 3f\n"                                         \
            "2:\n"                                                            \
            "  C.BSTART\n"                                                     \
            "  addi zero, 41, ->%0\n"                                         \
            "3:\n"                                                            \
            "  C.BSTART\n"                                                     \
            : "=&r"(false_result)                                              \
            : "r"(false_lhs)                                                   \
            : "memory");                                                       \
        return (true_result == TRUE_PATH) | ((false_result == FALSE_PATH) << 1); \
    }

DEFINE_SETC_IMM_BRANCH(setc_andi, "setc.andi", "4096", "4096",
                       0x1000ULL, 0x2000ULL)
DEFINE_SETC_IMM_BRANCH(setc_ori, "setc.ori", "4096", "0",
                       0x0ULL, 0x0ULL)
DEFINE_SETC_IMM_BRANCH(hl_setc_andi, "hl.setc.andi", "5, 74565", "5, 74565",
                       0x2468a0ULL, 0x400000ULL)
DEFINE_SETC_IMM_BRANCH(hl_setc_eqi, "hl.setc.eqi", "5, 74565", "5, 74565",
                       0x2468a0ULL, 0x2468c0ULL)
DEFINE_SETC_IMM_BRANCH(hl_setc_gei, "hl.setc.gei", "5, -74565", "5, -74565",
                       0xffffffffffdb9760ULL,
                       0xffffffffffdb975fULL)
DEFINE_SETC_IMM_BRANCH(hl_setc_geui, "hl.setc.geui", "5, 74565", "5, 74565",
                       0x2468a0ULL, 0x24689fULL)
DEFINE_SETC_IMM_BRANCH(hl_setc_lti, "hl.setc.lti", "5, -74565", "5, -74565",
                       0xffffffffffdb975fULL,
                       0xffffffffffdb9760ULL)
DEFINE_SETC_IMM_BRANCH(hl_setc_ltui, "hl.setc.ltui", "5, 74565", "5, 74565",
                       0x24689fULL, 0x2468a0ULL)
DEFINE_SETC_IMM_BRANCH(hl_setc_nei, "hl.setc.nei", "5, -74565", "5, -74565",
                       0x0ULL,
                       0xffffffffffdb9760ULL)
DEFINE_SETC_IMM_BRANCH(hl_setc_ori, "hl.setc.ori", "5, 74565", "0, 0", 0x0ULL,
                       0x0ULL)

static void test_setc_andi(void) {
    TEST_EQ64(executable_setc_imm_setc_andi(), 0x3, 0x2801);
}
static void test_setc_ori(void) {
    TEST_EQ64(executable_setc_imm_setc_ori(), 0x3, 0x2802);
}
static void test_hl_setc_andi(void) {
    TEST_EQ64(executable_setc_imm_hl_setc_andi(), 0x3, 0x2803);
}
static void test_hl_setc_eqi(void) {
    TEST_EQ64(executable_setc_imm_hl_setc_eqi(), 0x3, 0x2804);
}
static void test_hl_setc_gei(void) {
    TEST_EQ64(executable_setc_imm_hl_setc_gei(), 0x3, 0x2805);
}
static void test_hl_setc_geui(void) {
    TEST_EQ64(executable_setc_imm_hl_setc_geui(), 0x3, 0x2806);
}
static void test_hl_setc_lti(void) {
    TEST_EQ64(executable_setc_imm_hl_setc_lti(), 0x3, 0x2807);
}
static void test_hl_setc_ltui(void) {
    TEST_EQ64(executable_setc_imm_hl_setc_ltui(), 0x3, 0x2808);
}
static void test_hl_setc_nei(void) {
    TEST_EQ64(executable_setc_imm_hl_setc_nei(), 0x3, 0x2809);
}
static void test_hl_setc_ori(void) {
    TEST_EQ64(executable_setc_imm_hl_setc_ori(), 0x3, 0x280a);
}

__attribute__((optnone)) void run_setc_imm_tests(void) {
    test_suite_begin(0x2800);
    RUN_TEST(test_setc_andi, 0x2801);
    RUN_TEST(test_setc_ori, 0x2802);
    RUN_TEST(test_hl_setc_andi, 0x2803);
    RUN_TEST(test_hl_setc_eqi, 0x2804);
    RUN_TEST(test_hl_setc_gei, 0x2805);
    RUN_TEST(test_hl_setc_geui, 0x2806);
    RUN_TEST(test_hl_setc_lti, 0x2807);
    RUN_TEST(test_hl_setc_ltui, 0x2808);
    RUN_TEST(test_hl_setc_nei, 0x2809);
    RUN_TEST(test_hl_setc_ori, 0x280a);
    test_suite_end(10, 10);
}
