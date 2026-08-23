#include "linx_test.h"

#include <stdint.h>

enum {
    kDim = 4,
    kElements = kDim * kDim,
    kInputRowStrideBytes = kDim * sizeof(uint8_t),
    kOutputRowStrideBytes = kDim * sizeof(uint32_t),
};
static const uint32_t kTestId = 0x00002D01u;

static uint8_t lhs[kElements] __attribute__((aligned(64)));
static uint8_t rhs[kElements] __attribute__((aligned(64)));
static uint32_t output[kElements] __attribute__((aligned(64)));

extern void linx_v0583_cube_matmul(const uint8_t *a, const uint8_t *b,
                                   uint32_t *dst, uint64_t input_row_stride_bytes,
                                   uint64_t output_row_stride_bytes);

void run_tile_v0583_cube_tests(void)
{
    linx_test_disable_extension_first_use();
    test_start(kTestId);
    for (unsigned row = 0; row < kDim; ++row) {
        for (unsigned col = 0; col < kDim; ++col) {
            const unsigned index = row * kDim + col;
            lhs[index] = row == col ? 1 : 0;
            rhs[index] = (uint8_t)(index + 1u);
            output[index] = UINT32_C(0xA5A5A5A5);
        }
    }

    linx_v0583_cube_matmul(lhs, rhs, output, kInputRowStrideBytes,
                           kOutputRowStrideBytes);

    for (unsigned i = 0; i < kElements; ++i) {
        TEST_EQ32(output[i], (uint32_t)rhs[i], kTestId);
    }
    test_pass();
}
