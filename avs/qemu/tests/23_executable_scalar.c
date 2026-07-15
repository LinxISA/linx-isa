/* Dedicated per-form executable evidence for base scalar ALU and memory ops. */

#include "linx_test.h"

#include <stdint.h>

static const uint8_t load_bytes[16] __attribute__((aligned(8))) = {
    0x11, 0xfe, 0x34, 0xf2, 0xfe, 0x80, 0x34, 0xf2,
    0xef, 0xcd, 0xab, 0x89, 0x67, 0x45, 0x23, 0x01,
};
static volatile uint8_t store_bytes[24] __attribute__((aligned(8)));

__attribute__((noinline)) uint64_t executable_scalar_add(void) {
    const uint64_t left = 0x1234;
    const uint64_t right = 0x5678;
    uint64_t result;
    __asm__ volatile("add %1, %2, ->%0" : "=&r"(result) : "r"(left), "r"(right));
    return result;
}

__attribute__((noinline)) uint64_t executable_scalar_sub(void) {
    const uint64_t left = 0x9876;
    const uint64_t right = 0x1234;
    uint64_t result;
    __asm__ volatile("sub %1, %2, ->%0" : "=&r"(result) : "r"(left), "r"(right));
    return result;
}

__attribute__((noinline)) uint64_t executable_scalar_and(void) {
    const uint64_t left = 0xf0f0;
    const uint64_t right = 0x0ff0;
    uint64_t result;
    __asm__ volatile("and %1, %2, ->%0" : "=&r"(result) : "r"(left), "r"(right));
    return result;
}

__attribute__((noinline)) uint64_t executable_scalar_or(void) {
    const uint64_t left = 0xf0f0;
    const uint64_t right = 0x0ff0;
    uint64_t result;
    __asm__ volatile("or %1, %2, ->%0" : "=&r"(result) : "r"(left), "r"(right));
    return result;
}

__attribute__((noinline)) uint64_t executable_scalar_xor(void) {
    const uint64_t left = 0xaaaa;
    const uint64_t right = 0x0f0f;
    uint64_t result;
    __asm__ volatile("xor %1, %2, ->%0" : "=&r"(result) : "r"(left), "r"(right));
    return result;
}

__attribute__((noinline)) uint64_t executable_scalar_sll(void) {
    const uint64_t value = 0x123;
    const uint64_t shift = 68;
    uint64_t result;
    __asm__ volatile("sll %1, %2, ->%0" : "=&r"(result) : "r"(value), "r"(shift));
    return result;
}

__attribute__((noinline)) uint64_t executable_scalar_srl(void) {
    const uint64_t value = 0x8000000000000000ULL;
    const uint64_t shift = 68;
    uint64_t result;
    __asm__ volatile("srl %1, %2, ->%0" : "=&r"(result) : "r"(value), "r"(shift));
    return result;
}

__attribute__((noinline)) uint64_t executable_scalar_sra(void) {
    const uint64_t value = 0xffffffffffffff00ULL;
    const uint64_t shift = 68;
    uint64_t result;
    __asm__ volatile("sra %1, %2, ->%0" : "=&r"(result) : "r"(value), "r"(shift));
    return result;
}

__attribute__((noinline)) uint64_t executable_scalar_lb(void) {
    const uintptr_t base = (uintptr_t)load_bytes;
    const uint64_t offset = 1;
    uint64_t result;
    __asm__ volatile("lb [%1, %2], ->%0"
                     : "=&r"(result)
                     : "r"(base), "r"(offset)
                     : "memory");
    return result;
}

__attribute__((noinline)) uint64_t executable_scalar_lh(void) {
    const uintptr_t base = (uintptr_t)load_bytes;
    const uint64_t offset = 2;
    uint64_t result;
    __asm__ volatile("lh [%1, %2], ->%0"
                     : "=&r"(result)
                     : "r"(base), "r"(offset)
                     : "memory");
    return result;
}

__attribute__((noinline)) uint64_t executable_scalar_lw(void) {
    const uintptr_t base = (uintptr_t)load_bytes;
    const uint64_t offset = 4;
    uint64_t result;
    __asm__ volatile("lw [%1, %2], ->%0"
                     : "=&r"(result)
                     : "r"(base), "r"(offset)
                     : "memory");
    return result;
}

__attribute__((noinline)) uint64_t executable_scalar_ld(void) {
    const uintptr_t base = (uintptr_t)load_bytes;
    const uint64_t offset = 8;
    uint64_t result;
    __asm__ volatile("ld [%1, %2], ->%0"
                     : "=&r"(result)
                     : "r"(base), "r"(offset)
                     : "memory");
    return result;
}

__attribute__((noinline)) uint64_t executable_scalar_sb(void) {
    const uintptr_t base = (uintptr_t)store_bytes;
    const uint64_t offset = 1;
    const uint64_t value = 0xa5;
    store_bytes[0] = 0x11;
    store_bytes[1] = 0;
    store_bytes[2] = 0x22;
    __asm__ volatile("sb %0, [%1, %2]"
                     :
                     : "r"(value), "r"(base), "r"(offset)
                     : "memory");
    return (store_bytes[1] == 0xa5) |
           ((store_bytes[0] == 0x11) << 1) |
           ((store_bytes[2] == 0x22) << 2);
}

__attribute__((noinline)) uint64_t executable_scalar_sh(void) {
    const uintptr_t base = (uintptr_t)store_bytes;
    const uint64_t offset = 1;
    const uint64_t value = 0xb6c7;
    store_bytes[1] = 0x11;
    store_bytes[2] = 0;
    store_bytes[3] = 0;
    store_bytes[4] = 0x22;
    __asm__ volatile("sh %0, [%1, %2]"
                     :
                     : "r"(value), "r"(base), "r"(offset)
                     : "memory");
    return (store_bytes[2] == 0xc7) |
           ((store_bytes[3] == 0xb6) << 1) |
           ((store_bytes[1] == 0x11) << 2) |
           ((store_bytes[4] == 0x22) << 3);
}

__attribute__((noinline)) uint64_t executable_scalar_sw(void) {
    const uintptr_t base = (uintptr_t)store_bytes;
    const uint64_t offset = 1;
    const uint64_t value = 0xdeadbeef;
    store_bytes[3] = 0x11;
    *(volatile uint32_t *)(store_bytes + 4) = 0;
    store_bytes[8] = 0x22;
    __asm__ volatile("sw %0, [%1, %2]"
                     :
                     : "r"(value), "r"(base), "r"(offset)
                     : "memory");
    return (*(volatile uint32_t *)(store_bytes + 4) == 0xdeadbeefu) |
           ((store_bytes[3] == 0x11) << 1) |
           ((store_bytes[8] == 0x22) << 2);
}

__attribute__((noinline)) uint64_t executable_scalar_sd(void) {
    const uintptr_t base = (uintptr_t)store_bytes;
    const uint64_t offset = 1;
    const uint64_t value = 0x0123456789abcdefULL;
    store_bytes[7] = 0x11;
    *(volatile uint64_t *)(store_bytes + 8) = 0;
    store_bytes[16] = 0x22;
    __asm__ volatile("sd %0, [%1, %2]"
                     :
                     : "r"(value), "r"(base), "r"(offset)
                     : "memory");
    return (*(volatile uint64_t *)(store_bytes + 8) == value) |
           ((store_bytes[7] == 0x11) << 1) |
           ((store_bytes[16] == 0x22) << 2);
}

static void test_add(void) { TEST_EQ64(executable_scalar_add(), 0x68ac, 0x2501); }
static void test_sub(void) { TEST_EQ64(executable_scalar_sub(), 0x8642, 0x2502); }
static void test_and(void) { TEST_EQ64(executable_scalar_and(), 0x00f0, 0x2503); }
static void test_or(void) { TEST_EQ64(executable_scalar_or(), 0xfff0, 0x2504); }
static void test_xor(void) { TEST_EQ64(executable_scalar_xor(), 0xa5a5, 0x2505); }
static void test_sll(void) { TEST_EQ64(executable_scalar_sll(), 0x1230, 0x2506); }
static void test_srl(void) {
    TEST_EQ64(executable_scalar_srl(), 0x0800000000000000ULL, 0x2507);
}
static void test_sra(void) {
    TEST_EQ64(executable_scalar_sra(), 0xfffffffffffffff0ULL, 0x2508);
}
static void test_lb(void) {
    TEST_EQ64(executable_scalar_lb(), 0xfffffffffffffffeULL, 0x2509);
}
static void test_lh(void) {
    TEST_EQ64(executable_scalar_lh(), 0xfffffffffffff234ULL, 0x250a);
}
static void test_lw(void) {
    TEST_EQ64(executable_scalar_lw(), 0xfffffffff23480feULL, 0x250b);
}
static void test_ld(void) {
    TEST_EQ64(executable_scalar_ld(), 0x0123456789abcdefULL, 0x250c);
}
static void test_sb(void) { TEST_EQ64(executable_scalar_sb(), 0x7, 0x250d); }
static void test_sh(void) { TEST_EQ64(executable_scalar_sh(), 0xf, 0x250e); }
static __attribute__((noinline)) void test_sw(void) {
    TEST_EQ64(executable_scalar_sw(), 0x7, 0x250f);
}
static void test_sd(void) { TEST_EQ64(executable_scalar_sd(), 0x7, 0x2510); }

__attribute__((optnone)) void run_arithmetic_tests(void) {
    test_suite_begin(0x2500);
    RUN_TEST(test_add, 0x2501);
    RUN_TEST(test_sub, 0x2502);
    RUN_TEST(test_and, 0x2503);
    RUN_TEST(test_or, 0x2504);
    RUN_TEST(test_xor, 0x2505);
    RUN_TEST(test_sll, 0x2506);
    RUN_TEST(test_srl, 0x2507);
    RUN_TEST(test_sra, 0x2508);
    RUN_TEST(test_lb, 0x2509);
    RUN_TEST(test_lh, 0x250a);
    RUN_TEST(test_lw, 0x250b);
    RUN_TEST(test_ld, 0x250c);
    RUN_TEST(test_sb, 0x250d);
    RUN_TEST(test_sh, 0x250e);
    RUN_TEST(test_sw, 0x250f);
    RUN_TEST(test_sd, 0x2510);
    test_suite_end(16, 16);
}
