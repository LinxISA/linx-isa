// TMA-family execution tests: TLOAD/TSTORE, descriptors, and ordering.

#include "10_tile_test_common.hpp"

#include <pto/linx/TileOps.hpp>

using namespace linx::test::tile;

#ifndef LINX_TEST_ENABLE_TMA_DESC
#define LINX_TEST_ENABLE_TMA_DESC 0
#endif

static constexpr unsigned kFmtNorm = 0;
static constexpr unsigned kFmtND2NZ = 1;

static void run_tload_tstore_roundtrip_test()
{
    test_start(0x000A0002);
    uart_puts("PTO tload/tstore roundtrip ... ");

    alignas(16) static int32_t src[1024];
    alignas(16) static int32_t dst[1024];
    for (unsigned i = 0; i < 1024; i++) {
        src[i] = (int32_t)((int)i * 3 - 7);
        dst[i] = 0;
    }

    auto tile = pto::linx::tload<kTileSizeCode>(src);
    pto::linx::tstore<kTileSizeCode>(dst, tile);
    for (unsigned i = 0; i < 128; i++) {
        TEST_EQ32((uint32_t)dst[i], (uint32_t)src[i], 0x000A2000u + i);
    }
    test_pass();
}

static void run_tma_layout_and_padding_tests()
{
    test_start(0x000A000E);
    uart_puts("PTO TMA desc NORM (8x8 sanity) ... ");

    alignas(16) static int32_t norm_src[64];
    alignas(16) static int32_t norm_dst[64];
    for (unsigned i = 0; i < 64; i++) {
        norm_src[i] = (int32_t)((int)i * 11 - 123);
        norm_dst[i] = 0;
    }

    auto norm_tile =
        pto::linx::tload<kTileSizeCode, kFmtNorm, 8, 8, 8>(norm_src);
    pto::linx::tstore<kTileSizeCode, kFmtNorm, 8, 8, 8>(norm_dst,
                                                        norm_tile);
    for (unsigned i = 0; i < 64; i++) {
        TEST_EQ32((uint32_t)norm_dst[i], (uint32_t)norm_src[i],
                  0x000AE000u + i);
    }
    test_pass();

    test_start(0x000A000F);
    uart_puts("PTO TMA desc ND<->NZ (8x8 in 64x16 TR) ... ");

    alignas(16) static int32_t nz_src[1024];
    alignas(16) static int32_t nz_dst[1024];
    for (unsigned i = 0; i < 1024; i++) {
        nz_src[i] = i < 64 ? (int32_t)((int)i * 7 - 37) : 0;
        nz_dst[i] = 0;
    }

    auto nz_tile =
        pto::linx::tload<kTileSizeCode, kFmtND2NZ, 8, 8, 64>(nz_src);
    pto::linx::tstore<kTileSizeCode, kFmtND2NZ, 8, 8, 64>(nz_dst, nz_tile);
    for (unsigned i = 0; i < 64; i++) {
        TEST_EQ32((uint32_t)nz_dst[i], (uint32_t)nz_src[i],
                  0x000AF000u + i);
    }
    test_pass();

    test_start(0x000A0010);
    uart_puts("PTO TLOAD padding visibility (Null mode) ... ");

    alignas(16) static int32_t pad_src[1024];
    alignas(16) static int32_t pad_dump[1024];
    for (unsigned i = 0; i < 1024; i++) {
        pad_src[i] = i < 64 ? (int32_t)((int)i - 9) : 0;
        pad_dump[i] = (int32_t)0x5a5a5a5a;
    }

    auto pad_tile =
        pto::linx::tload<kTileSizeCode, kFmtND2NZ, 8, 8, 64>(pad_src);
    pto::linx::tstore<kTileSizeCode, kFmtND2NZ, 64, 16, 64>(pad_dump,
                                                            pad_tile);
    for (unsigned r = 0; r < 8; r++) {
        for (unsigned c = 0; c < 8; c++) {
            TEST_EQ32((uint32_t)pad_dump[r * 64u + c],
                      (uint32_t)pad_src[r * 8u + c],
                      0x000A10000u + r * 8u + c);
        }
    }

    bool saw_non_sentinel = false;
    const unsigned pad_samples[4] = {
        8u * 64u, 8u * 64u + 9u, 9u * 64u + 13u, 15u * 64u + 63u,
    };
    for (unsigned sample : pad_samples) {
        if ((uint32_t)pad_dump[sample] != 0x5a5a5a5au) {
            saw_non_sentinel = true;
        }
    }
    if (!saw_non_sentinel) {
        uart_puts("(pad lanes untouched) ");
    }
    test_pass();

    test_start(0x000A0011);
    uart_puts("PTO TMA desc NORM (non-pow2 30x17) ... ");

    alignas(16) static int32_t np2_src[1024];
    alignas(16) static int32_t np2_dst[1024];
    for (unsigned i = 0; i < 1024; i++) {
        np2_src[i] = i < 30u * 17u ? (int32_t)((int)i * 5 + 3) : 0;
        np2_dst[i] = 0;
    }

    auto np2_tile =
        pto::linx::tload<kTileSizeCode, kFmtNorm, 30, 17, 32>(np2_src);
    pto::linx::tstore<kTileSizeCode, kFmtNorm, 30, 17, 32>(np2_dst,
                                                           np2_tile);
    for (unsigned i = 0; i < 30u * 17u; i++) {
        TEST_EQ32((uint32_t)np2_dst[i], (uint32_t)np2_src[i],
                  0x000A11000u + i);
    }
    test_pass();
}

static void run_tso_store_store_order_smoke()
{
    test_start(0x000A000B);
    uart_puts("TSO store->store ordering (scalar + TMA) ... ");

    alignas(16) static int32_t src[1024];
    alignas(16) static int32_t dst[1024];
    static volatile uint32_t scalar_store;

    zero(src, 1024);
    zero(dst, 1024);
    src[0] = 1;
    auto tile = pto::linx::tload<kTileSizeCode>(src);

    for (unsigned iter = 0; iter < 128; iter++) {
        scalar_store = 0;
        dst[0] = 0;
        scalar_store = 1;
        pto::linx::tstore<kTileSizeCode>(dst, tile);

        const uint32_t tile_value = (uint32_t)dst[0];
        const uint32_t scalar_value = scalar_store;
        TEST_ASSERT(!(tile_value == 1u && scalar_value == 0u),
                    0x000AB000u + iter, 1,
                    ((uint64_t)tile_value << 32) | scalar_value);
    }
    test_pass();
}

extern "C" void run_tile_tma_tests(void)
{
    run_tload_tstore_roundtrip_test();
    if (LINX_TEST_ENABLE_TMA_DESC) {
        run_tma_layout_and_padding_tests();
    } else {
        uart_puts("PTO TMA descriptor stress tests ... (skipped)\n");
    }
    run_tso_store_store_order_smoke();
}
