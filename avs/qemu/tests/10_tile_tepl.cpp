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

extern "C" void run_tile_tepl_tests(void)
{
    run_tadd_test();
    run_tsub_test();
    run_tcmp_test();
}
