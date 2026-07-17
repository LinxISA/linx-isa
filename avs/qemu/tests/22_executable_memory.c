/* Dedicated per-form executable evidence for v0.57 HL memory operations. */

#include "linx_test.h"

#include <stdint.h>

static const uint32_t load_words[2] = {0x12345678u, 0x9abcdef0u};
static const uint64_t load_dwords[2] = {
    0x0123456789abcdefULL,
    0xdeadbeefcafebabeULL,
};
static uint32_t store_words[4];
static uint64_t store_dwords[2];

__attribute__((noinline)) uint64_t executable_memory_hl_lwui_po(void) {
    const uintptr_t base = (uintptr_t)load_words;
    uint64_t value = 0;
    uint64_t writeback = 0;
    __asm__ volatile("hl.lwui.po [%2, 4], ->%0, %1"
                     : "=r"(value), "=r"(writeback)
                     : "r"(base)
                     : "memory");
    return (value == 0x12345678ULL) | ((writeback == base + 4u) << 1);
}

__attribute__((noinline)) uint64_t executable_memory_hl_lwui_pr(void) {
    const uintptr_t base = (uintptr_t)load_words;
    uint64_t value = 0;
    uint64_t writeback = 0;
    __asm__ volatile("hl.lwui.pr [%2, 4], ->%0, %1"
                     : "=r"(value), "=r"(writeback)
                     : "r"(base)
                     : "memory");
    return (value == 0x9abcdef0ULL) | ((writeback == base + 4u) << 1);
}

__attribute__((noinline)) uint64_t executable_memory_hl_lwui_upo(void) {
    const uintptr_t base = (uintptr_t)load_words;
    uint64_t value = 0;
    uint64_t writeback = 0;
    __asm__ volatile("hl.lwui.upo [%2, 4], ->%0, %1"
                     : "=r"(value), "=r"(writeback)
                     : "r"(base)
                     : "memory");
    return (value == 0x12345678ULL) | ((writeback == base + 4u) << 1);
}

__attribute__((noinline)) uint64_t executable_memory_hl_lwui_upr(void) {
    const uintptr_t base = (uintptr_t)load_words;
    uint64_t value = 0;
    uint64_t writeback = 0;
    __asm__ volatile("hl.lwui.upr [%2, 4], ->%0, %1"
                     : "=r"(value), "=r"(writeback)
                     : "r"(base)
                     : "memory");
    return (value == 0x9abcdef0ULL) | ((writeback == base + 4u) << 1);
}

__attribute__((noinline)) uint64_t executable_memory_hl_swi_po(void) {
    const uintptr_t base = (uintptr_t)store_words;
    const uint64_t value = 0xaabbccddULL;
    uint64_t writeback = 0;
    store_words[0] = 0;
    store_words[1] = 0;
    __asm__ volatile("hl.swi.po %1, [%2, 4], ->%0"
                     : "=&r"(writeback)
                     : "r"(value), "r"(base)
                     : "memory");
    return (store_words[0] == 0xaabbccddu) | ((writeback == base + 4u) << 1);
}

__attribute__((noinline)) uint64_t executable_memory_hl_swi_pr(void) {
    const uintptr_t base = (uintptr_t)store_words;
    const uint64_t value = 0x11223344ULL;
    uint64_t writeback = 0;
    store_words[0] = 0;
    store_words[1] = 0;
    __asm__ volatile("hl.swi.pr %1, [%2, 4], ->%0"
                     : "=&r"(writeback)
                     : "r"(value), "r"(base)
                     : "memory");
    return (store_words[1] == 0x11223344u) | ((writeback == base + 4u) << 1);
}

__attribute__((noinline)) uint64_t executable_memory_hl_swi_upo(void) {
    const uintptr_t base = (uintptr_t)store_words;
    const uint64_t value = 0x55667788ULL;
    uint64_t writeback = 0;
    store_words[0] = 0;
    store_words[1] = 0;
    __asm__ volatile("hl.swi.upo %1, [%2, 4], ->%0"
                     : "=&r"(writeback)
                     : "r"(value), "r"(base)
                     : "memory");
    return (store_words[0] == 0x55667788u) | ((writeback == base + 4u) << 1);
}

__attribute__((noinline)) uint64_t executable_memory_hl_swi_upr(void) {
    const uintptr_t base = (uintptr_t)store_words;
    const uint64_t value = 0x99aabbccULL;
    uint64_t writeback = 0;
    store_words[0] = 0;
    store_words[1] = 0;
    __asm__ volatile("hl.swi.upr %1, [%2, 4], ->%0"
                     : "=&r"(writeback)
                     : "r"(value), "r"(base)
                     : "memory");
    return (store_words[1] == 0x99aabbccu) | ((writeback == base + 4u) << 1);
}

__attribute__((noinline)) uint64_t executable_memory_hl_lwuip(void) {
    const uintptr_t base = (uintptr_t)load_words;
    uint64_t first = 0;
    uint64_t second = 0;
    __asm__ volatile("hl.lwuip [%2, 0], ->%0, %1"
                     : "=r"(first), "=r"(second)
                     : "r"(base)
                     : "memory");
    return (first == 0x12345678ULL) | ((second == 0x9abcdef0ULL) << 1);
}

__attribute__((noinline)) uint64_t executable_memory_hl_swip(void) {
    const uintptr_t base = (uintptr_t)store_words;
    const uint64_t first = 0x01020304ULL;
    const uint64_t second = 0xa0b0c0d0ULL;
    store_words[0] = 0;
    store_words[1] = 0;
    __asm__ volatile("hl.swip %0, %1, [%2, 0]"
                     :
                     : "r"(first), "r"(second), "r"(base)
                     : "memory");
    return (store_words[0] == 0x01020304u) | ((store_words[1] == 0xa0b0c0d0u) << 1);
}

__attribute__((noinline)) uint64_t executable_memory_hl_swip_u(void) {
    const uintptr_t base = (uintptr_t)store_words;
    const uint64_t first = 0x0a0b0c0dULL;
    const uint64_t second = 0xeeff0011ULL;
    store_words[2] = 0;
    store_words[3] = 0;
    __asm__ volatile("hl.swip.u %0, %1, [%2, 8]"
                     :
                     : "r"(first), "r"(second), "r"(base)
                     : "memory");
    return (store_words[2] == 0x0a0b0c0du) | ((store_words[3] == 0xeeff0011u) << 1);
}

__attribute__((noinline)) uint64_t executable_memory_hl_ldip(void) {
    const uintptr_t base = (uintptr_t)load_dwords;
    uint64_t first = 0;
    uint64_t second = 0;
    __asm__ volatile("hl.ldip [%2, 0], ->%0, %1"
                     : "=r"(first), "=r"(second)
                     : "r"(base)
                     : "memory");
    return (first == 0x0123456789abcdefULL) |
           ((second == 0xdeadbeefcafebabeULL) << 1);
}

__attribute__((noinline)) uint64_t executable_memory_hl_sdip(void) {
    const uintptr_t base = (uintptr_t)store_dwords;
    const uint64_t first = 0x1122334455667788ULL;
    const uint64_t second = 0x8877665544332211ULL;
    store_dwords[0] = 0;
    store_dwords[1] = 0;
    __asm__ volatile("hl.sdip %0, %1, [%2, 0]"
                     :
                     : "r"(first), "r"(second), "r"(base)
                     : "memory");
    return (store_dwords[0] == 0x1122334455667788ULL) |
           ((store_dwords[1] == 0x8877665544332211ULL) << 1);
}

static void test_hl_lwui_po(void) {
    TEST_EQ64(executable_memory_hl_lwui_po(), 0x3, 0x2201);
}

static void test_hl_lwui_pr(void) {
    TEST_EQ64(executable_memory_hl_lwui_pr(), 0x3, 0x2202);
}

static void test_hl_lwui_upo(void) {
    TEST_EQ64(executable_memory_hl_lwui_upo(), 0x3, 0x2203);
}

static void test_hl_lwui_upr(void) {
    TEST_EQ64(executable_memory_hl_lwui_upr(), 0x3, 0x2204);
}

static void test_hl_swi_po(void) {
    TEST_EQ64(executable_memory_hl_swi_po(), 0x3, 0x2205);
}

static void test_hl_swi_pr(void) {
    TEST_EQ64(executable_memory_hl_swi_pr(), 0x3, 0x2206);
}

static void test_hl_swi_upo(void) {
    TEST_EQ64(executable_memory_hl_swi_upo(), 0x3, 0x2207);
}

static void test_hl_swi_upr(void) {
    TEST_EQ64(executable_memory_hl_swi_upr(), 0x3, 0x2208);
}

static void test_hl_lwuip(void) {
    TEST_EQ64(executable_memory_hl_lwuip(), 0x3, 0x2209);
}

static void test_hl_swip(void) {
    TEST_EQ64(executable_memory_hl_swip(), 0x3, 0x220a);
}

static void test_hl_swip_u(void) {
    TEST_EQ64(executable_memory_hl_swip_u(), 0x3, 0x220b);
}

static void test_hl_ldip(void) {
    TEST_EQ64(executable_memory_hl_ldip(), 0x3, 0x220c);
}

static void test_hl_sdip(void) {
    TEST_EQ64(executable_memory_hl_sdip(), 0x3, 0x220d);
}

void run_loadstore_tests(void) {
    test_suite_begin(0x2200);
    RUN_TEST(test_hl_lwui_po, 0x2201);
    RUN_TEST(test_hl_lwui_pr, 0x2202);
    RUN_TEST(test_hl_lwui_upo, 0x2203);
    RUN_TEST(test_hl_lwui_upr, 0x2204);
    RUN_TEST(test_hl_swi_po, 0x2205);
    RUN_TEST(test_hl_swi_pr, 0x2206);
    RUN_TEST(test_hl_swi_upo, 0x2207);
    RUN_TEST(test_hl_swi_upr, 0x2208);
    RUN_TEST(test_hl_lwuip, 0x2209);
    RUN_TEST(test_hl_swip, 0x220a);
    RUN_TEST(test_hl_swip_u, 0x220b);
    RUN_TEST(test_hl_ldip, 0x220c);
    RUN_TEST(test_hl_sdip, 0x220d);
    test_suite_end(13, 13);
}
