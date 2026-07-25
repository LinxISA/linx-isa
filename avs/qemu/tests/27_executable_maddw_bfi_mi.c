/* Dedicated executable evidence for MADDW, HL.BFI, HL.MIADD, and HL.MISUB. */

#include "linx_test.h"

#include <stdint.h>

__attribute__((noinline)) uint64_t executable_maddw(void) {
    const uint64_t lhs = 0xffffffffULL;
    const uint64_t rhs = 2;
    const uint64_t acc = 0x80000002ULL;
    uint64_t out;
    __asm__ volatile("maddw %1, %2, %3, ->%0"
                     : "=&r"(out)
                     : "r"(lhs), "r"(rhs), "r"(acc));
    return out;
}

__attribute__((noinline)) uint64_t executable_hl_bfi(void) {
    const uint64_t base = 0xffff000000000000ULL;
    const uint64_t src = 0x123456789abcdef0ULL;
    uint64_t out;
    __asm__ volatile("hl.bfi %1, %2, 12, 19, ->%0"
                     : "=&r"(out)
                     : "r"(base), "r"(src));
    return out;
}

__attribute__((noinline)) uint64_t executable_hl_miadd(void) {
    const uint64_t lhs = 0x0123456789abcdefULL;
    const uint64_t rhs = 0x100000003ULL;
    uint64_t out;
    __asm__ volatile("hl.miadd %1, %2, 344865, ->%0"
                     : "=&r"(out)
                     : "r"(lhs), "r"(rhs));
    return out;
}

__attribute__((noinline)) uint64_t executable_hl_misub(void) {
    const uint64_t lhs = 0x0123456789abcdefULL;
    const uint64_t rhs = 0x100000003ULL;
    uint64_t out;
    __asm__ volatile("hl.misub %1, %2, 344865, ->%0"
                     : "=&r"(out)
                     : "r"(lhs), "r"(rhs));
    return out;
}

static void test_maddw(void) {
    TEST_EQ64(executable_maddw(), 0xffffffff80000000ULL, 0x2901);
}

static void test_hl_bfi(void) {
    TEST_EQ64(executable_hl_bfi(), 0xffff0000000f0000ULL, 0x2902);
}

static void test_hl_miadd(void) {
    TEST_EQ64(executable_hl_miadd(), 0x0128888889bb9752ULL, 0x2903);
}

static void test_hl_misub(void) {
    TEST_EQ64(executable_hl_misub(), 0x011e0246899c048cULL, 0x2904);
}

__attribute__((optnone)) void run_maddw_bfi_mi_tests(void) {
    test_suite_begin(0x2900);
    RUN_TEST(test_maddw, 0x2901);
    RUN_TEST(test_hl_bfi, 0x2902);
    RUN_TEST(test_hl_miadd, 0x2903);
    RUN_TEST(test_hl_misub, 0x2904);
    test_suite_end(4, 4);
}
