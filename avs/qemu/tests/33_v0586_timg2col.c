#include "linx_test.h"

#include <stdint.h>

enum { kElements = 32, kRowStrideBytes = 8 * sizeof(uint32_t) };
static const uint32_t kTestId = 0x00002F01u;

extern void linx_v0586_timg2col(const uint32_t *input, uint32_t *output,
                                uint64_t param0, uint64_t param1,
                                uint64_t param2, uint64_t row_stride_bytes);

void run_tile_v0586_timg2col_tests(void)
{
    uint32_t input[kElements] __attribute__((aligned(64)));
    uint32_t output[kElements] __attribute__((aligned(64)));
    const uint64_t param0 = UINT64_C(1) |
                            (UINT64_C(4) << 16) |
                            (UINT64_C(8) << 32) |
                            (UINT64_C(1) << 48) |
                            (UINT64_C(1) << 56);
    const uint64_t param1 = (UINT64_C(1) << 32) |
                            (UINT64_C(1) << 37) |
                            (UINT64_C(1) << 42) |
                            (UINT64_C(1) << 48);

    linx_test_disable_extension_first_use();
    test_start(kTestId);
    for (unsigned i = 0; i < kElements; ++i) {
        input[i] = i + 1u;
        output[i] = UINT32_C(0xA5A5A5A5);
    }

    linx_v0586_timg2col(input, output, param0, param1, 0,
                        kRowStrideBytes);
    for (unsigned i = 0; i < kElements; ++i) {
        TEST_EQ32(output[i], input[i], 0x00002F10u + i);
    }
    test_pass();
}
