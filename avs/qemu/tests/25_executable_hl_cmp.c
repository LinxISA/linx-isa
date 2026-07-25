/* Dedicated executable evidence for HL.CMP immediate forms. */

#include "linx_test.h"

#include <stdint.h>

static inline uint64_t pack2(uint64_t lo, uint64_t hi) {
    return (lo & 1u) | ((hi & 1u) << 1);
}

__attribute__((noinline)) uint64_t executable_hl_cmp_eqi(void) {
    const uint64_t neg_one = 0xffffffffffffffffULL;
    const uint64_t pos_24 = 0x00ffffffULL;
    uint64_t equal;
    uint64_t unequal;
    __asm__ volatile("hl.cmp.eqi %1, -1, ->%0"
                     : "=&r"(equal)
                     : "r"(neg_one));
    __asm__ volatile("hl.cmp.eqi %1, -1, ->%0"
                     : "=&r"(unequal)
                     : "r"(pos_24));
    return pack2(equal, unequal);
}

__attribute__((noinline)) uint64_t executable_hl_cmp_nei(void) {
    const uint64_t pos_23 = 0x007fffffULL;
    const uint64_t neg_one = 0xffffffffffffffffULL;
    uint64_t unequal;
    uint64_t equal;
    __asm__ volatile("hl.cmp.nei %1, -1, ->%0"
                     : "=&r"(unequal)
                     : "r"(pos_23));
    __asm__ volatile("hl.cmp.nei %1, -1, ->%0"
                     : "=&r"(equal)
                     : "r"(neg_one));
    return pack2(unequal, equal);
}

__attribute__((noinline)) uint64_t executable_hl_cmp_gei(void) {
    const uint64_t at_min = 0xffffffffff800000ULL;
    const uint64_t below_min = 0xffffffffff7fffffULL;
    uint64_t ge_equal;
    uint64_t ge_false;
    __asm__ volatile("hl.cmp.gei %1, -8388608, ->%0"
                     : "=&r"(ge_equal)
                     : "r"(at_min));
    __asm__ volatile("hl.cmp.gei %1, -8388608, ->%0"
                     : "=&r"(ge_false)
                     : "r"(below_min));
    return pack2(ge_equal, ge_false);
}

__attribute__((noinline)) uint64_t executable_hl_cmp_geui(void) {
    const uint64_t above = 0x00ffffffULL;
    const uint64_t below = 0x007fffffULL;
    uint64_t ge_true;
    uint64_t ge_false;
    __asm__ volatile("hl.cmp.geui %1, 8388608, ->%0"
                     : "=&r"(ge_true)
                     : "r"(above));
    __asm__ volatile("hl.cmp.geui %1, 8388608, ->%0"
                     : "=&r"(ge_false)
                     : "r"(below));
    return pack2(ge_true, ge_false);
}

__attribute__((noinline)) uint64_t executable_hl_cmp_lti(void) {
    const uint64_t below_min = 0xffffffffff7fffffULL;
    const uint64_t at_min = 0xffffffffff800000ULL;
    uint64_t lt_true;
    uint64_t lt_false;
    __asm__ volatile("hl.cmp.lti %1, -8388608, ->%0"
                     : "=&r"(lt_true)
                     : "r"(below_min));
    __asm__ volatile("hl.cmp.lti %1, -8388608, ->%0"
                     : "=&r"(lt_false)
                     : "r"(at_min));
    return pack2(lt_true, lt_false);
}

__attribute__((noinline)) uint64_t executable_hl_cmp_ltui(void) {
    const uint64_t below = 0x007fffffULL;
    const uint64_t at = 0x00800000ULL;
    uint64_t lt_true;
    uint64_t lt_false;
    __asm__ volatile("hl.cmp.ltui %1, 8388608, ->%0"
                     : "=&r"(lt_true)
                     : "r"(below));
    __asm__ volatile("hl.cmp.ltui %1, 8388608, ->%0"
                     : "=&r"(lt_false)
                     : "r"(at));
    return pack2(lt_true, lt_false);
}

__attribute__((noinline)) uint64_t executable_hl_cmp_ori(void) {
    const uint64_t zero = 0;
    uint64_t zero_or_zero;
    uint64_t zero_or_signext;
    __asm__ volatile("hl.cmp.ori %1, 0, ->%0"
                     : "=&r"(zero_or_zero)
                     : "r"(zero));
    __asm__ volatile("hl.cmp.ori %1, -8388608, ->%0"
                     : "=&r"(zero_or_signext)
                     : "r"(zero));
    return pack2(zero_or_zero, zero_or_signext);
}

static void test_hl_cmp_eqi(void) {
    TEST_EQ64(executable_hl_cmp_eqi(), 0x1, 0x2701);
}
static void test_hl_cmp_nei(void) {
    TEST_EQ64(executable_hl_cmp_nei(), 0x1, 0x2702);
}
static void test_hl_cmp_gei(void) {
    TEST_EQ64(executable_hl_cmp_gei(), 0x1, 0x2703);
}
static void test_hl_cmp_geui(void) {
    TEST_EQ64(executable_hl_cmp_geui(), 0x1, 0x2704);
}
static void test_hl_cmp_lti(void) {
    TEST_EQ64(executable_hl_cmp_lti(), 0x1, 0x2705);
}
static void test_hl_cmp_ltui(void) {
    TEST_EQ64(executable_hl_cmp_ltui(), 0x1, 0x2706);
}
static void test_hl_cmp_ori(void) {
    TEST_EQ64(executable_hl_cmp_ori(), 0x2, 0x2707);
}

__attribute__((optnone)) void run_hl_cmp_tests(void) {
    test_suite_begin(0x2700);
    RUN_TEST(test_hl_cmp_eqi, 0x2701);
    RUN_TEST(test_hl_cmp_nei, 0x2702);
    RUN_TEST(test_hl_cmp_gei, 0x2703);
    RUN_TEST(test_hl_cmp_geui, 0x2704);
    RUN_TEST(test_hl_cmp_lti, 0x2705);
    RUN_TEST(test_hl_cmp_ltui, 0x2706);
    RUN_TEST(test_hl_cmp_ori, 0x2707);
    test_suite_end(7, 7);
}
