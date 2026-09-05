#include "linx_test.h"

#include <stdint.h>

enum { kElements = 32, kRowStrideBytes = kElements * sizeof(uint32_t) };
static const uint32_t kTestId = 0x00002E01u;

extern void linx_v0586_mgather_add(uint32_t *target, const uint32_t *indices,
                                   const uint32_t *values,
                                   uint32_t *old_values, uint64_t unused,
                                   uint64_t row_stride_bytes);
extern void linx_v0586_mscatter_popc(uint32_t *target,
                                     const uint32_t *indices,
                                     uint64_t row_stride_bytes);

void run_tile_v0586_gm_atom_red_tests(void)
{
    uint32_t target[kElements] __attribute__((aligned(64)));
    uint32_t indices[kElements] __attribute__((aligned(64)));
    uint32_t values[kElements] __attribute__((aligned(64)));
    uint32_t old_values[kElements] __attribute__((aligned(64)));

    linx_test_disable_extension_first_use();
    test_start(kTestId);
    for (unsigned i = 0; i < kElements; ++i) {
        target[i] = 3u + i;
        indices[i] = i * sizeof(uint32_t);
        values[i] = 5u;
        old_values[i] = 0u;
    }

    linx_v0586_mgather_add(target, indices, values, old_values, 0,
                           kRowStrideBytes);
    for (unsigned i = 0; i < kElements; ++i) {
        TEST_EQ32(old_values[i], 3u + i, 0x00002E10u + i);
        TEST_EQ32(target[i], 8u + i, 0x00002E30u + i);
    }

    target[0] = 100u;
    for (unsigned i = 0; i < kElements; ++i) {
        indices[i] = 0u;
        values[i] = 1u;
        old_values[i] = 0u;
    }
    linx_v0586_mgather_add(target, indices, values, old_values, 0,
                           kRowStrideBytes);
    for (unsigned i = 0; i < kElements; ++i) {
        TEST_EQ32(old_values[i], 100u + i, 0x00002E70u + i);
    }
    TEST_EQ32(target[0], 100u + kElements, 0x00002E90u);

    for (unsigned i = 0; i < kElements; ++i) {
        target[i] = 8u + i;
        indices[i] = i * sizeof(uint32_t);
    }
    linx_v0586_mscatter_popc(target, indices, kRowStrideBytes);
    for (unsigned i = 0; i < kElements; ++i) {
        TEST_EQ32(target[i], 9u + i, 0x00002E50u + i);
    }
    test_pass();
}
