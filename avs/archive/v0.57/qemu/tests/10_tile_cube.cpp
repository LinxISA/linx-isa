// CUBE-family execution tests: TMATMUL, TMATMUL_ACC, and CUBE-heavy kernels.

#include "10_tile_test_common.hpp"

#include <pto/linx/TileOps.hpp>

using namespace linx::test::tile;

extern "C" {
void linx_tgemv_s32(const int32_t *, const int32_t *, int32_t *);
void linx_tgemv_acc_s32(const int32_t *, const int32_t *, int32_t *);
void linx_tmatmul_bias_s32(const int32_t *, const int32_t *,
                           const int32_t *, int32_t *);
}

static void run_tmatmul_test()
{
    test_start(0x000A0001);
    uart_puts("PTO tile matmul (8x8 i32) ... ");

    alignas(16) static int32_t a[1024];
    alignas(16) static int32_t b[1024];
    alignas(16) static int32_t c[1024];
    alignas(16) static int32_t expected[64];

    for (unsigned i = 0; i < 1024; i++) {
        a[i] = 0;
        b[i] = 0;
        c[i] = 0;
        if (i < 64) {
            a[i] = (int32_t)((int)i % 7 - 3);
            b[i] = (int32_t)((int)i % 5 - 2);
        }
    }

    auto ta = pto::linx::tload<kTileSizeCode>(a);
    auto tb = pto::linx::tload<kTileSizeCode>(b);
    auto tc = pto::linx::tmatmul<8, 8, 8>(ta, tb);
    pto::linx::tstore<kTileSizeCode>(c, tc);

    matmul_ref_i32_8x8(expected, a, b);
    for (unsigned i = 0; i < 64; i++) {
        TEST_EQ32((uint32_t)c[i], (uint32_t)expected[i], 0x000A1000u + i);
    }
    test_pass();
}

static void run_tmatmul_acc_test()
{
    test_start(0x000A0003);
    uart_puts("PTO tmatmul_acc pipeline ... ");

    alignas(16) static int32_t a[1024];
    alignas(16) static int32_t b[1024];
    alignas(16) static int32_t c[1024];
    alignas(16) static int32_t expected[64];

    for (unsigned i = 0; i < 1024; i++) {
        a[i] = 0;
        b[i] = 0;
        c[i] = 0;
        if (i < 64) {
            a[i] = (int32_t)((int)i % 7 - 3);
            b[i] = (int32_t)((int)i % 5 - 2);
        }
    }

    auto ta = pto::linx::tload<kTileSizeCode>(a);
    auto tb = pto::linx::tload<kTileSizeCode>(b);
    auto seed = pto::linx::tmatmul<8, 8, 8>(ta, tb);
    auto out = pto::linx::tmatmul_acc<8, 8, 8>(seed, ta, tb);
    pto::linx::tstore<kTileSizeCode>(c, out);

    matmul_ref_i32_8x8(expected, a, b);
    for (unsigned i = 0; i < 64; i++) {
        const int32_t accumulated = (int32_t)((int64_t)expected[i] * 2);
        TEST_EQ32((uint32_t)c[i], (uint32_t)accumulated, 0x000A3000u + i);
    }
    test_pass();
}

static void run_tmatmul_bias_test()
{
    test_start(0x000A0026);
    uart_puts("PTO TMATMUL.BIAS (8x8 i32) ... ");

    alignas(16) static int32_t a[128];
    alignas(16) static int32_t b[128];
    alignas(16) static int32_t bias[128];
    alignas(16) static int32_t out[128];
    alignas(16) static int32_t expected[64];

    for (unsigned i = 0; i < 128; i++) {
        a[i] = 0;
        b[i] = 0;
        bias[i] = 0;
        out[i] = (int32_t)0x55555555;
        if (i < 64) {
            a[i] = (int32_t)((int)(i * 3u) % 11 - 5);
            b[i] = (int32_t)((int)(i * 5u) % 13 - 6);
        }
    }
    for (unsigned col = 0; col < 8; col++) {
        bias[col] = (int32_t)(17 - (int)(col * 5u));
    }

    linx_tmatmul_bias_s32(a, b, bias, out);
    matmul_ref_i32_8x8(expected, a, b);
    for (unsigned row = 0; row < 8; row++) {
        for (unsigned col = 0; col < 8; col++) {
            const unsigned lane = row * 8u + col;
            const int32_t want = expected[lane] + bias[col];
            TEST_EQ32((uint32_t)out[lane], (uint32_t)want,
                      0x000A6000u + lane);
        }
    }
    for (unsigned i = 64; i < 128; i++) {
        TEST_EQ32((uint32_t)out[i], 0, 0x000A6080u + i);
    }
    test_pass();
}

static void run_tgemv_test()
{
    test_start(0x000A0024);
    uart_puts("PTO TGEMV/TGEMV.ACC (8x1 i32) ... ");

    alignas(16) static int32_t a[128];
    alignas(16) static int32_t b[128];
    alignas(16) static int32_t out[128];

    for (unsigned i = 0; i < 128; i++) {
        a[i] = 0;
        b[i] = 0;
        out[i] = 0x55555555;
    }
    for (unsigned r = 0; r < 8; r++) {
        for (unsigned k = 0; k < 8; k++) {
            a[r * 8u + k] = (int32_t)(r + 1u) - (int32_t)(2u * k);
        }
        b[r * 8u] = (int32_t)(r + 1u);
    }

    linx_tgemv_s32(a, b, out);
    for (unsigned r = 0; r < 8; r++) {
        int32_t expected = 0;
        for (unsigned k = 0; k < 8; k++) {
            expected += a[r * 8u + k] * b[k * 8u];
        }
        TEST_EQ32((uint32_t)out[r * 8u], (uint32_t)expected,
                  0x000A2400u + r);
        for (unsigned c = 1; c < 8; c++) {
            TEST_EQ32((uint32_t)out[r * 8u + c], 0,
                      0x000A2440u + r * 8u + c);
        }
    }
    for (unsigned i = 64; i < 128; i++) {
        TEST_EQ32((uint32_t)out[i], 0, 0x000A2480u + i);
    }

    for (unsigned i = 0; i < 128; i++) {
        out[i] = 0x55555555;
    }
    linx_tgemv_acc_s32(a, b, out);
    for (unsigned r = 0; r < 8; r++) {
        int32_t expected = 0;
        for (unsigned k = 0; k < 8; k++) {
            expected += a[r * 8u + k] * b[k * 8u];
        }
        TEST_EQ32((uint32_t)out[r * 8u], (uint32_t)(expected * 2),
                  0x000A2500u + r);
        for (unsigned c = 1; c < 8; c++) {
            TEST_EQ32((uint32_t)out[r * 8u + c], 0,
                      0x000A2540u + r * 8u + c);
        }
    }
    for (unsigned i = 64; i < 128; i++) {
        TEST_EQ32((uint32_t)out[i], 0, 0x000A2580u + i);
    }

    test_pass();
}

static void run_auto_mode_gemm_test()
{
    test_start(0x000A0004);
    uart_puts("Auto-mode GEMM kernel ... ");

    alignas(16) static int32_t a[9 * kTileElemsI32];
    alignas(16) static int32_t b[8 * kTileElemsI32];
    alignas(16) static int32_t out[11 * kTileElemsI32];
    alignas(16) static int32_t expected[64];

    for (unsigned tile = 0; tile < 9; tile++) {
        init_tile_pattern(tile_ptr(a, tile), (int32_t)(3 + tile));
    }
    for (unsigned tile = 0; tile < 8; tile++) {
        init_tile_pattern(tile_ptr(b, tile), (int32_t)(11 + tile));
    }
    zero(out, 11 * kTileElemsI32);

    pto::linx::auto_mode::gemm_kernel_i32(a, b, out);

    const unsigned lhs_map[11] = {0, 1, 2, 3, 4, 5, 6, 7, 8, 0, 1};
    const unsigned rhs_map[11] = {0, 1, 2, 3, 4, 5, 6, 0, 1, 2, 7};
    for (unsigned tile = 0; tile < 11; tile++) {
        matmul_ref_i32_8x8(expected, tile_ptr(a, lhs_map[tile]),
                          tile_ptr(b, rhs_map[tile]));
        const int32_t *actual = tile_ptr(out, tile);
        for (unsigned i = 0; i < 64; i++) {
            TEST_EQ32((uint32_t)actual[i], (uint32_t)expected[i],
                      0x000A4000u + tile * 64u + i);
        }
    }

    print_checksum("QEMU_GEMM_CHECKSUM=", checksum_tiles_i32(out, 11));
    test_pass();
}

static void run_auto_mode_flash_test()
{
    test_start(0x000A0005);
    uart_puts("Auto-mode flash-attention kernel ... ");

    alignas(16) static int32_t q[5 * kTileElemsI32];
    alignas(16) static int32_t k[5 * kTileElemsI32];
    alignas(16) static int32_t v[4 * kTileElemsI32];
    alignas(16) static int32_t out[9 * kTileElemsI32];
    alignas(16) static int32_t score[64];
    alignas(16) static int32_t expected[64];

    for (unsigned tile = 0; tile < 5; tile++) {
        init_tile_pattern(tile_ptr(q, tile), (int32_t)(17 + tile));
        init_tile_pattern(tile_ptr(k, tile), (int32_t)(29 + tile));
    }
    for (unsigned tile = 0; tile < 4; tile++) {
        init_tile_pattern(tile_ptr(v, tile), (int32_t)(41 + tile));
    }
    zero(out, 9 * kTileElemsI32);

    pto::linx::auto_mode::flash_attention_kernel_i32(q, k, v, out);

    const unsigned q_map[9] = {0, 1, 2, 3, 4, 0, 1, 2, 3};
    const unsigned k_map[9] = {0, 1, 2, 3, 4, 1, 2, 3, 4};
    const unsigned v_map[9] = {0, 1, 2, 3, 0, 1, 2, 3, 0};
    for (unsigned tile = 0; tile < 9; tile++) {
        matmul_ref_i32_8x8(score, tile_ptr(q, q_map[tile]),
                          tile_ptr(k, k_map[tile]));
        matmul_ref_i32_8x8(expected, score, tile_ptr(v, v_map[tile]));
        const int32_t *actual = tile_ptr(out, tile);
        for (unsigned i = 0; i < 64; i++) {
            TEST_EQ32((uint32_t)actual[i], (uint32_t)expected[i],
                      0x000A5000u + tile * 64u + i);
        }
    }

    print_checksum("QEMU_FLASH_CHECKSUM=", checksum_tiles_i32(out, 9));
    test_pass();
}

extern "C" void run_tile_cube_tests(void)
{
    run_tmatmul_test();
    run_tmatmul_acc_test();
    run_tmatmul_bias_test();
    run_tgemv_test();
    run_auto_mode_gemm_test();
    run_auto_mode_flash_test();
}
