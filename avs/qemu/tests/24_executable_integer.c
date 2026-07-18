/* Dedicated per-form executable evidence for common integer C operations. */

#include "linx_test.h"

#include <stdint.h>

static const uint8_t unsigned_load_bytes[16] __attribute__((aligned(8))) = {
    0x11, 0xfe, 0xcd, 0xab, 0xef, 0xcd, 0xab, 0x89,
    0x67, 0x45, 0x23, 0x01, 0, 0, 0, 0,
};

__attribute__((noinline)) uint64_t executable_integer_lbu(void) {
    const uintptr_t base = (uintptr_t)unsigned_load_bytes;
    const uint64_t offset = 1;
    uint64_t result;
    __asm__ volatile("lbu [%1, %2], ->%0"
                     : "=&r"(result)
                     : "r"(base), "r"(offset)
                     : "memory");
    return result;
}

__attribute__((noinline)) uint64_t executable_integer_lhu(void) {
    const uintptr_t base = (uintptr_t)unsigned_load_bytes;
    const uint64_t offset = 2;
    uint64_t result;
    __asm__ volatile("lhu [%1, %2], ->%0"
                     : "=&r"(result)
                     : "r"(base), "r"(offset)
                     : "memory");
    return result;
}

__attribute__((noinline)) uint64_t executable_integer_lwu(void) {
    const uintptr_t base = (uintptr_t)unsigned_load_bytes;
    const uint64_t offset = 4;
    uint64_t result;
    __asm__ volatile("lwu [%1, %2], ->%0"
                     : "=&r"(result)
                     : "r"(base), "r"(offset)
                     : "memory");
    return result;
}

#define DEFINE_BINARY(NAME, ASM, LEFT, RIGHT)                    \
    __attribute__((noinline)) uint64_t executable_integer_##NAME(void) { \
        const uint64_t left = (LEFT);                            \
        const uint64_t right = (RIGHT);                          \
        uint64_t result;                                         \
        __asm__ volatile(ASM " %1, %2, ->%0"                    \
                         : "=&r"(result)                         \
                         : "r"(left), "r"(right));              \
        return result;                                           \
    }

DEFINE_BINARY(mul, "mul", 0xfffffffffffffff9ULL, 13)
DEFINE_BINARY(div, "div", 0xffffffffffffff9cULL, 7)
DEFINE_BINARY(divu, "divu", 0xfffffffffffffff0ULL, 16)
DEFINE_BINARY(rem, "rem", 0xffffffffffffff9cULL, 7)
DEFINE_BINARY(remu, "remu", 100, 7)
DEFINE_BINARY(cmp_eq, "cmp.eq", 0x123456789abcdef0ULL, 0x123456789abcdef0ULL)
DEFINE_BINARY(cmp_ne, "cmp.ne", 0x123456789abcdef0ULL, 0x123456789abcdef1ULL)
DEFINE_BINARY(cmp_lt, "cmp.lt", 0xffffffffffffffffULL, 1)
DEFINE_BINARY(cmp_ltu, "cmp.ltu", 0xffffffffffffffffULL, 1)
DEFINE_BINARY(cmp_ge, "cmp.ge", 0xffffffffffffffffULL, 1)
DEFINE_BINARY(cmp_geu, "cmp.geu", 0xffffffffffffffffULL, 1)

__attribute__((noinline)) uint64_t executable_integer_csel(uint64_t pred) {
    const uint64_t when_true = 0x1111222233334444ULL;
    const uint64_t when_false = 0xaaaabbbbccccddddULL;
    uint64_t result;
    __asm__ volatile("csel %1, %2, %3, ->%0"
                     : "=&r"(result)
                     : "r"(pred), "r"(when_true), "r"(when_false));
    return result;
}

static void test_lbu(void) { TEST_EQ64(executable_integer_lbu(), 0xfe, 0x2601); }
static void test_lhu(void) { TEST_EQ64(executable_integer_lhu(), 0xabcd, 0x2602); }
static void test_lwu(void) {
    TEST_EQ64(executable_integer_lwu(), 0x89abcdefULL, 0x2603);
}
static void test_mul(void) {
    TEST_EQ64(executable_integer_mul(), 0xffffffffffffffa5ULL, 0x2604);
}
static void test_div(void) {
    TEST_EQ64(executable_integer_div(), 0xfffffffffffffff2ULL, 0x2605);
}
static void test_divu(void) {
    TEST_EQ64(executable_integer_divu(), 0x0fffffffffffffffULL, 0x2606);
}
static void test_rem(void) {
    TEST_EQ64(executable_integer_rem(), 0xfffffffffffffffeULL, 0x2607);
}
static void test_remu(void) { TEST_EQ64(executable_integer_remu(), 0x2, 0x2608); }
static void test_cmp_eq(void) { TEST_EQ64(executable_integer_cmp_eq(), 0x1, 0x2609); }
static void test_cmp_ne(void) { TEST_EQ64(executable_integer_cmp_ne(), 0x1, 0x260a); }
static void test_cmp_lt(void) { TEST_EQ64(executable_integer_cmp_lt(), 0x1, 0x260b); }
static void test_cmp_ltu(void) { TEST_EQ64(executable_integer_cmp_ltu(), 0x0, 0x260c); }
static void test_cmp_ge(void) { TEST_EQ64(executable_integer_cmp_ge(), 0x0, 0x260d); }
static void test_cmp_geu(void) { TEST_EQ64(executable_integer_cmp_geu(), 0x1, 0x260e); }
static void test_csel(void) {
    const uint64_t true_result = executable_integer_csel(1);
    const uint64_t false_result = executable_integer_csel(0);
    const uint64_t result =
        (true_result == 0x1111222233334444ULL) |
        ((false_result == 0xaaaabbbbccccddddULL) << 1);
    TEST_EQ64(result, 0x3, 0x260f);
}

__attribute__((optnone)) void run_move_tests(void) {
    test_suite_begin(0x2600);
    RUN_TEST(test_lbu, 0x2601);
    RUN_TEST(test_lhu, 0x2602);
    RUN_TEST(test_lwu, 0x2603);
    RUN_TEST(test_mul, 0x2604);
    RUN_TEST(test_div, 0x2605);
    RUN_TEST(test_divu, 0x2606);
    RUN_TEST(test_rem, 0x2607);
    RUN_TEST(test_remu, 0x2608);
    RUN_TEST(test_cmp_eq, 0x2609);
    RUN_TEST(test_cmp_ne, 0x260a);
    RUN_TEST(test_cmp_lt, 0x260b);
    RUN_TEST(test_cmp_ltu, 0x260c);
    RUN_TEST(test_cmp_ge, 0x260d);
    RUN_TEST(test_cmp_geu, 0x260e);
    RUN_TEST(test_csel, 0x260f);
    test_suite_end(15, 15);
}
