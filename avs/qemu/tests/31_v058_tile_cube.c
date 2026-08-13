#include "linx_test.h"

#include <stdint.h>

enum { kDim = 4, kTileElements = 1024 };
static const uint32_t kTestId = 0x00002D01u;

static uint32_t lhs[kTileElements] __attribute__((aligned(64)));
static uint32_t rhs[kTileElements] __attribute__((aligned(64)));
static uint32_t output[kTileElements] __attribute__((aligned(64)));

extern void linx_v058_cube_matmul(const uint32_t *a, const uint32_t *b,
                                  uint32_t *dst, uint64_t stride);

void run_tile_v058_cube_tests(void)
{
    test_start(kTestId);
    for (unsigned i = 0; i < kTileElements; ++i) {
        lhs[i] = 0u;
        rhs[i] = 0u;
        output[i] = 0xBF800000u;
    }
    for (unsigned row = 0; row < kDim; ++row) {
        for (unsigned col = 0; col < kDim; ++col) {
            const unsigned index = row * kDim + col;
            lhs[index] = row == col ? 1u : 0u;
            rhs[index] = row * kDim + col + 1u;
        }
    }

    linx_v058_cube_matmul(lhs, rhs, output, 4u);

    for (unsigned i = 0; i < kDim * kDim; ++i) {
        TEST_EQ32(output[i], rhs[i], kTestId);
    }
    test_pass();
}
