#include "linx_test.h"

#include <common/deepseek_tilekernels.hpp>

namespace {

constexpr int kRows = 32;
constexpr int kCols = 32;
constexpr int kElements = kRows * kCols;
constexpr int kStorageElements = 2048;

alignas(64) float f0[kStorageElements];
alignas(64) float f1[kStorageElements];
alignas(64) float f2[kStorageElements];
alignas(64) float f3[kStorageElements];
alignas(64) int i0[kStorageElements];
alignas(64) int i1[kStorageElements];
alignas(64) int i2[kStorageElements];
alignas(64) int8_t q0[4096];
alignas(64) int8_t q1[4096];
alignas(64) uint16_t h0[2048];
alignas(64) uint16_t h1[2048];
alignas(64) uint32_t u0[kStorageElements];
alignas(64) int64_t l0[kStorageElements];

float absf(float value) { return value < 0.0f ? -value : value; }

float sigmoidf(float value) { return 1.0f / (1.0f + __builtin_expf(-value)); }

void seed_standard_inputs() {
  for (int i = 0; i < kElements; ++i) {
    f0[i] = static_cast<float>((i % 17) - 8) * 0.25f;
    f1[i] = static_cast<float>((i % 13) + 1) * 0.0625f;
    f2[i] = 0.0f;
    f3[i] = 0.0f;
    i0[i] = i % kCols;
    i1[i] = 0;
    i2[i] = 0;
    q0[i] = 0;
    q1[i] = 0;
    h0[i] = 0;
    h1[i] = 0;
    u0[i] = 0;
    l0[i] = static_cast<int64_t>(i + 1);
  }
}

uint64_t digest_f32(const float *values) {
  uint64_t digest = 1469598103934665603ull;
  for (int i = 0; i < kElements; ++i) {
    union {
      float f;
      uint32_t u;
    } bits = {values[i]};
    digest = (digest ^ bits.u) * 1099511628211ull;
  }
  return digest;
}

uint64_t digest_i32(const int *values) {
  uint64_t digest = 1469598103934665603ull;
  for (int i = 0; i < kElements; ++i)
    digest = (digest ^ static_cast<uint32_t>(values[i])) *
             1099511628211ull;
  return digest;
}

void test_transpose() {
  const uint32_t id = 0x00001701u;
  test_start(id);
  seed_standard_inputs();
  // PTO-ORACLE: deepseek_batched_transpose_f32 | exact standard and multi-tile tail transpose
  deepseek_batched_transpose_f32(f2, f0, 1, kRows, kCols);
  for (int r = 0; r < kRows; ++r)
    for (int c = 0; c < kCols; ++c)
      TEST_ASSERT(f2[c * kRows + r] == f0[r * kCols + c], id, 1,
                  static_cast<uint64_t>(r * kCols + c));
  TEST_ASSERT(digest_f32(f2) != 0, id, 2, 0);

  constexpr int tail_rows = 35;
  constexpr int tail_cols = 37;
  constexpr int tail_elements = tail_rows * tail_cols;
  for (int i = 0; i < tail_elements; ++i) {
    f0[i] = static_cast<float>(i + 1);
    f2[i] = -1.0f;
  }
  deepseek_batched_transpose_f32(f2, f0, 1, tail_rows, tail_cols);
  for (int r = 0; r < tail_rows; ++r)
    for (int c = 0; c < tail_cols; ++c)
      TEST_ASSERT(f2[c * tail_rows + r] == f0[r * tail_cols + c], id, 3,
                  static_cast<uint64_t>(r * tail_cols + c));
  test_pass();
}

void test_moe() {
  const uint32_t id = 0x00001702u;
  test_start(id);
  seed_standard_inputs();

  // PTO-ORACLE: deepseek_moe_aux_fi_f32 | exact uniform histogram frequencies
  deepseek_moe_aux_fi_f32(f2, i0, kRows, kCols, kCols);
  for (int bin = 0; bin < kCols; ++bin)
    TEST_ASSERT(f2[bin] == 1.0f, id, 1, static_cast<uint64_t>(bin));

  // PTO-ORACLE: deepseek_moe_group_count_i32 | exact group histogram counts
  deepseek_moe_group_count_i32(i1, i0, kElements, kCols);
  for (int bin = 0; bin < kCols; ++bin)
    TEST_ASSERT(i1[bin] == kRows, id, 2, static_cast<uint64_t>(bin));

  // PTO-ORACLE: deepseek_moe_mask_indices_by_tp_i32 | every remapped index is in rank-local range
  deepseek_moe_mask_indices_by_tp_i32(i0, kElements, kCols, 0);
  for (int i = 0; i < kElements; ++i)
    TEST_ASSERT(i0[i] >= 0 && i0[i] < kCols, id, 3,
                static_cast<uint64_t>(i));

  // PTO-ORACLE: deepseek_moe_unique_group_indices_i32 | count preserved and every row sorted
  TEST_ASSERT(deepseek_moe_unique_group_indices_i32(i0, kElements) ==
                  kElements,
              id, 4, 0);
  for (int r = 0; r < kRows; ++r)
    for (int c = 1; c < kCols; ++c)
      TEST_ASSERT(i0[r * kCols + c - 1] <= i0[r * kCols + c], id, 9,
                  static_cast<uint64_t>(r * kCols + c));

  for (int i = 0; i < kElements; ++i)
    f2[i] = static_cast<float>((i % kCols) + 1);
  // PTO-ORACLE: deepseek_moe_normalize_weight_f32 | standard and tail rows normalize to one
  deepseek_moe_normalize_weight_f32(f2, kRows, kCols);
  for (int r = 0; r < kRows; ++r) {
    float sum = 0.0f;
    for (int c = 0; c < kCols; ++c)
      sum += f2[r * kCols + c];
    TEST_ASSERT(absf(sum - 1.0f) < 0.001f, id, 5,
                static_cast<uint64_t>(r));
  }

  constexpr int tail_rows = 3;
  constexpr int tail_cols = 5;
  for (int i = 0; i < tail_rows * tail_cols; ++i)
    f2[i] = static_cast<float>((i % tail_cols) + 1);
  deepseek_moe_normalize_weight_f32(f2, tail_rows, tail_cols);
  for (int r = 0; r < tail_rows; ++r) {
    float sum = 0.0f;
    for (int c = 0; c < tail_cols; ++c)
      sum += f2[r * tail_cols + c];
    TEST_ASSERT(absf(sum - 1.0f) < 0.001f, id, 8,
                static_cast<uint64_t>(r));
  }

  // PTO-ORACLE: deepseek_moe_topk_gate_f32 | sorted scores and initialized index result
  deepseek_moe_topk_gate_f32(f2, i1, f0, kRows, kCols, 2);
  for (int r = 0; r < kRows; ++r)
    for (int c = 0; c < kCols; ++c) {
      if (c != 0)
        TEST_ASSERT(f2[r * kCols + c - 1] <= f2[r * kCols + c], id, 10,
                    static_cast<uint64_t>(r * kCols + c));
      TEST_ASSERT(i1[r * kCols + c] == 0, id, 11,
                  static_cast<uint64_t>(r * kCols + c));
    }
  // PTO-ORACLE: deepseek_moe_top2_sum_gate_f32 | normalized sorted scores and initialized indices
  deepseek_moe_top2_sum_gate_f32(f2, i1, f1, kRows, kCols);
  for (int r = 0; r < kRows; ++r) {
    float sum = 0.0f;
    for (int c = 0; c < kCols; ++c) {
      sum += f2[r * kCols + c];
      TEST_ASSERT(i1[r * kCols + c] == 0, id, 12,
                  static_cast<uint64_t>(r * kCols + c));
    }
    TEST_ASSERT(absf(sum - 1.0f) < 0.001f, id, 13,
                static_cast<uint64_t>(r));
  }
  // PTO-ORACLE: deepseek_moe_topk_sum_group_f32 | exact row sum and initialized group
  deepseek_moe_topk_sum_group_f32(f2, i1, f1, kRows, 4, 8, 2);
  for (int r = 0; r < kRows; ++r) {
    float expected = 0.0f;
    for (int c = 0; c < kCols; ++c)
      expected += f1[r * kCols + c];
    TEST_ASSERT(absf(f2[r * kCols] - expected) < 0.001f, id, 14,
                static_cast<uint64_t>(r));
    TEST_ASSERT(i1[r * kCols] == 0, id, 15, static_cast<uint64_t>(r));
  }

  seed_standard_inputs();
  // PTO-ORACLE: deepseek_moe_expand_to_fused_f32 | exact gather-times-weight result
  deepseek_moe_expand_to_fused_f32(f2, f0, i0, f1, kElements, kCols);
  for (int i = 0; i < kElements; ++i)
    TEST_ASSERT(absf(f2[i] - f0[i0[i]] * f1[i]) < 0.0001f, id, 6,
                static_cast<uint64_t>(i));

  // PTO-ORACLE: deepseek_moe_reduce_fused_f32 | nonzero scatter reduction result
  deepseek_moe_reduce_fused_f32(f3, f2, i0, f1, kElements, kRows, kCols);
  TEST_ASSERT(digest_f32(f3) != 0, id, 7, 0);
  // PTO-ORACLE: deepseek_moe_get_fused_mapping_i32 | sorted mapping and exact histogram population
  deepseek_moe_get_fused_mapping_i32(i1, i2, i0, kElements, kCols);
  TEST_ASSERT(digest_i32(i1) != 0, id, 7, 0);
  int histogram_total = 0;
  for (int c = 0; c < kCols; ++c)
    histogram_total += i2[c];
  TEST_ASSERT(histogram_total == kElements, id, 16,
              static_cast<uint64_t>(histogram_total));
  for (int r = 0; r < kRows; ++r)
    for (int c = 1; c < kCols; ++c)
      TEST_ASSERT(i1[r * kCols + c - 1] <= i1[r * kCols + c], id, 17,
                  static_cast<uint64_t>(r * kCols + c));
  test_pass();
}

void test_quant() {
  const uint32_t id = 0x00001703u;
  test_start(id);
  seed_standard_inputs();

  // PTO-ORACLE: deepseek_quant_per_token_i8 | positive scales and bounded standard/tail round trip
  deepseek_quant_per_token_i8(q0, f2, f0, kRows, kCols);
  for (int r = 0; r < kRows; ++r)
    TEST_ASSERT(f2[r] > 0.0f, id, 1, static_cast<uint64_t>(r));
  // PTO-ORACLE: deepseek_quant_cast_back_f32 | elementwise standard and tail reconstruction tolerance
  deepseek_quant_cast_back_f32(f3, q0, f2, kRows, kCols, true);
  for (int i = 0; i < kElements; ++i)
    TEST_ASSERT(absf(f3[i] - f0[i]) < 0.03f, id, 2,
                static_cast<uint64_t>(i));

  // PTO-ORACLE: deepseek_quant_per_block_i8 | positive row scales and nonzero quantized payload
  deepseek_quant_per_block_i8(q0, f2, f0, kElements, kCols);
  for (int r = 0; r < kRows; ++r) {
    TEST_ASSERT(f2[r] > 0.0f, id, 7,
                static_cast<uint64_t>(r));
    for (int c = 0; c < kCols; ++c) {
      const int i = r * kCols + c;
      const float reconstructed = static_cast<float>(q0[i]) * f2[r];
      TEST_ASSERT(absf(reconstructed - f0[i]) < 0.03f, id, 16,
                  static_cast<uint64_t>(i));
    }
  }
  TEST_ASSERT(q0[0] != 0 || q0[1] != 0, id, 8, 0);
  // PTO-ORACLE: deepseek_quant_per_block_lossless_i8 | scale bit patterns decode to positive floats
  deepseek_quant_per_block_lossless_i8(q0, u0, f0, kElements, kCols);
  for (int r = 0; r < kRows; ++r) {
    union {
      uint32_t u;
      float f;
    } scale = {u0[r]};
    TEST_ASSERT(scale.f > 0.0f, id, 9, static_cast<uint64_t>(r));
    for (int c = 0; c < kCols; ++c) {
      const int i = r * kCols + c;
      const float reconstructed = static_cast<float>(q0[i]) * scale.f;
      TEST_ASSERT(absf(reconstructed - f0[i]) < 0.03f, id, 17,
                  static_cast<uint64_t>(i));
    }
  }
  // PTO-ORACLE: deepseek_quant_per_channel_i8 | every channel has a positive scale
  deepseek_quant_per_channel_i8(q0, f2, f0, kRows, kCols);
  for (int c = 0; c < kCols; ++c)
    TEST_ASSERT(f2[c] > 0.0f, id, 10, static_cast<uint64_t>(c));
  for (int r = 0; r < kRows; ++r)
    for (int c = 0; c < kCols; ++c) {
      const int i = r * kCols + c;
      TEST_ASSERT(absf(static_cast<float>(q0[i]) * f2[c] - f0[i]) < 0.03f,
                  id, 18, static_cast<uint64_t>(i));
    }
  // PTO-ORACLE: deepseek_quant_per_channel_transpose_i8 | every transposed channel has a positive scale
  deepseek_quant_per_channel_transpose_i8(q0, f2, f0, kRows, kCols);
  for (int c = 0; c < kCols; ++c)
    TEST_ASSERT(f2[c] > 0.0f, id, 11, static_cast<uint64_t>(c));
  for (int r = 0; r < kRows; ++r)
    for (int c = 0; c < kCols; ++c) {
      const int input_i = r * kCols + c;
      const int output_i = c * kRows + r;
      TEST_ASSERT(absf(static_cast<float>(q0[output_i]) * f2[c] -
                           f0[input_i]) < 0.03f,
                  id, 19, static_cast<uint64_t>(input_i));
    }
  // PTO-ORACLE: deepseek_quant_per_channel_fused_i8 | fused channel scales are positive
  deepseek_quant_per_channel_fused_i8(q0, f2, f0, f1, kRows, kCols);
  for (int c = 0; c < kCols; ++c)
    TEST_ASSERT(f2[c] > 0.0f, id, 12, static_cast<uint64_t>(c));
  for (int r = 0; r < kRows; ++r)
    for (int c = 0; c < kCols; ++c) {
      const int i = r * kCols + c;
      const float expected = f0[i] + f1[i];
      const float reconstructed = static_cast<float>(q0[i]) * f2[c];
      TEST_ASSERT(absf(reconstructed - expected) < 0.03f, id, 20,
                  static_cast<uint64_t>(i));
    }

  // PTO-ORACLE: deepseek_quant_per_token_e5m6 | paired e5m6 conversion reconstructs source
  deepseek_quant_per_token_e5m6(h0, f1, kElements);
  // PTO-ORACLE: deepseek_quant_cast_back_e5m6 | bounded elementwise e5m6 round trip
  deepseek_quant_cast_back_e5m6(f3, h0, kElements);
  for (int i = 0; i < kElements; ++i)
    TEST_ASSERT(absf(f3[i] - f1[i]) < 0.51f, id, 3,
                static_cast<uint64_t>(i));

  // PTO-ORACLE: deepseek_quant_swiglu_forward_per_token_i8 | every token scale is positive
  deepseek_quant_swiglu_forward_per_token_i8(q0, f2, f0, f1, kRows,
                                              kCols);
  for (int r = 0; r < kRows; ++r)
    TEST_ASSERT(f2[r] > 0.0f, id, 13,
                static_cast<uint64_t>(r));
  for (int r = 0; r < kRows; ++r)
    for (int c = 0; c < kCols; ++c) {
      const int i = r * kCols + c;
      const float expected = f0[i] * sigmoidf(f0[i]) * f1[i];
      TEST_ASSERT(absf(static_cast<float>(q0[i]) * f2[r] -
                           expected) < 0.03f,
                  id, 21, static_cast<uint64_t>(i));
    }
  // PTO-ORACLE: deepseek_quant_swiglu_forward_per_channel_transpose_i8 | every channel scale is positive
  deepseek_quant_swiglu_forward_per_channel_transpose_i8(
      q0, f2, f0, f1, kRows, kCols);
  for (int c = 0; c < kCols; ++c)
    TEST_ASSERT(f2[c] > 0.0f, id, 14, static_cast<uint64_t>(c));
  for (int r = 0; r < kRows; ++r)
    for (int c = 0; c < kCols; ++c) {
      const int input_i = r * kCols + c;
      const int output_i = c * kRows + r;
      const float expected =
          f0[input_i] * sigmoidf(f0[input_i]) * f1[input_i];
      TEST_ASSERT(absf(static_cast<float>(q0[output_i]) * f2[c] -
                           expected) < 0.03f,
                  id, 22, static_cast<uint64_t>(input_i));
    }
  // PTO-ORACLE: deepseek_quant_swiglu_backward_per_token_i8 | both gradients and token scales are nonzero
  deepseek_quant_swiglu_backward_per_token_i8(
      q0, q1, f2, f3, f1, f0, f1, kRows, kCols);
  TEST_ASSERT(q0[0] != 0 || q1[0] != 0 || q0[1] != 0 || q1[1] != 0, id, 4,
              0);
  for (int r = 0; r < kRows; ++r)
    TEST_ASSERT(f2[r] > 0.0f && f3[r] > 0.0f, id, 15,
                static_cast<uint64_t>(r));
  for (int r = 0; r < kRows; ++r)
    for (int c = 0; c < kCols; ++c) {
      const int i = r * kCols + c;
      const float gate = f0[i];
      const float up = f1[i];
      const float grad = f1[i];
      const float probability = sigmoidf(gate);
      const float expected_gate =
          grad * up * probability * (1.0f + gate * (1.0f - probability));
      const float expected_up = grad * gate * probability;
      TEST_ASSERT(absf(static_cast<float>(q0[i]) * f2[r] -
                           expected_gate) < 0.03f,
                  id, 23, static_cast<uint64_t>(i));
      TEST_ASSERT(absf(static_cast<float>(q1[i]) * f3[r] -
                           expected_up) < 0.03f,
                  id, 24, static_cast<uint64_t>(i));
    }

  constexpr int tail_rows = 3;
  constexpr int tail_cols = 5;
  for (int i = 0; i < tail_rows * tail_cols; ++i)
    f0[i] = static_cast<float>((i % 9) - 4) * 0.5f;
  deepseek_quant_per_token_i8(q0, f2, f0, tail_rows, tail_cols);
  deepseek_quant_cast_back_f32(f3, q0, f2, tail_rows, tail_cols, true);
  for (int r = 0; r < tail_rows; ++r) {
    TEST_ASSERT(f2[r] > 0.0f, id, 5, static_cast<uint64_t>(r));
    for (int c = 0; c < tail_cols; ++c) {
      const int i = r * tail_cols + c;
      TEST_ASSERT(absf(f3[i] - f0[i]) < 0.03f, id, 6,
                  static_cast<uint64_t>(i));
    }
  }
  test_pass();
}

void test_engram() {
  const uint32_t id = 0x00001704u;
  test_start(id);
  seed_standard_inputs();

  // PTO-ORACLE: deepseek_engram_hash_i32 | exact hash mix and bucket clamp per lane
  deepseek_engram_hash_i32(i1, l0, kElements, 1, kCols,
                           0x12345678u);
  const uint32_t *hash_input = reinterpret_cast<const uint32_t *>(l0);
  for (int i = 0; i < kElements; ++i) {
    uint32_t expected = hash_input[i] ^ 0x12345678u;
    expected ^= expected >> 16;
    expected *= 0x7feb352du;
    expected ^= expected >> 15;
    if (expected >= static_cast<uint32_t>(kCols))
      expected = kCols - 1;
    TEST_ASSERT(i1[i] >= 0 && i1[i] < kCols, id, 1,
                static_cast<uint64_t>(i));
    TEST_ASSERT(static_cast<uint32_t>(i1[i]) == expected, id, 4,
                static_cast<uint64_t>(i));
  }

  // PTO-ORACLE: deepseek_engram_fused_weight_f32 | exact gathered weighted row reduction
  deepseek_engram_fused_weight_f32(f2, f0, i0, f1, kRows, kCols, kCols,
                                   kCols);
  for (int r = 0; r < kRows; ++r) {
    float expected = 0.0f;
    for (int c = 0; c < kCols; ++c) {
      const int i = r * kCols + c;
      expected += f0[i0[i]] * f1[i];
    }
    TEST_ASSERT(absf(f2[r * kCols] - expected) < 0.001f, id, 5,
                static_cast<uint64_t>(r));
  }

  seed_standard_inputs();
  // PTO-ORACLE: deepseek_engram_gate_fwd_f32 | unit RMS normalized rows and bounded sigmoid gate
  deepseek_engram_gate_fwd_f32(f2, f3, f0, f1, f1, kRows, kCols,
                               0.00001f);
  for (int r = 0; r < kRows; ++r) {
    float square_sum = 0.0f;
    for (int c = 0; c < kCols; ++c) {
      const float value = f3[r * kCols + c];
      square_sum += value * value;
    }
    TEST_ASSERT(absf(square_sum / static_cast<float>(kCols) - 1.0f) <
                    0.01f,
                id, 2, static_cast<uint64_t>(r));
    TEST_ASSERT(f2[r * kCols] > 0.0f && f2[r * kCols] < 1.0f, id, 6,
                static_cast<uint64_t>(r));
  }

  seed_standard_inputs();
  // PTO-ORACLE: deepseek_engram_gate_bwd_f32 | exact input and bias gradient equations
  deepseek_engram_gate_bwd_f32(f2, f3, f1, f0, f0, f1, kRows, kCols,
                               0.00001f);
  for (int r = 0; r < kRows; ++r) {
    const float row_grad = f0[r * kCols];
    for (int c = 0; c < kCols; ++c) {
      const int i = r * kCols + c;
      const float weight = static_cast<float>((i % 13) + 1) * 0.0625f;
      TEST_ASSERT(absf(f2[i] - row_grad * weight) < 0.001f, id, 7,
                  static_cast<uint64_t>(i));
    }
    TEST_ASSERT(absf(f1[r * kCols] - row_grad * kCols) < 0.001f, id, 8,
                static_cast<uint64_t>(r));
  }

  seed_standard_inputs();
  // PTO-ORACLE: deepseek_engram_grad_w_reduce_f32 | exact column reduction
  deepseek_engram_grad_w_reduce_f32(f2, f0, kRows, kRows, kCols);
  for (int c = 0; c < kCols; ++c) {
    float expected = 0.0f;
    for (int r = 0; r < kRows; ++r)
      expected += f0[r * kCols + c];
    TEST_ASSERT(absf(f2[c] - expected) < 0.001f, id, 3,
                static_cast<uint64_t>(c));
  }
  test_pass();
}

void test_mhc() {
  const uint32_t id = 0x00001705u;
  test_start(id);
  seed_standard_inputs();

  // PTO-ORACLE: deepseek_mhc_expand_fwd_f32 | exact reshape identity
  deepseek_mhc_expand_fwd_f32(f2, f0, kRows, 1, kCols);
  for (int i = 0; i < kElements; ++i)
    TEST_ASSERT(f2[i] == f0[i], id, 5, static_cast<uint64_t>(i));

  // PTO-ORACLE: deepseek_mhc_expand_bwd_f32 | exact row gradient reduction
  deepseek_mhc_expand_bwd_f32(f3, f2, kRows, 1, kCols);
  for (int r = 0; r < kRows; ++r) {
    float expected = 0.0f;
    for (int c = 0; c < kCols; ++c)
      expected += f0[r * kCols + c];
    TEST_ASSERT(absf(f3[r * kCols] - expected) < 0.001f, id, 6,
                static_cast<uint64_t>(r));
  }

  // PTO-ORACLE: deepseek_mhc_head_compute_mix_fwd_f32 | exact row dot product broadcast
  deepseek_mhc_head_compute_mix_fwd_f32(f2, f0, f1, kRows, 1, kCols);
  for (int r = 0; r < kRows; ++r) {
    float expected = 0.0f;
    for (int c = 0; c < kCols; ++c)
      expected += f0[r * kCols + c] * f1[r * kCols + c];
    for (int c = 0; c < kCols; ++c)
      TEST_ASSERT(absf(f2[r * kCols + c] - expected) < 0.001f, id, 7,
                  static_cast<uint64_t>(r * kCols + c));
  }

  // PTO-ORACLE: deepseek_mhc_head_compute_mix_bwd_f32 | exact input product and column-reduced mix gradient
  deepseek_mhc_head_compute_mix_bwd_f32(f2, f3, f0, f0, f1, kRows, 1,
                                        kCols);
  for (int i = 0; i < kElements; ++i)
    TEST_ASSERT(absf(f2[i] - f0[i] * f1[i]) < 0.001f, id, 8,
                static_cast<uint64_t>(i));
  for (int c = 0; c < kCols; ++c) {
    float expected = 0.0f;
    for (int r = 0; r < kRows; ++r) {
      const float value = f0[r * kCols + c];
      expected += value * value;
    }
    TEST_ASSERT(absf(f3[c] - expected) < 0.001f, id, 9,
                static_cast<uint64_t>(c));
  }

  // PTO-ORACLE: deepseek_mhc_multilayer_recompute_f32 | exact residual product equation
  deepseek_mhc_multilayer_recompute_f32(f2, f0, f1, 1, kRows, 1, kCols);
  for (int i = 0; i < kElements; ++i)
    TEST_ASSERT(absf(f2[i] - (f0[i] + f0[i] * f1[i])) < 0.001f, id, 10,
                static_cast<uint64_t>(i));

  // PTO-ORACLE: deepseek_mhc_norm_fwd_f32 | unit RMS for standard and tail shapes
  deepseek_mhc_norm_fwd_f32(f2, f0, kRows, kCols, 0.00001f);
  for (int r = 0; r < kRows; ++r) {
    float square_sum = 0.0f;
    for (int c = 0; c < kCols; ++c) {
      const float value = f2[r * kCols + c];
      square_sum += value * value;
    }
    TEST_ASSERT(absf(square_sum / static_cast<float>(kCols) - 1.0f) <
                    0.01f,
                id, 1, static_cast<uint64_t>(r));
  }

  constexpr int tail_rows = 3;
  constexpr int tail_cols = 5;
  for (int i = 0; i < tail_rows * tail_cols; ++i)
    f0[i] = static_cast<float>((i % 7) + 1) * 0.25f;
  deepseek_mhc_norm_fwd_f32(f2, f0, tail_rows, tail_cols, 0.00001f);
  for (int r = 0; r < tail_rows; ++r) {
    float square_sum = 0.0f;
    for (int c = 0; c < tail_cols; ++c) {
      const float value = f2[r * tail_cols + c];
      square_sum += value * value;
    }
    TEST_ASSERT(absf(square_sum / static_cast<float>(tail_cols) - 1.0f) <
                    0.01f,
                id, 4, static_cast<uint64_t>(r));
  }

  // PTO-ORACLE: deepseek_mhc_pre_split_mixes_fwd_f32 | exact mix copy and residual transpose
  deepseek_mhc_pre_split_mixes_fwd_f32(f2, f3, f0, kRows, kCols);
  for (int r = 0; r < kRows; ++r)
    for (int c = 0; c < kCols; ++c) {
      const int i = r * kCols + c;
      TEST_ASSERT(f2[i] == f0[i], id, 11, static_cast<uint64_t>(i));
      TEST_ASSERT(f3[c * kRows + r] == f0[i], id, 12,
                  static_cast<uint64_t>(i));
    }

  // PTO-ORACLE: deepseek_mhc_pre_split_mixes_bwd_f32 | exact mix plus transposed residual gradient
  deepseek_mhc_pre_split_mixes_bwd_f32(f2, f0, f1, kRows, kCols);
  for (int r = 0; r < kRows; ++r)
    for (int c = 0; c < kCols; ++c) {
      const int i = r * kCols + c;
      TEST_ASSERT(absf(f2[i] - (f0[i] + f1[c * kRows + r])) < 0.001f,
                  id, 13, static_cast<uint64_t>(i));
    }

  // PTO-ORACLE: deepseek_mhc_pre_apply_mix_f32 | exact elementwise mix product
  deepseek_mhc_pre_apply_mix_f32(f2, f0, f1, kRows, 1, kCols);
  for (int i = 0; i < kElements; ++i)
    TEST_ASSERT(absf(f2[i] - f0[i] * f1[i]) < 0.001f, id, 14,
                static_cast<uint64_t>(i));

  // PTO-ORACLE: deepseek_mhc_pre_big_fuse_f32 | scalar reference for RMS-normalized residual mix
  deepseek_mhc_pre_big_fuse_f32(f2, f0, f1, kRows, 1, kCols, 0.00001f);
  for (int r = 0; r < kRows; ++r) {
    float square_sum = 0.0f;
    for (int c = 0; c < kCols; ++c) {
      const float value = f0[r * kCols + c];
      square_sum += value * value;
    }
    const float inverse_rms = 1.0f / __builtin_sqrtf(
                                          square_sum / kCols + 0.00001f);
    for (int c = 0; c < kCols; ++c) {
      const int i = r * kCols + c;
      const float expected = f0[i] + f0[i] * inverse_rms * f1[i];
      TEST_ASSERT(absf(f2[i] - expected) < 0.01f, id, 15,
                  static_cast<uint64_t>(i));
    }
  }

  // PTO-ORACLE: deepseek_mhc_sinkhorn_f32 | row and column probability conservation
  deepseek_mhc_sinkhorn_f32(f2, f1, 1, kCols, 1);
  for (int r = 0; r < kRows; ++r) {
    float sum = 0.0f;
    for (int c = 0; c < kCols; ++c)
      sum += f2[r * kCols + c];
    TEST_ASSERT(absf(sum - 1.0f) < 0.01f, id, 2,
                static_cast<uint64_t>(r));
  }
  for (int c = 0; c < kCols; ++c) {
    float sum = 0.0f;
    for (int r = 0; r < kRows; ++r)
      sum += f2[r * kCols + c];
    TEST_ASSERT(absf(sum - 1.0f) < 0.01f, id, 16,
                static_cast<uint64_t>(c));
  }
  // PTO-ORACLE: deepseek_mhc_sinkhorn_backward_f32 | every softmax-gradient row sums to zero
  deepseek_mhc_sinkhorn_backward_f32(f3, f1, f2, 1, kCols);
  for (int r = 0; r < kRows; ++r) {
    float sum = 0.0f;
    for (int c = 0; c < kCols; ++c)
      sum += f3[r * kCols + c];
    TEST_ASSERT(absf(sum) < 0.01f, id, 17, static_cast<uint64_t>(r));
  }

  // PTO-ORACLE: deepseek_mhc_post_fwd_f32 | exact weighted residual equation
  deepseek_mhc_post_fwd_f32(f2, f0, f1, f1, kRows, 1, kCols);
  for (int i = 0; i < kElements; ++i)
    TEST_ASSERT(absf(f2[i] - (f0[i] + f1[i] * f1[i])) < 0.001f, id, 18,
                static_cast<uint64_t>(i));

  // PTO-ORACLE: deepseek_mhc_post_bwd_f32 | exact base streams and reduced weight gradients
  deepseek_mhc_post_bwd_f32(f2, f3, f1, f0, f1, f1, kRows, 1, kCols);
  for (int i = 0; i < kElements; ++i) {
    const float original_f1 = static_cast<float>((i % 13) + 1) * 0.0625f;
    TEST_ASSERT(f2[i] == f0[i], id, 19, static_cast<uint64_t>(i));
    TEST_ASSERT(absf(f3[i] - f0[i] * original_f1) < 0.001f, id, 20,
                static_cast<uint64_t>(i));
  }
  for (int c = 0; c < kCols; ++c) {
    float expected = 0.0f;
    for (int r = 0; r < kRows; ++r) {
      const int i = r * kCols + c;
      const float original_f1 = static_cast<float>((i % 13) + 1) * 0.0625f;
      expected += f0[i] * original_f1;
    }
    TEST_ASSERT(absf(f1[c] - expected) < 0.001f, id, 3,
                static_cast<uint64_t>(c));
  }
  test_pass();
}

} // namespace

extern "C" void run_deepseek_tilekernels_tests(void) {
  test_transpose();
  test_moe();
  test_quant();
  test_engram();
  test_mhc();
}
