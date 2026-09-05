#include "linx_test.h"

#include <stdint.h>

enum { kElements = 1024, kRowStrideBytes = 32 * sizeof(int32_t) };
static const uint32_t kTestId = 0x00002A01u;

extern void linx_v0583_tlsu_copy(const int32_t *src, int32_t *dst,
                                 uint64_t row_stride_bytes);

void run_tile_v0583_tlsu_tests(void)
{
    int32_t input[kElements] __attribute__((aligned(64)));
    int32_t output[kElements] __attribute__((aligned(64)));

    linx_test_disable_extension_first_use();
    test_start(kTestId);
    for (unsigned i = 0; i < kElements; ++i) {
        input[i] = (int32_t)(i * 17u) - 4091;
        output[i] = (int32_t)0x55555555u;
    }

    linx_v0583_tlsu_copy(input, output, kRowStrideBytes);

    for (unsigned i = 0; i < kElements; ++i) {
        TEST_EQ32((uint32_t)output[i], (uint32_t)input[i], kTestId);
    }
    test_pass();
}
