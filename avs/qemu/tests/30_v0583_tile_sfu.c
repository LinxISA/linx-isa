#include "linx_test.h"

#include <stdint.h>

enum { kElements = 1024, kRowStrideBytes = 32 * sizeof(uint32_t) };
static const uint32_t kTestId = 0x00002C01u;

static uint32_t input[kElements] __attribute__((aligned(64)));
static uint32_t output[kElements] __attribute__((aligned(64)));

extern void linx_v0583_sfu_exp(const uint32_t *src, uint32_t *dst,
                               uint64_t row_stride_bytes);

void run_tile_v0583_sfu_tests(void)
{
    test_start(kTestId);
    for (unsigned i = 0; i < kElements; ++i) {
        input[i] = 0x00000000u;
        output[i] = 0xBF800000u;
    }

    linx_v0583_sfu_exp(input, output, kRowStrideBytes);

    for (unsigned i = 0; i < kElements; ++i) {
        TEST_EQ32(output[i], 0x3F800000u, kTestId);
    }
    test_pass();
}
