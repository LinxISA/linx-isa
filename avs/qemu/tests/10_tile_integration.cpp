// Cross-family PTO kernel digest tests. These intentionally exercise complete
// kernels and therefore do not belong to one ISA family test file.

#include "10_tile_test_common.hpp"

#include <common/runtime/kernel_api.hpp>

using namespace linx::test::tile;

#ifndef PTO_QEMU_SMOKE
#define PTO_QEMU_SMOKE 0
#endif

extern "C" void run_tile_integration_tests(void)
{
    constexpr unsigned kMatElems = PTO_QEMU_SMOKE ? 16u * 16u : 256u * 256u;
    constexpr unsigned kVecElems = PTO_QEMU_SMOKE ? 32u * 32u : 1024u * 1024u;
    constexpr unsigned kFlashI32Q = PTO_QEMU_SMOKE ? 16u * 4u : 256u * 4u;
    constexpr unsigned kFlashI32K = PTO_QEMU_SMOKE ? 4u * 16u : 4u * 256u;
    constexpr unsigned kFlashI32V = PTO_QEMU_SMOKE ? 16u * 16u : 256u * 16u;
    constexpr unsigned kFlashI32O = PTO_QEMU_SMOKE ? 16u * 16u : 256u * 16u;
    constexpr unsigned kFlashMaskQ = PTO_QEMU_SMOKE ? 18u * 16u : 130u * 16u;
    constexpr unsigned kFlashMaskK = PTO_QEMU_SMOKE ? 16u * 18u : 16u * 130u;
    constexpr unsigned kFlashMaskV = PTO_QEMU_SMOKE ? 18u * 16u : 130u * 16u;
    constexpr unsigned kFlashMaskO = PTO_QEMU_SMOKE ? 18u * 16u : 130u * 16u;

#if PTO_QEMU_SMOKE
    constexpr uint64_t kDigestTloadStore = UINT64_C(0xA1248F48FF3C7199);
    constexpr uint64_t kDigestMamulb = UINT64_C(0x5400A6A0D6991D4D);
    constexpr uint64_t kDigestTmatmulAcc = UINT64_C(0x2A37199ED1CBD94D);
    constexpr uint64_t kDigestGemm = UINT64_C(0x5400A6A0D6991D4D);
    constexpr uint64_t kDigestFlash = UINT64_C(0x754D619AB6075DA1);
    constexpr uint64_t kDigestFlashMasked = UINT64_C(0xE56690EBAB5372C9);
#else
    constexpr uint64_t kDigestTloadStore = UINT64_C(0xABFA311400C734C3);
    constexpr uint64_t kDigestMamulb = UINT64_C(0xACA73824B88635A3);
    constexpr uint64_t kDigestTmatmulAcc = UINT64_C(0xBA7AB93F72C13823);
    constexpr uint64_t kDigestGemm = UINT64_C(0xACA73824B88635A3);
    constexpr uint64_t kDigestFlash = UINT64_C(0x88745CBAC7A57629);
    constexpr uint64_t kDigestFlashMasked = UINT64_C(0x29C9E1D314B63C33);
#endif

    alignas(64) static int32_t mat_a[kMatElems];
    alignas(64) static int32_t mat_b[kMatElems];
    alignas(64) static int32_t mat_c[kMatElems];
    alignas(64) static int32_t vec_src[kVecElems];
    alignas(64) static int32_t vec_dst[kVecElems];
    alignas(64) static int32_t flash_q[kFlashI32Q];
    alignas(64) static int32_t flash_k[kFlashI32K];
    alignas(64) static int32_t flash_v[kFlashI32V];
    alignas(64) static int32_t flash_o[kFlashI32O];
    alignas(64) static float flash_m_q[kFlashMaskQ];
    alignas(64) static float flash_m_k[kFlashMaskK];
    alignas(64) static float flash_m_v[kFlashMaskV];
    alignas(64) static float flash_m_o[kFlashMaskO];

    seed_i32(mat_a, kMatElems, 0x1001u);
    seed_i32(mat_b, kMatElems, 0x1002u);
    zero(mat_c, kMatElems);
    seed_i32(vec_src, kVecElems, 0x1003u);
    zero(vec_dst, kVecElems);
    seed_i32(flash_q, kFlashI32Q, 0x3001u);
    seed_i32(flash_k, kFlashI32K, 0x3002u);
    seed_i32(flash_v, kFlashI32V, 0x3003u);
    zero(flash_o, kFlashI32O);
    seed_f32(flash_m_q, kFlashMaskQ, 0x5001u);
    seed_f32(flash_m_k, kFlashMaskK, 0x5002u);
    seed_f32(flash_m_v, kFlashMaskV, 0x5003u);
    zero(flash_m_o, kFlashMaskO);

    test_start(0x000A0006);
    uart_puts("PTO kernel tload_store digest ... ");
    pto::kernels::pto_tload_store(vec_dst, vec_src, nullptr);
    TEST_EQ64(fnv1a_bytes(vec_dst, sizeof(vec_dst)), kDigestTloadStore,
              0x000A6001u);
    test_pass();

    test_start(0x000A0007);
    uart_puts("PTO kernel mamulb digest ... ");
    zero(mat_c, kMatElems);
    pto::kernels::pto_mamulb(mat_c, mat_a, mat_b, nullptr);
    TEST_EQ64(fnv1a_bytes(mat_c, sizeof(mat_c)), kDigestMamulb,
              0x000A7001u);
    test_pass();

    test_start(0x000A0008);
    uart_puts("PTO kernel tmatmul_acc digest ... ");
    zero(mat_c, kMatElems);
    pto::kernels::pto_tmatmul_acc(mat_c, mat_a, mat_b, nullptr);
    TEST_EQ64(fnv1a_bytes(mat_c, sizeof(mat_c)), kDigestTmatmulAcc,
              0x000A8001u);
    test_pass();

    test_start(0x000A0009);
    uart_puts("PTO kernel gemm digest ... ");
    zero(mat_c, kMatElems);
    pto::kernels::pto_gemm(mat_c, mat_a, mat_b, nullptr);
    TEST_EQ64(fnv1a_bytes(mat_c, sizeof(mat_c)), kDigestGemm, 0x000A9001u);
    test_pass();

    test_start(0x000A000A);
    uart_puts("PTO kernel flash_attention digest ... ");
    zero(flash_o, kFlashI32O);
    pto::kernels::pto_flash_attention(flash_o, flash_q, flash_k, flash_v,
                                      nullptr);
    TEST_EQ64(fnv1a_bytes(flash_o, sizeof(flash_o)), kDigestFlash,
              0x000AA001u);
    test_pass();

    test_start(0x000A0012);
    uart_puts("PTO kernel flash_attention_masked digest ... ");
    zero(flash_m_o, kFlashMaskO);
    pto::kernels::pto_flash_attention_masked(
        flash_m_o, flash_m_q, flash_m_k, flash_m_v, nullptr);
    TEST_EQ64(fnv1a_bytes(flash_m_o, sizeof(flash_m_o)), kDigestFlashMasked,
              0x000A1201u);
    test_pass();
}
