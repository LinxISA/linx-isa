#include "linx_test.h"

#include <stdint.h>

enum { kElements = 1024 };
static const uint32_t kTestId = 0x00002A01u;

static int32_t input[kElements] __attribute__((aligned(64)));
static int32_t output[kElements] __attribute__((aligned(64)));

extern void linx_v058_tlsu_copy(const int32_t *src, int32_t *dst,
                                uint64_t stride);

void run_tile_v058_tlsu_tests(void)
{
    test_start(kTestId);
    for (unsigned i = 0; i < kElements; ++i) {
        input[i] = (int32_t)(i * 17u) - 4091;
        output[i] = (int32_t)0x55555555u;
    }

    linx_v058_tlsu_copy(input, output, 32u);

    for (unsigned i = 0; i < kElements; ++i) {
        TEST_EQ32((uint32_t)output[i], (uint32_t)input[i], kTestId);
    }
    test_pass();
}
