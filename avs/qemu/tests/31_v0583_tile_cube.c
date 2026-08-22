#include "linx_test.h"

#include <stdint.h>

enum { kDim = 4, kElements = kDim * kDim, kRowStrideBytes = kDim * sizeof(int32_t) };
static const uint32_t kTestId = 0x00002D01u;

static int32_t lhs[kElements] __attribute__((aligned(64)));
static int32_t rhs[kElements] __attribute__((aligned(64)));
static int32_t output[kElements] __attribute__((aligned(64)));

extern void linx_v0583_cube_matmul(const int32_t *a, const int32_t *b,
                                   int32_t *dst, uint64_t row_stride_bytes);

void run_tile_v0583_cube_tests(void)
{
    linx_test_disable_extension_first_use();
    test_start(kTestId);
    for (unsigned row = 0; row < kDim; ++row) {
        for (unsigned col = 0; col < kDim; ++col) {
            const unsigned index = row * kDim + col;
            lhs[index] = row == col ? 1 : 0;
            rhs[index] = (int32_t)(index + 1u);
            output[index] = (int32_t)0xA5A5A5A5u;
        }
    }

    linx_v0583_cube_matmul(lhs, rhs, output, kRowStrideBytes);

    for (unsigned i = 0; i < kElements; ++i) {
        TEST_EQ32((uint32_t)output[i], (uint32_t)rhs[i], kTestId);
    }
    test_pass();
}
