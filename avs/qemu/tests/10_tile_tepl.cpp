// TEPL-family execution tests: elementwise arithmetic and comparisons.

#include "10_tile_test_common.hpp"

#include <pto/linx/TileOps.hpp>

using namespace linx::test::tile;

extern "C" {
void linx_tcmp_s32_eq(const int32_t *, const int32_t *, uint32_t *);
void linx_tcmp_s32_ne(const int32_t *, const int32_t *, uint32_t *);
void linx_tcmp_s32_lt(const int32_t *, const int32_t *, uint32_t *);
void linx_tcmp_s32_le(const int32_t *, const int32_t *, uint32_t *);
void linx_tcmp_s32_gt(const int32_t *, const int32_t *, uint32_t *);
void linx_tcmp_s32_ge(const int32_t *, const int32_t *, uint32_t *);
void linx_tcmp_u32_lt(const uint32_t *, const uint32_t *, uint32_t *);
void linx_tcmp_s16_lt(const int16_t *, const int16_t *, uint32_t *);
void linx_tcmp_u16_lt(const uint16_t *, const uint16_t *, uint32_t *);
void linx_tcmp_s8_lt(const int8_t *, const int8_t *, uint32_t *);
void linx_tcmp_u8_lt(const uint8_t *, const uint8_t *, uint32_t *);
void linx_tcmp_f32_ne(const float *, const float *, uint32_t *);
void linx_tcmp_f32_ge(const float *, const float *, uint32_t *);
void linx_tcmp_f16_lt(const uint16_t *, const uint16_t *, uint32_t *);
void linx_tcmps_s32_lt(const int32_t *, int32_t, uint32_t *);
void linx_tmax_s8(const int8_t *, const int8_t *, int8_t *);
void linx_tshr_s8(const int8_t *, const int8_t *, int8_t *);
void linx_tabs_s8(const int8_t *, int8_t *);
void linx_tneg_s16(const int16_t *, int16_t *);
void linx_trem_s32(const int32_t *, const int32_t *, int32_t *);
void linx_trems_s32(const int32_t *, int32_t, int32_t *);
void linx_tdiv_s16(const int16_t *, const int16_t *, int16_t *);
void linx_tadd_f16(const uint16_t *, const uint16_t *, uint16_t *);
void linx_tmul_bf16(const uint16_t *, const uint16_t *, uint16_t *);
void linx_tadd_rect_s32(const int32_t *, const int32_t *, int32_t *);
}

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

template <typename T>
static void check_tcmp_lt_profile(void (*kernel)(const T *, const T *,
                                                 uint32_t *),
                                  uint32_t test_id_base)
{
    alignas(16) static T lhs[4096 / sizeof(T)];
    alignas(16) static T rhs[4096 / sizeof(T)];
    alignas(16) static uint32_t mask[1024];
    uint32_t expected[32] = {};

    for (unsigned i = 0; i < 4096 / sizeof(T); i++) {
        lhs[i] = (T)((int32_t)(i % 17u) - 8);
        rhs[i] = (T)((int32_t)(i % 13u) - 6);
    }
    for (unsigned i = 0; i < 1024; i++) {
        mask[i] = 0xdeadbeefu;
    }
    for (unsigned row = 0; row < 32; row++) {
        for (unsigned col = 0; col < 31; col++) {
            const unsigned lane = row * 32u + col;
            if (lhs[lane] < rhs[lane]) {
                expected[row] |= 1u << col;
            }
        }
    }

    kernel(lhs, rhs, mask);
    for (unsigned i = 0; i < 32; i++) {
        TEST_EQ32(mask[i], expected[i], test_id_base + i);
    }
    for (unsigned i = 32; i < 64; i++) {
        TEST_EQ32(mask[i], 0u, test_id_base + 0x40u + i);
    }
}

static void run_tcmp_integer_modes_test()
{
    using TCmpKernel = void (*)(const int32_t *, const int32_t *, uint32_t *);
    const TCmpKernel kernels[6] = {
        linx_tcmp_s32_eq, linx_tcmp_s32_ne, linx_tcmp_s32_lt,
        linx_tcmp_s32_le, linx_tcmp_s32_gt, linx_tcmp_s32_ge,
    };
    alignas(16) static int32_t lhs[1024];
    alignas(16) static int32_t rhs[1024];
    alignas(16) static uint32_t mask[1024];

    for (unsigned i = 0; i < 1024; i++) {
        lhs[i] = (int32_t)(i % 17u) - 8;
        rhs[i] = (int32_t)(i % 11u) - 5;
    }

    for (unsigned mode = 0; mode < 6; mode++) {
        uint32_t expected[32] = {};
        for (unsigned i = 0; i < 1024; i++) {
            mask[i] = 0xdeadbeefu;
        }
        for (unsigned row = 0; row < 32; row++) {
            for (unsigned col = 0; col < 31; col++) {
                const unsigned lane = row * 32u + col;
                const bool result =
                    mode == 0u ? lhs[lane] == rhs[lane] :
                    mode == 1u ? lhs[lane] != rhs[lane] :
                    mode == 2u ? lhs[lane] < rhs[lane] :
                    mode == 3u ? lhs[lane] <= rhs[lane] :
                    mode == 4u ? lhs[lane] > rhs[lane] :
                                 lhs[lane] >= rhs[lane];
                if (result) {
                    expected[row] |= 1u << col;
                }
            }
        }

        kernels[mode](lhs, rhs, mask);
        for (unsigned i = 0; i < 32; i++) {
            TEST_EQ32(mask[i], expected[i],
                      0x000AE000u + mode * 0x80u + i);
        }
        for (unsigned i = 32; i < 64; i++) {
            TEST_EQ32(mask[i], 0u,
                      0x000AE040u + mode * 0x80u + i);
        }
    }

    check_tcmp_lt_profile<uint32_t>(linx_tcmp_u32_lt, 0x000AF000u);
    check_tcmp_lt_profile<int16_t>(linx_tcmp_s16_lt, 0x000AF100u);
    check_tcmp_lt_profile<uint16_t>(linx_tcmp_u16_lt, 0x000AF200u);
    check_tcmp_lt_profile<int8_t>(linx_tcmp_s8_lt, 0x000AF300u);
    check_tcmp_lt_profile<uint8_t>(linx_tcmp_u8_lt, 0x000AF400u);
}

static void run_tcmp_fp32_test(uint32_t *mask)
{
    alignas(16) static float lhs[1024];
    alignas(16) static float rhs[1024];
    using TCmpKernel = void (*)(const float *, const float *, uint32_t *);
    const TCmpKernel kernels[2] = {linx_tcmp_f32_ne, linx_tcmp_f32_ge};

    for (unsigned i = 0; i < 1024; i++) {
        lhs[i] = (float)((int32_t)(i % 17u) - 8);
        rhs[i] = (float)((int32_t)(i % 11u) - 5);
    }
    lhs[0] = __builtin_nanf("");
    rhs[1] = __builtin_nanf("");

    for (unsigned profile = 0; profile < 2; profile++) {
        uint32_t expected[32] = {};
        for (unsigned i = 0; i < 1024; i++) {
            mask[i] = 0xdeadbeefu;
        }
        for (unsigned row = 0; row < 32; row++) {
            for (unsigned col = 0; col < 31; col++) {
                const unsigned lane = row * 32u + col;
                const bool result = profile == 0u
                    ? lhs[lane] != rhs[lane]
                    : lhs[lane] >= rhs[lane];
                if (result) {
                    expected[row] |= 1u << col;
                }
            }
        }
        kernels[profile](lhs, rhs, mask);
        for (unsigned i = 0; i < 32; i++) {
            TEST_EQ32(mask[i], expected[i],
                      0x000AF500u + profile * 0x80u + i);
        }
    }
}

static void run_tcmp_fp16_test(uint32_t *mask)
{
    alignas(16) static uint16_t lhs[2048];
    alignas(16) static uint16_t rhs[2048];
    static const uint16_t values[5] = {
        0xc000u, 0xbc00u, 0x0000u, 0x3c00u, 0x4000u,
    };
    uint32_t expected[32] = {};

    for (unsigned i = 0; i < 2048; i++) {
        lhs[i] = values[i % 5u];
        rhs[i] = values[(i + 2u) % 5u];
    }
    for (unsigned i = 0; i < 1024; i++) {
        mask[i] = 0xdeadbeefu;
    }
    for (unsigned row = 0; row < 32; row++) {
        for (unsigned col = 0; col < 31; col++) {
            const unsigned lane = row * 32u + col;
            if ((lane % 5u) < ((lane + 2u) % 5u)) {
                expected[row] |= 1u << col;
            }
        }
    }

    linx_tcmp_f16_lt(lhs, rhs, mask);
    for (unsigned i = 0; i < 32; i++) {
        TEST_EQ32(mask[i], expected[i], 0x000AF600u + i);
    }
}

static void run_tcmp_test()
{
    test_start(0x000A0013);
    uart_puts("PTO tile tcmp modes packed mask ... ");

    alignas(16) static uint32_t mask[1024];
    run_tcmp_integer_modes_test();
    run_tcmp_fp32_test(mask);
    run_tcmp_fp16_test(mask);
    test_pass();
}

static void run_tcmps_test()
{
    test_start(0x000A001A);
    uart_puts("PTO tile tcmps packed mask ... ");

    alignas(16) static int32_t src[1024];
    alignas(16) static uint32_t mask[1024];
    uint32_t expected[32] = {};
    const int32_t scalar = -1;

    for (unsigned i = 0; i < 1024; i++) {
        src[i] = (int32_t)(i % 17u) - 8;
        mask[i] = 0xdeadbeefu;
    }
    for (unsigned row = 0; row < 32; row++) {
        for (unsigned col = 0; col < 31; col++) {
            const unsigned lane = row * 32u + col;
            if (src[lane] < scalar) {
                expected[row] |= 1u << col;
            }
        }
    }

    linx_tcmps_s32_lt(src, scalar, mask);
    for (unsigned i = 0; i < 32; i++) {
        TEST_EQ32(mask[i], expected[i], 0x000BA000u + i);
    }
    for (unsigned i = 32; i < 64; i++) {
        TEST_EQ32(mask[i], 0u, 0x000BA040u + i);
    }
    test_pass();
}

static uint8_t arithmetic_shift_right_s8(uint8_t value, unsigned shift)
{
    shift &= 31u;
    if (shift >= 8u) {
        return (value & 0x80u) != 0u ? 0xffu : 0u;
    }
    if (shift == 0u || (value & 0x80u) == 0u) {
        return value >> shift;
    }
    return (uint8_t)((value >> shift) | (0xffu << (8u - shift)));
}

static void run_signed_narrow_lane_test()
{
    test_start(0x000A0015);
    uart_puts("PTO TEPL signed narrow lanes ... ");

    alignas(16) static int8_t lhs8[1024];
    alignas(16) static int8_t rhs8[1024];
    alignas(16) static int8_t out8[1024];
    alignas(16) static int16_t lhs16[1024];
    alignas(16) static int16_t rhs16[1024];
    alignas(16) static int16_t out16[1024];
    static const int8_t values8[] = {-128, -63, -7, -1, 0, 1, 9, 127};
    static const int16_t values16[] = {
        -32768, -30001, -257, -1, 0, 1, 257, 32767,
    };
    static const int16_t divisors16[] = {-1, 3, -7, 11, -13, 17, -19, 23};

    for (unsigned i = 0; i < 1024; i++) {
        lhs8[i] = values8[i % 8u];
        rhs8[i] = values8[(i * 3u + 1u) % 8u];
        lhs16[i] = values16[i % 8u];
        rhs16[i] = divisors16[(i * 5u + 2u) % 8u];
    }

    linx_tmax_s8(lhs8, rhs8, out8);
    for (unsigned i = 0; i < 1024; i++) {
        const int8_t expected = lhs8[i] > rhs8[i] ? lhs8[i] : rhs8[i];
        TEST_EQ32((uint8_t)out8[i], (uint8_t)expected, 0x000B0000u + i);
    }

    for (unsigned i = 0; i < 1024; i++) {
        rhs8[i] = (int8_t)(i % 10u);
    }
    linx_tshr_s8(lhs8, rhs8, out8);
    for (unsigned i = 0; i < 1024; i++) {
        const uint8_t expected =
            arithmetic_shift_right_s8((uint8_t)lhs8[i], (uint8_t)rhs8[i]);
        TEST_EQ32((uint8_t)out8[i], expected, 0x000B1000u + i);
    }

    linx_tabs_s8(lhs8, out8);
    for (unsigned i = 0; i < 1024; i++) {
        const int16_t value = lhs8[i];
        const uint8_t expected = (uint8_t)(value < 0 ? -value : value);
        TEST_EQ32((uint8_t)out8[i], expected, 0x000B2000u + i);
    }

    linx_tdiv_s16(lhs16, rhs16, out16);
    for (unsigned i = 0; i < 1024; i++) {
        const int16_t expected =
            (int16_t)((int32_t)lhs16[i] / (int32_t)rhs16[i]);
        TEST_EQ32((uint16_t)out16[i], (uint16_t)expected,
                  0x000B3000u + i);
    }
    test_pass();
}

static void run_float16_lane_test()
{
    test_start(0x000A0016);
    uart_puts("PTO TEPL FP16/BF16 softfloat lanes ... ");

    alignas(16) static uint16_t lhs[1024];
    alignas(16) static uint16_t rhs[1024];
    alignas(16) static uint16_t out[1024];
    static const uint16_t f16_lhs[8] = {
        0x3c00, 0xbc00, 0xc000, 0x0000,
        0x4400, 0x3400, 0x7bff, 0x0400,
    };
    static const uint16_t f16_rhs[8] = {
        0x4000, 0x3800, 0x3c00, 0x8000,
        0xc000, 0x3400, 0x0000, 0x0400,
    };
    static const uint16_t f16_expected[8] = {
        0x4200, 0xb800, 0xbc00, 0x0000,
        0x4000, 0x3800, 0x7bff, 0x0800,
    };
    static const uint16_t bf16_lhs[8] = {
        0x3f80, 0xbf80, 0xc000, 0x0000,
        0x4040, 0x3e80, 0x3f00, 0x0080,
    };
    static const uint16_t bf16_rhs[8] = {
        0x4000, 0x3f00, 0xc000, 0xbf80,
        0x3f00, 0x4080, 0x4000, 0x4000,
    };
    static const uint16_t bf16_expected[8] = {
        0x4000, 0xbf00, 0x4080, 0x8000,
        0x3fc0, 0x3f80, 0x3f80, 0x0100,
    };

    for (unsigned i = 0; i < 1024; i++) {
        lhs[i] = f16_lhs[i % 8u];
        rhs[i] = f16_rhs[i % 8u];
    }
    linx_tadd_f16(lhs, rhs, out);
    for (unsigned i = 0; i < 1024; i++) {
        TEST_EQ32(out[i], f16_expected[i % 8u], 0x000B4000u + i);
    }

    for (unsigned i = 0; i < 1024; i++) {
        lhs[i] = bf16_lhs[i % 8u];
        rhs[i] = bf16_rhs[i % 8u];
    }
    linx_tmul_bf16(lhs, rhs, out);
    for (unsigned i = 0; i < 1024; i++) {
        TEST_EQ32(out[i], bf16_expected[i % 8u], 0x000B5000u + i);
    }
    test_pass();
}

static void run_persistent_shape_test()
{
    test_start(0x000A0017);
    uart_puts("PTO tile persistent rectangular shape ... ");

    alignas(16) static int32_t lhs[1024];
    alignas(16) static int32_t rhs[1024];
    alignas(16) static int32_t out[1024];
    for (unsigned i = 0; i < 1024; i++) {
        lhs[i] = (int32_t)(10u + i);
        rhs[i] = (int32_t)(100u + i * 3u);
        out[i] = -1;
    }

    linx_tadd_rect_s32(lhs, rhs, out);
    for (unsigned i = 0; i < 6; i++) {
        TEST_EQ32((uint32_t)out[i], (uint32_t)(lhs[i] + rhs[i]),
                  0x000B6000u + i);
    }
    for (unsigned i = 6; i < 16; i++) {
        TEST_EQ32((uint32_t)out[i], UINT32_C(0xffffffff),
                  0x000B6100u + i);
    }
    test_pass();
}

static void run_tneg_test()
{
    test_start(0x000A0018);
    uart_puts("PTO tile tneg signed lanes ... ");

    alignas(16) static int16_t src[1024];
    alignas(16) static int16_t out[1024];
    static const int16_t values[] = {
        0, 1, -1, 32767, (int16_t)0x8000, 1234, -2345, 42,
    };
    for (unsigned i = 0; i < 1024; i++) {
        src[i] = values[i % (sizeof(values) / sizeof(values[0]))];
        out[i] = 0;
    }

    linx_tneg_s16(src, out);
    for (unsigned i = 0; i < 1024; i++) {
        const uint16_t expected = (uint16_t)(0u - (uint16_t)src[i]);
        TEST_EQ32((uint16_t)out[i], expected, 0x000B7000u + i);
    }
    test_pass();
}

static int32_t floor_rem_s32(int32_t lhs, int32_t rhs)
{
    int32_t rem = lhs % rhs;
    if (rem != 0 && ((rem < 0) != (rhs < 0))) {
        rem += rhs;
    }
    return rem;
}

static void run_trem_test()
{
    test_start(0x000A0019);
    uart_puts("PTO tile floor remainder ... ");

    alignas(16) static int32_t lhs[1024];
    alignas(16) static int32_t rhs[1024];
    alignas(16) static int32_t out[1024];
    static const int32_t dividends[] = {-17, -7, -1, 0, 1, 7, 17, 12345};
    static const int32_t divisors[] = {5, 3, -5, -3, 7, -7, 11, -13};
    for (unsigned i = 0; i < 1024; i++) {
        lhs[i] = dividends[i % 8u];
        rhs[i] = divisors[(i / 8u) % 8u];
        out[i] = 0;
    }

    linx_trem_s32(lhs, rhs, out);
    for (unsigned i = 0; i < 1024; i++) {
        TEST_EQ32((uint32_t)out[i],
                  (uint32_t)floor_rem_s32(lhs[i], rhs[i]),
                  0x000B8000u + i);
    }

    linx_trems_s32(lhs, -7, out);
    for (unsigned i = 0; i < 1024; i++) {
        TEST_EQ32((uint32_t)out[i],
                  (uint32_t)floor_rem_s32(lhs[i], -7),
                  0x000B9000u + i);
    }
    test_pass();
}

extern "C" void run_tile_tepl_tests(void)
{
    run_tadd_test();
    run_tsub_test();
    run_tcmp_test();
    run_tcmps_test();
    run_signed_narrow_lane_test();
    run_float16_lane_test();
    run_persistent_shape_test();
    run_tneg_test();
    run_trem_test();
}
