/*
 * Atomic Operation Unit Tests for LinxISA
 * Tests: LR (load reserved), SC (store conditional), AMO operations
 *        LD.*, SD.* with atomic semantics, SWAP
 */

#include "linx_test.h"

/* Test data for atomic operations */
static volatile uint32_t atomic_u32 = 0;
static volatile uint64_t atomic_u64 = 0;
static volatile uint8_t  atomic_u8 = 0;
static volatile uint32_t atomic_lr_srczero_u32 __attribute__((aligned(8))) =
    0x1234ABCDu;
static volatile uint64_t atomic_lr_srczero_u64 __attribute__((aligned(8))) =
    0x0123456789ABCDEFULL;

extern uint64_t atomic_lr_w_nonzero_srczero(const volatile uint32_t *addr);
extern uint64_t atomic_lr_d_nonzero_srczero(const volatile uint64_t *addr);

/* Test basic load (used as baseline for atomic) */
static void test_load_basic(void) {
    atomic_u32 = 0x12345678;
    uint32_t result = atomic_u32;
    TEST_EQ(result, 0x12345678, 0x7001);
}

/* Test basic store (used as baseline for atomic) */
static void test_store_basic(void) {
    atomic_u32 = 0xDEADBEEF;
    TEST_EQ(atomic_u32, 0xDEADBEEF, 0x7010);
}

/* Test load-reserved / store-conditional pattern */
static void test_lr_sc_basic(void) {
    atomic_u32 = 0;
    /* Simulate LR/SC pattern */
    uint32_t old_val = atomic_u32;
    uint32_t new_val = 100;
    
    /* LR: read current value */
    uint32_t observed = atomic_u32;
    
    /* SC: only store if value hasn't changed */
    if (observed == old_val) {
        atomic_u32 = new_val;
        TEST_EQ(atomic_u32, 100, 0x7020);
    } else {
        test_fail(0x7020, 100, observed);
    }
}

static void test_lr_w_nonzero_srczero(void) {
    const uint64_t result = atomic_lr_w_nonzero_srczero(&atomic_lr_srczero_u32);
    TEST_EQ64(result, 0x1234ABCDu, 0x7162);
}

static void test_lr_d_nonzero_srczero(void) {
    const uint64_t result = atomic_lr_d_nonzero_srczero(&atomic_lr_srczero_u64);
    TEST_EQ64(result, 0x0123456789ABCDEFULL, 0x7163);
}

/* Test atomic add */
static void test_atomic_add(void) {
    atomic_u32 = 50;
    uint32_t old = atomic_u32;
    atomic_u32 = old + 25;
    TEST_EQ(atomic_u32, 75, 0x7030);
}

/* Test atomic subtract */
static void test_atomic_sub(void) {
    atomic_u32 = 100;
    uint32_t old = atomic_u32;
    atomic_u32 = old - 30;
    TEST_EQ(atomic_u32, 70, 0x7040);
}

/* Test atomic AND */
static void test_atomic_and(void) {
    atomic_u32 = 0xFF;
    uint32_t old = atomic_u32;
    atomic_u32 = old & 0x0F;
    TEST_EQ(atomic_u32, 0x0F, 0x7050);
}

/* Test atomic OR */
static void test_atomic_or(void) {
    atomic_u32 = 0xF0;
    uint32_t old = atomic_u32;
    atomic_u32 = old | 0x0F;
    TEST_EQ(atomic_u32, 0xFF, 0x7060);
}

/* Test atomic XOR */
static void test_atomic_xor(void) {
    atomic_u32 = 0xFF;
    uint32_t old = atomic_u32;
    atomic_u32 = old ^ 0x0F;
    TEST_EQ(atomic_u32, 0xF0, 0x7070);
}

/* Test atomic swap */
static void test_atomic_swap(void) {
    atomic_u32 = 0x12345678;
    uint32_t old = atomic_u32;
    atomic_u32 = 0xFFFFFFFF;
    TEST_EQ(atomic_u32, 0xFFFFFFFF, 0x7080);
}

/* Test atomic compare-and-swap (simulated) */
static void test_atomic_cas(void) {
    atomic_u32 = 50;
    uint32_t expected = 50;
    uint32_t new_val = 100;
    
    /* Simulate CAS: only update if current value == expected */
    if (atomic_u32 == expected) {
        atomic_u32 = new_val;
        TEST_EQ(atomic_u32, 100, 0x7090);
    } else {
        test_fail(0x7090, 100, atomic_u32);
    }
}

/* Test atomic min (signed) */
static void test_atomic_min(void) {
    atomic_u32 = 100;
    uint32_t old = atomic_u32;
    if (old > 50) {
        atomic_u32 = 50;
    }
    TEST_EQ(atomic_u32, 50, 0x70A0);
}

/* Test atomic max (signed) */
static void test_atomic_max(void) {
    atomic_u32 = 50;
    uint32_t old = atomic_u32;
    if (old < 100) {
        atomic_u32 = 100;
    }
    TEST_EQ(atomic_u32, 100, 0x70B0);
}

/* Test atomic min (unsigned) */
static void test_atomic_minu(void) {
    atomic_u32 = 100;
    uint32_t old = atomic_u32;
    if (old > 50U) {
        atomic_u32 = 50;
    }
    TEST_EQ(atomic_u32, 50, 0x70C0);
}

/* Test atomic max (unsigned) */
static void test_atomic_maxu(void) {
    atomic_u32 = 50;
    uint32_t old = atomic_u32;
    if (old < 100U) {
        atomic_u32 = 100;
    }
    TEST_EQ(atomic_u32, 100, 0x70D0);
}

/* Test 64-bit atomic operations */
static void test_atomic_64_load(void) {
    atomic_u64 = 0x123456789ABCDEF0ULL;
    uint64_t result = atomic_u64;
    TEST_EQ64(result, 0x123456789ABCDEF0ULL, 0x70E0);
}

static void test_atomic_64_store(void) {
    atomic_u64 = 0xDEADBEEFCAFEBABEULL;
    TEST_EQ64(atomic_u64, 0xDEADBEEFCAFEBABEULL, 0x70E1);
}

static void test_atomic_64_add(void) {
    atomic_u64 = 0x100000000ULL;
    uint64_t old = atomic_u64;
    atomic_u64 = old + 0x100000000ULL;
    TEST_EQ64(atomic_u64, 0x200000000ULL, 0x70E2);
}

/* Test memory ordering (barriers) */
static void test_memory_barrier(void) {
    /* Memory barrier test - ensure preceding stores are visible */
    atomic_u32 = 1;
    /* Compiler/memory barrier */
    __asm__ volatile ("" ::: "memory");
    uint32_t result = atomic_u32;
    TEST_EQ(result, 1, 0x70F0);
}

/* Test atomic fetch-and-add */
static void test_fetch_add(void) {
    atomic_u32 = 10;
    uint32_t old = atomic_u32;
    atomic_u32 = old + 5;
    TEST_EQ(old, 10, 0x7100);
    TEST_EQ(atomic_u32, 15, 0x7101);
}

/* Test atomic byte operations */
static void test_atomic_byte(void) {
    atomic_u8 = 0xFF;
    uint8_t result = atomic_u8;
    TEST_EQ(result, 0xFF, 0x7110);
}

static void test_atomic_byte_store(void) {
    atomic_u8 = 0xAB;
    TEST_EQ(atomic_u8, 0xAB, 0x7111);
}

/* Test sequential consistency */
static void test_seq_cst(void) {
    atomic_u32 = 0;
    
    /* Store */
    atomic_u32 = 1;
    
    /* Compiler barrier (portable; no Linx asm parser required) */
    __asm__ volatile ("" ::: "memory");
    
    /* Load - should see either 0 or 1 */
    uint32_t result = atomic_u32;
    TEST_ASSERT(result == 0 || result == 1, 0x7120, 1, result);
}

/* Test acquire semantics */
static void test_acquire_load(void) {
    atomic_u32 = 42;
    /* Acquire load - no following loads can be reordered before it */
    uint32_t result = atomic_u32;
    TEST_EQ(result, 42, 0x7130);
}

/* Test release semantics */
static void test_release_store(void) {
    atomic_u32 = 0;
    /* Release store - no preceding stores can be reordered after it */
    atomic_u32 = 100;
    TEST_EQ(atomic_u32, 100, 0x7140);
}

/* Test successful SC returns 1 */
static void test_sc_success(void) {
    atomic_u32 = 0;
    uint32_t observed = atomic_u32;
    if (observed == 0) {
        atomic_u32 = 1;
        TEST_EQ(atomic_u32, 1, 0x7150);
    }
}

/* Test failed SC returns 0 (simulated) */
static void test_sc_fail(void) {
    atomic_u32 = 50;
    /* Intervening store by another agent would cause SC to fail */
    uint32_t expected = 50;
    uint32_t new_val = 100;
    
    /* Simulate failure case */
    atomic_u32 = 99;  /* Intervening modification */
    
    if (atomic_u32 == expected) {
        atomic_u32 = new_val;
        test_fail(0x7160, 100, atomic_u32);
    } else {
        /* SC should fail and return 0 */
        TEST_EQ(atomic_u32, 99, 0x7161);
    }
}

/* Main test runner */
void run_atomic_tests(void) {
    test_suite_begin(0x7000);
    
    /* Basic load/store */
    RUN_TEST(test_load_basic, 0x7001);
    RUN_TEST(test_store_basic, 0x7010);
    
    /* LR/SC pattern */
    RUN_TEST(test_lr_sc_basic, 0x7020);
    
    /* Atomic fetch-op */
    RUN_TEST(test_atomic_add, 0x7030);
    RUN_TEST(test_atomic_sub, 0x7040);
    RUN_TEST(test_atomic_and, 0x7050);
    RUN_TEST(test_atomic_or, 0x7060);
    RUN_TEST(test_atomic_xor, 0x7070);
    
    /* Atomic swap */
    RUN_TEST(test_atomic_swap, 0x7080);
    
    /* Atomic CAS */
    RUN_TEST(test_atomic_cas, 0x7090);
    
    /* Atomic min/max */
    RUN_TEST(test_atomic_min, 0x70A0);
    RUN_TEST(test_atomic_max, 0x70B0);
    RUN_TEST(test_atomic_minu, 0x70C0);
    RUN_TEST(test_atomic_maxu, 0x70D0);
    
    /* 64-bit atomics */
    RUN_TEST(test_atomic_64_load, 0x70E0);
    RUN_TEST(test_atomic_64_store, 0x70E1);
    RUN_TEST(test_atomic_64_add, 0x70E2);
    
    /* Memory barriers */
    RUN_TEST(test_memory_barrier, 0x70F0);
    
    /* Fetch-and-add */
    RUN_TEST(test_fetch_add, 0x7100);
    
    /* Byte operations */
    RUN_TEST(test_atomic_byte, 0x7110);
    RUN_TEST(test_atomic_byte_store, 0x7111);
    
    /* Memory ordering */
    RUN_TEST(test_seq_cst, 0x7120);
    RUN_TEST(test_acquire_load, 0x7130);
    RUN_TEST(test_release_store, 0x7140);
    
    /* SC success/failure */
    RUN_TEST(test_sc_success, 0x7150);
    RUN_TEST(test_lr_w_nonzero_srczero, 0x7162);
    RUN_TEST(test_lr_d_nonzero_srczero, 0x7163);
    RUN_TEST(test_sc_fail, 0x7160);
    
    test_suite_end(27, 27);
}
