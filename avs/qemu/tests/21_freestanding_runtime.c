#include "linx_test.h"

#include <malloc.h>
#include <stdint.h>
#include <stdlib.h>
#include <sys/time.h>

static void test_memalign_contract(void)
{
    void *p64 = memalign(64, 33);
    void *p256 = memalign(256, 1);

    TEST_ASSERT(p64 != 0, 0x2101, 1, 0);
    TEST_EQ((uintptr_t)p64 & 63u, 0, 0x2102);
    TEST_ASSERT(p256 != 0, 0x2103, 1, 0);
    TEST_EQ((uintptr_t)p256 & 255u, 0, 0x2104);
    TEST_EQ((uintptr_t)memalign(3, 16), 0, 0x2105);
    TEST_EQ((uintptr_t)memalign(sizeof(void *) / 2, 16), 0, 0x2106);
}

static void test_gettimeofday_monotonic(void)
{
    struct timeval first;
    struct timeval second;
    uint64_t first_us;
    uint64_t second_us;

    TEST_EQ(gettimeofday(&first, 0), 0, 0x2110);
    TEST_EQ(gettimeofday(&second, 0), 0, 0x2111);
    first_us = (uint64_t)first.tv_sec * 1000000ull + (uint64_t)first.tv_usec;
    second_us = (uint64_t)second.tv_sec * 1000000ull + (uint64_t)second.tv_usec;
    TEST_ASSERT(second_us >= first_us, 0x2112, first_us, second_us);
    TEST_ASSERT(first.tv_usec >= 0 && first.tv_usec < 1000000, 0x2113, 1, first.tv_usec);
    TEST_ASSERT(second.tv_usec >= 0 && second.tv_usec < 1000000, 0x2114, 1, second.tv_usec);
}

void run_freestanding_runtime_tests(void)
{
    test_suite_begin(0x2100);
    RUN_TEST(test_memalign_contract, 0x2101);
    RUN_TEST(test_gettimeofday_monotonic, 0x2110);
    test_suite_end(2, 2);
}
