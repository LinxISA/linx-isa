#include "linx_test.h"

#include <common/deepseek_tilekernels.hpp>

namespace {

constexpr int kRows = 32;
constexpr int kCols = 32;
constexpr int kElements = kRows * kCols;

alignas(64) float f0[kElements];
alignas(64) float f1[kElements];
alignas(64) float f2[kElements];
alignas(64) float f3[kElements];
alignas(64) int i0[kElements];
alignas(64) int i1[kElements];
alignas(64) int i2[kElements];
alignas(64) int8_t q0[4096];
alignas(64) int8_t q1[4096];
alignas(64) uint16_t h0[2048];
alignas(64) uint16_t h1[2048];
alignas(64) uint32_t u0[kElements];
alignas(64) int64_t l0[kElements];

float absf(float value) { return value < 0.0f ? -value : value; }

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
  deepseek_batched_transpose_f32(f2, f0, 1, kRows, kCols);
  for (int r = 0; r < kRows; ++r)
    for (int c = 0; c < kCols; ++c)
      TEST_ASSERT(f2[c * kRows + r] == f0[r * kCols + c], id, 1,
                  static_cast<uint64_t>(r * kCols + c));
  TEST_ASSERT(digest_f32(f2) != 0, id, 2, 0);
  test_pass();
}

void test_moe() {
  const uint32_t id = 0x00001702u;
  test_start(id);
  seed_standard_inputs();

  deepseek_moe_aux_fi_f32(f2, i0, kRows, kCols, kCols);
  for (int bin = 0; bin < kCols; ++bin)
    TEST_ASSERT(f2[bin] == 1.0f, id, 1, static_cast<uint64_t>(bin));

  deepseek_moe_group_count_i32(i1, i0, kElements, kCols);
  for (int bin = 0; bin < kCols; ++bin)
    TEST_ASSERT(i1[bin] == kRows, id, 2, static_cast<uint64_t>(bin));

  deepseek_moe_mask_indices_by_tp_i32(i0, kElements, kCols, 0);
  for (int i = 0; i < kElements; ++i)
    TEST_ASSERT(i0[i] >= 0 && i0[i] < kCols, id, 3,
                static_cast<uint64_t>(i));

  TEST_ASSERT(deepseek_moe_unique_group_indices_i32(i0, kElements) ==
                  kElements,
              id, 4, 0);

  for (int i = 0; i < kElements; ++i)
    f2[i] = static_cast<float>((i % kCols) + 1);
  deepseek_moe_normalize_weight_f32(f2, kRows, kCols);
  for (int r = 0; r < kRows; ++r) {
    float sum = 0.0f;
    for (int c = 0; c < kCols; ++c)
      sum += f2[r * kCols + c];
    TEST_ASSERT(absf(sum - 1.0f) < 0.001f, id, 5,
                static_cast<uint64_t>(r));
  }

  deepseek_moe_topk_gate_f32(f2, i1, f0, kRows, kCols, 2);
  deepseek_moe_top2_sum_gate_f32(f2, i1, f1, kRows, kCols);
  deepseek_moe_topk_sum_group_f32(f2, i1, f1, kRows, 4, 8, 2);

  seed_standard_inputs();
  deepseek_moe_expand_to_fused_f32(f2, f0, i0, f1, kElements, kCols);
  for (int i = 0; i < kElements; ++i)
    TEST_ASSERT(absf(f2[i] - f0[i0[i]] * f1[i]) < 0.0001f, id, 6,
                static_cast<uint64_t>(i));

  deepseek_moe_reduce_fused_f32(f3, f2, i0, f1, kElements, kRows, kCols);
  deepseek_moe_get_fused_mapping_i32(i1, i2, i0, kElements, kCols);
  TEST_ASSERT(digest_f32(f3) != 0 && digest_i32(i1) != 0, id, 7, 0);
  test_pass();
}

void test_quant() {
  const uint32_t id = 0x00001703u;
  test_start(id);
  seed_standard_inputs();

  deepseek_quant_per_token_i8(q0, f2, f0, kRows, kCols);
  for (int r = 0; r < kRows; ++r)
    TEST_ASSERT(f2[r * kCols] > 0.0f, id, 1,
                static_cast<uint64_t>(r));
  deepseek_quant_cast_back_f32(f3, q0, f2, kRows, kCols, true);
  for (int i = 0; i < kElements; ++i)
    TEST_ASSERT(absf(f3[i] - f0[i]) < 0.03f, id, 2,
                static_cast<uint64_t>(i));

  deepseek_quant_per_block_i8(q0, f2, f0, kElements, kCols);
  deepseek_quant_per_block_lossless_i8(q0, u0, f0, kElements, kCols);
  deepseek_quant_per_channel_i8(q0, f2, f0, kRows, kCols);
  deepseek_quant_per_channel_transpose_i8(q0, f2, f0, kRows, kCols);
  deepseek_quant_per_channel_fused_i8(q0, f2, f0, f1, kRows, kCols);

  deepseek_quant_per_token_e5m6(h0, f1, kElements);
  deepseek_quant_cast_back_e5m6(f3, h0, kElements);
  for (int i = 0; i < kElements; ++i)
    TEST_ASSERT(absf(f3[i] - f1[i]) < 0.51f, id, 3,
                static_cast<uint64_t>(i));

  deepseek_quant_swiglu_forward_per_token_i8(q0, f2, f0, f1, kRows,
                                              kCols);
  deepseek_quant_swiglu_forward_per_channel_transpose_i8(
      q0, f2, f0, f1, kRows, kCols);
  deepseek_quant_swiglu_backward_per_token_i8(
      q0, q1, f2, f3, f1, f0, f1, kRows, kCols);
  TEST_ASSERT(q0[0] != 0 || q1[0] != 0 || q0[1] != 0 || q1[1] != 0, id, 4,
              0);
  test_pass();
}

void test_engram() {
  const uint32_t id = 0x00001704u;
  test_start(id);
  seed_standard_inputs();

  deepseek_engram_hash_i32(i1, l0, kElements, 1, kCols,
                           0x12345678u);
  for (int i = 0; i < kElements; ++i)
    TEST_ASSERT(i1[i] >= 0 && i1[i] < kCols, id, 1,
                static_cast<uint64_t>(i));

  deepseek_engram_fused_weight_f32(f2, f0, i0, f1, kRows, kCols, kCols,
                                   kCols);
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
  }

  deepseek_engram_gate_bwd_f32(f2, f3, f1, f0, f0, f1, kRows, kCols,
                               0.00001f);
  deepseek_engram_grad_w_reduce_f32(f2, f0, kRows, kRows, kCols);
  TEST_ASSERT(digest_f32(f2) != 0, id, 3, 0);
  test_pass();
}

void test_mhc() {
  const uint32_t id = 0x00001705u;
  test_start(id);
  seed_standard_inputs();

  deepseek_mhc_expand_fwd_f32(f2, f0, kRows, 1, kCols);
  deepseek_mhc_expand_bwd_f32(f3, f2, kRows, 1, kCols);
  deepseek_mhc_head_compute_mix_fwd_f32(f2, f0, f1, kRows, 1, kCols);
  deepseek_mhc_head_compute_mix_bwd_f32(f2, f3, f0, f0, f1, kRows, 1,
                                        kCols);
  deepseek_mhc_multilayer_recompute_f32(f2, f0, f1, 1, kRows, 1, kCols);

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

  deepseek_mhc_pre_split_mixes_fwd_f32(f2, f3, f0, kRows, kCols);
  deepseek_mhc_pre_split_mixes_bwd_f32(f2, f0, f1, kRows, kCols);
  deepseek_mhc_pre_apply_mix_f32(f2, f0, f1, kRows, 1, kCols);
  deepseek_mhc_pre_big_fuse_f32(f2, f0, f1, kRows, 1, kCols, 0.00001f);

  deepseek_mhc_sinkhorn_f32(f2, f1, 1, kCols, 1);
  for (int r = 0; r < kRows; ++r) {
    float sum = 0.0f;
    for (int c = 0; c < kCols; ++c)
      sum += f2[r * kCols + c];
    TEST_ASSERT(absf(sum - 1.0f) < 0.01f, id, 2,
                static_cast<uint64_t>(r));
  }
  deepseek_mhc_sinkhorn_backward_f32(f3, f1, f2, 1, kCols);

  deepseek_mhc_post_fwd_f32(f2, f0, f1, f1, kRows, 1, kCols);
  deepseek_mhc_post_bwd_f32(f2, f3, f1, f0, f1, f1, kRows, 1, kCols);
  TEST_ASSERT(digest_f32(f2) != 0 && digest_f32(f3) != 0, id, 3, 0);
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
