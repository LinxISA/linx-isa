#include "linx_test.h"

enum {
    TESTID_SIMT_AUTOVEC_FOUND_MID = 0x1F80,
    TESTID_SIMT_AUTOVEC_FOUND_TAIL = 0x1F81,
    TESTID_SIMT_AUTOVEC_NOT_FOUND = 0x1F82,
    TESTID_SIMT_AUTOVEC_RUNNING_SUM_STORE_BASE = 0x1F84,
    TESTID_SIMT_AUTOVEC_RUNNING_SUM_LIVEOUT = 0x1F85,
    TESTID_SIMT_AUTOVEC_REDUCTION_LIVEOUT = 0x1F86,
    TESTID_SIMT_AUTOVEC_IFCVT_INNER_BASE = 0x1F90,
    TESTID_SIMT_AUTOVEC_IFCVT_NESTED_BASE = 0x1FD0,
    TESTID_SIMT_AUTOVEC_STORE_DIAMOND_BASE = 0x2010,
    TESTID_SIMT_AUTOVEC_SPLIT_ADDR_B_BASE = 0x2050,
    TESTID_SIMT_AUTOVEC_SPLIT_ADDR_C_BASE = 0x2090,
    TESTID_SIMT_AUTOVEC_SPLIT_ADDR_OUT = 0x20C8,
    TESTID_SIMT_AUTOVEC_SHIFT_HALF_BASE = 0x20D0,
    TESTID_SIMT_AUTOVEC_MIN_SELECT_BASE = 0x2150,
    TESTID_SIMT_AUTOVEC_SHIFTED_OUT_BASE = 0x2190,
    TESTID_SIMT_AUTOVEC_LAST_VALUE_LIVEOUT = 0x21D0,
    TESTID_SIMT_AUTOVEC_I32_FILL_BASE = 0x2210,
    TESTID_SIMT_AUTOVEC_I8_FILL_BASE = 0x2250,
    TESTID_SIMT_AUTOVEC_I16_FILL_BASE = 0x2290,
    TESTID_SIMT_AUTOVEC_U8_COPY_BASE = 0x22D0,
    TESTID_SIMT_AUTOVEC_U16_COPY_BASE = 0x2310,
    TESTID_SIMT_AUTOVEC_I8_WIDEN_BASE = 0x2350,
    TESTID_SIMT_AUTOVEC_I16_WIDEN_BASE = 0x2390,
    TESTID_SIMT_AUTOVEC_I8_SIGN_CLASSIFY_BASE = 0x23D0,
    TESTID_SIMT_AUTOVEC_I16_SIGN_CLASSIFY_BASE = 0x2410,
};

__attribute__((noinline, optnone))
static void fill_i32(int32_t *buf, int32_t value, uint32_t count) {
    for (uint32_t i = 0; i < count; ++i) {
        buf[i] = value;
    }
}

__attribute__((noinline))
static void fill_i32_autovec(int32_t *buf, int32_t value) {
    for (uint64_t i = 0; i < 64; ++i) {
        buf[i] = value;
    }
}

__attribute__((noinline))
static void fill_i8_autovec(int8_t *buf, int8_t value) {
    for (uint64_t i = 0; i < 64; ++i) {
        buf[i] = value;
    }
}

__attribute__((noinline))
static void fill_i16_autovec(int16_t *buf, int16_t value) {
    for (uint64_t i = 0; i < 64; ++i) {
        buf[i] = value;
    }
}

__attribute__((noinline))
static void copy_u8_autovec(const uint8_t *src, uint8_t *dst) {
    for (uint64_t i = 0; i < 64; ++i) {
        dst[i] = src[i];
    }
}

__attribute__((noinline))
static void copy_u16_autovec(const uint16_t *src, uint16_t *dst) {
    for (uint64_t i = 0; i < 64; ++i) {
        dst[i] = src[i];
    }
}

__attribute__((noinline))
static void widen_i8_to_i32_autovec(const int8_t *src, int32_t *dst) {
    for (uint64_t i = 0; i < 64; ++i) {
        dst[i] = src[i];
    }
}

__attribute__((noinline))
static void widen_i16_to_i32_autovec(const int16_t *src, int32_t *dst) {
    for (uint64_t i = 0; i < 64; ++i) {
        dst[i] = src[i];
    }
}

__attribute__((noinline))
static void sign_classify_i8_autovec(const int8_t *src, int32_t *dst) {
    for (uint64_t i = 0; i < 64; ++i) {
        int8_t v = src[i];
        dst[i] = (v < 0) ? -1 : 1;
    }
}

__attribute__((noinline))
static void sign_classify_i16_autovec(const int16_t *src, int32_t *dst) {
    for (uint64_t i = 0; i < 64; ++i) {
        int16_t v = src[i];
        dst[i] = (v < 0) ? -1 : 1;
    }
}

__attribute__((noinline))
static void search_store_index_grouped_boundary(const int32_t *a, int32_t *out) {
    int32_t found = -1;

    for (uint64_t i = 0; i < 64; ++i) {
        int32_t v = a[i];
        if (v > 0) {
            found = (int32_t)i;
            break;
        }
    }

    *out = found;
}

__attribute__((noinline))
static void search_store_index_split_addrs_autovec(const int32_t *a, float *b,
                                                   float *c, int32_t *out) {
    int32_t found = -1;

    for (uint64_t i = 0; i < 64; ++i) {
        int32_t v = a[i];
        if (v > 10) {
            found = (int32_t)i;
            break;
        }
        if (v < 5) {
            b[i] = 1.0f;
        } else {
            c[i] = 2.0f;
        }
    }

    *out = found;
}

__attribute__((noinline))
static void running_sum_store(const float *a, float *out) {
    float acc = 0.0f;

    for (uint64_t i = 0; i < 64; ++i) {
        acc += a[i];
        out[i] = acc;
    }
}

__attribute__((noinline))
static void running_sum_liveout(const float *a, float *out) {
    float acc = 1.0f;

    for (uint64_t i = 0; i < 64; ++i) {
        acc += a[i];
    }

    *out = acc;
}

__attribute__((noinline))
static void reduction_sum_liveout(const float *a, float *out) {
    float acc = 0.0f;

    for (uint64_t i = 0; i < 64; ++i) {
        acc += a[i];
    }

    *out = acc;
}

__attribute__((noinline))
static void copy_and_last_value_liveout(const float *a, float *tmp, float *out) {
    float last = -99.0f;

    for (uint64_t i = 0; i < 64; ++i) {
        last = a[i];
        tmp[i] = last;
    }

    *out = last;
}

__attribute__((noinline))
static void vector_inner_if_ifcvt(const float *b, float *a) {
    for (uint64_t i = 0; i < 64; ++i) {
        float bv = b[i];
        float out = (bv > 0.0f) ? (bv + 1.0f) : (0.0f - bv);
        a[i] = out;
    }
}

__attribute__((noinline))
static void vector_nested_if_ifcvt(const float *b, float *a) {
    for (uint64_t i = 0; i < 64; ++i) {
        float bv = b[i];
        float out;
        if (bv > 0.0f) {
            out = (bv > 10.0f) ? 1.0f : 2.0f;
        } else {
            out = 3.0f;
        }
        a[i] = out;
    }
}

__attribute__((noinline))
static void vector_store_diamond_ifcvt(const float *b, float *a) {
    for (uint64_t i = 0; i < 64; ++i) {
        float bv = b[i];
        if (bv > 0.0f) {
            a[i] = bv + 1.0f;
        } else {
            a[i] = 0.0f - bv;
        }
    }
}

__attribute__((noinline))
static void vector_shift_half_index(const int32_t *b, const int32_t *c,
                                    const int32_t *d, int32_t *a) {
    for (uint64_t i = 0; i < 64; ++i) {
        (void)d;
        a[i] = b[i] + c[i >> 1];
    }
}

__attribute__((noinline))
static void vector_min_select_store(const float *a, const float *b, float *out) {
    for (uint64_t i = 0; i < 64; ++i) {
        float av = a[i];
        float bv = b[i];
        out[i] = (av > bv) ? bv : av;
    }
}

__attribute__((noinline))
static void vector_shifted_out_store(float *a, const float *b) {
    for (uint64_t i = 0; i < 32; ++i) {
        a[i + 32] = a[i] + b[i];
    }
}

static void fill_ifcvt_pattern(float *buf) {
    static const float kPattern[8] = {
        -4.0f, -1.0f, 0.0f, 0.5f,
        5.0f, 11.0f, -2.5f, 12.0f,
    };

    for (uint32_t i = 0; i < 64; ++i) {
        buf[i] = kPattern[i & 7u];
    }
}

static void test_search_found_mid(void) {
    int32_t a[64];
    int32_t out = -1;

    fill_i32(a, 0, 64);
    a[37] = 7;

    search_store_index_grouped_boundary(a, &out);
    TEST_EQ32(out, 37, TESTID_SIMT_AUTOVEC_FOUND_MID);
}

static void test_search_found_tail(void) {
    int32_t a[64];
    int32_t out = -1;

    fill_i32(a, 0, 64);
    a[63] = 3;

    search_store_index_grouped_boundary(a, &out);
    TEST_EQ32(out, 63, TESTID_SIMT_AUTOVEC_FOUND_TAIL);
}

static void test_search_not_found_preserves_out(void) {
    int32_t a[64];
    int32_t out = 0x13579BDF;

    fill_i32(a, 0, 64);

    search_store_index_grouped_boundary(a, &out);
    TEST_EQ32(out, (uint32_t)-1, TESTID_SIMT_AUTOVEC_NOT_FOUND);
}

static void test_search_split_addrs_found_mid(void) {
    int32_t a[64];
    float b[64];
    float c[64];
    int32_t out = -1;

    for (uint32_t i = 0; i < 64; ++i) {
        a[i] = 99;
        b[i] = 9.0f;
        c[i] = 9.0f;
    }
    for (uint32_t i = 0; i < 16; ++i) {
        a[i] = (i & 1u) ? 7 : 0;
    }
    a[16] = 12;

    search_store_index_split_addrs_autovec(a, b, c, &out);
    TEST_EQ32((uint32_t)out, 16u, TESTID_SIMT_AUTOVEC_SPLIT_ADDR_OUT);

    for (uint32_t i = 0; i < 64; ++i) {
        union {
            float f;
            uint32_t u;
        } got_b = { .f = b[i] }, got_c = { .f = c[i] };
        union {
            float f;
            uint32_t u;
        } expect_b = { .f = 9.0f }, expect_c = { .f = 9.0f };
        if (i < 16) {
            if (a[i] < 5) {
                expect_b.f = 1.0f;
            } else {
                expect_c.f = 2.0f;
            }
        }
        TEST_EQ32(got_b.u, expect_b.u,
                  TESTID_SIMT_AUTOVEC_SPLIT_ADDR_B_BASE + i);
        TEST_EQ32(got_c.u, expect_c.u,
                  TESTID_SIMT_AUTOVEC_SPLIT_ADDR_C_BASE + i);
    }
}

static void test_running_sum_store(void) {
    float src[64];
    float dst[64];
    float acc = 0.0f;

    for (uint32_t i = 0; i < 64; ++i) {
        src[i] = (float)((i & 3u) + 1u);
        dst[i] = -1.0f;
    }

    running_sum_store(src, dst);

    for (uint32_t i = 0; i < 64; ++i) {
        union {
            float f;
            uint32_t u;
        } got, expect;
        acc += src[i];
        got.f = dst[i];
        expect.f = acc;
        TEST_EQ32(got.u, expect.u,
                  TESTID_SIMT_AUTOVEC_RUNNING_SUM_STORE_BASE + i);
    }
}

static void test_running_sum_liveout(void) {
    float src[64];
    float out = -1.0f;
    float acc = 1.0f;

    for (uint32_t i = 0; i < 64; ++i) {
        src[i] = (float)((i % 5u) - 2u);
        acc += src[i];
    }

    running_sum_liveout(src, &out);

    union {
        float f;
        uint32_t u;
    } got = { .f = out }, expect = { .f = acc };
    TEST_EQ32(got.u, expect.u, TESTID_SIMT_AUTOVEC_RUNNING_SUM_LIVEOUT);
}

static void test_reduction_sum_liveout(void) {
    float src[64];
    float out = -1.0f;
    float acc = 0.0f;

    for (uint32_t i = 0; i < 64; ++i) {
        src[i] = (float)((int32_t)(i & 7u) - 3);
        acc += src[i];
    }

    reduction_sum_liveout(src, &out);

    union {
        float f;
        uint32_t u;
    } got = { .f = out }, expect = { .f = acc };
    TEST_EQ32(got.u, expect.u, TESTID_SIMT_AUTOVEC_REDUCTION_LIVEOUT);
}

static void test_last_value_liveout(void) {
    float src[64];
    float tmp[64];
    float out = -1.0f;

    for (uint32_t i = 0; i < 64; ++i) {
        src[i] = (float)((int32_t)i - 11);
        tmp[i] = 99.0f;
    }

    copy_and_last_value_liveout(src, tmp, &out);

    for (uint32_t i = 0; i < 64; ++i) {
        union {
            float f;
            uint32_t u;
        } got = { .f = tmp[i] }, expect = { .f = src[i] };
        TEST_EQ32(got.u, expect.u, TESTID_SIMT_AUTOVEC_LAST_VALUE_LIVEOUT + 1u + i);
    }

    union {
        float f;
        uint32_t u;
    } got = { .f = out }, expect = { .f = src[63] };
    TEST_EQ32(got.u, expect.u, TESTID_SIMT_AUTOVEC_LAST_VALUE_LIVEOUT);
}

static void test_vector_inner_if_ifcvt(void) {
    float src[64];
    float dst[64];
    static const uint32_t expect_bits[8] = {
        0x40800000u, 0x3f800000u, 0x00000000u, 0x3fc00000u,
        0x40c00000u, 0x41400000u, 0x40200000u, 0x41500000u,
    };

    fill_ifcvt_pattern(src);
    for (uint32_t i = 0; i < 64; ++i) {
        dst[i] = 99.0f;
    }

    vector_inner_if_ifcvt(src, dst);

    for (uint32_t i = 0; i < 64; ++i) {
        union {
            float f;
            uint32_t u;
        } got = { .f = dst[i] };
        TEST_EQ32(got.u, expect_bits[i & 7u], TESTID_SIMT_AUTOVEC_IFCVT_INNER_BASE + i);
    }
}

static void test_vector_nested_if_ifcvt(void) {
    float src[64];
    float dst[64];
    static const uint32_t expect_bits[8] = {
        0x40400000u, 0x40400000u, 0x40400000u, 0x40000000u,
        0x40000000u, 0x3f800000u, 0x40400000u, 0x3f800000u,
    };

    fill_ifcvt_pattern(src);
    for (uint32_t i = 0; i < 64; ++i) {
        dst[i] = 77.0f;
    }

    vector_nested_if_ifcvt(src, dst);

    for (uint32_t i = 0; i < 64; ++i) {
        union {
            float f;
            uint32_t u;
        } got = { .f = dst[i] };
        TEST_EQ32(got.u, expect_bits[i & 7u], TESTID_SIMT_AUTOVEC_IFCVT_NESTED_BASE + i);
    }
}

static void test_vector_store_diamond_ifcvt(void) {
    float src[64];
    float dst[64];
    static const uint32_t expect_bits[8] = {
        0x40800000u, 0x3f800000u, 0x00000000u, 0x3fc00000u,
        0x40c00000u, 0x41400000u, 0x40200000u, 0x41500000u,
    };

    fill_ifcvt_pattern(src);
    for (uint32_t i = 0; i < 64; ++i) {
        dst[i] = 55.0f;
    }

    vector_store_diamond_ifcvt(src, dst);

    for (uint32_t i = 0; i < 64; ++i) {
        union {
            float f;
            uint32_t u;
        } got = { .f = dst[i] };
        TEST_EQ32(got.u, expect_bits[i & 7u],
                  TESTID_SIMT_AUTOVEC_STORE_DIAMOND_BASE + i);
    }
}

static void test_vector_shift_half_index(void) {
    int32_t b[64];
    int32_t c[32];
    int32_t d[64];
    int32_t a[64];

    for (uint32_t i = 0; i < 64; ++i) {
        b[i] = (int32_t)(i & 1u);
        d[i] = 0;
        a[i] = 99;
    }
    for (uint32_t i = 0; i < 32; ++i) {
        c[i] = (int32_t)(2 + i);
    }

    vector_shift_half_index(b, c, d, a);

    for (uint32_t i = 0; i < 64; ++i) {
        int32_t expect = b[i] + c[i >> 1];
        TEST_EQ32((uint32_t)a[i], (uint32_t)expect,
                  TESTID_SIMT_AUTOVEC_SHIFT_HALF_BASE + i);
    }
}

static void test_vector_min_select_store(void) {
    float a[64];
    float b[64];
    float out[64];
    static const uint32_t expect_bits[8] = {
        0x40800000u, 0x3f800000u, 0xc0000000u, 0x3f000000u,
        0x41000000u, 0x40400000u, 0xbf800000u, 0x00000000u,
    };
    static const float pat_a[8] = {
        5.0f, 1.0f, -1.0f, 1.5f, 8.0f, 3.0f, 4.0f, 0.0f,
    };
    static const float pat_b[8] = {
        4.0f, 2.0f, -2.0f, 0.5f, 9.0f, 4.0f, -1.0f, 1.0f,
    };

    for (uint32_t i = 0; i < 64; ++i) {
        a[i] = pat_a[i & 7u];
        b[i] = pat_b[i & 7u];
        out[i] = 77.0f;
    }

    vector_min_select_store(a, b, out);

    for (uint32_t i = 0; i < 64; ++i) {
        union {
            float f;
            uint32_t u;
        } got = { .f = out[i] };
        TEST_EQ32(got.u, expect_bits[i & 7u],
                  TESTID_SIMT_AUTOVEC_MIN_SELECT_BASE + i);
    }
}

static void test_vector_shifted_out_store(void) {
    float a[64];
    float b[32];

    for (uint32_t i = 0; i < 32; ++i) {
        a[i] = (float)i;
        b[i] = (float)(100 + i);
    }
    for (uint32_t i = 32; i < 64; ++i) {
        a[i] = -1.0f;
    }

    vector_shifted_out_store(a, b);

    for (uint32_t i = 0; i < 32; ++i) {
        union {
            float f;
            uint32_t u;
        } got = { .f = a[i + 32] };
        union {
            float f;
            uint32_t u;
        } expect = { .f = (float)(100 + (2 * (int32_t)i)) };
        TEST_EQ32(got.u, expect.u, TESTID_SIMT_AUTOVEC_SHIFTED_OUT_BASE + i);
    }
}

static void test_fill_i32_autovec(void) {
    int32_t buf[64];

    for (uint32_t i = 0; i < 64; ++i) {
        buf[i] = (int32_t)i;
    }

    fill_i32_autovec(buf, -17);

    for (uint32_t i = 0; i < 64; ++i) {
        TEST_EQ32((uint32_t)buf[i], (uint32_t)-17,
                  TESTID_SIMT_AUTOVEC_I32_FILL_BASE + i);
    }
}

static void test_fill_i8_autovec(void) {
    int8_t buf[64];

    for (uint32_t i = 0; i < 64; ++i) {
        buf[i] = (int8_t)i;
    }

    fill_i8_autovec(buf, (int8_t)-9);

    for (uint32_t i = 0; i < 64; ++i) {
        TEST_EQ32((uint32_t)(uint8_t)buf[i], (uint32_t)(uint8_t)-9,
                  TESTID_SIMT_AUTOVEC_I8_FILL_BASE + i);
    }
}

static void test_fill_i16_autovec(void) {
    int16_t buf[64];

    for (uint32_t i = 0; i < 64; ++i) {
        buf[i] = (int16_t)i;
    }

    fill_i16_autovec(buf, (int16_t)-513);

    for (uint32_t i = 0; i < 64; ++i) {
        TEST_EQ32((uint32_t)(uint16_t)buf[i], (uint32_t)(uint16_t)-513,
                  TESTID_SIMT_AUTOVEC_I16_FILL_BASE + i);
    }
}

static void test_copy_u8_autovec(void) {
    uint8_t src[64];
    uint8_t dst[64];

    for (uint32_t i = 0; i < 64; ++i) {
        src[i] = (uint8_t)(0x80u + (3u * i));
        dst[i] = 0;
    }

    copy_u8_autovec(src, dst);

    for (uint32_t i = 0; i < 64; ++i) {
        TEST_EQ32((uint32_t)dst[i], (uint32_t)src[i],
                  TESTID_SIMT_AUTOVEC_U8_COPY_BASE + i);
    }
}

static void test_copy_u16_autovec(void) {
    uint16_t src[64];
    uint16_t dst[64];

    for (uint32_t i = 0; i < 64; ++i) {
        src[i] = (uint16_t)(0x8000u + (257u * i));
        dst[i] = 0;
    }

    copy_u16_autovec(src, dst);

    for (uint32_t i = 0; i < 64; ++i) {
        TEST_EQ32((uint32_t)dst[i], (uint32_t)src[i],
                  TESTID_SIMT_AUTOVEC_U16_COPY_BASE + i);
    }
}

static void test_widen_i8_to_i32_autovec(void) {
    int8_t src[64];
    int32_t dst[64];

    for (uint32_t i = 0; i < 64; ++i) {
        src[i] = (int8_t)((int32_t)(i * 5u) - 97);
        dst[i] = 0x13579BDF;
    }

    widen_i8_to_i32_autovec(src, dst);

    for (uint32_t i = 0; i < 64; ++i) {
        TEST_EQ32((uint32_t)dst[i], (uint32_t)(int32_t)src[i],
                  TESTID_SIMT_AUTOVEC_I8_WIDEN_BASE + i);
    }
}

static void test_widen_i16_to_i32_autovec(void) {
    int16_t src[64];
    int32_t dst[64];

    for (uint32_t i = 0; i < 64; ++i) {
        src[i] = (int16_t)((int32_t)(i * 257u) - 20000);
        dst[i] = 0x2468ACE0;
    }

    widen_i16_to_i32_autovec(src, dst);

    for (uint32_t i = 0; i < 64; ++i) {
        TEST_EQ32((uint32_t)dst[i], (uint32_t)(int32_t)src[i],
                  TESTID_SIMT_AUTOVEC_I16_WIDEN_BASE + i);
    }
}

static void test_sign_classify_i8_autovec(void) {
    int8_t src[64];
    int32_t dst[64];

    for (uint32_t i = 0; i < 64; ++i) {
        src[i] = (i & 1u) ? (int8_t)(i + 3u) : (int8_t)(-1 - (int32_t)i);
        dst[i] = 0;
    }

    sign_classify_i8_autovec(src, dst);

    for (uint32_t i = 0; i < 64; ++i) {
        const int32_t expected = (src[i] < 0) ? -1 : 1;
        TEST_EQ32((uint32_t)dst[i], (uint32_t)expected,
                  TESTID_SIMT_AUTOVEC_I8_SIGN_CLASSIFY_BASE + i);
    }
}

static void test_sign_classify_i16_autovec(void) {
    int16_t src[64];
    int32_t dst[64];

    for (uint32_t i = 0; i < 64; ++i) {
        src[i] =
            (i & 1u) ? (int16_t)(1000 + (int32_t)(17u * i))
                     : (int16_t)(-2000 - (int32_t)(33u * i));
        dst[i] = 0;
    }

    sign_classify_i16_autovec(src, dst);

    for (uint32_t i = 0; i < 64; ++i) {
        const int32_t expected = (src[i] < 0) ? -1 : 1;
        TEST_EQ32((uint32_t)dst[i], (uint32_t)expected,
                  TESTID_SIMT_AUTOVEC_I16_SIGN_CLASSIFY_BASE + i);
    }
}

__attribute__((noinline, optnone))
static void run_simt_autovec_narrow_load_tests(void) {
    test_start(TESTID_SIMT_AUTOVEC_U8_COPY_BASE);
    uart_puts("SIMT autovec grouped u8 copy ... ");
    test_copy_u8_autovec();
    test_pass();

    test_start(TESTID_SIMT_AUTOVEC_U16_COPY_BASE);
    uart_puts("SIMT autovec grouped u16 copy ... ");
    test_copy_u16_autovec();
    test_pass();

    test_start(TESTID_SIMT_AUTOVEC_I8_WIDEN_BASE);
    uart_puts("SIMT autovec grouped i8 sign-widen ... ");
    test_widen_i8_to_i32_autovec();
    test_pass();

    test_start(TESTID_SIMT_AUTOVEC_I16_WIDEN_BASE);
    uart_puts("SIMT autovec grouped i16 sign-widen ... ");
    test_widen_i16_to_i32_autovec();
    test_pass();

    test_start(TESTID_SIMT_AUTOVEC_I8_SIGN_CLASSIFY_BASE);
    uart_puts("SIMT autovec grouped i8 signed classify ... ");
    test_sign_classify_i8_autovec();
    test_pass();

    test_start(TESTID_SIMT_AUTOVEC_I16_SIGN_CLASSIFY_BASE);
    uart_puts("SIMT autovec grouped i16 signed classify ... ");
    test_sign_classify_i16_autovec();
    test_pass();
}

__attribute__((noinline, optnone))
void run_simt_autovec_tests(void) {
    test_suite_begin(0x1F80);

    test_start(TESTID_SIMT_AUTOVEC_FOUND_MID);
    uart_puts("SIMT autovec grouped active-replay mid hit ... ");
    test_search_found_mid();
    test_pass();

    test_start(TESTID_SIMT_AUTOVEC_FOUND_TAIL);
    uart_puts("SIMT autovec grouped active-replay tail hit ... ");
    test_search_found_tail();
    test_pass();

    test_start(TESTID_SIMT_AUTOVEC_NOT_FOUND);
    uart_puts("SIMT autovec grouped active-replay miss ... ");
    test_search_not_found_preserves_out();
    test_pass();

    test_start(TESTID_SIMT_AUTOVEC_SPLIT_ADDR_B_BASE);
    uart_puts("SIMT autovec grouped split-address replay ... ");
    test_search_split_addrs_found_mid();
    test_pass();

    test_start(TESTID_SIMT_AUTOVEC_RUNNING_SUM_STORE_BASE);
    uart_puts("SIMT autovec grouped recurrence prefix sum ... ");
    test_running_sum_store();
    test_pass();

    test_start(TESTID_SIMT_AUTOVEC_RUNNING_SUM_LIVEOUT);
    uart_puts("SIMT autovec grouped recurrence liveout ... ");
    test_running_sum_liveout();
    test_pass();

    test_start(TESTID_SIMT_AUTOVEC_REDUCTION_LIVEOUT);
    uart_puts("SIMT autovec grouped reduction liveout ... ");
    test_reduction_sum_liveout();
    test_pass();

    test_start(TESTID_SIMT_AUTOVEC_LAST_VALUE_LIVEOUT);
    uart_puts("SIMT autovec grouped generic liveout ... ");
    test_last_value_liveout();
    test_pass();

    test_start(TESTID_SIMT_AUTOVEC_IFCVT_INNER_BASE);
    uart_puts("SIMT autovec grouped if-convert inner diamond ... ");
    test_vector_inner_if_ifcvt();
    test_pass();

    test_start(TESTID_SIMT_AUTOVEC_IFCVT_NESTED_BASE);
    uart_puts("SIMT autovec grouped if-convert nested diamond ... ");
    test_vector_nested_if_ifcvt();
    test_pass();

    test_start(TESTID_SIMT_AUTOVEC_STORE_DIAMOND_BASE);
    uart_puts("SIMT autovec grouped if-convert store diamond ... ");
    test_vector_store_diamond_ifcvt();
    test_pass();

    test_start(TESTID_SIMT_AUTOVEC_SHIFT_HALF_BASE);
    uart_puts("SIMT autovec TSVC shifted half-index boundary ... ");
    test_vector_shift_half_index();
    test_pass();

    test_start(TESTID_SIMT_AUTOVEC_MIN_SELECT_BASE);
    uart_puts("SIMT autovec grouped elemental min select ... ");
    test_vector_min_select_store();
    test_pass();

    test_start(TESTID_SIMT_AUTOVEC_SHIFTED_OUT_BASE);
    uart_puts("SIMT autovec grouped shifted output store ... ");
    test_vector_shifted_out_store();
    test_pass();

    test_start(TESTID_SIMT_AUTOVEC_I32_FILL_BASE);
    uart_puts("SIMT autovec grouped invariant i32 fill ... ");
    test_fill_i32_autovec();
    test_pass();

    test_start(TESTID_SIMT_AUTOVEC_I8_FILL_BASE);
    uart_puts("SIMT autovec grouped invariant i8 fill ... ");
    test_fill_i8_autovec();
    test_pass();

    test_start(TESTID_SIMT_AUTOVEC_I16_FILL_BASE);
    uart_puts("SIMT autovec grouped invariant i16 fill ... ");
    test_fill_i16_autovec();
    test_pass();

    run_simt_autovec_narrow_load_tests();
}
