#ifndef LINX_AVS_QEMU_TILE_TEST_COMMON_HPP
#define LINX_AVS_QEMU_TILE_TEST_COMMON_HPP

#include "linx_test.h"

#define __LINX_TAU__ 1
#include <pto/linx/AutoModeKernels.hpp>

namespace linx::test::tile {

static constexpr unsigned kTileElemsI32 = pto::linx::auto_mode::kTileElemsI32;
static constexpr unsigned kTileSizeCode = pto::linx::auto_mode::kFullTileSizeCode;

static inline void matmul_ref_i32_8x8(int32_t out[64], const int32_t a[64],
                                     const int32_t b[64])
{
    for (unsigned i = 0; i < 8; i++) {
        for (unsigned j = 0; j < 8; j++) {
            int64_t acc = 0;
            for (unsigned k = 0; k < 8; k++) {
                acc += (int64_t)a[i * 8u + k] * (int64_t)b[k * 8u + j];
            }
            out[i * 8u + j] = (int32_t)acc;
        }
    }
}

static inline int32_t *tile_ptr(int32_t *buffer, unsigned tile_idx)
{
    return buffer + tile_idx * kTileElemsI32;
}

static inline const int32_t *tile_ptr(const int32_t *buffer, unsigned tile_idx)
{
    return buffer + tile_idx * kTileElemsI32;
}

static inline void init_tile_pattern(int32_t *tile, int32_t seed)
{
    for (unsigned i = 0; i < kTileElemsI32; i++) {
        tile[i] = 0;
    }
    for (unsigned i = 0; i < 64; i++) {
        const int32_t lane = (int32_t)(i % 13u) - 6;
        const int32_t col = (int32_t)(i & 7u) - 3;
        tile[i] = lane * seed + col;
    }
}

static inline int64_t checksum_tiles_i32(const int32_t *tiles,
                                         unsigned tile_count)
{
    int64_t checksum = 0;
    for (unsigned tile = 0; tile < tile_count; tile++) {
        const int32_t *base = tile_ptr(tiles, tile);
        for (unsigned i = 0; i < 64; i++) {
            checksum += (int64_t)base[i];
        }
    }
    return checksum;
}

static inline void print_checksum(const char *label, int64_t value)
{
    uart_puts(label);
    uart_puts("0x");
    uart_puthex64((uint64_t)value);
    uart_puts("\r\n");
}

static inline uint64_t fnv1a_bytes(const void *ptr, unsigned bytes)
{
    const uint8_t *p = (const uint8_t *)ptr;
    uint64_t h = UINT64_C(1469598103934665603);
    for (unsigned i = 0; i < bytes; ++i) {
        h ^= (uint64_t)p[i];
        h *= UINT64_C(1099511628211);
    }
    return h;
}

static inline uint32_t lcg32(uint32_t state)
{
    return state * 1664525u + 1013904223u;
}

static inline void seed_i32(int32_t *buf, unsigned n, uint32_t seed)
{
    uint32_t state = seed;
    for (unsigned i = 0; i < n; ++i) {
        state = lcg32(state);
        buf[i] = (int32_t)((state & 0x7fffu) - 0x3fffu);
    }
}

static inline void seed_f32(float *buf, unsigned n, uint32_t seed)
{
    uint32_t state = seed;
    for (unsigned i = 0; i < n; ++i) {
        state = lcg32(state);
        const uint32_t mantissa = state & 0xffffu;
        buf[i] = (float)((int32_t)mantissa - 32768) / 8192.0f;
    }
}

template <typename T>
static inline void zero(T *buf, unsigned n)
{
    for (unsigned i = 0; i < n; ++i) {
        buf[i] = (T)0;
    }
}

} // namespace linx::test::tile

#endif
