// TEPL-family execution tests: elementwise arithmetic and comparisons.

#include "10_tile_test_common.hpp"

#include <pto/linx/TileOps.hpp>

using namespace linx::test::tile;

static void run_tadd_test()
{
    test_start(0x000A000C);
    uart_puts("PTO tile tadd (VPAR) ... ");

    alignas(16) static int32_t a[1024];
    alignas(16) static int32_t b[1024];
    alignas(16) static int32_t sum[1024];
    for (unsigned i = 0; i < 1024; i++) {
        a[i] = (int32_t)((int)i * 3 - 7);
        b[i] = (int32_t)((int)i * 5 + 11);
        sum[i] = 0;
    }

    auto ta = pto::linx::tload<kTileSizeCode>(a);
    auto tb = pto::linx::tload<kTileSizeCode>(b);
    auto result = pto::linx::tadd<kTileSizeCode>(ta, tb);
    pto::linx::tstore<kTileSizeCode>(sum, result);
    for (unsigned i = 0; i < 256; i++) {
        const int32_t expected = (int32_t)((int64_t)a[i] + (int64_t)b[i]);
        TEST_EQ32((uint32_t)sum[i], (uint32_t)expected, 0x000AC000u + i);
    }
    test_pass();
}

static void run_tsub_test()
{
    test_start(0x000A000D);
    uart_puts("PTO tile tsub (VPAR) ... ");

    alignas(16) static int32_t a[1024];
    alignas(16) static int32_t b[1024];
    alignas(16) static int32_t difference[1024];
    for (unsigned i = 0; i < 1024; i++) {
        a[i] = (int32_t)((int)i * 3 - 7);
        b[i] = (int32_t)((int)i * 5 + 11);
        difference[i] = 0;
    }

    auto ta = pto::linx::tload<kTileSizeCode>(a);
    auto tb = pto::linx::tload<kTileSizeCode>(b);
    auto result = pto::linx::tsub<kTileSizeCode>(ta, tb);
    pto::linx::tstore<kTileSizeCode>(difference, result);
    for (unsigned i = 0; i < 256; i++) {
        const int32_t expected = (int32_t)((int64_t)a[i] - (int64_t)b[i]);
        TEST_EQ32((uint32_t)difference[i], (uint32_t)expected,
                  0x000AD000u + i);
    }
    test_pass();
}

extern "C" void run_tile_tepl_tests(void)
{
    run_tadd_test();
    run_tsub_test();
}
