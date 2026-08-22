#include "linx_test.h"

#include <stdint.h>

enum { kElements = 1024, kRowStrideBytes = 32 * sizeof(uint32_t) };
static const uint32_t kTestId = 0x00002B01u;

static uint32_t lhs[kElements] __attribute__((aligned(64)));
static uint32_t rhs[kElements] __attribute__((aligned(64)));
static uint32_t output[kElements] __attribute__((aligned(64)));

extern void linx_v0583_vec_add(const uint32_t *a, const uint32_t *b,
                               uint32_t *dst, uint64_t row_stride_bytes);

void run_tile_v0583_vec_tests(void)
{
    test_start(kTestId);
    for (unsigned i = 0; i < kElements; ++i) {
        lhs[i] = 0x3F800000u;
        rhs[i] = 0x40000000u;
        output[i] = 0x55555555u;
    }

    linx_v0583_vec_add(lhs, rhs, output, kRowStrideBytes);

    for (unsigned i = 0; i < kElements; ++i) {
        TEST_EQ32(output[i], 0x40400000u, kTestId);
    }
    test_pass();
}
