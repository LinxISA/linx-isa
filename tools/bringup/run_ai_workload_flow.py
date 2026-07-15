#!/usr/bin/env python3
"""Run the AI workload hard-break flow through LLVM, QEMU, and LinxCoreModel."""
from __future__ import annotations

import argparse
import dataclasses
import hashlib
import json
import os
import re
import shlex
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from qemu_build_paths import default_qemu_binary


PASS_STATUSES = {"pass", "skipped", "not_applicable", "not_run"}
DIGEST_RE = re.compile(r"PTO_DIGEST\s+([A-Za-z0-9_]+)\s+0x([0-9A-Fa-f]+)")
GFSIM_BROB_RE = re.compile(
    r"Retired blocks\s+(?P<blocks>\d+)\.\s+BROB head info:\s+"
    r"(?P<head>.*?\bBPC\s+0x(?P<bpc>[0-9A-Fa-f]+).*?)(?:\n|$)"
)
GFSIM_UART_RE = re.compile(r"^linx_uart:\s*(?P<line>.*)$", re.MULTILINE)
GFSIM_FINISHER_RE = re.compile(
    r"linx_test_finisher write addr=0x10009000 val=0x(?P<value>[0-9A-Fa-f]+)\s+(?P<status>pass|fail)"
)
GFSIM_ASSERT_RE = re.compile(r"ASSERTION FAILED:\s*(?P<assertion>[^\n]+)")
FORBIDDEN_ASM_RE = re.compile(
    r"((^|[^A-Za-z0-9_])L\.|set_flag|wait_flag|TSync|B\.SET|B\.WAIT)",
    re.IGNORECASE,
)
FINISHER_PASS_LOW8 = 0x55
FINISHER_FAIL_LOW8 = 0x33
FINISHER_RESET_LOW8 = 0x77
LINX_DIRECT_BOOT_LINK_SCRIPT = """ENTRY(_start)
PHDRS {
  text PT_LOAD FLAGS(5);
  data PT_LOAD FLAGS(6);
}
SECTIONS {
  . = 0x00010000;
  .text : { KEEP(*(.text._start)) *(.text*) } :text
  .rodata : { *(.rodata*) *(.eh_frame*) } :text
  . = ALIGN(0x1000);
  .init_array : { *(.init_array*) *(.fini_array*) } :data
  .data : { *(.sdata*) *(.data*) *(.got*) } :data
  .bss (NOLOAD) : { *(.bss*) *(.sbss*) *(.relro_padding*) *(COMMON) } :data
  . = ALIGN(16);
  .bootstack (NOLOAD) : {
    __start_init_stack = .;
    . += 0x4000;
    __end_init_stack = .;
  } :data
}
"""
LINX_MODEL_SMOKE_SOURCE = r"""extern "C" __attribute__((noreturn, section(".text._start"))) void _start(void) {
  __asm__ volatile(
      "BSTART.STD\n"
      "lui 65545, ->u\n"
      "lui 5, ->t\n"
      "addi t#1, 1365, ->t\n"
      "c.swi t#1, [u#1, 0]\n"
      "BSTOP\n"
      ::: "memory");
  while (1) {
    __asm__ volatile("" ::: "memory");
  }
}
"""
PTO_TLOAD_STORE_HARNESS_SOURCE = r"""extern "C" void tload_store_i32(int *src_ptr, int *dst_ptr);

namespace {

constexpr int kRows = 32;
constexpr int kCols = 32;
constexpr int kElems = kRows * kCols;

int src[kElems];
int dst[kElems];

static inline __attribute__((noreturn)) void linx_pto_exit(unsigned int code) {
  if (code == 0) {
    __asm__ volatile(
        "BSTART.STD\n"
        "lui 65545, ->u\n"
        "lui 5, ->t\n"
        "addi t#1, 1365, ->t\n"
        "c.swi t#1, [u#1, 0]\n"
        "BSTOP\n"
        ::: "memory");
  } else {
    __asm__ volatile(
        "BSTART.STD\n"
        "lui 65545, ->u\n"
        "lui 19, ->t\n"
        "addi t#1, 819, ->t\n"
        "c.swi t#1, [u#1, 0]\n"
        "BSTOP\n"
        ::: "memory");
  }
  while (1) {
    __asm__ volatile("" ::: "memory");
  }
}

} // namespace

int main() {
  for (int i = 0; i < kElems; ++i) {
    src[i] = (i * 17) ^ (i >> 1);
    dst[i] = -1;
  }

  tload_store_i32(src, dst);

  for (int i = 0; i < kElems; ++i) {
    if (dst[i] != src[i]) {
      return 1;
    }
  }
  return 0;
}

extern "C" __attribute__((noreturn, section(".text._start"))) void _start(void) {
  linx_pto_exit(static_cast<unsigned int>(main()));
}
"""
PTO_I32_MATMUL_HARNESS_TEMPLATE = r"""extern "C" void __FUNCTION_NAME__(int *lhs_ptr, int *rhs_ptr, int *dst_ptr);

namespace {

constexpr int kM = 16;
constexpr int kN = 16;
constexpr int kK = 16;
constexpr int kTK = 4;

int lhs[kM * kK];
int rhs[kN * kK];
int dst[kM * kN];

static inline int lhs_value(int m, int k) {
  return ((m + 1) * (k + 3)) & 7;
}

static inline int rhs_value(int n, int k) {
  return ((n + 2) * (k + 1) + 1) & 5;
}

static inline int bias_value(int m, int n) {
  return (m * 3) - (n * 2);
}

static inline int expected_value(int m, int n) {
  long long acc = __EXPECTED_BIAS__;
  for (int k = 0; k < kK; ++k) {
    acc += static_cast<long long>(lhs_value(m, k)) *
           static_cast<long long>(rhs_value(n, k));
  }
__EXTRA_EXPECTED_ACC__
  return static_cast<int>(acc);
}

static inline __attribute__((noreturn)) void linx_pto_exit(unsigned int code) {
  if (code == 0) {
    __asm__ volatile(
        "BSTART.STD\n"
        "lui 65545, ->u\n"
        "lui 5, ->t\n"
        "addi t#1, 1365, ->t\n"
        "c.swi t#1, [u#1, 0]\n"
        "BSTOP\n"
        ::: "memory");
  } else {
    __asm__ volatile(
        "BSTART.STD\n"
        "lui 65545, ->u\n"
        "lui 19, ->t\n"
        "addi t#1, 819, ->t\n"
        "c.swi t#1, [u#1, 0]\n"
        "BSTOP\n"
        ::: "memory");
  }
  while (1) {
    __asm__ volatile("" ::: "memory");
  }
}

} // namespace

int main() {
  for (int m = 0; m < kM; ++m) {
    for (int k = 0; k < kK; ++k) {
      lhs[m * kK + k] = lhs_value(m, k);
    }
  }
  for (int n = 0; n < kN; ++n) {
    for (int k = 0; k < kK; ++k) {
      rhs[n * kK + k] = rhs_value(n, k);
    }
  }
  for (int m = 0; m < kM; ++m) {
    for (int n = 0; n < kN; ++n) {
      dst[m * kN + n] = __INITIAL_DST_VALUE__;
    }
  }

  __FUNCTION_NAME__(lhs, rhs, dst);

  for (int m = 0; m < kM; ++m) {
    for (int n = 0; n < kN; ++n) {
      if (dst[m * kN + n] != expected_value(m, n)) {
        return 1;
      }
    }
  }
  return 0;
}

extern "C" __attribute__((noreturn, section(".text._start"))) void _start(void) {
  linx_pto_exit(static_cast<unsigned int>(main()));
}
"""


def pto_i32_matmul_harness_source(
    function_name: str,
    *,
    use_bias: bool,
    extra_first_tile: bool,
) -> str:
    extra_expected_acc = ""
    if extra_first_tile:
        extra_expected_acc = """  for (int k = 0; k < kTK; ++k) {
    acc += static_cast<long long>(lhs_value(m, k)) *
           static_cast<long long>(rhs_value(n, k));
  }
"""
    return (
        PTO_I32_MATMUL_HARNESS_TEMPLATE.replace("__FUNCTION_NAME__", function_name)
        .replace(
            "__EXPECTED_BIAS__",
            "static_cast<long long>(bias_value(m, n))" if use_bias else "0",
        )
        .replace("__INITIAL_DST_VALUE__", "bias_value(m, n)" if use_bias else "0")
        .replace("__EXTRA_EXPECTED_ACC__", extra_expected_acc)
    )


PTO_GEMM_I32_HARNESS_SOURCE = pto_i32_matmul_harness_source(
    "gemm_i32",
    use_bias=True,
    extra_first_tile=False,
)
PTO_MAMULB_I32_HARNESS_SOURCE = pto_i32_matmul_harness_source(
    "mamulb_i32",
    use_bias=False,
    extra_first_tile=False,
)
PTO_TMATMUL_ACC_I32_HARNESS_SOURCE = pto_i32_matmul_harness_source(
    "tmatmul_acc_i32",
    use_bias=False,
    extra_first_tile=True,
)
PTO_F32_GEMM_COPY_HARNESS_TEMPLATE = r"""__FUNCTION_DECL__

namespace {

constexpr int kM = 16;
constexpr int kN = 16;
constexpr int kK = 16;
constexpr int kRepeatTiles = __REPEAT_TILES__;

float lhs[kM * kK];
float rhs[kN * kK];
float dst[kM * kN];

static inline unsigned int f32_bits(float value) {
  union {
    float f;
    unsigned int u;
  } bits;
  bits.f = value;
  return bits.u;
}

static inline float f32_from_bits(unsigned int value) {
  union {
    unsigned int u;
    float f;
  } bits;
  bits.u = value;
  return bits.f;
}

static inline unsigned int f32_bits_from_u32(unsigned int value) {
  if (value == 0) {
    return 0;
  }
  int msb = 31;
  while (((value >> msb) & 1U) == 0) {
    --msb;
  }
  unsigned int mantissa = 0;
  if (msb >= 23) {
    mantissa = value >> (msb - 23);
  } else {
    mantissa = value << (23 - msb);
  }
  return (static_cast<unsigned int>(msb + 127) << 23) | (mantissa & 0x007fffffU);
}

static inline unsigned int lhs_int(int m, int k) {
  return static_cast<unsigned int>(((m + 1) * (k + 3)) % 19 + 1);
}

static inline unsigned int rhs_int(int n, int k) {
  return static_cast<unsigned int>(((n + 2) * (k + 5)) % 23 + 2);
}

static inline unsigned int lhs_bits(int m, int k) {
  return f32_bits_from_u32(lhs_int(m, k));
}

static inline unsigned int rhs_bits(int n, int k) {
  return f32_bits_from_u32(rhs_int(n, k));
}

static constexpr unsigned int kExpectedBits[kM * kN] = {
__EXPECTED_BITS_ARRAY__
};

static inline unsigned int expected_bits(int m, int n) {
  return kExpectedBits[m * kN + n];
}

static inline __attribute__((noreturn)) void linx_pto_exit(unsigned int code) {
  if (code == 0) {
    __asm__ volatile(
        "BSTART.STD\n"
        "lui 65545, ->u\n"
        "lui 5, ->t\n"
        "addi t#1, 1365, ->t\n"
        "c.swi t#1, [u#1, 0]\n"
        "BSTOP\n"
        ::: "memory");
  } else {
    __asm__ volatile(
        "BSTART.STD\n"
        "lui 65545, ->u\n"
        "lui 19, ->t\n"
        "addi t#1, 819, ->t\n"
        "c.swi t#1, [u#1, 0]\n"
        "BSTOP\n"
        ::: "memory");
  }
  while (1) {
    __asm__ volatile("" ::: "memory");
  }
}

} // namespace

int main() {
  for (int m = 0; m < kM; ++m) {
    for (int k = 0; k < kK; ++k) {
      lhs[m * kK + k] = f32_from_bits(lhs_bits(m, k));
    }
  }
  for (int n = 0; n < kN; ++n) {
    for (int k = 0; k < kK; ++k) {
      rhs[n * kK + k] = f32_from_bits(rhs_bits(n, k));
    }
  }
  for (int m = 0; m < kM; ++m) {
    for (int n = 0; n < kN; ++n) {
      dst[m * kN + n] = f32_from_bits(0);
    }
  }

  __CALL_EXPR__;

  for (int m = 0; m < kM; ++m) {
    for (int n = 0; n < kN; ++n) {
      if (f32_bits(dst[m * kN + n]) != expected_bits(m, n)) {
        return 1;
      }
    }
  }
  return 0;
}

extern "C" __attribute__((noreturn, section(".text._start"))) void _start(void) {
  linx_pto_exit(static_cast<unsigned int>(main()));
}
"""


def pto_f32_bits_from_u32(value: int) -> int:
    if value == 0:
        return 0
    msb = 31
    while ((value >> msb) & 1) == 0:
        msb -= 1
    if msb >= 23:
        mantissa = value >> (msb - 23)
    else:
        mantissa = value << (23 - msb)
    return ((msb + 127) << 23) | (mantissa & 0x007FFFFF)


def pto_f32_gemm_expected_bits_array(repeat_tiles: int) -> str:
    expected_rep = max(repeat_tiles, 1) - 1

    def lhs_bits(m: int, k: int) -> int:
        return pto_f32_bits_from_u32(((m + 1) * (k + 3)) % 19 + 1)

    def rhs_bits(n: int, k: int) -> int:
        return pto_f32_bits_from_u32(((n + 2) * (k + 5)) % 23 + 2)

    values: list[int] = []
    for m in range(16):
        for n in range(16):
            if (expected_rep + m + n) & 1:
                values.append(lhs_bits(m, (n + expected_rep) % 16))
            else:
                values.append(rhs_bits(n, (m + expected_rep) % 16))

    lines = []
    for start in range(0, len(values), 8):
        chunk = ", ".join(f"0x{value:08x}U" for value in values[start : start + 8])
        lines.append(f"    {chunk},")
    return "\n".join(lines)


def pto_f32_gemm_copy_harness_source(
    function_decl: str, call_expr: str, repeat_tiles: int = 1
) -> str:
    return (
        PTO_F32_GEMM_COPY_HARNESS_TEMPLATE.replace("__FUNCTION_DECL__", function_decl)
        .replace("__CALL_EXPR__", call_expr)
        .replace("__REPEAT_TILES__", str(repeat_tiles))
        .replace(
            "__EXPECTED_BITS_ARRAY__",
            pto_f32_gemm_expected_bits_array(repeat_tiles),
        )
    )


PTO_GEMM_BASIC_F32_HARNESS_SOURCE = pto_f32_gemm_copy_harness_source(
    'extern "C" void gemm_basic_f32(float *lhs_ptr, float *rhs_ptr, float *dst_ptr);',
    "gemm_basic_f32(lhs, rhs, dst)",
)
PTO_GEMM_DEMO_F32_HARNESS_SOURCE = pto_f32_gemm_copy_harness_source(
    'extern "C" void gemm_demo_f32(float *out_ptr, float *a_ptr, float *b_ptr);',
    "gemm_demo_f32(dst, lhs, rhs)",
)
PTO_GEMM_PERFORMANCE_F32_HARNESS_SOURCE = pto_f32_gemm_copy_harness_source(
    'extern "C" void gemm_performance_f32(float *lhs_ptr, float *rhs_ptr, float *dst_ptr, int repeat_tiles);',
    "gemm_performance_f32(lhs, rhs, dst, kRepeatTiles)",
    repeat_tiles=3,
)
PTO_FP16_GEMM_REUSE_HARNESS_TEMPLATE = r"""#include <common/linx_lowp_types.hpp>

__FUNCTION_DECL__

namespace {

constexpr int kM = 16;
constexpr int kN = 16;
constexpr int kK = 16;

pto::fp16_t lhs[kM * kK];
pto::fp16_t rhs[kK * kN];
pto::fp16_t dst[kM * kN];

static inline unsigned int f32_bits(float value) {
  union {
    float f;
    unsigned int u;
  } bits;
  bits.f = value;
  return bits.u;
}

static inline float f32_from_bits(unsigned int value) {
  union {
    unsigned int u;
    float f;
  } bits;
  bits.u = value;
  return bits.f;
}

static inline unsigned int f32_bits_from_u32(unsigned int value) {
  if (value == 0) {
    return 0;
  }
  int msb = 31;
  while (((value >> msb) & 1U) == 0) {
    --msb;
  }
  unsigned int mantissa = 0;
  if (msb >= 23) {
    mantissa = value >> (msb - 23);
  } else {
    mantissa = value << (23 - msb);
  }
  return (static_cast<unsigned int>(msb + 127) << 23) | (mantissa & 0x007fffffU);
}

static inline unsigned int u32_from_f32_bits(unsigned int bits) {
  if ((bits & 0x7fffffffU) == 0) {
    return 0;
  }
  const unsigned int exp = (bits >> 23) & 0xffU;
  const unsigned int mantissa = (bits & 0x007fffffU) | 0x00800000U;
  const int shift = static_cast<int>(exp) - 127 - 23;
  if (shift >= 0) {
    return mantissa << shift;
  }
  return mantissa >> static_cast<unsigned int>(-shift);
}

static inline unsigned short fp16_bits_from_u32(unsigned int value) {
  if (value == 0) {
    return 0;
  }
  int msb = 31;
  while (((value >> msb) & 1U) == 0) {
    --msb;
  }
  unsigned int mantissa = 0;
  if (msb >= 10) {
    mantissa = value >> (msb - 10);
  } else {
    mantissa = value << (10 - msb);
  }
  return static_cast<unsigned short>(((msb + 15) << 10) | (mantissa & 0x03ffU));
}

static inline unsigned int lhs_int(int m, int k) {
  return static_cast<unsigned int>(((m + (2 * k)) % 5) + 1);
}

static inline unsigned int rhs_int(int k, int n) {
  return static_cast<unsigned int>((((3 * k) + n) % 7) + 1);
}

static inline unsigned int expected_int(int m, int n) {
  unsigned int acc = 0;
  for (int k = 0; k < kK; ++k) {
    acc += lhs_int(m, k) * rhs_int(k, n);
  }
  return acc;
}

static inline __attribute__((noreturn)) void linx_pto_exit(unsigned int code) {
  if (code == 0) {
    __asm__ volatile(
        "BSTART.STD\n"
        "lui 65545, ->u\n"
        "lui 5, ->t\n"
        "addi t#1, 1365, ->t\n"
        "c.swi t#1, [u#1, 0]\n"
        "BSTOP\n"
        ::: "memory");
  } else {
    __asm__ volatile(
        "BSTART.STD\n"
        "lui 65545, ->u\n"
        "lui 19, ->t\n"
        "addi t#1, 819, ->t\n"
        "c.swi t#1, [u#1, 0]\n"
        "BSTOP\n"
        ::: "memory");
  }
  while (1) {
    __asm__ volatile("" ::: "memory");
  }
}

} // namespace

extern "C" float __mulsf3(float a, float b) {
  const unsigned int a_int = u32_from_f32_bits(f32_bits(a));
  const unsigned int b_int = u32_from_f32_bits(f32_bits(b));
  return f32_from_bits(f32_bits_from_u32(a_int * b_int));
}

extern "C" float __addsf3(float a, float b) {
  const unsigned int a_int = u32_from_f32_bits(f32_bits(a));
  const unsigned int b_int = u32_from_f32_bits(f32_bits(b));
  return f32_from_bits(f32_bits_from_u32(a_int + b_int));
}

int main() {
  for (int m = 0; m < kM; ++m) {
    for (int k = 0; k < kK; ++k) {
      lhs[m * kK + k].bits = fp16_bits_from_u32(lhs_int(m, k));
    }
  }
  for (int k = 0; k < kK; ++k) {
    for (int n = 0; n < kN; ++n) {
      rhs[k * kN + n].bits = fp16_bits_from_u32(rhs_int(k, n));
    }
  }
  for (int i = 0; i < kM * kN; ++i) {
    dst[i].bits = 0;
  }

  __CALL_EXPR__;

  for (int m = 0; m < kM; ++m) {
    for (int n = 0; n < kN; ++n) {
      if (dst[m * kN + n].bits != fp16_bits_from_u32(expected_int(m, n))) {
        return 1;
      }
    }
  }
  return 0;
}

extern "C" __attribute__((noreturn, section(".text._start"))) void _start(void) {
  linx_pto_exit(static_cast<unsigned int>(main()));
}
"""


def pto_fp16_gemm_reuse_harness_source(function_name: str) -> str:
    function_decl = (
        f'extern "C" void {function_name}(pto::fp16_t *lhs_ptr, '
        "pto::fp16_t *rhs_ptr, pto::fp16_t *dst_ptr);"
    )
    return (
        PTO_FP16_GEMM_REUSE_HARNESS_TEMPLATE.replace("__FUNCTION_DECL__", function_decl)
        .replace("__CALL_EXPR__", f"{function_name}(lhs, rhs, dst)")
    )


PTO_GEMM_REUSE_A_FP16_HARNESS_SOURCE = pto_fp16_gemm_reuse_harness_source(
    "gemm_reuse_a_f16"
)
PTO_GEMM_REUSE_B_FP16_HARNESS_SOURCE = pto_fp16_gemm_reuse_harness_source(
    "gemm_reuse_b_f16"
)
PTO_GEMM_REUSE_AB_FP16_HARNESS_SOURCE = pto_fp16_gemm_reuse_harness_source(
    "gemm_reuse_ab_f16"
)
PTO_RELU_F32_HARNESS_SOURCE = r"""extern "C" void relu_f32(float *out_ptr, float *x_ptr, int n);

namespace {

constexpr int kElems = 32;

float src[kElems];
float dst[kElems];

static inline float src_value(int i) {
  return static_cast<float>((i % 11) - 5);
}

static inline float expected_value(float x) {
  return x > 0.0f ? x : 0.0f;
}

static inline __attribute__((noreturn)) void linx_pto_exit(unsigned int code) {
  if (code == 0) {
    __asm__ volatile(
        "BSTART.STD\n"
        "lui 65545, ->u\n"
        "lui 5, ->t\n"
        "addi t#1, 1365, ->t\n"
        "c.swi t#1, [u#1, 0]\n"
        "BSTOP\n"
        ::: "memory");
  } else {
    __asm__ volatile(
        "BSTART.STD\n"
        "lui 65545, ->u\n"
        "lui 19, ->t\n"
        "addi t#1, 819, ->t\n"
        "c.swi t#1, [u#1, 0]\n"
        "BSTOP\n"
        ::: "memory");
  }
  while (1) {
    __asm__ volatile("" ::: "memory");
  }
}

} // namespace

int main() {
  for (int i = 0; i < kElems; ++i) {
    src[i] = src_value(i);
    dst[i] = -99.0f;
  }

  relu_f32(dst, src, kElems);

  for (int i = 0; i < kElems; ++i) {
    if (dst[i] != expected_value(src[i])) {
      return 1;
    }
  }
  return 0;
}

extern "C" __attribute__((noreturn, section(".text._start"))) void _start(void) {
  linx_pto_exit(static_cast<unsigned int>(main()));
}
"""
PTO_UNARY_COPY_F32_HARNESS_TEMPLATE = r"""extern "C" void __FUNCTION_NAME__(float *out_ptr, float *in_ptr, int n);

namespace {

constexpr int kElems = 32;

float src[kElems];
float dst[kElems];

static inline float src_value(int i) {
  return static_cast<float>((i % 13) - 6);
}

static inline __attribute__((noreturn)) void linx_pto_exit(unsigned int code) {
  if (code == 0) {
    __asm__ volatile(
        "BSTART.STD\n"
        "lui 65545, ->u\n"
        "lui 5, ->t\n"
        "addi t#1, 1365, ->t\n"
        "c.swi t#1, [u#1, 0]\n"
        "BSTOP\n"
        ::: "memory");
  } else {
    __asm__ volatile(
        "BSTART.STD\n"
        "lui 65545, ->u\n"
        "lui 19, ->t\n"
        "addi t#1, 819, ->t\n"
        "c.swi t#1, [u#1, 0]\n"
        "BSTOP\n"
        ::: "memory");
  }
  while (1) {
    __asm__ volatile("" ::: "memory");
  }
}

} // namespace

int main() {
  for (int i = 0; i < kElems; ++i) {
    src[i] = src_value(i);
    dst[i] = -99.0f;
  }

  __FUNCTION_NAME__(dst, src, kElems);

  for (int i = 0; i < kElems; ++i) {
    if (dst[i] != src[i]) {
      return 1;
    }
  }
  return 0;
}

extern "C" __attribute__((noreturn, section(".text._start"))) void _start(void) {
  linx_pto_exit(static_cast<unsigned int>(main()));
}
"""


def pto_unary_copy_f32_harness_source(function_name: str) -> str:
    return PTO_UNARY_COPY_F32_HARNESS_TEMPLATE.replace(
        "__FUNCTION_NAME__", function_name
    )


PTO_FLATTEN_F32_HARNESS_SOURCE = pto_unary_copy_f32_harness_source("flatten_f32")
PTO_RESHAPE_F32_HARNESS_SOURCE = pto_unary_copy_f32_harness_source("reshape_f32")
PTO_SQUEEZE_F32_HARNESS_SOURCE = pto_unary_copy_f32_harness_source("squeeze_f32")
PTO_UNSQUEEZE_F32_HARNESS_SOURCE = pto_unary_copy_f32_harness_source("unsqueeze_f32")
PTO_CONCAT_F32_HARNESS_SOURCE = r"""extern "C" void concat_f32(float *out_ptr, float *a_ptr, float *b_ptr, int n_a, int n_b);

namespace {

constexpr int kA = 11;
constexpr int kB = 7;
constexpr int kOut = kA + kB;

float a[kA];
float b[kB];
float out[kOut];

static inline float a_value(int i) {
  return static_cast<float>((i % 9) - 4);
}

static inline float b_value(int i) {
  return static_cast<float>(20 + i);
}

static inline __attribute__((noreturn)) void linx_pto_exit(unsigned int code) {
  if (code == 0) {
    __asm__ volatile(
        "BSTART.STD\n"
        "lui 65545, ->u\n"
        "lui 5, ->t\n"
        "addi t#1, 1365, ->t\n"
        "c.swi t#1, [u#1, 0]\n"
        "BSTOP\n"
        ::: "memory");
  } else {
    __asm__ volatile(
        "BSTART.STD\n"
        "lui 65545, ->u\n"
        "lui 19, ->t\n"
        "addi t#1, 819, ->t\n"
        "c.swi t#1, [u#1, 0]\n"
        "BSTOP\n"
        ::: "memory");
  }
  while (1) {
    __asm__ volatile("" ::: "memory");
  }
}

} // namespace

int main() {
  for (int i = 0; i < kA; ++i) {
    a[i] = a_value(i);
  }
  for (int i = 0; i < kB; ++i) {
    b[i] = b_value(i);
  }
  for (int i = 0; i < kOut; ++i) {
    out[i] = -99.0f;
  }

  concat_f32(out, a, b, kA, kB);

  for (int i = 0; i < kA; ++i) {
    if (out[i] != a[i]) {
      return 1;
    }
  }
  for (int i = 0; i < kB; ++i) {
    if (out[kA + i] != b[i]) {
      return 1;
    }
  }
  return 0;
}

extern "C" __attribute__((noreturn, section(".text._start"))) void _start(void) {
  linx_pto_exit(static_cast<unsigned int>(main()));
}
"""
PTO_SPLIT_F32_HARNESS_SOURCE = r"""extern "C" void split_f32(float *out_a_ptr, float *out_b_ptr, float *in_ptr, int n_a, int n_b);

namespace {

constexpr int kA = 9;
constexpr int kB = 6;
constexpr int kIn = kA + kB;

float in_values[kIn];
float out_a[kA];
float out_b[kB];

static inline float in_value(int i) {
  return static_cast<float>((i % 17) - 8);
}

static inline __attribute__((noreturn)) void linx_pto_exit(unsigned int code) {
  if (code == 0) {
    __asm__ volatile(
        "BSTART.STD\n"
        "lui 65545, ->u\n"
        "lui 5, ->t\n"
        "addi t#1, 1365, ->t\n"
        "c.swi t#1, [u#1, 0]\n"
        "BSTOP\n"
        ::: "memory");
  } else {
    __asm__ volatile(
        "BSTART.STD\n"
        "lui 65545, ->u\n"
        "lui 19, ->t\n"
        "addi t#1, 819, ->t\n"
        "c.swi t#1, [u#1, 0]\n"
        "BSTOP\n"
        ::: "memory");
  }
  while (1) {
    __asm__ volatile("" ::: "memory");
  }
}

} // namespace

int main() {
  for (int i = 0; i < kIn; ++i) {
    in_values[i] = in_value(i);
  }
  for (int i = 0; i < kA; ++i) {
    out_a[i] = -99.0f;
  }
  for (int i = 0; i < kB; ++i) {
    out_b[i] = -99.0f;
  }

  split_f32(out_a, out_b, in_values, kA, kB);

  for (int i = 0; i < kA; ++i) {
    if (out_a[i] != in_values[i]) {
      return 1;
    }
  }
  for (int i = 0; i < kB; ++i) {
    if (out_b[i] != in_values[kA + i]) {
      return 1;
    }
  }
  return 0;
}

extern "C" __attribute__((noreturn, section(".text._start"))) void _start(void) {
  linx_pto_exit(static_cast<unsigned int>(main()));
}
"""
PTO_STACK_F32_HARNESS_SOURCE = r"""extern "C" void stack_f32(float *out_ptr, float *a_ptr, float *b_ptr, int n);

namespace {

constexpr int kElems = 12;
constexpr int kOut = kElems * 2;

float a[kElems];
float b[kElems];
float out[kOut];

static inline float a_value(int i) {
  return static_cast<float>((i % 9) - 3);
}

static inline float b_value(int i) {
  return static_cast<float>(30 - i);
}

static inline __attribute__((noreturn)) void linx_pto_exit(unsigned int code) {
  if (code == 0) {
    __asm__ volatile(
        "BSTART.STD\n"
        "lui 65545, ->u\n"
        "lui 5, ->t\n"
        "addi t#1, 1365, ->t\n"
        "c.swi t#1, [u#1, 0]\n"
        "BSTOP\n"
        ::: "memory");
  } else {
    __asm__ volatile(
        "BSTART.STD\n"
        "lui 65545, ->u\n"
        "lui 19, ->t\n"
        "addi t#1, 819, ->t\n"
        "c.swi t#1, [u#1, 0]\n"
        "BSTOP\n"
        ::: "memory");
  }
  while (1) {
    __asm__ volatile("" ::: "memory");
  }
}

} // namespace

int main() {
  for (int i = 0; i < kElems; ++i) {
    a[i] = a_value(i);
    b[i] = b_value(i);
  }
  for (int i = 0; i < kOut; ++i) {
    out[i] = -99.0f;
  }

  stack_f32(out, a, b, kElems);

  for (int i = 0; i < kElems; ++i) {
    if (out[i] != a[i] || out[kElems + i] != b[i]) {
      return 1;
    }
  }
  return 0;
}

extern "C" __attribute__((noreturn, section(".text._start"))) void _start(void) {
  linx_pto_exit(static_cast<unsigned int>(main()));
}
"""
PTO_SLICE_F32_HARNESS_SOURCE = r"""extern "C" void slice_f32(float *out_ptr, float *in_ptr, int start, int len);

namespace {

constexpr int kStart = 5;
constexpr int kLen = 12;
constexpr int kInput = 24;

float in_values[kInput];
float out[kLen];

static inline float in_value(int i) {
  return static_cast<float>((i % 19) - 9);
}

static inline __attribute__((noreturn)) void linx_pto_exit(unsigned int code) {
  if (code == 0) {
    __asm__ volatile(
        "BSTART.STD\n"
        "lui 65545, ->u\n"
        "lui 5, ->t\n"
        "addi t#1, 1365, ->t\n"
        "c.swi t#1, [u#1, 0]\n"
        "BSTOP\n"
        ::: "memory");
  } else {
    __asm__ volatile(
        "BSTART.STD\n"
        "lui 65545, ->u\n"
        "lui 19, ->t\n"
        "addi t#1, 819, ->t\n"
        "c.swi t#1, [u#1, 0]\n"
        "BSTOP\n"
        ::: "memory");
  }
  while (1) {
    __asm__ volatile("" ::: "memory");
  }
}

} // namespace

int main() {
  for (int i = 0; i < kInput; ++i) {
    in_values[i] = in_value(i);
  }
  for (int i = 0; i < kLen; ++i) {
    out[i] = -99.0f;
  }

  slice_f32(out, in_values, kStart, kLen);

  for (int i = 0; i < kLen; ++i) {
    if (out[i] != in_values[kStart + i]) {
      return 1;
    }
  }
  return 0;
}

extern "C" __attribute__((noreturn, section(".text._start"))) void _start(void) {
  linx_pto_exit(static_cast<unsigned int>(main()));
}
"""
PTO_GATHER_F32_HARNESS_SOURCE = r"""extern "C" void gather_f32(float *out_ptr, float *in_ptr, int *indices_ptr, int n);

namespace {

constexpr int kInput = 16;
constexpr int kElems = 8;

float in_values[kInput];
float out[kElems];
int indices[kElems];

static inline int index_value(int i) {
  constexpr int kIndices[kElems] = {7, 0, 11, 3, 14, 5, 2, 9};
  return kIndices[i];
}

static inline float in_value(int i) {
  return static_cast<float>((i % 23) - 11);
}

static inline __attribute__((noreturn)) void linx_pto_exit(unsigned int code) {
  if (code == 0) {
    __asm__ volatile(
        "BSTART.STD\n"
        "lui 65545, ->u\n"
        "lui 5, ->t\n"
        "addi t#1, 1365, ->t\n"
        "c.swi t#1, [u#1, 0]\n"
        "BSTOP\n"
        ::: "memory");
  } else {
    __asm__ volatile(
        "BSTART.STD\n"
        "lui 65545, ->u\n"
        "lui 19, ->t\n"
        "addi t#1, 819, ->t\n"
        "c.swi t#1, [u#1, 0]\n"
        "BSTOP\n"
        ::: "memory");
  }
  while (1) {
    __asm__ volatile("" ::: "memory");
  }
}

} // namespace

int main() {
  for (int i = 0; i < kInput; ++i) {
    in_values[i] = in_value(i);
  }
  for (int i = 0; i < kElems; ++i) {
    indices[i] = index_value(i);
    out[i] = -99.0f;
  }

  gather_f32(out, in_values, indices, kElems);

  for (int i = 0; i < kElems; ++i) {
    if (out[i] != in_values[index_value(i)]) {
      return 1;
    }
  }
  return 0;
}

extern "C" __attribute__((noreturn, section(".text._start"))) void _start(void) {
  linx_pto_exit(static_cast<unsigned int>(main()));
}
"""
PTO_SCATTER_F32_HARNESS_SOURCE = r"""extern "C" void scatter_f32(float *out_ptr, float *in_ptr, int *indices_ptr, float *updates_ptr, int n);

namespace {

constexpr int kElems = 8;

float in_values[kElems];
float updates[kElems];
float out[kElems];
int indices[kElems];

static inline int index_value(int i) {
  constexpr int kIndices[kElems] = {3, 0, 7, 1, 6, 4, 2, 5};
  return kIndices[i];
}

static inline float in_value(int i) {
  return static_cast<float>((i % 11) - 5);
}

static inline float update_value(int i) {
  return static_cast<float>(40 + i);
}

static inline float expected_value(int idx) {
  for (int i = 0; i < kElems; ++i) {
    if (index_value(i) == idx) {
      return update_value(i);
    }
  }
  return in_value(idx);
}

static inline __attribute__((noreturn)) void linx_pto_exit(unsigned int code) {
  if (code == 0) {
    __asm__ volatile(
        "BSTART.STD\n"
        "lui 65545, ->u\n"
        "lui 5, ->t\n"
        "addi t#1, 1365, ->t\n"
        "c.swi t#1, [u#1, 0]\n"
        "BSTOP\n"
        ::: "memory");
  } else {
    __asm__ volatile(
        "BSTART.STD\n"
        "lui 65545, ->u\n"
        "lui 19, ->t\n"
        "addi t#1, 819, ->t\n"
        "c.swi t#1, [u#1, 0]\n"
        "BSTOP\n"
        ::: "memory");
  }
  while (1) {
    __asm__ volatile("" ::: "memory");
  }
}

} // namespace

int main() {
  for (int i = 0; i < kElems; ++i) {
    in_values[i] = in_value(i);
    updates[i] = update_value(i);
    indices[i] = index_value(i);
    out[i] = -99.0f;
  }

  scatter_f32(out, in_values, indices, updates, kElems);

  for (int i = 0; i < kElems; ++i) {
    if (out[i] != expected_value(i)) {
      return 1;
    }
  }
  return 0;
}

extern "C" __attribute__((noreturn, section(".text._start"))) void _start(void) {
  linx_pto_exit(static_cast<unsigned int>(main()));
}
"""
PTO_WHERE_F32_HARNESS_SOURCE = r"""extern "C" void where_f32(float *out_ptr, float *cond_ptr, float *x_ptr, float *y_ptr, int n);

namespace {

constexpr int kElems = 16;

float cond[kElems];
float x[kElems];
float y[kElems];
float out[kElems];

static inline float cond_value(int i) {
  return static_cast<float>((i % 5) - 2);
}

static inline float x_value(int i) {
  return static_cast<float>(10 + i);
}

static inline float y_value(int i) {
  return static_cast<float>(-20 - i);
}

static inline float expected_value(int i) {
  return cond_value(i) > 0.0f ? x_value(i) : y_value(i);
}

static inline __attribute__((noreturn)) void linx_pto_exit(unsigned int code) {
  if (code == 0) {
    __asm__ volatile(
        "BSTART.STD\n"
        "lui 65545, ->u\n"
        "lui 5, ->t\n"
        "addi t#1, 1365, ->t\n"
        "c.swi t#1, [u#1, 0]\n"
        "BSTOP\n"
        ::: "memory");
  } else {
    __asm__ volatile(
        "BSTART.STD\n"
        "lui 65545, ->u\n"
        "lui 19, ->t\n"
        "addi t#1, 819, ->t\n"
        "c.swi t#1, [u#1, 0]\n"
        "BSTOP\n"
        ::: "memory");
  }
  while (1) {
    __asm__ volatile("" ::: "memory");
  }
}

} // namespace

int main() {
  for (int i = 0; i < kElems; ++i) {
    cond[i] = cond_value(i);
    x[i] = x_value(i);
    y[i] = y_value(i);
    out[i] = -99.0f;
  }

  where_f32(out, cond, x, y, kElems);

  for (int i = 0; i < kElems; ++i) {
    if (out[i] != expected_value(i)) {
      return 1;
    }
  }
  return 0;
}

extern "C" __attribute__((noreturn, section(".text._start"))) void _start(void) {
  linx_pto_exit(static_cast<unsigned int>(main()));
}
"""
PTO_ARGMAX_F32_HARNESS_SOURCE = r"""extern "C" void argmax_f32(int *idx_ptr, float *x_ptr, int rows, int cols);

namespace {

constexpr int kRows = 4;
constexpr int kCols = 5;
constexpr int kElems = kRows * kCols;

float x[kElems];
int idx[kRows];

static inline int expected_index(int row) {
  constexpr int kExpected[kRows] = {3, 1, 4, 2};
  return kExpected[row];
}

static inline float value_at(int row, int col) {
  return static_cast<float>((row * 3) - (col * 2) + (col == expected_index(row) ? 50 : 0));
}

static inline __attribute__((noreturn)) void linx_pto_exit(unsigned int code) {
  if (code == 0) {
    __asm__ volatile(
        "BSTART.STD\n"
        "lui 65545, ->u\n"
        "lui 5, ->t\n"
        "addi t#1, 1365, ->t\n"
        "c.swi t#1, [u#1, 0]\n"
        "BSTOP\n"
        ::: "memory");
  } else {
    __asm__ volatile(
        "BSTART.STD\n"
        "lui 65545, ->u\n"
        "lui 19, ->t\n"
        "addi t#1, 819, ->t\n"
        "c.swi t#1, [u#1, 0]\n"
        "BSTOP\n"
        ::: "memory");
  }
  while (1) {
    __asm__ volatile("" ::: "memory");
  }
}

} // namespace

int main() {
  for (int r = 0; r < kRows; ++r) {
    idx[r] = -1;
    for (int c = 0; c < kCols; ++c) {
      x[r * kCols + c] = value_at(r, c);
    }
  }

  argmax_f32(idx, x, kRows, kCols);

  for (int r = 0; r < kRows; ++r) {
    if (idx[r] != expected_index(r)) {
      return 1;
    }
  }
  return 0;
}

extern "C" __attribute__((noreturn, section(".text._start"))) void _start(void) {
  linx_pto_exit(static_cast<unsigned int>(main()));
}
"""
PTO_UNIQUE_I32_HARNESS_SOURCE = r"""extern "C" void unique_i32(int *out_values_ptr, int *out_count_ptr, int *in_values_ptr, int n);

namespace {

constexpr int kElems = 12;
constexpr int kUnique = 6;

int in_values[kElems];
int out_values[kElems];
int out_count[1];

static inline int input_value(int i) {
  constexpr int kValues[kElems] = {4, -1, 7, 4, 0, -1, 9, 7, 5, 0, 5, 9};
  return kValues[i];
}

static inline int expected_value(int i) {
  constexpr int kExpected[kUnique] = {4, -1, 7, 0, 9, 5};
  return kExpected[i];
}

static inline __attribute__((noreturn)) void linx_pto_exit(unsigned int code) {
  if (code == 0) {
    __asm__ volatile(
        "BSTART.STD\n"
        "lui 65545, ->u\n"
        "lui 5, ->t\n"
        "addi t#1, 1365, ->t\n"
        "c.swi t#1, [u#1, 0]\n"
        "BSTOP\n"
        ::: "memory");
  } else {
    __asm__ volatile(
        "BSTART.STD\n"
        "lui 65545, ->u\n"
        "lui 19, ->t\n"
        "addi t#1, 819, ->t\n"
        "c.swi t#1, [u#1, 0]\n"
        "BSTOP\n"
        ::: "memory");
  }
  while (1) {
    __asm__ volatile("" ::: "memory");
  }
}

} // namespace

int main() {
  for (int i = 0; i < kElems; ++i) {
    in_values[i] = input_value(i);
    out_values[i] = -999;
  }
  out_count[0] = -1;

  unique_i32(out_values, out_count, in_values, kElems);

  if (out_count[0] != kUnique) {
    return 1;
  }
  for (int i = 0; i < kUnique; ++i) {
    if (out_values[i] != expected_value(i)) {
      return 1;
    }
  }
  return 0;
}

extern "C" __attribute__((noreturn, section(".text._start"))) void _start(void) {
  linx_pto_exit(static_cast<unsigned int>(main()));
}
"""
PTO_HASH_TABLE_INSERT_F32_HARNESS_SOURCE = r"""extern "C" void hash_table_insert_f32(int *table_keys_ptr, float *table_values_ptr, int table_size, int *keys_ptr, float *values_ptr, int n);

namespace {

constexpr int kTableSize = 8;
constexpr int kElems = 5;

int table_keys[kTableSize];
float table_values[kTableSize];
int keys[kElems];
float values[kElems];

static inline float f32_from_u32(unsigned int value) {
  return static_cast<float>(static_cast<int>(value));
}

static inline int initial_key(int i) {
  constexpr int kInitial[kTableSize] = {-1, 7, -1, 11, -1, -1, 5, -1};
  return kInitial[i];
}

static inline unsigned int initial_value(int i) {
  constexpr unsigned int kInitial[kTableSize] = {0, 70, 0, 110, 0, 0, 50, 0};
  return kInitial[i];
}

static inline int input_key(int i) {
  constexpr int kKeys[kElems] = {3, 7, 12, 5, 19};
  return kKeys[i];
}

static inline unsigned int input_value(int i) {
  constexpr unsigned int kValues[kElems] = {30, 71, 120, 51, 190};
  return kValues[i];
}

static inline int expected_key(int i) {
  constexpr int kExpected[kTableSize] = {3, 7, 12, 11, 19, -1, 5, -1};
  return kExpected[i];
}

static inline unsigned int expected_value(int i) {
  constexpr unsigned int kExpected[kTableSize] = {30, 71, 120, 110, 190, 0, 51, 0};
  return kExpected[i];
}

static inline __attribute__((noreturn)) void linx_pto_exit(unsigned int code) {
  if (code == 0) {
    __asm__ volatile(
        "BSTART.STD\n"
        "lui 65545, ->u\n"
        "lui 5, ->t\n"
        "addi t#1, 1365, ->t\n"
        "c.swi t#1, [u#1, 0]\n"
        "BSTOP\n"
        ::: "memory");
  } else {
    __asm__ volatile(
        "BSTART.STD\n"
        "lui 65545, ->u\n"
        "lui 19, ->t\n"
        "addi t#1, 819, ->t\n"
        "c.swi t#1, [u#1, 0]\n"
        "BSTOP\n"
        ::: "memory");
  }
  while (1) {
    __asm__ volatile("" ::: "memory");
  }
}

} // namespace

int main() {
  for (int i = 0; i < kTableSize; ++i) {
    table_keys[i] = initial_key(i);
    table_values[i] = f32_from_u32(initial_value(i));
  }
  for (int i = 0; i < kElems; ++i) {
    keys[i] = input_key(i);
    values[i] = f32_from_u32(input_value(i));
  }

  hash_table_insert_f32(table_keys, table_values, kTableSize, keys, values, kElems);

  for (int i = 0; i < kTableSize; ++i) {
    if (table_keys[i] != expected_key(i) ||
        table_values[i] != f32_from_u32(expected_value(i))) {
      return 1;
    }
  }
  return 0;
}

extern "C" __attribute__((noreturn, section(".text._start"))) void _start(void) {
  linx_pto_exit(static_cast<unsigned int>(main()));
}
"""
PTO_HASH_TABLE_LOOKUP_F32_HARNESS_SOURCE = r"""extern "C" void hash_table_lookup_f32(float *out_values_ptr, int *keys_ptr, int *table_keys_ptr, float *table_values_ptr, int table_size, int nkeys);

namespace {

constexpr int kTableSize = 8;
constexpr int kKeys = 6;

int table_keys[kTableSize];
float table_values[kTableSize];
int keys[kKeys];
float out_values[kKeys];

static inline float f32_from_u32(unsigned int value) {
  return static_cast<float>(static_cast<int>(value));
}

static inline int table_key(int i) {
  constexpr int kTableKeys[kTableSize] = {3, 7, 12, 11, 19, -1, 5, -1};
  return kTableKeys[i];
}

static inline unsigned int table_value(int i) {
  constexpr unsigned int kTableValues[kTableSize] = {30, 71, 120, 110, 190, 0, 51, 0};
  return kTableValues[i];
}

static inline int lookup_key(int i) {
  constexpr int kLookup[kKeys] = {19, 5, 42, 3, 11, 8};
  return kLookup[i];
}

static inline unsigned int expected_value(int i) {
  constexpr unsigned int kExpected[kKeys] = {190, 51, 0, 30, 110, 0};
  return kExpected[i];
}

static inline __attribute__((noreturn)) void linx_pto_exit(unsigned int code) {
  if (code == 0) {
    __asm__ volatile(
        "BSTART.STD\n"
        "lui 65545, ->u\n"
        "lui 5, ->t\n"
        "addi t#1, 1365, ->t\n"
        "c.swi t#1, [u#1, 0]\n"
        "BSTOP\n"
        ::: "memory");
  } else {
    __asm__ volatile(
        "BSTART.STD\n"
        "lui 65545, ->u\n"
        "lui 19, ->t\n"
        "addi t#1, 819, ->t\n"
        "c.swi t#1, [u#1, 0]\n"
        "BSTOP\n"
        ::: "memory");
  }
  while (1) {
    __asm__ volatile("" ::: "memory");
  }
}

} // namespace

int main() {
  for (int i = 0; i < kTableSize; ++i) {
    table_keys[i] = table_key(i);
    table_values[i] = f32_from_u32(table_value(i));
  }
  for (int i = 0; i < kKeys; ++i) {
    keys[i] = lookup_key(i);
    out_values[i] = f32_from_u32(999);
  }

  hash_table_lookup_f32(out_values, keys, table_keys, table_values, kTableSize, kKeys);

  for (int i = 0; i < kKeys; ++i) {
    if (out_values[i] != f32_from_u32(expected_value(i))) {
      return 1;
    }
  }
  return 0;
}

extern "C" __attribute__((noreturn, section(".text._start"))) void _start(void) {
  linx_pto_exit(static_cast<unsigned int>(main()));
}
"""
PTO_UNSORTED_SEGMENT_SUM_F32_HARNESS_SOURCE = r"""extern "C" void unsorted_segment_sum_f32(float *out_ptr, int *segment_ids_ptr, float *data_ptr, int n, int num_segments);

namespace {

constexpr int kElems = 10;
constexpr int kSegments = 4;

float out_values[kSegments];
int segment_ids[kElems];
float data[kElems];

static inline unsigned int f32_bits(float value) {
  union {
    float f;
    unsigned int u;
  } bits;
  bits.f = value;
  return bits.u;
}

static inline float f32_from_bits(unsigned int value) {
  union {
    unsigned int u;
    float f;
  } bits;
  bits.u = value;
  return bits.f;
}

static inline unsigned int f32_bits_from_u32(unsigned int value) {
  if (value == 0) {
    return 0;
  }
  int msb = 31;
  while (((value >> msb) & 1U) == 0) {
    --msb;
  }
  unsigned int mantissa = 0;
  if (msb >= 23) {
    mantissa = value >> (msb - 23);
  } else {
    mantissa = value << (23 - msb);
  }
  return (static_cast<unsigned int>(msb + 127) << 23) | (mantissa & 0x007fffffU);
}

static inline unsigned int u32_from_f32_bits(unsigned int bits) {
  if ((bits & 0x7fffffffU) == 0) {
    return 0;
  }
  const unsigned int exponent = (bits >> 23) & 0xffU;
  const unsigned int mantissa = (bits & 0x007fffffU) | 0x00800000U;
  const int shift = static_cast<int>(exponent) - 127 - 23;
  return shift >= 0 ? (mantissa << shift) : (mantissa >> -shift);
}

static inline int segment_id(int i) {
  constexpr int kIds[kElems] = {2, 0, 1, 2, -1, 1, 3, 0, 5, 2};
  return kIds[i];
}

static inline unsigned int data_value(int i) {
  return static_cast<unsigned int>(i + 1);
}

static inline unsigned int expected_value(int i) {
  constexpr unsigned int kExpected[kSegments] = {10, 9, 15, 7};
  return kExpected[i];
}

static inline __attribute__((noreturn)) void linx_pto_exit(unsigned int code) {
  if (code == 0) {
    __asm__ volatile(
        "BSTART.STD\n"
        "lui 65545, ->u\n"
        "lui 5, ->t\n"
        "addi t#1, 1365, ->t\n"
        "c.swi t#1, [u#1, 0]\n"
        "BSTOP\n"
        ::: "memory");
  } else {
    __asm__ volatile(
        "BSTART.STD\n"
        "lui 65545, ->u\n"
        "lui 19, ->t\n"
        "addi t#1, 819, ->t\n"
        "c.swi t#1, [u#1, 0]\n"
        "BSTOP\n"
        ::: "memory");
  }
  while (1) {
    __asm__ volatile("" ::: "memory");
  }
}

} // namespace

extern "C" float __addsf3(float a, float b) {
  const unsigned int a_int = u32_from_f32_bits(f32_bits(a));
  const unsigned int b_int = u32_from_f32_bits(f32_bits(b));
  return f32_from_bits(f32_bits_from_u32(a_int + b_int));
}

int main() {
  for (int i = 0; i < kSegments; ++i) {
    out_values[i] = f32_from_bits(f32_bits_from_u32(999));
  }
  for (int i = 0; i < kElems; ++i) {
    segment_ids[i] = segment_id(i);
    data[i] = f32_from_bits(f32_bits_from_u32(data_value(i)));
  }

  unsorted_segment_sum_f32(out_values, segment_ids, data, kElems, kSegments);

  for (int i = 0; i < kSegments; ++i) {
    if (f32_bits(out_values[i]) != f32_bits_from_u32(expected_value(i))) {
      return 1;
    }
  }
  return 0;
}

extern "C" __attribute__((noreturn, section(".text._start"))) void _start(void) {
  linx_pto_exit(static_cast<unsigned int>(main()));
}
"""
PTO_PERMUTE_NHWC_NCHW_F32_HARNESS_SOURCE = r"""extern "C" void permute_nhwc_nchw_f32(float *out_ptr, float *in_ptr, int n, int h, int w, int c);

namespace {

constexpr int kN = 2;
constexpr int kH = 3;
constexpr int kW = 4;
constexpr int kC = 5;
constexpr int kElems = kN * kH * kW * kC;

float in_values[kElems];
float out_values[kElems];

static inline float input_value(int i) {
  return static_cast<float>((i % 29) - 14);
}

static inline int src_index(int nn, int hh, int ww, int cc) {
  return ((nn * kH + hh) * kW + ww) * kC + cc;
}

static inline int dst_index(int nn, int hh, int ww, int cc) {
  return ((nn * kC + cc) * kH + hh) * kW + ww;
}

static inline __attribute__((noreturn)) void linx_pto_exit(unsigned int code) {
  if (code == 0) {
    __asm__ volatile(
        "BSTART.STD\n"
        "lui 65545, ->u\n"
        "lui 5, ->t\n"
        "addi t#1, 1365, ->t\n"
        "c.swi t#1, [u#1, 0]\n"
        "BSTOP\n"
        ::: "memory");
  } else {
    __asm__ volatile(
        "BSTART.STD\n"
        "lui 65545, ->u\n"
        "lui 19, ->t\n"
        "addi t#1, 819, ->t\n"
        "c.swi t#1, [u#1, 0]\n"
        "BSTOP\n"
        ::: "memory");
  }
  while (1) {
    __asm__ volatile("" ::: "memory");
  }
}

} // namespace

int main() {
  for (int i = 0; i < kElems; ++i) {
    in_values[i] = input_value(i);
    out_values[i] = -99.0f;
  }

  permute_nhwc_nchw_f32(out_values, in_values, kN, kH, kW, kC);

  for (int nn = 0; nn < kN; ++nn) {
    for (int hh = 0; hh < kH; ++hh) {
      for (int ww = 0; ww < kW; ++ww) {
        for (int cc = 0; cc < kC; ++cc) {
          if (out_values[dst_index(nn, hh, ww, cc)] !=
              in_values[src_index(nn, hh, ww, cc)]) {
            return 1;
          }
        }
      }
    }
  }
  return 0;
}

extern "C" __attribute__((noreturn, section(".text._start"))) void _start(void) {
  linx_pto_exit(static_cast<unsigned int>(main()));
}
"""
PTO_TRANSPOSE_LARGE_F32_HARNESS_SOURCE = r"""extern "C" void transpose_large_f32(float *out_ptr, float *in_ptr, int rows, int cols);

namespace {

constexpr int kRows = 7;
constexpr int kCols = 9;
constexpr int kElems = kRows * kCols;

float in_values[kElems];
float out_values[kElems];

static inline float input_value(int i) {
  return static_cast<float>((i % 31) - 15);
}

static inline __attribute__((noreturn)) void linx_pto_exit(unsigned int code) {
  if (code == 0) {
    __asm__ volatile(
        "BSTART.STD\n"
        "lui 65545, ->u\n"
        "lui 5, ->t\n"
        "addi t#1, 1365, ->t\n"
        "c.swi t#1, [u#1, 0]\n"
        "BSTOP\n"
        ::: "memory");
  } else {
    __asm__ volatile(
        "BSTART.STD\n"
        "lui 65545, ->u\n"
        "lui 19, ->t\n"
        "addi t#1, 819, ->t\n"
        "c.swi t#1, [u#1, 0]\n"
        "BSTOP\n"
        ::: "memory");
  }
  while (1) {
    __asm__ volatile("" ::: "memory");
  }
}

} // namespace

int main() {
  for (int i = 0; i < kElems; ++i) {
    in_values[i] = input_value(i);
    out_values[i] = -99.0f;
  }

  transpose_large_f32(out_values, in_values, kRows, kCols);

  for (int r = 0; r < kRows; ++r) {
    for (int c = 0; c < kCols; ++c) {
      if (out_values[c * kRows + r] != in_values[r * kCols + c]) {
        return 1;
      }
    }
  }
  return 0;
}

extern "C" __attribute__((noreturn, section(".text._start"))) void _start(void) {
  linx_pto_exit(static_cast<unsigned int>(main()));
}
"""
PTO_ADD_CUSTOM_F32_HARNESS_SOURCE = r"""#include <common/runtime/kernel_shapes.hpp>

extern "C" void add_custom_f32(float *x_ptr, float *y_ptr, float *z_ptr);

namespace {

constexpr int kRows = pto::kernels::shapes::kMemoryRows;
constexpr int kCols = pto::kernels::shapes::kMemoryCols;
constexpr int kElems = kRows * kCols;

float x[kElems];
float y[kElems];
float z[kElems];

static inline unsigned int f32_bits(float value) {
  union {
    float f;
    unsigned int u;
  } bits;
  bits.f = value;
  return bits.u;
}

static inline float f32_from_bits(unsigned int value) {
  union {
    unsigned int u;
    float f;
  } bits;
  bits.u = value;
  return bits.f;
}

static inline unsigned int f32_bits_from_u32(unsigned int value) {
  static constexpr unsigned int kSmallValueBits[] = {
      0x00000000U, 0x3f800000U, 0x40000000U, 0x40400000U,
      0x40800000U, 0x40a00000U, 0x40c00000U, 0x40e00000U,
      0x41000000U, 0x41100000U, 0x41200000U, 0x41300000U,
      0x41400000U, 0x41500000U, 0x41600000U, 0x41700000U,
      0x41800000U, 0x41880000U, 0x41900000U, 0x41980000U,
      0x41a00000U, 0x41a80000U, 0x41b00000U, 0x41b80000U,
      0x41c00000U, 0x41c80000U, 0x41d00000U, 0x41d80000U,
      0x41e00000U, 0x41e80000U, 0x41f00000U, 0x41f80000U,
  };
  if (value < (sizeof(kSmallValueBits) / sizeof(kSmallValueBits[0]))) {
    return kSmallValueBits[value];
  }
  if (value == 0) {
    return 0;
  }
  int msb = 31;
  while (((value >> msb) & 1U) == 0) {
    --msb;
  }
  unsigned int mantissa = 0;
  if (msb >= 23) {
    mantissa = value >> (msb - 23);
  } else {
    mantissa = value << (23 - msb);
  }
  return (static_cast<unsigned int>(msb + 127) << 23) | (mantissa & 0x007fffffU);
}

static inline unsigned int u32_from_f32_bits(unsigned int bits) {
  if ((bits & 0x7fffffffU) == 0) {
    return 0;
  }
  const unsigned int exponent = (bits >> 23) & 0xffU;
  const unsigned int mantissa = (bits & 0x007fffffU) | 0x00800000U;
  const int shift = static_cast<int>(exponent) - 127 - 23;
  return shift >= 0 ? (mantissa << shift) : (mantissa >> -shift);
}

static inline unsigned int x_int(int i) {
  return static_cast<unsigned int>((i % 13) + 1);
}

static inline unsigned int y_int(int i) {
  return static_cast<unsigned int>(((i / 7) % 11) + (i & 1));
}

static inline float make_input(unsigned int value) {
  return f32_from_bits(f32_bits_from_u32(value));
}

static inline __attribute__((noreturn)) void linx_pto_exit(unsigned int code) {
  if (code == 0) {
    __asm__ volatile(
        "BSTART.STD\n"
        "lui 65545, ->u\n"
        "lui 5, ->t\n"
        "addi t#1, 1365, ->t\n"
        "c.swi t#1, [u#1, 0]\n"
        "BSTOP\n"
        ::: "memory");
  } else {
    __asm__ volatile(
        "BSTART.STD\n"
        "lui 65545, ->u\n"
        "lui 19, ->t\n"
        "addi t#1, 819, ->t\n"
        "c.swi t#1, [u#1, 0]\n"
        "BSTOP\n"
        ::: "memory");
  }
  while (1) {
    __asm__ volatile("" ::: "memory");
  }
}

} // namespace

extern "C" float __addsf3(float a, float b) {
  const unsigned int a_int = u32_from_f32_bits(f32_bits(a));
  const unsigned int b_int = u32_from_f32_bits(f32_bits(b));
  return f32_from_bits(f32_bits_from_u32(a_int + b_int));
}

int main() {
  for (int i = 0; i < kElems; ++i) {
    x[i] = make_input(x_int(i));
    y[i] = make_input(y_int(i));
    z[i] = make_input(0);
  }

  add_custom_f32(x, y, z);

  for (int i = 0; i < kElems; ++i) {
    const unsigned int expected = f32_bits_from_u32(x_int(i) + y_int(i));
    if (f32_bits(z[i]) != expected) {
      return 1;
    }
  }
  return 0;
}

extern "C" __attribute__((noreturn, section(".text._start"))) void _start(void) {
  linx_pto_exit(static_cast<unsigned int>(main()));
}
"""
SUPER_SMOKE_TESTCASES = {"TAdd", "MatMul"}
PTO_HARNESS_SOURCES: dict[str, tuple[str, str]] = {
    "tload_store_i32": ("pto-tload-store-harness.cpp", PTO_TLOAD_STORE_HARNESS_SOURCE),
    "gemm_i32": ("pto-gemm-i32-harness.cpp", PTO_GEMM_I32_HARNESS_SOURCE),
    "gemm_basic_f32": (
        "pto-gemm-basic-f32-harness.cpp",
        PTO_GEMM_BASIC_F32_HARNESS_SOURCE,
    ),
    "gemm_demo_f32": (
        "pto-gemm-demo-f32-harness.cpp",
        PTO_GEMM_DEMO_F32_HARNESS_SOURCE,
    ),
    "gemm_performance_f32": (
        "pto-gemm-performance-f32-harness.cpp",
        PTO_GEMM_PERFORMANCE_F32_HARNESS_SOURCE,
    ),
    "gemm_reuse_a_f16": (
        "pto-gemm-reuse-a-f16-harness.cpp",
        PTO_GEMM_REUSE_A_FP16_HARNESS_SOURCE,
    ),
    "gemm_reuse_b_f16": (
        "pto-gemm-reuse-b-f16-harness.cpp",
        PTO_GEMM_REUSE_B_FP16_HARNESS_SOURCE,
    ),
    "gemm_reuse_ab_f16": (
        "pto-gemm-reuse-ab-f16-harness.cpp",
        PTO_GEMM_REUSE_AB_FP16_HARNESS_SOURCE,
    ),
    "mamulb_i32": ("pto-mamulb-i32-harness.cpp", PTO_MAMULB_I32_HARNESS_SOURCE),
    "tmatmul_acc_i32": (
        "pto-tmatmul-acc-i32-harness.cpp",
        PTO_TMATMUL_ACC_I32_HARNESS_SOURCE,
    ),
    "relu_f32": ("pto-relu-f32-harness.cpp", PTO_RELU_F32_HARNESS_SOURCE),
    "flatten_f32": ("pto-flatten-f32-harness.cpp", PTO_FLATTEN_F32_HARNESS_SOURCE),
    "reshape_f32": ("pto-reshape-f32-harness.cpp", PTO_RESHAPE_F32_HARNESS_SOURCE),
    "squeeze_f32": ("pto-squeeze-f32-harness.cpp", PTO_SQUEEZE_F32_HARNESS_SOURCE),
    "unsqueeze_f32": (
        "pto-unsqueeze-f32-harness.cpp",
        PTO_UNSQUEEZE_F32_HARNESS_SOURCE,
    ),
    "concat_f32": ("pto-concat-f32-harness.cpp", PTO_CONCAT_F32_HARNESS_SOURCE),
    "split_f32": ("pto-split-f32-harness.cpp", PTO_SPLIT_F32_HARNESS_SOURCE),
    "stack_f32": ("pto-stack-f32-harness.cpp", PTO_STACK_F32_HARNESS_SOURCE),
    "slice_f32": ("pto-slice-f32-harness.cpp", PTO_SLICE_F32_HARNESS_SOURCE),
    "gather_f32": ("pto-gather-f32-harness.cpp", PTO_GATHER_F32_HARNESS_SOURCE),
    "scatter_f32": ("pto-scatter-f32-harness.cpp", PTO_SCATTER_F32_HARNESS_SOURCE),
    "where_f32": ("pto-where-f32-harness.cpp", PTO_WHERE_F32_HARNESS_SOURCE),
    "argmax_f32": ("pto-argmax-f32-harness.cpp", PTO_ARGMAX_F32_HARNESS_SOURCE),
    "unique_i32": ("pto-unique-i32-harness.cpp", PTO_UNIQUE_I32_HARNESS_SOURCE),
    "hash_table_insert_f32": (
        "pto-hash-table-insert-f32-harness.cpp",
        PTO_HASH_TABLE_INSERT_F32_HARNESS_SOURCE,
    ),
    "hash_table_lookup_f32": (
        "pto-hash-table-lookup-f32-harness.cpp",
        PTO_HASH_TABLE_LOOKUP_F32_HARNESS_SOURCE,
    ),
    "unsorted_segment_sum_f32": (
        "pto-unsorted-segment-sum-f32-harness.cpp",
        PTO_UNSORTED_SEGMENT_SUM_F32_HARNESS_SOURCE,
    ),
    "permute_nhwc_nchw_f32": (
        "pto-permute-nhwc-nchw-f32-harness.cpp",
        PTO_PERMUTE_NHWC_NCHW_F32_HARNESS_SOURCE,
    ),
    "transpose_large_f32": (
        "pto-transpose-large-f32-harness.cpp",
        PTO_TRANSPOSE_LARGE_F32_HARNESS_SOURCE,
    ),
    "add_custom_f32": (
        "pto-add-custom-f32-harness.cpp",
        PTO_ADD_CUSTOM_F32_HARNESS_SOURCE,
    ),
}
PTO_STANDALONE_HARNESSES: dict[str, dict[str, Any]] = {
    "elementwise/add_custom.cpp": {
        "standalone_harness": "add_custom_f32",
        "harness_profile": "qemu_smoke",
        "compile_defines": ["-DPTO_QEMU_SMOKE=1"],
        "expected": "PTO add_custom_f32 standalone smoke ELF passes QEMU then gfsim",
        "description": "PTO catalog float32 add_custom direct-boot smoke harness",
    },
    "elementwise/relu_fp32.cpp": {
        "standalone_harness": "relu_f32",
        "harness_profile": "qemu_smoke",
        "compile_defines": ["-DPTO_QEMU_SMOKE=1"],
        "expected": "PTO relu_f32 standalone smoke ELF passes QEMU then gfsim",
        "description": "PTO catalog float32 ReLU direct-boot smoke harness",
    },
    "layout/flatten_fp32.cpp": {
        "standalone_harness": "flatten_f32",
        "harness_profile": "qemu_smoke",
        "compile_defines": ["-DPTO_QEMU_SMOKE=1"],
        "expected": "PTO flatten_f32 standalone smoke ELF passes QEMU then gfsim",
        "description": "PTO catalog float32 flatten direct-boot smoke harness",
    },
    "layout/reshape_fp32.cpp": {
        "standalone_harness": "reshape_f32",
        "harness_profile": "qemu_smoke",
        "compile_defines": ["-DPTO_QEMU_SMOKE=1"],
        "expected": "PTO reshape_f32 standalone smoke ELF passes QEMU then gfsim",
        "description": "PTO catalog float32 reshape direct-boot smoke harness",
    },
    "layout/squeeze_fp32.cpp": {
        "standalone_harness": "squeeze_f32",
        "harness_profile": "qemu_smoke",
        "compile_defines": ["-DPTO_QEMU_SMOKE=1"],
        "expected": "PTO squeeze_f32 standalone smoke ELF passes QEMU then gfsim",
        "description": "PTO catalog float32 squeeze direct-boot smoke harness",
    },
    "layout/unsqueeze_fp32.cpp": {
        "standalone_harness": "unsqueeze_f32",
        "harness_profile": "qemu_smoke",
        "compile_defines": ["-DPTO_QEMU_SMOKE=1"],
        "expected": "PTO unsqueeze_f32 standalone smoke ELF passes QEMU then gfsim",
        "description": "PTO catalog float32 unsqueeze direct-boot smoke harness",
    },
    "layout/concat_fp32.cpp": {
        "standalone_harness": "concat_f32",
        "harness_profile": "qemu_smoke",
        "compile_defines": ["-DPTO_QEMU_SMOKE=1"],
        "expected": "PTO concat_f32 standalone smoke ELF passes QEMU then gfsim",
        "description": "PTO catalog float32 concat direct-boot smoke harness",
    },
    "layout/split_fp32.cpp": {
        "standalone_harness": "split_f32",
        "harness_profile": "qemu_smoke",
        "compile_defines": ["-DPTO_QEMU_SMOKE=1"],
        "expected": "PTO split_f32 standalone smoke ELF passes QEMU then gfsim",
        "description": "PTO catalog float32 split direct-boot smoke harness",
    },
    "layout/stack_fp32.cpp": {
        "standalone_harness": "stack_f32",
        "harness_profile": "qemu_smoke",
        "compile_defines": ["-DPTO_QEMU_SMOKE=1"],
        "expected": "PTO stack_f32 standalone smoke ELF passes QEMU then gfsim",
        "description": "PTO catalog float32 stack direct-boot smoke harness",
    },
    "layout/permute_nhwc_nchw_fp32.cpp": {
        "standalone_harness": "permute_nhwc_nchw_f32",
        "harness_profile": "qemu_smoke",
        "compile_defines": ["-DPTO_QEMU_SMOKE=1"],
        "expected": "PTO permute_nhwc_nchw_f32 standalone smoke ELF passes QEMU then gfsim",
        "description": "PTO catalog float32 NHWC-to-NCHW permute direct-boot smoke harness",
    },
    "layout/transpose_large_fp32.cpp": {
        "standalone_harness": "transpose_large_f32",
        "harness_profile": "qemu_smoke",
        "compile_defines": ["-DPTO_QEMU_SMOKE=1"],
        "expected": "PTO transpose_large_f32 standalone smoke ELF passes QEMU then gfsim",
        "description": "PTO catalog float32 large transpose direct-boot smoke harness",
    },
    "indexing/argmax_fp32.cpp": {
        "standalone_harness": "argmax_f32",
        "harness_profile": "qemu_smoke",
        "compile_defines": ["-DPTO_QEMU_SMOKE=1"],
        "expected": "PTO argmax_f32 standalone smoke ELF passes QEMU then gfsim",
        "description": "PTO catalog float32 argmax model-lane maturity harness",
    },
    "indexing/hash_table_insert_fp32.cpp": {
        "standalone_harness": "hash_table_insert_f32",
        "harness_profile": "qemu_smoke",
        "compile_defines": ["-DPTO_QEMU_SMOKE=1"],
        "expected": "PTO hash_table_insert_f32 standalone smoke ELF passes QEMU then gfsim",
        "description": "PTO catalog float32 hash-table insert direct-boot smoke harness",
    },
    "indexing/hash_table_lookup_fp32.cpp": {
        "standalone_harness": "hash_table_lookup_f32",
        "harness_profile": "qemu_smoke",
        "compile_defines": ["-DPTO_QEMU_SMOKE=1"],
        "expected": "PTO hash_table_lookup_f32 standalone smoke ELF passes QEMU then gfsim",
        "description": "PTO catalog float32 hash-table lookup direct-boot smoke harness",
    },
    "indexing/gather_fp32.cpp": {
        "standalone_harness": "gather_f32",
        "harness_profile": "qemu_smoke",
        "compile_defines": ["-DPTO_QEMU_SMOKE=1"],
        "expected": "PTO gather_f32 standalone smoke ELF passes QEMU then gfsim",
        "description": "PTO catalog float32 gather direct-boot smoke harness",
    },
    "indexing/scatter_fp32.cpp": {
        "standalone_harness": "scatter_f32",
        "harness_profile": "qemu_smoke",
        "compile_defines": ["-DPTO_QEMU_SMOKE=1"],
        "expected": "PTO scatter_f32 standalone smoke ELF passes QEMU then gfsim",
        "description": "PTO catalog float32 scatter direct-boot smoke harness",
    },
    "indexing/slice_fp32.cpp": {
        "standalone_harness": "slice_f32",
        "harness_profile": "qemu_smoke",
        "compile_defines": ["-DPTO_QEMU_SMOKE=1"],
        "expected": "PTO slice_f32 standalone smoke ELF passes QEMU then gfsim",
        "description": "PTO catalog float32 slice direct-boot smoke harness",
    },
    "indexing/unique_i32.cpp": {
        "standalone_harness": "unique_i32",
        "harness_profile": "qemu_smoke",
        "compile_defines": ["-DPTO_QEMU_SMOKE=1"],
        "expected": "PTO unique_i32 standalone smoke ELF passes QEMU then gfsim",
        "description": "PTO catalog int32 unique model-lane maturity harness",
    },
    "indexing/unsorted_segment_sum_fp32.cpp": {
        "standalone_harness": "unsorted_segment_sum_f32",
        "harness_profile": "qemu_smoke",
        "compile_defines": ["-DPTO_QEMU_SMOKE=1"],
        "expected": "PTO unsorted_segment_sum_f32 standalone smoke ELF passes QEMU then gfsim",
        "description": "PTO catalog float32 unsorted segment sum direct-boot smoke harness",
    },
    "indexing/where_fp32.cpp": {
        "standalone_harness": "where_f32",
        "harness_profile": "qemu_smoke",
        "compile_defines": ["-DPTO_QEMU_SMOKE=1"],
        "expected": "PTO where_f32 standalone smoke ELF passes QEMU then gfsim",
        "description": "PTO catalog float32 where direct-boot smoke harness",
    },
    "memory/tload_store.cpp": {
        "standalone_harness": "tload_store_i32",
        "harness_profile": "qemu_smoke",
        "compile_defines": ["-DPTO_QEMU_SMOKE=1"],
        "expected": "PTO tload_store standalone smoke ELF passes QEMU then gfsim",
        "description": "PTO catalog tload_store direct-boot smoke harness",
    },
    "matmul/gemm.cpp": {
        "standalone_harness": "gemm_i32",
        "harness_profile": "qemu_smoke",
        "compile_defines": ["-DPTO_QEMU_SMOKE=1"],
        "expected": "PTO gemm_i32 standalone smoke ELF passes QEMU then gfsim",
        "description": "PTO catalog int32 GEMM direct-boot smoke harness",
    },
    "matmul/gemm_basic.cpp": {
        "standalone_harness": "gemm_basic_f32",
        "harness_profile": "qemu_smoke",
        "compile_defines": ["-DPTO_QEMU_SMOKE=1"],
        "expected": "PTO gemm_basic_f32 standalone smoke ELF passes QEMU then gfsim",
        "description": "PTO catalog float32 GEMM basic direct-boot smoke harness",
    },
    "matmul/gemm_demo.cpp": {
        "standalone_harness": "gemm_demo_f32",
        "harness_profile": "qemu_smoke",
        "compile_defines": ["-DPTO_QEMU_SMOKE=1"],
        "expected": "PTO gemm_demo_f32 standalone smoke ELF passes QEMU then gfsim",
        "description": "PTO catalog float32 GEMM demo direct-boot smoke harness",
    },
    "matmul/gemm_performance.cpp": {
        "standalone_harness": "gemm_performance_f32",
        "harness_profile": "qemu_smoke",
        "compile_defines": ["-DPTO_QEMU_SMOKE=1"],
        "expected": "PTO gemm_performance_f32 standalone smoke ELF passes QEMU then gfsim",
        "description": "PTO catalog float32 GEMM performance repeat direct-boot smoke harness",
    },
    "matmul/gemm_reuse_a_fp16.cpp": {
        "standalone_harness": "gemm_reuse_a_f16",
        "harness_profile": "qemu_smoke",
        "compile_defines": ["-DPTO_QEMU_SMOKE=1"],
        "expected": "PTO gemm_reuse_a_f16 standalone smoke ELF passes QEMU then gfsim",
        "description": "PTO catalog fp16 GEMM reuse-A direct-boot smoke harness",
    },
    "matmul/gemm_reuse_b_fp16.cpp": {
        "standalone_harness": "gemm_reuse_b_f16",
        "harness_profile": "qemu_smoke",
        "compile_defines": ["-DPTO_QEMU_SMOKE=1"],
        "expected": "PTO gemm_reuse_b_f16 standalone smoke ELF passes QEMU then gfsim",
        "description": "PTO catalog fp16 GEMM reuse-B direct-boot smoke harness",
    },
    "matmul/gemm_reuse_ab_fp16.cpp": {
        "standalone_harness": "gemm_reuse_ab_f16",
        "harness_profile": "qemu_smoke",
        "compile_defines": ["-DPTO_QEMU_SMOKE=1"],
        "expected": "PTO gemm_reuse_ab_f16 standalone smoke ELF passes QEMU then gfsim",
        "description": "PTO catalog fp16 GEMM blocked reuse-A/B direct-boot smoke harness",
    },
    "matmul/mamulb.cpp": {
        "standalone_harness": "mamulb_i32",
        "harness_profile": "qemu_smoke",
        "compile_defines": ["-DPTO_QEMU_SMOKE=1"],
        "expected": "PTO mamulb_i32 standalone smoke ELF passes QEMU then gfsim",
        "description": "PTO catalog int32 MAMULB direct-boot smoke harness",
    },
    "matmul/tmatmul_acc.cpp": {
        "standalone_harness": "tmatmul_acc_i32",
        "harness_profile": "qemu_smoke",
        "compile_defines": ["-DPTO_QEMU_SMOKE=1"],
        "expected": "PTO tmatmul_acc_i32 standalone smoke ELF passes QEMU then gfsim",
        "description": "PTO catalog int32 TMATMUL.ACC direct-boot smoke harness",
    }
}


@dataclasses.dataclass
class Case:
    id: str
    kind: str
    suite: str
    tier: int
    source_paths: list[Path]
    manifest_path: Path | None
    workdir: Path
    compile_command: str | list[str] | None
    qemu_command: str | list[str] | None
    model_eligible: bool
    produces_elf: bool
    expected: str
    metadata: dict[str, Any]


@dataclasses.dataclass
class CaseState:
    case: Case
    case_dir: Path
    stages: dict[str, dict[str, Any]] = dataclasses.field(default_factory=dict)
    artifacts: dict[str, str] = dataclasses.field(default_factory=dict)
    qemu_digests: dict[str, str] = dataclasses.field(default_factory=dict)
    model_digests: dict[str, str] = dataclasses.field(default_factory=dict)
    failure_stage: str | None = None
    failure_owner: str | None = None
    failure_evidence: str | None = None


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def default_run_id() -> str:
    return datetime.now(timezone.utc).strftime("ai-%Y%m%d-%H%M%S")


def default_flow_path(root: Path) -> Path:
    return root / "docs" / "bringup" / "ai_workload_bringup_flow.json"


def relpath(root: Path, path: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return str(path)


def slug(text: str) -> str:
    text = re.sub(r"[^A-Za-z0-9_.-]+", "-", text.strip())
    text = text.strip("-._")
    return text or "case"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fp:
        for chunk in iter(lambda: fp.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def read_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"error: invalid JSON {path}: {exc}") from exc


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def executable(path: Path) -> bool:
    return path.is_file() and os.access(path, os.X_OK)


def submodule_sha(root: Path, rel: str) -> str | None:
    path = root / rel
    if not path.exists():
        return None
    try:
        return subprocess.check_output(
            ["git", "-C", str(path), "rev-parse", "HEAD"],
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
    except (OSError, subprocess.CalledProcessError):
        return None


def load_flow(path: Path) -> dict[str, Any]:
    data = read_json(path)
    if data.get("schema_version") != 1:
        raise SystemExit(f"error: unsupported flow schema_version in {path}")
    profiles = data.get("profiles")
    if not isinstance(profiles, dict) or not profiles:
        raise SystemExit(f"error: flow has no profiles: {path}")
    stages = data.get("stages")
    if not isinstance(stages, list) or not stages:
        raise SystemExit(f"error: flow has no stages: {path}")
    stage_ids: set[str] = set()
    for stage in stages:
        if not isinstance(stage, dict):
            raise SystemExit("error: each stage must be an object")
        stage_id = str(stage.get("id", "")).strip()
        if not stage_id:
            raise SystemExit("error: stage missing id")
        if stage_id in stage_ids:
            raise SystemExit(f"error: duplicate stage id: {stage_id}")
        stage_ids.add(stage_id)
        stage_profiles = stage.get("profiles")
        if not isinstance(stage_profiles, list) or not stage_profiles:
            raise SystemExit(f"error: stage {stage_id} missing profiles")
        invalid = sorted(str(p) for p in stage_profiles if p not in profiles)
        if invalid:
            raise SystemExit(
                f"error: stage {stage_id} has invalid profiles: {', '.join(invalid)}"
            )
    return data


def selected_stages(
    flow: dict[str, Any],
    profile: str,
    requested: list[str],
    start_at: str | None,
    stop_after: str | None,
) -> list[dict[str, Any]]:
    if profile not in flow["profiles"]:
        raise SystemExit(
            "error: invalid --profile "
            f"{profile}; choose one of {', '.join(sorted(flow['profiles']))}"
        )
    stages = [
        stage
        for stage in flow["stages"]
        if profile in {str(p) for p in stage.get("profiles", [])}
    ]
    if requested:
        wanted = set(requested)
        stages = [stage for stage in stages if stage["id"] in wanted]
        missing = sorted(wanted - {stage["id"] for stage in stages})
        if missing:
            raise SystemExit(
                "error: requested stage is not enabled for profile "
                f"{profile}: {', '.join(missing)}"
            )
    if start_at:
        ids = [stage["id"] for stage in stages]
        if start_at not in ids:
            raise SystemExit(f"error: --start-at stage not selected: {start_at}")
        stages = stages[ids.index(start_at) :]
    if stop_after:
        ids = [stage["id"] for stage in stages]
        if stop_after not in ids:
            raise SystemExit(f"error: --stop-after stage not selected: {stop_after}")
        stages = stages[: ids.index(stop_after) + 1]
    return stages


def profile_tiers(flow: dict[str, Any], profile: str, override: list[int]) -> set[int]:
    if override:
        return set(override)
    raw = flow["profiles"][profile].get("tiers", [])
    if not isinstance(raw, list) or not raw:
        raise SystemExit(f"error: profile {profile} has no tier list")
    return {int(t) for t in raw}


def parse_compile_all_line(line: str) -> tuple[str, dict[str, str]] | None:
    stripped = line.strip()
    if not stripped or stripped.startswith("#"):
        return None
    parts = [part.strip() for part in stripped.split(";") if part.strip()]
    if not parts:
        return None
    command = parts[-1]
    try:
        tokens = shlex.split(command)
    except ValueError:
        return None
    if not tokens or tokens[0] != "make":
        return None
    vars_out: dict[str, str] = {}
    for token in tokens[1:]:
        if "=" not in token:
            continue
        key, value = token.split("=", 1)
        vars_out[key] = value
    testcase = vars_out.get("TESTCASE")
    if not testcase:
        return None
    return command, vars_out


def supernpu_tier(suite_rel: str, make_vars: dict[str, str]) -> int:
    testcase = make_vars.get("TESTCASE", "")
    if suite_rel == "tileop_api" and testcase in SUPER_SMOKE_TESTCASES:
        return 0
    if suite_rel in {"tileop_api", "other/tileop_api"}:
        return 1
    if suite_rel == "other/tileop_test":
        return 2
    if suite_rel == "kernel/control":
        extra_defines = make_vars.get("EXTRA_DEFINES", "")
        if (
            testcase == "hashtable_lookup_simt"
            and "-DkNum=16" in extra_defines
            and "-DLINX_HT_DIRECT=1" in extra_defines
            and "-DFOR_GFSIM" in extra_defines
        ):
            return 1
        return 2
    if suite_rel.startswith("other/deepseek"):
        return 3
    if suite_rel.startswith("kernel/fusion"):
        return 3
    if suite_rel.startswith("kernel/gemm") or suite_rel.startswith("accelerator/"):
        return 2
    if suite_rel.startswith("kernel/memory") or suite_rel.startswith("kernel/reduction"):
        return 2
    if suite_rel.startswith("kernel/"):
        return 2
    if "py_api" in suite_rel:
        return 3
    return 4


def pto_kernel_tier(rel: str) -> int:
    if "deepseek" in rel:
        return 3
    family = rel.split("/", 1)[0]
    if family in {"memory", "matmul", "elementwise"}:
        return 1
    if family in {"attention", "normalization", "routing", "decode"}:
        return 3
    if family in {"indexing", "layout"}:
        return 2
    return 4


def supernpu_test_root(root: Path) -> Path:
    """Return the sole supported SuperNPUBench test root."""
    return (
        root
        / "workloads"
        / "SuperNPUBench"
        / "benchmark"
        / "two-level-arch"
        / "test"
    )


def supernpu_elf_path(root: Path, suite_dir: Path, make_vars: dict[str, str]) -> Path:
    bench_root = root / "workloads" / "SuperNPUBench"
    test_root = supernpu_test_root(root)
    suite_rel = suite_dir.relative_to(test_root).as_posix()
    category_name = suite_rel.replace("/", "_")
    testcase = make_vars["TESTCASE"]
    output_root = bench_root / "benchmark" / "two-level-arch" / "output"
    return output_root / suite_rel / "elf" / f"{category_name}_{testcase}_linx.elf"


def supernpu_elf_dir(root: Path, suite_dir: Path) -> Path:
    bench_root = root / "workloads" / "SuperNPUBench"
    test_root = supernpu_test_root(root)
    suite_rel = suite_dir.relative_to(test_root).as_posix()
    return bench_root / "benchmark" / "two-level-arch" / "output" / suite_rel / "elf"


def _norm_key(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", text.lower())


def supernpu_source_keys(make_vars: dict[str, str]) -> list[str]:
    keys: list[str] = []
    for name in ("TYPE", "TESTCASE"):
        value = make_vars.get(name, "").strip()
        if value and value not in keys:
            keys.append(value)
    return keys


def existing_path_with_actual_case(candidate: Path) -> Path | None:
    if not candidate.exists():
        return None
    parent = candidate.parent
    if not parent.exists():
        return candidate
    for child in parent.iterdir():
        if child.name == candidate.name:
            return child
    norm_name = _norm_key(candidate.name)
    matches = [child for child in parent.iterdir() if _norm_key(child.name) == norm_name]
    if len(matches) == 1:
        return matches[0]
    return candidate


def supernpu_source_paths(suite_dir: Path, make_vars: dict[str, str]) -> list[Path]:
    source_keys = supernpu_source_keys(make_vars)
    candidates = []
    for key in source_keys:
        candidates.extend(
            [
                suite_dir / "src" / f"{key}.cpp",
                suite_dir / key / f"{key}.cpp",
                suite_dir / f"{key}.cpp",
            ]
        )
    for candidate in candidates:
        existing = existing_path_with_actual_case(candidate)
        if existing is not None:
            return [existing]

    cpp_files = sorted(suite_dir.rglob("*.cpp"))
    for source_key in source_keys:
        norm_source_key = _norm_key(source_key)
        matching = [
            path
            for path in cpp_files
            if _norm_key(path.stem) == norm_source_key
            or _norm_key(path.stem) in norm_source_key
            or norm_source_key in _norm_key(path.stem)
        ]
        if matching:
            return [matching[0]]

    src_dir = suite_dir / "src"
    src_cpp_files = sorted(src_dir.rglob("*.cpp")) if src_dir.exists() else []
    if len(src_cpp_files) == 1:
        return [src_cpp_files[0]]

    return [suite_dir / "src" / f"{make_vars['TESTCASE']}.cpp"]


def snapshot_elf_mtimes(elf_dir: Path) -> dict[Path, float]:
    if not elf_dir.exists():
        return {}
    return {path: path.stat().st_mtime for path in elf_dir.glob("*.elf") if path.is_file()}


def find_supernpu_elf_after_compile(
    case: Case,
    root: Path,
    before: dict[Path, float],
    *,
    elf_dir: Path | None = None,
) -> Path | None:
    expected = Path(case.metadata["elf"])
    if elf_dir is not None:
        expected = elf_dir / expected.name
    elif not expected.is_absolute():
        expected = root / expected
    if expected.exists():
        return expected

    if elf_dir is None:
        elf_dir = Path(case.metadata.get("elf_dir", ""))
        if not elf_dir.is_absolute():
            elf_dir = root / elf_dir
    if not elf_dir.exists():
        return None
    candidates = [path for path in elf_dir.glob("*.elf") if path.is_file()]
    if not candidates:
        return None
    produced = [
        path
        for path in candidates
        if path not in before or path.stat().st_mtime > before[path]
    ]
    if produced:
        return max(produced, key=lambda path: path.stat().st_mtime)
    return max(candidates, key=lambda path: path.stat().st_mtime)


def discover_cases(root: Path) -> list[Case]:
    cases: list[Case] = []

    qemu_tests = root / "avs" / "qemu" / "tests"
    cases.append(
        Case(
            id="avs-tile-smoke",
            kind="avs_pto",
            suite="tile",
            tier=0,
            source_paths=[qemu_tests / "10_tile_compile_smoke.cpp"],
            manifest_path=root / "avs" / "qemu" / "run_tests.py",
            workdir=root,
            compile_command=None,
            qemu_command=None,
            model_eligible=True,
            produces_elf=True,
            expected="QEMU PASS marker, then gfsim exit 0",
            metadata={
                "avs_suite": "tile",
                "avs_source_profile": "compile-smoke",
                "description": "PTO tile direct-boot compile-smoke source",
            },
        )
    )
    cases.append(
        Case(
            id="avs-pto-parity-smoke",
            kind="avs_pto",
            suite="pto_parity",
            tier=0,
            source_paths=[qemu_tests / "16_pto_kernel_parity.cpp"],
            manifest_path=root / "avs" / "qemu" / "run_tests.py",
            workdir=root,
            compile_command=None,
            qemu_command=None,
            model_eligible=True,
            produces_elf=True,
            expected="tload_store PTO_DIGEST parity stage under QEMU, then gfsim exit 0",
            metadata={
                "avs_suite": "pto_parity",
                "avs_extra_cflags": ["-DPTO_PARITY_TLOAD_STORE_ONLY=1"],
                "description": "PTO parity tload_store direct-boot smoke case",
            },
        )
    )
    cases.append(
        Case(
            id="avs-pto-parity-prefix-gemm-performance",
            kind="avs_pto",
            suite="pto_parity",
            tier=1,
            source_paths=[qemu_tests / "16_pto_kernel_parity.cpp"],
            manifest_path=root / "avs" / "qemu" / "run_tests.py",
            workdir=root,
            compile_command=None,
            qemu_command=None,
            model_eligible=True,
            produces_elf=True,
            expected="PTO parity prefix through gemm_performance under QEMU, then gfsim exit 0",
            metadata={
                "avs_suite": "pto_parity",
                "avs_extra_cflags": [
                    "-DPTO_PARITY_FAST_F32_SEED=1",
                    "-DPTO_PARITY_FAST_FP16_SEED=1",
                    "-DPTO_PARITY_STOP_AFTER_STAGE=PTO_PARITY_STAGE_GEMM_PERFORMANCE",
                ],
                "description": "PTO parity direct-boot prefix boundary before float-helper model maturity targets",
            },
        )
    )
    cases.append(
        Case(
            id="avs-pto-parity-prefix-flash-attention",
            kind="avs_pto",
            suite="pto_parity",
            tier=1,
            source_paths=[qemu_tests / "16_pto_kernel_parity.cpp"],
            manifest_path=root / "avs" / "qemu" / "run_tests.py",
            workdir=root,
            compile_command=None,
            qemu_command=None,
            model_eligible=True,
            produces_elf=True,
            expected="PTO parity prefix through flash_attention under QEMU, then gfsim exit 0",
            metadata={
                "avs_suite": "pto_parity",
                "avs_extra_cflags": [
                    "-DPTO_PARITY_FAST_F32_SEED=1",
                    "-DPTO_PARITY_FAST_FP16_SEED=1",
                    "-DPTO_PARITY_STOP_AFTER_STAGE=PTO_PARITY_STAGE_FLASH_ATTENTION",
                ],
                "description": "PTO parity direct-boot prefix boundary through flash_attention before flash_attention_softmax model maturity",
            },
        )
    )
    cases.append(
        Case(
            id="avs-pto-parity-prefix-flash-attention-softmax",
            kind="avs_pto",
            suite="pto_parity",
            tier=1,
            source_paths=[qemu_tests / "16_pto_kernel_parity.cpp"],
            manifest_path=root / "avs" / "qemu" / "run_tests.py",
            workdir=root,
            compile_command=None,
            qemu_command=None,
            model_eligible=True,
            produces_elf=True,
            expected="PTO parity prefix through flash_attention_softmax under QEMU, then gfsim exit 0",
            metadata={
                "avs_suite": "pto_parity",
                "avs_extra_cflags": [
                    "-DPTO_PARITY_FAST_F32_SEED=1",
                    "-DPTO_PARITY_FAST_FP16_SEED=1",
                    "-DPTO_ATTENTION_SMOKE_SEQ=1",
                    "-DPTO_ATTENTION_LARGE_SMOKE_SEQ=1",
                    "-DPTO_ATTENTION_SMOKE_QD=1",
                    "-DPTO_ATTENTION_SMOKE_VD=1",
                    "-DPTO_ATTENTION_SMALL_SMOKE_QD=1",
                    "-DPTO_FLASH_TILE_M=1",
                    "-DPTO_FLASH_TILE_K=1",
                    "-DPTO_PARITY_STOP_AFTER_STAGE=PTO_PARITY_STAGE_FLASH_ATTENTION_SOFTMAX",
                ],
                "description": "PTO parity direct-boot 1x attention micro-profile through flash_attention_softmax before masked attention model maturity",
            },
        )
    )
    cases.append(
        Case(
            id="avs-pto-parity-prefix-flash-attention-softmax-2x",
            kind="avs_pto",
            suite="pto_parity",
            tier=1,
            source_paths=[qemu_tests / "16_pto_kernel_parity.cpp"],
            manifest_path=root / "avs" / "qemu" / "run_tests.py",
            workdir=root,
            compile_command=None,
            qemu_command=None,
            model_eligible=True,
            produces_elf=True,
            expected="PTO parity 2x prefix through flash_attention_softmax under QEMU, then gfsim exit 0",
            metadata={
                "avs_suite": "pto_parity",
                "avs_extra_cflags": [
                    "-DPTO_PARITY_FAST_F32_SEED=1",
                    "-DPTO_PARITY_FAST_FP16_SEED=1",
                    "-DPTO_ATTENTION_SMOKE_SEQ=2",
                    "-DPTO_ATTENTION_LARGE_SMOKE_SEQ=2",
                    "-DPTO_ATTENTION_SMOKE_QD=2",
                    "-DPTO_ATTENTION_SMOKE_VD=2",
                    "-DPTO_ATTENTION_SMALL_SMOKE_QD=2",
                    "-DPTO_FLASH_TILE_M=1",
                    "-DPTO_FLASH_TILE_K=1",
                    "-DPTO_PARITY_STOP_AFTER_STAGE=PTO_PARITY_STAGE_FLASH_ATTENTION_SOFTMAX",
                ],
                "description": "PTO parity direct-boot 2x attention micro-profile through flash_attention_softmax between the 1x proof and full-row model closure",
            },
        )
    )
    cases.append(
        Case(
            id="avs-pto-parity-prefix-flash-attention-masked",
            kind="avs_pto",
            suite="pto_parity",
            tier=1,
            source_paths=[qemu_tests / "16_pto_kernel_parity.cpp"],
            manifest_path=root / "avs" / "qemu" / "run_tests.py",
            workdir=root,
            compile_command=None,
            qemu_command=None,
            model_eligible=True,
            produces_elf=True,
            expected="PTO parity prefix through flash_attention_masked under QEMU, then gfsim exit 0",
            metadata={
                "avs_suite": "pto_parity",
                "avs_extra_cflags": [
                    "-DPTO_PARITY_FAST_F32_SEED=1",
                    "-DPTO_PARITY_FAST_FP16_SEED=1",
                    "-DPTO_ATTENTION_SMOKE_SEQ=1",
                    "-DPTO_ATTENTION_LARGE_SMOKE_SEQ=1",
                    "-DPTO_ATTENTION_SMOKE_QD=1",
                    "-DPTO_ATTENTION_SMOKE_VD=1",
                    "-DPTO_ATTENTION_SMALL_SMOKE_QD=1",
                    "-DPTO_FLASH_TILE_M=1",
                    "-DPTO_FLASH_TILE_K=1",
                    "-DPTO_ATTENTION_MASKED_SMOKE_SEQ=1",
                    "-DPTO_ATTENTION_MASKED_SMOKE_QD=1",
                    "-DPTO_ATTENTION_MASKED_SMOKE_VD=1",
                    "-DPTO_PARITY_STOP_AFTER_STAGE=PTO_PARITY_STAGE_FLASH_ATTENTION_MASKED",
                ],
                "description": "PTO parity direct-boot 1x attention micro-profile through flash_attention_masked before FA performance model maturity",
            },
        )
    )
    cases.append(
        Case(
            id="avs-pto-parity-prefix-fa-performance",
            kind="avs_pto",
            suite="pto_parity",
            tier=1,
            source_paths=[qemu_tests / "16_pto_kernel_parity.cpp"],
            manifest_path=root / "avs" / "qemu" / "run_tests.py",
            workdir=root,
            compile_command=None,
            qemu_command=None,
            model_eligible=True,
            produces_elf=True,
            expected="PTO parity prefix through fa_performance under QEMU, then gfsim exit 0",
            metadata={
                "avs_suite": "pto_parity",
                "avs_extra_cflags": [
                    "-DPTO_PARITY_FAST_F32_SEED=1",
                    "-DPTO_PARITY_FAST_FP16_SEED=1",
                    "-DPTO_ATTENTION_SMOKE_SEQ=1",
                    "-DPTO_ATTENTION_LARGE_SMOKE_SEQ=1",
                    "-DPTO_ATTENTION_SMOKE_QD=1",
                    "-DPTO_ATTENTION_SMOKE_VD=1",
                    "-DPTO_ATTENTION_SMALL_SMOKE_QD=1",
                    "-DPTO_FLASH_TILE_M=1",
                    "-DPTO_FLASH_TILE_K=1",
                    "-DPTO_ATTENTION_MASKED_SMOKE_SEQ=1",
                    "-DPTO_ATTENTION_MASKED_SMOKE_QD=1",
                    "-DPTO_ATTENTION_MASKED_SMOKE_VD=1",
                    "-DPTO_PARITY_STOP_AFTER_STAGE=PTO_PARITY_STAGE_FA_PERFORMANCE",
                ],
                "description": "PTO parity direct-boot 1x attention micro-profile through fa_performance before MLA attention model maturity",
            },
        )
    )
    cases.append(
        Case(
            id="avs-pto-parity-prefix-mla-attention",
            kind="avs_pto",
            suite="pto_parity",
            tier=1,
            source_paths=[qemu_tests / "16_pto_kernel_parity.cpp"],
            manifest_path=root / "avs" / "qemu" / "run_tests.py",
            workdir=root,
            compile_command=None,
            qemu_command=None,
            model_eligible=True,
            produces_elf=True,
            expected="PTO parity prefix through mla_attention under QEMU, then gfsim exit 0",
            metadata={
                "avs_suite": "pto_parity",
                "avs_extra_cflags": [
                    "-DPTO_PARITY_FAST_F32_SEED=1",
                    "-DPTO_PARITY_FAST_FP16_SEED=1",
                    "-DPTO_ATTENTION_SMOKE_SEQ=1",
                    "-DPTO_ATTENTION_LARGE_SMOKE_SEQ=1",
                    "-DPTO_ATTENTION_SMOKE_QD=1",
                    "-DPTO_ATTENTION_SMOKE_VD=1",
                    "-DPTO_ATTENTION_SMALL_SMOKE_QD=1",
                    "-DPTO_FLASH_TILE_M=1",
                    "-DPTO_FLASH_TILE_K=1",
                    "-DPTO_ATTENTION_MASKED_SMOKE_SEQ=1",
                    "-DPTO_ATTENTION_MASKED_SMOKE_QD=1",
                    "-DPTO_ATTENTION_MASKED_SMOKE_VD=1",
                    "-DPTO_PARITY_STOP_AFTER_STAGE=PTO_PARITY_STAGE_MLA_ATTENTION",
                ],
                "description": "PTO parity direct-boot 1x attention micro-profile through mla_attention before cube/vector attention model maturity",
            },
        )
    )
    cases.append(
        Case(
            id="avs-pto-parity-prefix-flash-attention-cube",
            kind="avs_pto",
            suite="pto_parity",
            tier=1,
            source_paths=[qemu_tests / "16_pto_kernel_parity.cpp"],
            manifest_path=root / "avs" / "qemu" / "run_tests.py",
            workdir=root,
            compile_command=None,
            qemu_command=None,
            model_eligible=True,
            produces_elf=True,
            expected="PTO parity prefix through flash_attention_cube under QEMU, then gfsim exit 0",
            metadata={
                "avs_suite": "pto_parity",
                "avs_extra_cflags": [
                    "-DPTO_PARITY_FAST_F32_SEED=1",
                    "-DPTO_PARITY_FAST_FP16_SEED=1",
                    "-DPTO_ATTENTION_SMOKE_SEQ=1",
                    "-DPTO_ATTENTION_LARGE_SMOKE_SEQ=1",
                    "-DPTO_ATTENTION_SMOKE_QD=1",
                    "-DPTO_ATTENTION_SMOKE_VD=1",
                    "-DPTO_ATTENTION_SMALL_SMOKE_QD=1",
                    "-DPTO_FLASH_TILE_M=1",
                    "-DPTO_FLASH_TILE_K=1",
                    "-DPTO_ATTENTION_MASKED_SMOKE_SEQ=1",
                    "-DPTO_ATTENTION_MASKED_SMOKE_QD=1",
                    "-DPTO_ATTENTION_MASKED_SMOKE_VD=1",
                    "-DPTO_PARITY_FLASH_CUBE_SEQ=1",
                    "-DPTO_PARITY_FLASH_CUBE_MAX_SEQ=1",
                    "-DPTO_PARITY_FLASH_CUBE_DIM=1",
                    "-DPTO_FLASH_CUBE_TILE_M=1",
                    "-DPTO_FLASH_CUBE_TILE_K=1",
                    "-DPTO_FLASH_CUBE_YDIM=1",
                    "-DPTO_PARITY_STOP_AFTER_STAGE=PTO_PARITY_STAGE_FLASH_ATTENTION_CUBE",
                ],
                "description": "PTO parity direct-boot 1x attention micro-profile through flash_attention_cube before vector attention model maturity",
            },
        )
    )
    cases.append(
        Case(
            id="avs-pto-parity-prefix-flash-attention-vec",
            kind="avs_pto",
            suite="pto_parity",
            tier=1,
            source_paths=[qemu_tests / "16_pto_kernel_parity.cpp"],
            manifest_path=root / "avs" / "qemu" / "run_tests.py",
            workdir=root,
            compile_command=None,
            qemu_command=None,
            model_eligible=True,
            produces_elf=True,
            expected="PTO parity prefix through flash_attention_vec under QEMU, then gfsim exit 0",
            metadata={
                "avs_suite": "pto_parity",
                "avs_extra_cflags": [
                    "-DPTO_PARITY_FAST_F32_SEED=1",
                    "-DPTO_PARITY_FAST_FP16_SEED=1",
                    "-DPTO_ATTENTION_SMOKE_SEQ=1",
                    "-DPTO_ATTENTION_LARGE_SMOKE_SEQ=1",
                    "-DPTO_ATTENTION_SMOKE_QD=1",
                    "-DPTO_ATTENTION_SMOKE_VD=1",
                    "-DPTO_ATTENTION_SMALL_SMOKE_QD=1",
                    "-DPTO_FLASH_TILE_M=1",
                    "-DPTO_FLASH_TILE_K=1",
                    "-DPTO_ATTENTION_MASKED_SMOKE_SEQ=1",
                    "-DPTO_ATTENTION_MASKED_SMOKE_QD=1",
                    "-DPTO_ATTENTION_MASKED_SMOKE_VD=1",
                    "-DPTO_PARITY_FLASH_CUBE_SEQ=1",
                    "-DPTO_PARITY_FLASH_CUBE_MAX_SEQ=1",
                    "-DPTO_PARITY_FLASH_CUBE_DIM=1",
                    "-DPTO_FLASH_CUBE_TILE_M=1",
                    "-DPTO_FLASH_CUBE_TILE_K=1",
                    "-DPTO_FLASH_CUBE_YDIM=1",
                    "-DPTO_FLASH_VEC_TILE_M=1",
                    "-DPTO_FLASH_VEC_TILE_K=1",
                    "-DPTO_FLASH_VEC_YDIM=1",
                    "-DPTO_PARITY_STOP_AFTER_STAGE=PTO_PARITY_STAGE_FLASH_ATTENTION_VEC",
                ],
                "description": "PTO parity direct-boot 1x attention micro-profile through flash_attention_vec before GQA model maturity",
            },
        )
    )
    cases.append(
        Case(
            id="avs-pto-parity-prefix-gqa",
            kind="avs_pto",
            suite="pto_parity",
            tier=1,
            source_paths=[qemu_tests / "16_pto_kernel_parity.cpp"],
            manifest_path=root / "avs" / "qemu" / "run_tests.py",
            workdir=root,
            compile_command=None,
            qemu_command=None,
            model_eligible=True,
            produces_elf=True,
            expected="PTO parity prefix through gqa under QEMU, then gfsim exit 0",
            metadata={
                "avs_suite": "pto_parity",
                "avs_extra_cflags": [
                    "-DPTO_PARITY_FAST_F32_SEED=1",
                    "-DPTO_PARITY_FAST_FP16_SEED=1",
                    "-DPTO_ATTENTION_SMOKE_SEQ=1",
                    "-DPTO_ATTENTION_LARGE_SMOKE_SEQ=1",
                    "-DPTO_ATTENTION_SMOKE_QD=1",
                    "-DPTO_ATTENTION_SMOKE_VD=1",
                    "-DPTO_ATTENTION_SMALL_SMOKE_QD=1",
                    "-DPTO_FLASH_TILE_M=1",
                    "-DPTO_FLASH_TILE_K=1",
                    "-DPTO_ATTENTION_MASKED_SMOKE_SEQ=1",
                    "-DPTO_ATTENTION_MASKED_SMOKE_QD=1",
                    "-DPTO_ATTENTION_MASKED_SMOKE_VD=1",
                    "-DPTO_PARITY_FLASH_CUBE_SEQ=1",
                    "-DPTO_PARITY_FLASH_CUBE_MAX_SEQ=1",
                    "-DPTO_PARITY_FLASH_CUBE_DIM=1",
                    "-DPTO_FLASH_CUBE_TILE_M=1",
                    "-DPTO_FLASH_CUBE_TILE_K=1",
                    "-DPTO_FLASH_CUBE_YDIM=1",
                    "-DPTO_FLASH_VEC_TILE_M=1",
                    "-DPTO_FLASH_VEC_TILE_K=1",
                    "-DPTO_FLASH_VEC_YDIM=1",
                    "-DPTO_PARITY_GQA_SEQ=1",
                    "-DPTO_PARITY_GQA_Q_HEADS=1",
                    "-DPTO_PARITY_GQA_KV_HEADS=1",
                    "-DPTO_PARITY_GQA_DIM=1",
                    "-DPTO_GQA_SMOKE_SEQ=1",
                    "-DPTO_GQA_SMOKE_Q_HEADS=1",
                    "-DPTO_GQA_SMOKE_KV_HEADS=1",
                    "-DPTO_GQA_SMOKE_DIM=1",
                    "-DPTO_PARITY_STOP_AFTER_STAGE=PTO_PARITY_STAGE_GQA",
                ],
                "description": "PTO parity direct-boot 1x attention micro-profile through GQA before sparse attention model maturity",
            },
        )
    )
    cases.append(
        Case(
            id="avs-pto-parity-prefix-sparse-attention-local",
            kind="avs_pto",
            suite="pto_parity",
            tier=1,
            source_paths=[qemu_tests / "16_pto_kernel_parity.cpp"],
            manifest_path=root / "avs" / "qemu" / "run_tests.py",
            workdir=root,
            compile_command=None,
            qemu_command=None,
            model_eligible=True,
            produces_elf=True,
            expected="PTO parity prefix through sparse_attention_local under QEMU, then gfsim exit 0",
            metadata={
                "avs_suite": "pto_parity",
                "avs_extra_cflags": [
                    "-DPTO_PARITY_FAST_F32_SEED=1",
                    "-DPTO_PARITY_FAST_FP16_SEED=1",
                    "-DPTO_ATTENTION_SMOKE_SEQ=1",
                    "-DPTO_ATTENTION_LARGE_SMOKE_SEQ=1",
                    "-DPTO_ATTENTION_SMOKE_QD=1",
                    "-DPTO_ATTENTION_SMOKE_VD=1",
                    "-DPTO_ATTENTION_SMALL_SMOKE_QD=1",
                    "-DPTO_FLASH_TILE_M=1",
                    "-DPTO_FLASH_TILE_K=1",
                    "-DPTO_ATTENTION_MASKED_SMOKE_SEQ=1",
                    "-DPTO_ATTENTION_MASKED_SMOKE_QD=1",
                    "-DPTO_ATTENTION_MASKED_SMOKE_VD=1",
                    "-DPTO_PARITY_FLASH_CUBE_SEQ=1",
                    "-DPTO_PARITY_FLASH_CUBE_MAX_SEQ=1",
                    "-DPTO_PARITY_FLASH_CUBE_DIM=1",
                    "-DPTO_FLASH_CUBE_TILE_M=1",
                    "-DPTO_FLASH_CUBE_TILE_K=1",
                    "-DPTO_FLASH_CUBE_YDIM=1",
                    "-DPTO_FLASH_VEC_TILE_M=1",
                    "-DPTO_FLASH_VEC_TILE_K=1",
                    "-DPTO_FLASH_VEC_YDIM=1",
                    "-DPTO_PARITY_GQA_SEQ=1",
                    "-DPTO_PARITY_GQA_Q_HEADS=1",
                    "-DPTO_PARITY_GQA_KV_HEADS=1",
                    "-DPTO_PARITY_GQA_DIM=1",
                    "-DPTO_GQA_SMOKE_SEQ=1",
                    "-DPTO_GQA_SMOKE_Q_HEADS=1",
                    "-DPTO_GQA_SMOKE_KV_HEADS=1",
                    "-DPTO_GQA_SMOKE_DIM=1",
                    "-DPTO_PARITY_SPARSE_SEQ=1",
                    "-DPTO_PARITY_SPARSE_HEADS=1",
                    "-DPTO_PARITY_SPARSE_DIM=1",
                    "-DPTO_PARITY_SPARSE_WINDOW=1",
                    "-DPTO_SPARSE_LOCAL_SMOKE_SEQ=1",
                    "-DPTO_SPARSE_LOCAL_SMOKE_DIM=1",
                    "-DPTO_PARITY_STOP_AFTER_STAGE=PTO_PARITY_STAGE_SPARSE_ATTENTION_LOCAL",
                ],
                "description": "PTO parity direct-boot 1x attention micro-profile through sparse local attention before normalization model maturity",
            },
        )
    )
    cases.append(
        Case(
            id="avs-pto-parity-prefix-rmsnorm",
            kind="avs_pto",
            suite="pto_parity",
            tier=1,
            source_paths=[qemu_tests / "16_pto_kernel_parity.cpp"],
            manifest_path=root / "avs" / "qemu" / "run_tests.py",
            workdir=root,
            compile_command=None,
            qemu_command=None,
            model_eligible=True,
            produces_elf=True,
            expected="PTO parity prefix through rmsnorm under QEMU, then gfsim exit 0",
            metadata={
                "avs_suite": "pto_parity",
                "avs_extra_cflags": [
                    "-DPTO_PARITY_FAST_F32_SEED=1",
                    "-DPTO_PARITY_FAST_FP16_SEED=1",
                    "-DPTO_ATTENTION_SMOKE_SEQ=1",
                    "-DPTO_ATTENTION_LARGE_SMOKE_SEQ=1",
                    "-DPTO_ATTENTION_SMOKE_QD=1",
                    "-DPTO_ATTENTION_SMOKE_VD=1",
                    "-DPTO_ATTENTION_SMALL_SMOKE_QD=1",
                    "-DPTO_FLASH_TILE_M=1",
                    "-DPTO_FLASH_TILE_K=1",
                    "-DPTO_ATTENTION_MASKED_SMOKE_SEQ=1",
                    "-DPTO_ATTENTION_MASKED_SMOKE_QD=1",
                    "-DPTO_ATTENTION_MASKED_SMOKE_VD=1",
                    "-DPTO_PARITY_FLASH_CUBE_SEQ=1",
                    "-DPTO_PARITY_FLASH_CUBE_MAX_SEQ=1",
                    "-DPTO_PARITY_FLASH_CUBE_DIM=1",
                    "-DPTO_FLASH_CUBE_TILE_M=1",
                    "-DPTO_FLASH_CUBE_TILE_K=1",
                    "-DPTO_FLASH_CUBE_YDIM=1",
                    "-DPTO_FLASH_VEC_TILE_M=1",
                    "-DPTO_FLASH_VEC_TILE_K=1",
                    "-DPTO_FLASH_VEC_YDIM=1",
                    "-DPTO_PARITY_GQA_SEQ=1",
                    "-DPTO_PARITY_GQA_Q_HEADS=1",
                    "-DPTO_PARITY_GQA_KV_HEADS=1",
                    "-DPTO_PARITY_GQA_DIM=1",
                    "-DPTO_GQA_SMOKE_SEQ=1",
                    "-DPTO_GQA_SMOKE_Q_HEADS=1",
                    "-DPTO_GQA_SMOKE_KV_HEADS=1",
                    "-DPTO_GQA_SMOKE_DIM=1",
                    "-DPTO_PARITY_SPARSE_SEQ=1",
                    "-DPTO_PARITY_SPARSE_HEADS=1",
                    "-DPTO_PARITY_SPARSE_DIM=1",
                    "-DPTO_PARITY_SPARSE_WINDOW=1",
                    "-DPTO_SPARSE_LOCAL_SMOKE_SEQ=1",
                    "-DPTO_SPARSE_LOCAL_SMOKE_DIM=1",
                    "-DPTO_PARITY_RMS_TOKENS=1",
                    "-DPTO_PARITY_RMS_CHANNELS=1",
                    "-DPTO_RMSNORM_SMOKE_TOKENS=1",
                    "-DPTO_RMSNORM_SMOKE_CHANNELS=1",
                    "-DPTO_PARITY_STOP_AFTER_STAGE=PTO_PARITY_STAGE_RMSNORM",
                ],
                "description": "PTO parity direct-boot 1x normalization micro-profile through RMSNorm before batchnorm model maturity",
            },
        )
    )
    cases.append(
        Case(
            id="avs-pto-parity",
            kind="avs_pto",
            suite="pto_parity",
            tier=1,
            source_paths=[qemu_tests / "16_pto_kernel_parity.cpp"],
            manifest_path=root / "avs" / "qemu" / "run_tests.py",
            workdir=root,
            compile_command=None,
            qemu_command=None,
            model_eligible=False,
            produces_elf=True,
            expected="All smoke-sized PTO_DIGEST parity stages under QEMU; final full-model closure is tracked by avs-pto-parity-full-model",
            metadata={
                "avs_suite": "pto_parity",
                "avs_extra_cflags": [
                    "-DPTO_PARITY_FAST_F32_SEED=1",
                    "-DPTO_PARITY_FAST_FP16_SEED=1",
                ],
                "description": "PTO parity direct-boot QEMU maturity suite across all smoke-sized stages",
                "model_deferred_reason": "Full-row model execution currently reaches flash_attention_softmax and times out in scalar flash_attention_demo_f32 soft-float normalization; keep PR on QEMU parity plus micro-profile model prefixes.",
            },
        )
    )
    cases.append(
        Case(
            id="avs-pto-parity-full-model",
            kind="avs_pto",
            suite="pto_parity",
            tier=4,
            source_paths=[qemu_tests / "16_pto_kernel_parity.cpp"],
            manifest_path=root / "avs" / "qemu" / "run_tests.py",
            workdir=root,
            compile_command=None,
            qemu_command=None,
            model_eligible=True,
            produces_elf=True,
            expected="All smoke-sized PTO_DIGEST parity stages under QEMU, then gfsim exit 0",
            metadata={
                "avs_suite": "pto_parity",
                "avs_extra_cflags": [
                    "-DPTO_PARITY_FAST_F32_SEED=1",
                    "-DPTO_PARITY_FAST_FP16_SEED=1",
                ],
                "description": "Tier-4 full AVS PTO parity LinxCoreModel closure target",
            },
        )
    )

    catalog = root / "workloads" / "pto_kernels" / "kernels" / "catalog.txt"
    if catalog.exists():
        for raw in catalog.read_text(encoding="utf-8").splitlines():
            entry = raw.strip()
            if not entry or entry.startswith("#"):
                continue
            source = catalog.parent / entry
            name = Path(entry).stem
            standalone = PTO_STANDALONE_HARNESSES.get(entry, {})
            metadata = {"catalog_entry": entry}
            metadata.update(standalone)
            cases.append(
                Case(
                    id=f"pto-kernel-{slug(name)}",
                    kind="pto_kernel",
                    suite=entry.split("/", 1)[0],
                    tier=pto_kernel_tier(entry),
                    source_paths=[source],
                    manifest_path=catalog,
                    workdir=root,
                    compile_command=None,
                    qemu_command=None,
                    model_eligible=bool(standalone),
                    produces_elf=bool(standalone),
                    expected=standalone.get(
                        "expected",
                        "compile/static contract; standalone ELF harness pending",
                    ),
                    metadata=metadata,
                )
            )

    test_root = supernpu_test_root(root)
    if test_root.exists():
        for compile_all in sorted(test_root.rglob("compile.all")):
            suite_dir = compile_all.parent
            suite_rel = suite_dir.relative_to(test_root).as_posix()
            for line_no, line in enumerate(compile_all.read_text(encoding="utf-8").splitlines(), start=1):
                parsed = parse_compile_all_line(line)
                if parsed is None:
                    continue
                command, make_vars = parsed
                testcase = make_vars["TESTCASE"]
                sources = supernpu_source_paths(suite_dir, make_vars)
                case_vars = dict(make_vars)
                case_vars["PLAT"] = "linx"
                case_id = f"supernpu-{slug(suite_rel)}-{slug(testcase)}"
                if len(make_vars) > 1:
                    sig = "-".join(
                        f"{slug(k)}-{slug(v)}"
                        for k, v in sorted(make_vars.items())
                        if k != "TESTCASE"
                    )
                    if sig:
                        case_id = f"{case_id}-{sig}"
                cases.append(
                    Case(
                        id=case_id,
                        kind="supernpu",
                        suite=suite_rel,
                        tier=supernpu_tier(suite_rel, make_vars),
                        source_paths=sources,
                        manifest_path=compile_all,
                        workdir=suite_dir,
                        compile_command=command,
                        qemu_command=None,
                        model_eligible=True,
                        produces_elf=True,
                        expected="SuperNPUBench make/sim pass, then gfsim exit 0",
                        metadata={
                            "compile_all": relpath(root, compile_all),
                            "line": line_no,
                            "make_vars": make_vars,
                            "elf": relpath(root, supernpu_elf_path(root, suite_dir, make_vars)),
                            "elf_dir": relpath(root, supernpu_elf_dir(root, suite_dir)),
                        },
                    )
                )
    return dedupe_cases(cases)


def dedupe_cases(cases: list[Case]) -> list[Case]:
    seen: dict[str, int] = {}
    out: list[Case] = []
    for case in cases:
        base = case.id
        count = seen.get(base, 0)
        seen[base] = count + 1
        if count:
            case.id = f"{base}-{count + 1}"
        out.append(case)
    return out


def filter_cases(
    cases: list[Case],
    tiers: set[int],
    kinds: list[str],
    patterns: list[str],
    limit: int,
) -> list[Case]:
    selected = [case for case in cases if case.tier in tiers]
    if kinds:
        wanted = set(kinds)
        selected = [case for case in selected if case.kind in wanted]
    if patterns:
        selected = [
            case
            for case in selected
            if any(case_matches_pattern(case, pattern) for pattern in patterns)
        ]
    selected.sort(key=lambda c: (c.tier, c.kind, c.suite, c.id))
    if limit > 0:
        selected = selected[:limit]
    return selected


def case_matches_pattern(case: Case, pattern: str) -> bool:
    if pattern.startswith("="):
        exact = pattern[1:]
        return exact in {case.id, case.suite, case.kind}
    return pattern in case.id or pattern in case.suite or pattern in case.kind


def tool_paths(root: Path, args: argparse.Namespace) -> dict[str, str]:
    llvm_bin = root / "compiler" / "llvm" / "build-linxisa-clang" / "bin"
    qemu_default = default_qemu_binary(root)
    model_root = Path(args.model_root).expanduser().resolve() if args.model_root else root / "tools" / "LinxCoreModel"
    gfsim = Path(args.gfsim).expanduser().resolve() if args.gfsim else model_root / "bin" / "gfsim"
    return {
        "clang": str(Path(args.clang).expanduser().resolve() if args.clang else llvm_bin / "clang"),
        "clangxx": str(Path(args.clangxx).expanduser().resolve() if args.clangxx else llvm_bin / "clang++"),
        "lld": str(Path(args.lld).expanduser().resolve() if args.lld else llvm_bin / "ld.lld"),
        "llvm_objdump": str(
            Path(args.llvm_objdump).expanduser().resolve()
            if args.llvm_objdump
            else llvm_bin / "llvm-objdump"
        ),
        "llvm_objcopy": str(
            Path(args.llvm_objcopy).expanduser().resolve()
            if args.llvm_objcopy
            else llvm_bin / "llvm-objcopy"
        ),
        "qemu": str(Path(args.qemu).expanduser().resolve() if args.qemu else qemu_default),
        "model_root": str(model_root),
        "gfsim": str(gfsim),
    }


def tool_manifest(paths: dict[str, str]) -> dict[str, dict[str, Any]]:
    version_args = {
        "clang": ["--version"],
        "clangxx": ["--version"],
        "lld": ["--version"],
        "llvm_objdump": ["--version"],
        "llvm_objcopy": ["--version"],
        "qemu": ["--version"],
    }

    def first_version_line(key: str, value: str) -> str | None:
        args = version_args.get(key)
        path = Path(value)
        if args is None or not executable(path):
            return None
        try:
            proc = subprocess.run(
                [str(path), *args],
                check=False,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                timeout=10,
            )
        except (OSError, subprocess.TimeoutExpired):
            return None
        return (proc.stdout or "").splitlines()[0] if proc.stdout else None

    return {
        key: {
            "path": value,
            "exists": Path(value).exists(),
            "executable": executable(Path(value)),
            "version": first_version_line(key, value),
        }
        for key, value in paths.items()
        if key != "model_root"
    } | {
        "model_root": {
            "path": paths["model_root"],
            "exists": Path(paths["model_root"]).exists(),
            "executable": False,
            "version": None,
        }
    }


def command_text(command: str | list[str]) -> str:
    if isinstance(command, list):
        return shlex.join(str(c) for c in command)
    return command


def run_command(
    command: str | list[str],
    *,
    cwd: Path,
    env: dict[str, str],
    timeout: int,
    log_path: Path,
    dry_run: bool,
) -> dict[str, Any]:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    rendered = command_text(command)
    log_path.write_text(f"$ {rendered}\n", encoding="utf-8")
    row = {
        "command": rendered,
        "cwd": str(cwd),
        "log": str(log_path),
        "timeout_seconds": timeout,
        "returncode": 0,
        "status": "not_run" if dry_run else "pass",
    }
    if dry_run:
        return row

    try:
        proc = subprocess.run(
            command,
            cwd=str(cwd),
            env=env,
            shell=isinstance(command, str),
            executable="/bin/bash" if isinstance(command, str) else None,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout if timeout > 0 else None,
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        output = exc.stdout or ""
        if isinstance(output, bytes):
            output = output.decode("utf-8", errors="replace")
        elif not isinstance(output, str):
            output = str(output)
        log_path.write_text(f"$ {rendered}\n\n{output}", encoding="utf-8", errors="replace")
        row["status"] = "timeout"
        row["returncode"] = 124
        return row

    log_path.write_text(
        f"$ {rendered}\n\n{proc.stdout or ''}",
        encoding="utf-8",
        errors="replace",
    )
    row["returncode"] = proc.returncode
    row["status"] = "pass" if proc.returncode == 0 else "fail"
    return row


def normalize_qemu_finisher_result(result: dict[str, Any], log_path: Path) -> dict[str, Any]:
    """Treat the Linx direct-boot test finisher as a successful QEMU exit."""
    returncode = int(result.get("returncode", 0))
    finisher_low8 = returncode & 0xFF
    if result.get("status") == "fail" and finisher_low8 == FINISHER_PASS_LOW8:
        result = dict(result)
        result["status"] = "pass"
        result["finisher"] = "pass"
        with log_path.open("a", encoding="utf-8", errors="replace") as log:
            log.write(f"\n[ai-flow] guest finisher pass exit={returncode}\n")
        return result
    if result.get("status") == "fail" and finisher_low8 == FINISHER_FAIL_LOW8:
        result = dict(result)
        result["finisher"] = "fail"
    elif result.get("status") == "fail" and finisher_low8 == FINISHER_RESET_LOW8:
        result = dict(result)
        result["finisher"] = "reset"
    return result


def parse_digests(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}
    text = path.read_text(encoding="utf-8", errors="replace")
    return {m.group(1): "0x" + m.group(2).upper() for m in DIGEST_RE.finditer(text)}


def append_uart_context(evidence: str, artifacts: dict[str, str]) -> str:
    uart_tail = artifacts.get("uart_tail")
    if not uart_tail:
        return evidence
    return f"{evidence}; uart tail: {uart_tail}"


def summarize_gfsim_log(status: str, log_path: Path) -> tuple[str, dict[str, str]]:
    if not log_path.exists():
        return "gfsim failed; log missing", {}

    text = log_path.read_text(encoding="utf-8", errors="replace")
    artifacts: dict[str, str] = {}
    uart_lines = [match.group("line").strip() for match in GFSIM_UART_RE.finditer(text)]
    if uart_lines:
        artifacts["uart_count"] = str(len(uart_lines))
        artifacts["uart_tail"] = " | ".join(uart_lines[-3:])

    if status == "pass":
        return append_uart_context("gfsim passed", artifacts), artifacts

    finisher = list(GFSIM_FINISHER_RE.finditer(text))
    if finisher:
        match = finisher[-1]
        value = "0x" + match.group("value").lower()
        finisher_status = match.group("status")
        artifacts["finisher_value"] = value
        artifacts["finisher_status"] = finisher_status
        return append_uart_context(f"gfsim finisher {finisher_status} ({value})", artifacts), artifacts

    assertion = GFSIM_ASSERT_RE.search(text)
    if assertion:
        reason = assertion.group("assertion").strip()
        artifacts["assertion"] = reason
        return append_uart_context(f"gfsim {status}: {reason}", artifacts), artifacts

    brob = list(GFSIM_BROB_RE.finditer(text))
    if brob:
        match = brob[-1]
        bpc = "0x" + match.group("bpc").lower()
        artifacts["last_brob_bpc"] = bpc
        artifacts["last_retired_blocks"] = match.group("blocks")
        artifacts["last_brob_head"] = match.group("head").strip()
        status_text = "timed out" if status == "timeout" else "failed"
        return append_uart_context(f"gfsim {status_text}; last BROB head BPC {bpc}", artifacts), artifacts

    if status == "timeout":
        return append_uart_context("gfsim timed out; no terminal model marker found", artifacts), artifacts
    return append_uart_context("gfsim failed; no terminal model marker found", artifacts), artifacts


def mark_failure(state: CaseState, stage_id: str, owner: str, evidence: str) -> None:
    if state.failure_stage is None:
        state.failure_stage = stage_id
        state.failure_owner = owner
        state.failure_evidence = evidence


def stage_row(
    state: CaseState,
    stage_id: str,
    status: str,
    *,
    owner: str,
    evidence: str = "",
    command: str | None = None,
    artifacts: dict[str, str] | None = None,
) -> dict[str, Any]:
    row = {
        "stage": stage_id,
        "status": status,
        "owner": owner,
        "evidence": evidence,
        "command": command,
        "artifacts": artifacts or {},
    }
    state.stages[stage_id] = row
    if status not in PASS_STATUSES:
        mark_failure(state, stage_id, owner, evidence)
    return row


def case_can_enter(state: CaseState, previous_stage: str) -> bool:
    row = state.stages.get(previous_stage)
    return row is not None and row["status"] in PASS_STATUSES


def source_contract(root: Path, states: list[CaseState], dry_run: bool) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for state in states:
        case = state.case
        case_source_dir = state.case_dir / "source"
        artifacts: dict[str, str] = {}
        missing: list[str] = []
        source_rows: list[dict[str, str]] = []
        for source in case.source_paths:
            if not source.exists():
                missing.append(relpath(root, source))
                continue
            digest = sha256_file(source)
            source_rows.append({"path": relpath(root, source), "sha256": digest})
            case_source_dir.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, case_source_dir / source.name)
        if case.manifest_path is not None:
            if not case.manifest_path.exists():
                missing.append(relpath(root, case.manifest_path))
            else:
                artifacts["manifest"] = relpath(root, case.manifest_path)
        source_manifest = state.case_dir / "source_manifest.json"
        write_json(
            source_manifest,
            {
                "case": case.id,
                "kind": case.kind,
                "suite": case.suite,
                "tier": case.tier,
                "sources": source_rows,
                "metadata": case.metadata,
                "dry_run": dry_run,
            },
        )
        artifacts["source_manifest"] = str(source_manifest)
        if missing:
            rows.append(
                stage_row(
                    state,
                    "source-contract",
                    "fail",
                    owner="benchmark",
                    evidence="missing source/manifest: " + ", ".join(missing),
                    artifacts=artifacts,
                )
            )
        else:
            rows.append(
                stage_row(
                    state,
                    "source-contract",
                    "pass",
                    owner="benchmark",
                    evidence=f"{len(source_rows)} source file(s) hashed",
                    artifacts=artifacts,
                )
            )
    return rows


def avs_command(
    root: Path,
    case: Case,
    paths: dict[str, str],
    out_dir: Path,
    *,
    timeout: int,
    compile_only: bool,
) -> list[str]:
    cmd = [
        sys.executable,
        str(root / "avs" / "qemu" / "run_tests.py"),
        "--suite",
        str(case.metadata["avs_suite"]),
        "--out-dir",
        str(out_dir),
        "--timeout",
        str(timeout),
        "--clang",
        paths["clang"],
        "--clangxx",
        paths["clangxx"],
        "--lld",
        paths["lld"],
        "--llvm-objdump",
        paths["llvm_objdump"],
    ]
    if compile_only:
        cmd.append("--compile-only")
    else:
        cmd += ["--qemu", paths["qemu"]]
        if case.metadata.get("avs_source_profile") == "compile-smoke":
            cmd.append("--smoke-source-overrides")
    for flag in case.metadata.get("avs_extra_cflags", []):
        cmd.append(f"--extra-cflag={flag}")
    return cmd


def pto_compile_command(root: Path, case: Case, paths: dict[str, str], asm_out: Path) -> list[str]:
    return [
        paths["clangxx"],
        "-target",
        "linx64-linx-none-elf",
        "-O2",
        "-S",
        "-ffreestanding",
        "-fno-builtin",
        "-fno-stack-protector",
        "-fno-exceptions",
        "-fno-rtti",
        "-nostdlib",
        "-I",
        str(root / "workloads" / "pto_kernels" / "include"),
        str(case.source_paths[0]),
        "-o",
        str(asm_out),
    ]


def pto_kernel_elf_command(
    root: Path,
    case: Case,
    paths: dict[str, str],
    harness_source: Path,
    linker_script: Path,
    elf_out: Path,
) -> list[str]:
    cmd = [
        paths["clangxx"],
        "-target",
        "linx64-linx-none-elf",
        "-O2",
        "-ffreestanding",
        "-fno-builtin",
        "-fno-stack-protector",
        "-fno-exceptions",
        "-fno-rtti",
        "-fno-vectorize",
        "-fno-slp-vectorize",
        "-nostdlib",
    ]
    cmd.extend(str(flag) for flag in case.metadata.get("compile_defines", []))
    cmd += [
        "-I",
        str(root / "workloads" / "pto_kernels" / "include"),
        str(case.source_paths[0]),
        str(harness_source),
        "-Wl,-e,_start",
        f"-Wl,-T,{linker_script}",
        "-o",
        str(elf_out),
    ]
    return cmd


def supernpu_make_command(
    case: Case,
    paths: dict[str, str],
    *,
    target: str | None = None,
    linker_script: Path | None = None,
    obj_root: Path | None = None,
) -> str:
    vars_part = " ".join(
        f"{shlex.quote(k)}={shlex.quote(str(v))}"
        for k, v in sorted(case.metadata["make_vars"].items())
    )
    obj_root_part = f" OBJ_ROOT={shlex.quote(str(obj_root))}" if obj_root is not None else ""
    compiler_dir = shlex.quote(str(Path(paths["clang"]).parent))
    linx_compile_flags = shlex.quote("-c -target linx64-linx-none-elf -fenable-matrix -O2")
    linker_flags = "-Wl,-e,_start"
    if linker_script is not None:
        linker_flags += f" -Wl,-T,{linker_script}"
    linx_link_flags = shlex.quote(f"-target linx64-linx-none-elf -nostdlib {linker_flags}")
    prefix = (
        f"make {vars_part} PLAT=linx COMPILER_DIR={compiler_dir} "
        f"CC_O={linx_compile_flags} CC_LINK={linx_link_flags}{obj_root_part}"
    )
    if target:
        return f"{prefix} {shlex.quote(target)}"
    bench_root = next((p for p in [case.workdir, *case.workdir.parents] if p.name == "SuperNPUBench"), None)
    output_root = (
        obj_root
        if obj_root is not None
        else (
            bench_root / "benchmark" / "two-level-arch" / "output"
            if bench_root
            else None
        )
    )
    mkdir_output = f"mkdir -p {shlex.quote(str(output_root))}" if output_root else "true"
    clean = f"make{obj_root_part} clean" if obj_root_part else "make clean"
    return f"{mkdir_output} && {clean} && {prefix}"


def classify_supernpu_compile_failure(log_path: Path) -> tuple[str, str]:
    text = log_path.read_text(encoding="utf-8", errors="replace") if log_path.exists() else ""
    if re.search(r"use of undeclared identifier '[A-Z0-9_]+_Impl'", text):
        return "benchmark", "SuperNPUBench Linx tile API implementation is not available"
    unsupported_linx_source_markers = [
        "unknown type name '__vbuf__'",
        "use of undeclared identifier 'blkv_get_",
        "Linx smoke TCOPYIN supports only unboxed tiles",
        "Linx scalar MATMUL supports only unboxed layouts",
        "Linx scalar MATMUL does not support ACC tile operands",
        "TADD not support Boxed Layout!",
    ]
    if any(marker in text for marker in unsupported_linx_source_markers):
        return "benchmark", "SuperNPUBench source uses unsupported Linx tile runtime contract"
    direct_boot_runtime_markers = [
        "undefined symbol: calloc",
        "undefined symbol: malloc",
        "undefined symbol: free",
        "undefined symbol: puts",
        "undefined symbol: printf",
        "undefined symbol: exit",
        "undefined symbol: memcpy",
        "undefined symbol: __divsf3",
        "undefined symbol: __mulsf3",
        "undefined symbol: __addsf3",
    ]
    if any(marker in text for marker in direct_boot_runtime_markers):
        return "benchmark", "SuperNPUBench source is not adapted to the Linx direct-boot runtime"
    source_markers = [
        "-mlxbc",
        "-enable-all-vector-as-tilereg",
        "bits/alltypes.h",
        "unknown target triple 'linx64v5'",
        "fatal error: 'benchmark.h' file not found",
        "unknown type name '__half'",
        "use of undeclared identifier '__fp32'",
        "use of undeclared identifier '__tf32'",
        "use of undeclared identifier '__hf32'",
        "include/c++/v1/iostream",
        "workloads/SuperNPUBench/benchmark/two-level-arch/include/jcore/type.hpp",
    ]
    if any(marker in text for marker in source_markers):
        return "benchmark", "SuperNPUBench source/toolchain manifest mismatch"
    return "compiler", "SuperNPUBench compile failed"


def classify_supernpu_missing_elf(log_path: Path, elf: Path) -> tuple[str, str]:
    owner, evidence = classify_supernpu_compile_failure(log_path)
    if owner == "benchmark":
        return owner, evidence
    return "compiler", f"expected ELF was not produced: {elf}"


def classify_avs_compile_failure(log_path: Path) -> tuple[str, str]:
    text = log_path.read_text(encoding="utf-8", errors="replace") if log_path.exists() else ""
    source_markers = [
        "__builtin_linx_lc",
        "<<<",
        ">>>",
        "PTO kernel",
        "block_vector_kernels.hpp",
        "block_vector_compat.hpp",
    ]
    if any(marker in text for marker in source_markers):
        return "benchmark", "AVS PTO source/API contract failed under Linx clang"
    return "compiler", "AVS compile failed"


def run_obj_tool(
    tool: str,
    args: list[str],
    *,
    cwd: Path,
    out_path: Path,
    timeout: int,
    dry_run: bool,
) -> dict[str, Any]:
    if dry_run:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text("", encoding="utf-8")
        return {"status": "not_run", "command": shlex.join([tool, *args]), "output": str(out_path)}
    proc = subprocess.run(
        [tool, *args],
        cwd=str(cwd),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=timeout,
        check=False,
    )
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(proc.stdout or "", encoding="utf-8", errors="replace")
    return {
        "status": "pass" if proc.returncode == 0 else "fail",
        "returncode": proc.returncode,
        "command": shlex.join([tool, *args]),
        "output": str(out_path),
    }


def emit_elf_objdump_artifacts(
    *,
    paths: dict[str, str],
    root: Path,
    elf: Path,
    out_dir: Path,
    dry_run: bool,
) -> dict[str, str]:
    objdump = Path(paths["llvm_objdump"])
    if not (dry_run or executable(objdump)):
        return {}
    dump = run_obj_tool(
        paths["llvm_objdump"],
        ["-d", str(elf)],
        cwd=root,
        out_path=out_dir / "objdump.disasm.txt",
        timeout=120,
        dry_run=dry_run,
    )
    sym = run_obj_tool(
        paths["llvm_objdump"],
        ["-t", str(elf)],
        cwd=root,
        out_path=out_dir / "objdump.symbols.txt",
        timeout=120,
        dry_run=dry_run,
    )
    sec = run_obj_tool(
        paths["llvm_objdump"],
        ["-h", str(elf)],
        cwd=root,
        out_path=out_dir / "objdump.sections.txt",
        timeout=120,
        dry_run=dry_run,
    )
    rel = run_obj_tool(
        paths["llvm_objdump"],
        ["-r", str(elf)],
        cwd=root,
        out_path=out_dir / "objdump.relocs.txt",
        timeout=120,
        dry_run=dry_run,
    )
    return {
        "disasm": dump["output"],
        "symbols": sym["output"],
        "sections": sec["output"],
        "relocations": rel["output"],
    }


def emit_bpc_disassembly_window(
    *,
    paths: dict[str, str],
    root: Path,
    elf: Path,
    bpc: str | None,
    out_dir: Path,
    dry_run: bool,
) -> dict[str, str]:
    if not bpc:
        return {}
    try:
        bpc_addr = int(bpc, 16)
    except ValueError:
        return {}
    objdump = Path(paths["llvm_objdump"])
    if not (dry_run or executable(objdump)):
        return {}
    start = max(0, bpc_addr - 0x80)
    stop = bpc_addr + 0x80
    safe_bpc = f"0x{bpc_addr:x}"
    window = run_obj_tool(
        paths["llvm_objdump"],
        [
            "-d",
            "--no-show-raw-insn",
            f"--start-address=0x{start:x}",
            f"--stop-address=0x{stop:x}",
            str(elf),
        ],
        cwd=root,
        out_path=out_dir / f"last-bpc-{safe_bpc}.disasm.txt",
        timeout=120,
        dry_run=dry_run,
    )
    return {
        "last_brob_bpc_disasm": window["output"],
        "last_brob_bpc_window": f"0x{start:x}..0x{stop:x}",
    }


def static_check_text(text: str, *, require_entry: bool) -> tuple[bool, list[str]]:
    findings: list[str] = []
    if FORBIDDEN_ASM_RE.search(text):
        findings.append("forbidden retired pre-v0.56 token found")
    if require_entry and not re.search(r"(\b_start\b|\bmain\b)", text):
        findings.append("missing _start/main symbol in objdump evidence")
    return not findings, findings


def compiler_contract(
    root: Path,
    states: list[CaseState],
    paths: dict[str, str],
    dry_run: bool,
    timeout: int,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    env = os.environ.copy()
    env.setdefault("LINXISA_ROOT", str(root))
    for state in states:
        case = state.case
        if not case_can_enter(state, "source-contract"):
            rows.append(
                stage_row(
                    state,
                    "compiler-contract",
                    "skipped",
                    owner="compiler",
                    evidence="source contract did not pass",
                )
            )
            continue
        case_artifacts = state.case_dir / "compiler"
        log_path = case_artifacts / "compile.log"
        artifacts: dict[str, str] = {}
        if case.kind == "avs_pto":
            out_dir = case_artifacts / "avs"
            elf = out_dir / "linx-qemu-tests.elf"
            elf_mtime_before = elf.stat().st_mtime if elf.exists() else None
            cmd = avs_command(root, case, paths, out_dir, timeout=timeout, compile_only=True)
            result = run_command(
                cmd,
                cwd=root,
                env=env,
                timeout=timeout,
                log_path=log_path,
                dry_run=dry_run,
            )
            obj = out_dir / "linx-qemu-tests.o"
            artifacts.update({"log": str(log_path), "object": str(obj)})
            if result["status"] == "pass" and obj.exists():
                state.artifacts["object"] = str(obj)
            owner = "compiler"
            status = result["status"]
            evidence = (
                "AVS direct-boot suite compiled"
                if result["status"] == "pass"
                else "AVS compile failed"
            )
            fresh_elf = dry_run or (
                elf.exists()
                and (elf_mtime_before is None or elf.stat().st_mtime > elf_mtime_before)
            )
            if result["status"] == "pass" and fresh_elf:
                artifacts["elf"] = str(elf)
                state.artifacts["elf"] = str(elf)
                sidecars = emit_elf_objdump_artifacts(
                    paths=paths,
                    root=root,
                    elf=elf,
                    out_dir=case_artifacts,
                    dry_run=dry_run,
                )
                artifacts.update(sidecars)
                if not dry_run and sidecars:
                    static_text = "\n".join(
                        Path(p).read_text(encoding="utf-8", errors="replace")
                        for p in [sidecars.get("disasm"), sidecars.get("symbols")]
                        if p and Path(p).exists()
                    )
                    ok, findings = static_check_text(static_text, require_entry=True)
                    if not ok:
                        status = "fail"
                        evidence = "static legality check failed: " + "; ".join(findings)
            if result["status"] not in PASS_STATUSES:
                owner, evidence = classify_avs_compile_failure(log_path)
            rows.append(
                stage_row(
                    state,
                    "compiler-contract",
                    status,
                    owner=owner,
                    evidence=evidence,
                    command=result["command"],
                    artifacts=artifacts,
                )
            )
            continue

        if case.kind == "pto_kernel":
            if case.produces_elf:
                harness_name = str(case.metadata.get("standalone_harness", ""))
                harness_spec = PTO_HARNESS_SOURCES.get(harness_name)
                if harness_spec is None:
                    rows.append(
                        stage_row(
                            state,
                            "compiler-contract",
                            "fail",
                            owner="benchmark",
                            evidence=f"unsupported PTO standalone harness: {harness_name}",
                        )
                    )
                    continue
                harness_filename, harness_text = harness_spec
                harness_source = case_artifacts / harness_filename
                linker_script = case_artifacts / "linx-pto-directboot.ld"
                elf = case_artifacts / f"{case.id}.elf"
                harness_source.parent.mkdir(parents=True, exist_ok=True)
                harness_source.write_text(harness_text, encoding="utf-8")
                linker_script.write_text(LINX_DIRECT_BOOT_LINK_SCRIPT, encoding="utf-8")
                cmd = pto_kernel_elf_command(root, case, paths, harness_source, linker_script, elf)
                result = run_command(
                    cmd,
                    cwd=root,
                    env=env,
                    timeout=timeout,
                    log_path=log_path,
                    dry_run=dry_run,
                )
                artifacts.update(
                    {
                        "log": str(log_path),
                        "harness_source": str(harness_source),
                        "linker_script": str(linker_script),
                        "elf": str(elf),
                    }
                )
                status = result["status"]
                evidence = "PTO kernel compiled to standalone Linx ELF"
                if status == "pass":
                    if not dry_run and not elf.exists():
                        status = "fail"
                        evidence = f"expected ELF was not produced: {elf}"
                    else:
                        state.artifacts["elf"] = str(elf)
                        objdump = Path(paths["llvm_objdump"])
                        if dry_run or executable(objdump):
                            dump = run_obj_tool(
                                paths["llvm_objdump"],
                                ["-d", str(elf)],
                                cwd=root,
                                out_path=case_artifacts / "objdump.disasm.txt",
                                timeout=120,
                                dry_run=dry_run,
                            )
                            sym = run_obj_tool(
                                paths["llvm_objdump"],
                                ["-t", str(elf)],
                                cwd=root,
                                out_path=case_artifacts / "objdump.symbols.txt",
                                timeout=120,
                                dry_run=dry_run,
                            )
                            sec = run_obj_tool(
                                paths["llvm_objdump"],
                                ["-h", str(elf)],
                                cwd=root,
                                out_path=case_artifacts / "objdump.sections.txt",
                                timeout=120,
                                dry_run=dry_run,
                            )
                            rel = run_obj_tool(
                                paths["llvm_objdump"],
                                ["-r", str(elf)],
                                cwd=root,
                                out_path=case_artifacts / "objdump.relocs.txt",
                                timeout=120,
                                dry_run=dry_run,
                            )
                            artifacts.update(
                                {
                                    "disasm": dump["output"],
                                    "symbols": sym["output"],
                                    "sections": sec["output"],
                                    "relocations": rel["output"],
                                }
                            )
                            if not dry_run:
                                text = "\n".join(
                                    Path(p).read_text(encoding="utf-8", errors="replace")
                                    for p in [dump["output"], sym["output"], sec["output"], rel["output"]]
                                    if Path(p).exists()
                                )
                                ok, findings = static_check_text(text, require_entry=True)
                                if not ok:
                                    status = "fail"
                                    evidence = "; ".join(findings)
                        objcopy = Path(paths["llvm_objcopy"])
                        if dry_run or executable(objcopy):
                            raw = case_artifacts / f"{case.id}.bin"
                            objcopy_row = run_obj_tool(
                                paths["llvm_objcopy"],
                                ["-O", "binary", str(elf), str(raw)],
                                cwd=root,
                                out_path=case_artifacts / "objcopy.log",
                                timeout=120,
                                dry_run=dry_run,
                            )
                            artifacts["raw_bin"] = str(raw)
                            artifacts["objcopy_log"] = objcopy_row["output"]
                elif status == "not_run":
                    state.artifacts["elf"] = str(elf)
                    evidence = "dry-run standalone PTO compile command recorded"
                else:
                    evidence = "PTO kernel standalone ELF compile/link failed"
                rows.append(
                    stage_row(
                        state,
                        "compiler-contract",
                        status,
                        owner="compiler",
                        evidence=evidence,
                        command=result["command"],
                        artifacts=artifacts,
                    )
                )
                continue

            asm_out = case_artifacts / f"{case.id}.s"
            cmd = pto_compile_command(root, case, paths, asm_out)
            result = run_command(
                cmd,
                cwd=root,
                env=env,
                timeout=timeout,
                log_path=log_path,
                dry_run=dry_run,
            )
            artifacts.update({"log": str(log_path), "asm": str(asm_out)})
            status = result["status"]
            evidence = "PTO kernel compiled to Linx assembly"
            if status == "pass" and asm_out.exists():
                text = asm_out.read_text(encoding="utf-8", errors="replace")
                ok, findings = static_check_text(text, require_entry=False)
                if not ok:
                    status = "fail"
                    evidence = "; ".join(findings)
                state.artifacts["asm"] = str(asm_out)
            elif status == "not_run":
                evidence = "dry-run compile command recorded"
            else:
                evidence = "PTO kernel compile failed"
            rows.append(
                stage_row(
                    state,
                    "compiler-contract",
                    status,
                    owner="compiler",
                    evidence=evidence,
                    command=result["command"],
                    artifacts=artifacts,
                )
            )
            continue

        if case.kind == "supernpu":
            linker_script = case_artifacts / "linx-supernpu-directboot.ld"
            linker_script.parent.mkdir(parents=True, exist_ok=True)
            linker_script.write_text(LINX_DIRECT_BOOT_LINK_SCRIPT, encoding="utf-8")
            artifacts["linker_script"] = str(linker_script)
            supernpu_output = case_artifacts / "supernpu-output"
            elf_dir = supernpu_output / case.suite / "elf"
            artifacts["obj_root"] = str(supernpu_output)
            before_elves = snapshot_elf_mtimes(elf_dir)
            cmd = supernpu_make_command(
                case,
                paths,
                linker_script=linker_script,
                obj_root=supernpu_output,
            )
            result = run_command(
                cmd,
                cwd=case.workdir,
                env=env,
                timeout=timeout,
                log_path=log_path,
                dry_run=dry_run,
            )
            metadata_elf = Path(case.metadata["elf"])
            elf = elf_dir / metadata_elf.name
            artifacts["log"] = str(log_path)
            artifacts["elf_source"] = str(elf)
            status = result["status"]
            evidence = "SuperNPUBench case compiled to Linx ELF"
            owner = "compiler"
            if status == "pass":
                if not dry_run:
                    actual_elf = find_supernpu_elf_after_compile(
                        case,
                        root,
                        before_elves,
                        elf_dir=elf_dir,
                    )
                    if actual_elf is not None:
                        elf = actual_elf
                        artifacts["elf_source"] = str(elf)
                if not dry_run and not elf.exists():
                    status = "fail"
                    owner, evidence = classify_supernpu_missing_elf(log_path, elf)
                else:
                    copied = case_artifacts / f"{case.id}.elf"
                    copied.parent.mkdir(parents=True, exist_ok=True)
                    if not dry_run and elf.exists():
                        shutil.copy2(elf, copied)
                    state.artifacts["elf"] = str(copied)
                    artifacts["elf"] = str(copied)
                    objdump = Path(paths["llvm_objdump"])
                    if dry_run or executable(objdump):
                        dump = run_obj_tool(
                            paths["llvm_objdump"],
                            ["-d", str(copied)],
                            cwd=root,
                            out_path=case_artifacts / "objdump.disasm.txt",
                            timeout=120,
                            dry_run=dry_run,
                        )
                        sym = run_obj_tool(
                            paths["llvm_objdump"],
                            ["-t", str(copied)],
                            cwd=root,
                            out_path=case_artifacts / "objdump.symbols.txt",
                            timeout=120,
                            dry_run=dry_run,
                        )
                        sec = run_obj_tool(
                            paths["llvm_objdump"],
                            ["-h", str(copied)],
                            cwd=root,
                            out_path=case_artifacts / "objdump.sections.txt",
                            timeout=120,
                            dry_run=dry_run,
                        )
                        rel = run_obj_tool(
                            paths["llvm_objdump"],
                            ["-r", str(copied)],
                            cwd=root,
                            out_path=case_artifacts / "objdump.relocs.txt",
                            timeout=120,
                            dry_run=dry_run,
                        )
                        artifacts.update(
                            {
                                "disasm": dump["output"],
                                "symbols": sym["output"],
                                "sections": sec["output"],
                                "relocations": rel["output"],
                            }
                        )
                        if not dry_run:
                            text = "\n".join(
                                Path(p).read_text(encoding="utf-8", errors="replace")
                                for p in [dump["output"], sym["output"], sec["output"], rel["output"]]
                                if Path(p).exists()
                            )
                            ok, findings = static_check_text(text, require_entry=True)
                            if not ok:
                                status = "fail"
                                evidence = "; ".join(findings)
                    objcopy = Path(paths["llvm_objcopy"])
                    if dry_run or executable(objcopy):
                        raw = case_artifacts / f"{case.id}.bin"
                        objcopy_row = run_obj_tool(
                            paths["llvm_objcopy"],
                            ["-O", "binary", str(copied), str(raw)],
                            cwd=root,
                            out_path=case_artifacts / "objcopy.log",
                            timeout=120,
                            dry_run=dry_run,
                        )
                        artifacts["raw_bin"] = str(raw)
                        artifacts["objcopy_log"] = objcopy_row["output"]
            elif status == "not_run":
                copied = case_artifacts / f"{case.id}.elf"
                state.artifacts["elf"] = str(copied)
                artifacts["elf"] = str(copied)
                evidence = "dry-run compile command recorded"
                owner = "compiler"
            else:
                owner, evidence = classify_supernpu_compile_failure(log_path)
            rows.append(
                stage_row(
                    state,
                    "compiler-contract",
                    status,
                    owner=owner,
                    evidence=evidence,
                    command=result["command"],
                    artifacts=artifacts,
                )
            )
            continue

        rows.append(
            stage_row(
                state,
                "compiler-contract",
                "fail",
                owner="compiler",
                evidence=f"unsupported case kind: {case.kind}",
            )
        )
    return rows


def qemu_execution(
    root: Path,
    states: list[CaseState],
    paths: dict[str, str],
    dry_run: bool,
    timeout: int,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    env = os.environ.copy()
    env.setdefault("LINXISA_ROOT", str(root))
    env.setdefault("LINX_VIRT_TEST_FINISHER", "1")
    for state in states:
        case = state.case
        if not case_can_enter(state, "compiler-contract"):
            rows.append(
                stage_row(
                    state,
                    "qemu-execution",
                    "skipped",
                    owner="emulator",
                    evidence="compiler contract did not pass",
                )
            )
            continue
        if not case.produces_elf:
            rows.append(
                stage_row(
                    state,
                    "qemu-execution",
                    "not_applicable",
                    owner="emulator",
                    evidence="case has no standalone ELF harness yet",
                )
            )
            continue
        artifacts: dict[str, str] = {}
        case_artifacts = state.case_dir / "qemu"
        log_path = case_artifacts / "qemu.log"
        if case.kind == "avs_pto":
            out_dir = state.case_dir / "compiler" / "avs"
            cmd = avs_command(root, case, paths, out_dir, timeout=timeout, compile_only=False)
            result = run_command(
                cmd,
                cwd=root,
                env=env,
                timeout=timeout + 120,
                log_path=log_path,
                dry_run=dry_run,
            )
            elf = out_dir / "linx-qemu-tests.elf"
            artifacts.update({"log": str(log_path), "elf": str(elf)})
            if dry_run or elf.exists():
                sidecars = emit_elf_objdump_artifacts(
                    paths=paths,
                    root=root,
                    elf=elf,
                    out_dir=state.case_dir / "compiler",
                    dry_run=dry_run,
                )
                artifacts.update(sidecars)
                state.artifacts.update(sidecars)
            if result["status"] == "pass" or dry_run:
                state.artifacts["elf"] = str(elf)
                if result["status"] == "pass":
                    state.qemu_digests = parse_digests(log_path)
            rows.append(
                stage_row(
                    state,
                    "qemu-execution",
                    result["status"],
                    owner="emulator",
                    evidence="QEMU direct-boot AVS suite passed" if result["status"] == "pass" else "QEMU direct-boot AVS suite failed",
                    command=result["command"],
                    artifacts=artifacts,
                )
            )
            continue
        if case.kind == "pto_kernel":
            elf = Path(state.artifacts.get("elf", ""))
            if not elf.exists() and not dry_run:
                rows.append(
                    stage_row(
                        state,
                        "qemu-execution",
                        "fail",
                        owner="emulator",
                        evidence="missing compiler-produced PTO ELF for QEMU",
                    )
                )
                continue
            cmd = [
                paths["qemu"],
                "-machine",
                "virt",
                "-bios",
                "none",
                "-kernel",
                str(elf),
                "-nographic",
                "-monitor",
                "none",
            ]
            result = run_command(
                cmd,
                cwd=root,
                env=env,
                timeout=timeout,
                log_path=log_path,
                dry_run=dry_run,
            )
            result = normalize_qemu_finisher_result(result, log_path)
            artifacts.update({"log": str(log_path), "elf": str(elf)})
            if result["status"] == "pass":
                state.qemu_digests = parse_digests(log_path)
            rows.append(
                stage_row(
                    state,
                    "qemu-execution",
                    result["status"],
                    owner="emulator",
                    evidence="PTO kernel ELF passed QEMU" if result["status"] == "pass" else "PTO kernel QEMU execution failed",
                    command=result["command"],
                    artifacts=artifacts,
                )
            )
            continue
        if case.kind == "supernpu":
            elf_text = state.artifacts.get("elf")
            if elf_text:
                elf = Path(elf_text)
            else:
                metadata_elf = Path(case.metadata["elf"])
                elf = metadata_elf if metadata_elf.is_absolute() else root / metadata_elf
            if not elf.exists() and not dry_run:
                rows.append(
                    stage_row(
                        state,
                        "qemu-execution",
                        "fail",
                        owner="emulator",
                        evidence="missing compiler-produced ELF for QEMU",
                    )
                )
                continue
            cmd = [
                paths["qemu"],
                "-machine",
                "virt",
                "-bios",
                "none",
                "-kernel",
                str(elf),
                "-nographic",
                "-monitor",
                "none",
            ]
            result = run_command(
                cmd,
                cwd=root,
                env=env,
                timeout=timeout,
                log_path=log_path,
                dry_run=dry_run,
            )
            result = normalize_qemu_finisher_result(result, log_path)
            artifacts.update({"log": str(log_path), "elf": str(elf)})
            if result["status"] == "pass":
                state.qemu_digests = parse_digests(log_path)
            rows.append(
                stage_row(
                    state,
                    "qemu-execution",
                    result["status"],
                    owner="emulator",
                    evidence="SuperNPUBench ELF passed QEMU" if result["status"] == "pass" else "SuperNPUBench QEMU execution failed",
                    command=result["command"],
                    artifacts=artifacts,
                )
            )
            continue
        rows.append(
            stage_row(
                state,
                "qemu-execution",
                "not_applicable",
                owner="emulator",
                evidence=f"QEMU stage not defined for kind {case.kind}",
            )
        )
    return rows


def find_smoke_elf(states: list[CaseState], override: str | None) -> Path | None:
    if override:
        return Path(override).expanduser().resolve()
    return None


def build_model_smoke_elf(
    root: Path,
    paths: dict[str, str],
    stage_dir: Path,
    env: dict[str, str],
    dry_run: bool,
    timeout: int,
) -> tuple[Path, list[dict[str, Any]]]:
    source = stage_dir / "linx-model-smoke.cpp"
    linker = stage_dir / "linx-model-smoke.ld"
    elf = stage_dir / "linx-model-smoke.elf"
    source.write_text(LINX_MODEL_SMOKE_SOURCE, encoding="utf-8")
    linker.write_text(LINX_DIRECT_BOOT_LINK_SCRIPT, encoding="utf-8")
    cmd = [
        paths["clangxx"],
        "-target",
        "linx64-linx-none-elf",
        "-O2",
        "-ffreestanding",
        "-fno-builtin",
        "-fno-stack-protector",
        "-fno-exceptions",
        "-fno-rtti",
        "-nostdlib",
        str(source),
        "-Wl,-e,_start",
        f"-Wl,-T,{linker}",
        "-o",
        str(elf),
    ]
    row = run_command(
        cmd,
        cwd=root,
        env=env,
        timeout=timeout,
        log_path=stage_dir / "linx-model-smoke-compile.log",
        dry_run=dry_run,
    )
    return elf, [row]


def model_build_smoke(
    root: Path,
    states: list[CaseState],
    paths: dict[str, str],
    dry_run: bool,
    build_timeout: int,
    smoke_timeout: int,
    skip_build: bool,
    smoke_elf_override: str | None,
) -> dict[str, Any]:
    model_root = Path(paths["model_root"])
    gfsim = Path(paths["gfsim"])
    if not any(state.case.model_eligible and state.case.produces_elf for state in states):
        row = {
            "stage": "model-build-smoke",
            "status": "not_applicable",
            "owner": "model",
            "evidence": "no selected model-eligible executable cases",
            "gfsim": str(gfsim),
            "smoke_elf": None,
            "commands": [],
        }
        artifacts = {"gfsim": str(gfsim)}
        for state in states:
            state.stages["model-build-smoke"] = {
                "stage": "model-build-smoke",
                "status": "not_applicable",
                "owner": "model",
                "evidence": row["evidence"],
                "command": None,
                "commands": [],
                "artifacts": artifacts,
            }
        return row

    stage_dir = states[0].case_dir.parent / "_model" if states else root / "workloads" / "generated" / "_model"
    stage_dir.mkdir(parents=True, exist_ok=True)
    env = os.environ.copy()
    rows: list[dict[str, Any]] = []
    if not dry_run and not skip_build:
        configure = run_command(
            [
                "cmake",
                "-S",
                str(model_root),
                "-B",
                str(model_root / "build"),
                "-DCMAKE_POLICY_VERSION_MINIMUM=3.5",
                "-DOPT_LEVEL=O3",
                "-DDISABLE_DEBUG_SYMBOLS=ON",
            ],
            cwd=root,
            env=env,
            timeout=build_timeout,
            log_path=stage_dir / "cmake-configure.log",
            dry_run=False,
        )
        rows.append(configure)
        if configure["status"] == "pass":
            build = run_command(
                ["cmake", "--build", str(model_root / "build"), "--target", "gfsim"],
                cwd=root,
                env=env,
                timeout=build_timeout,
                log_path=stage_dir / "cmake-build-gfsim.log",
                dry_run=False,
            )
            rows.append(build)
    elif dry_run:
        rows.append(
            {
                "status": "not_run",
                "command": (
                    f"cmake -S {model_root} -B {model_root / 'build'} "
                    "-DCMAKE_POLICY_VERSION_MINIMUM=3.5 -DOPT_LEVEL=O3 "
                    f"-DDISABLE_DEBUG_SYMBOLS=ON && cmake --build {model_root / 'build'} --target gfsim"
                ),
                "log": str(stage_dir / "cmake-build-gfsim.log"),
            }
        )

    smoke_elf = find_smoke_elf(states, smoke_elf_override)
    if smoke_elf is None:
        smoke_elf, smoke_compile_rows = build_model_smoke_elf(
            root,
            paths,
            stage_dir,
            env,
            dry_run,
            build_timeout,
        )
        rows.extend(smoke_compile_rows)
    else:
        smoke_compile_rows = []

    gfsim_exists = dry_run or executable(gfsim)
    smoke_row: dict[str, Any] | None = None
    if gfsim_exists and smoke_elf is not None:
        smoke_cmd = [str(gfsim), "-f", str(smoke_elf)]
        smoke_row = run_command(
            smoke_cmd,
            cwd=model_root,
            env=env,
            timeout=smoke_timeout,
            log_path=stage_dir / "gfsim-smoke.log",
            dry_run=dry_run,
        )
        rows.append(smoke_row)

    failed_build = next((row for row in rows if row.get("status") not in PASS_STATUSES), None)
    owner = "model"
    if failed_build is not None:
        status = failed_build["status"]
        owner = "compiler" if failed_build in smoke_compile_rows else "model"
        if failed_build in smoke_compile_rows:
            evidence = "model smoke ELF compile timed out" if status == "timeout" else "model smoke ELF compile failed"
        else:
            evidence = "LinxCoreModel build/smoke timed out" if status == "timeout" else "LinxCoreModel build/smoke failed"
    elif not gfsim_exists:
        status = "fail"
        evidence = f"gfsim not found or not executable: {gfsim}"
    elif smoke_elf is None:
        status = "skipped"
        evidence = "no QEMU-passing smoke ELF available yet"
    elif smoke_row and smoke_row["status"] == "not_run":
        status = "not_run"
        evidence = "dry-run model build/smoke recorded"
    else:
        status = "pass"
        evidence = "gfsim available and smoke command passed"

    row = {
        "stage": "model-build-smoke",
        "status": status,
        "owner": owner,
        "evidence": evidence,
        "gfsim": str(gfsim),
        "smoke_elf": str(smoke_elf) if smoke_elf is not None else None,
        "commands": rows,
    }
    artifacts = {
        "gfsim": str(gfsim),
        "configure_log": str(stage_dir / "cmake-configure.log"),
        "build_log": str(stage_dir / "cmake-build-gfsim.log"),
        "smoke_log": str(stage_dir / "gfsim-smoke.log"),
    }
    if smoke_elf is not None:
        artifacts["smoke_elf"] = str(smoke_elf)
    if smoke_elf_override is None:
        artifacts.update(
            {
                "smoke_source": str(stage_dir / "linx-model-smoke.cpp"),
                "smoke_linker_script": str(stage_dir / "linx-model-smoke.ld"),
                "smoke_compile_log": str(stage_dir / "linx-model-smoke-compile.log"),
            }
        )
    for state in states:
        state.stages["model-build-smoke"] = {
            "stage": "model-build-smoke",
            "status": status,
            "owner": owner,
            "evidence": evidence,
            "command": row["commands"][-1]["command"] if row["commands"] else None,
            "commands": rows,
            "artifacts": artifacts,
        }
        if status not in PASS_STATUSES:
            mark_failure(state, "model-build-smoke", owner, evidence)
    return row


def linxcoremodel_execution(
    root: Path,
    states: list[CaseState],
    paths: dict[str, str],
    dry_run: bool,
    timeout: int,
    model_stage_ok: bool,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    model_root = Path(paths["model_root"])
    gfsim = Path(paths["gfsim"])
    env = os.environ.copy()
    for state in states:
        case = state.case
        qemu_row = state.stages.get("qemu-execution")
        if not model_stage_ok:
            rows.append(
                stage_row(
                    state,
                    "linxcoremodel-execution",
                    "skipped",
                    owner="model",
                    evidence="model build/smoke did not pass",
                )
            )
            continue
        if not case.model_eligible or not case.produces_elf:
            rows.append(
                stage_row(
                    state,
                    "linxcoremodel-execution",
                    "not_applicable",
                    owner="model",
                    evidence="case is not model-eligible yet",
                )
            )
            continue
        if qemu_row is None or qemu_row["status"] != "pass":
            rows.append(
                stage_row(
                    state,
                    "linxcoremodel-execution",
                    "skipped",
                    owner="model",
                    evidence="QEMU did not pass for this case",
                )
            )
            continue
        elf = Path(state.artifacts.get("elf", ""))
        if not dry_run and not elf.exists():
            rows.append(
                stage_row(
                    state,
                    "linxcoremodel-execution",
                    "fail",
                    owner="model",
                    evidence=f"missing QEMU-passing ELF: {elf}",
                )
            )
            continue
        log_path = state.case_dir / "model" / "gfsim.log"
        cmd = [str(gfsim), "-f", str(elf)]
        result = run_command(
            cmd,
            cwd=model_root,
            env=env,
            timeout=timeout,
            log_path=log_path,
            dry_run=dry_run,
        )
        if result["status"] == "pass":
            state.model_digests = parse_digests(log_path)
        evidence, diagnostics = summarize_gfsim_log(result["status"], log_path)
        artifacts = {"log": str(log_path), "elf": str(elf)}
        artifacts.update(diagnostics)
        artifacts.update(
            emit_bpc_disassembly_window(
                paths=paths,
                root=root,
                elf=elf,
                bpc=diagnostics.get("last_brob_bpc"),
                out_dir=state.case_dir / "model",
                dry_run=dry_run,
            )
        )
        rows.append(
            stage_row(
                state,
                "linxcoremodel-execution",
                result["status"],
                owner="model",
                evidence=evidence,
                command=result["command"],
                artifacts=artifacts,
            )
        )
    return rows


def differential_triage(states: list[CaseState]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for state in states:
        case = state.case
        qemu = state.qemu_digests
        model = state.model_digests
        status = "pass"
        evidence = "no digest comparison required"
        if qemu and model:
            missing = sorted(set(qemu) ^ set(model))
            mismatched = sorted(k for k in set(qemu) & set(model) if qemu[k] != model[k])
            if missing or mismatched:
                status = "fail"
                evidence = (
                    f"digest mismatch; missing={missing or []}; mismatched={mismatched or []}"
                )
                mark_failure(state, "differential-triage", "model", evidence)
            else:
                evidence = f"{len(qemu)} digest(s) matched between QEMU and model"
        elif qemu and not model:
            model_row = state.stages.get("linxcoremodel-execution", {})
            if model_row.get("status") == "pass":
                status = "fail"
                evidence = "QEMU emitted digests but model emitted none"
                mark_failure(state, "differential-triage", "model", evidence)
            else:
                status = "skipped"
                evidence = "model did not pass, digest comparison skipped"
        elif state.failure_stage:
            status = "skipped"
            evidence = f"first failure already assigned to {state.failure_owner}"
        rows.append(
            stage_row(
                state,
                "differential-triage",
                status,
                owner=state.failure_owner or "integration",
                evidence=evidence,
                artifacts={
                    "qemu_digest_count": str(len(qemu)),
                    "model_digest_count": str(len(model)),
                },
            )
        )
    return rows


def write_fix_packets(out_dir: Path, states: list[CaseState]) -> list[dict[str, Any]]:
    packet_dir = out_dir / "fix-packets"
    rows: list[dict[str, Any]] = []
    for state in states:
        packet_path = packet_dir / f"{state.case.id}.json"
        if not state.failure_stage:
            if packet_path.exists():
                packet_path.unlink()
            rows.append(
                stage_row(
                    state,
                    "fix-packets",
                    "not_applicable",
                    owner="integration",
                    evidence="case is green or only skipped for non-applicable stages",
                )
            )
            continue
        case = state.case
        failed_row = state.stages.get(state.failure_stage, {})
        packet = {
            "schema_version": 1,
            "generated_at_utc": utc_now(),
            "case": {
                "id": case.id,
                "kind": case.kind,
                "suite": case.suite,
                "tier": case.tier,
                "sources": [str(path) for path in case.source_paths],
                "manifest": str(case.manifest_path) if case.manifest_path else None,
                "workdir": str(case.workdir),
                "model_eligible": case.model_eligible,
                "produces_elf": case.produces_elf,
                "expected": case.expected,
                "metadata": case.metadata,
            },
            "failure": {
                "stage": state.failure_stage,
                "owner": state.failure_owner,
                "evidence": state.failure_evidence,
                "row": failed_row,
            },
            "repro": {
                "command": failed_row.get("command"),
                "cwd": str(case.workdir),
                "expected_next_boundary": next_boundary(state.failure_stage),
            },
            "artifacts": state.artifacts,
            "stage_rows": state.stages,
        }
        write_json(packet_path, packet)
        rows.append(
            stage_row(
                state,
                "fix-packets",
                "pass",
                owner="integration",
                evidence=f"fix packet emitted for {state.failure_owner}",
                artifacts={"fix_packet": str(packet_path)},
            )
        )
    return rows


def next_boundary(stage_id: str | None) -> str:
    order = [
        "source-contract",
        "compiler-contract",
        "qemu-execution",
        "model-build-smoke",
        "linxcoremodel-execution",
        "differential-triage",
    ]
    if stage_id not in order:
        return "source-contract"
    idx = order.index(stage_id)
    return order[min(idx + 1, len(order) - 1)]


def write_skill_doc_evolution(out_dir: Path, states: list[CaseState], evolve_note: str | None = None) -> dict[str, Any]:
    counts: dict[str, int] = {}
    for state in states:
        if state.failure_owner:
            counts[state.failure_owner] = counts.get(state.failure_owner, 0) + 1
    if evolve_note:
        note = evolve_note.strip()
        if note.startswith(("updated", "no-update")):
            line = f"skill-evolve: {note}"
        else:
            line = f"skill-evolve: updated {note}"
    else:
        line = "skill-evolve: no-update (runner emitted reusable evidence; update skills only after a material repeated finding)"
    payload = {
        "stage": "skill-doc-evolution",
        "status": "pass",
        "owner": "docs-skills",
        "generated_at_utc": utc_now(),
        "skill_evolve": line,
        "failure_owner_counts": counts,
        "documentation": [
            "docs/bringup/ai_workload_bringup_flow.json",
            "tools/bringup/run_ai_workload_flow.py",
        ],
    }
    write_json(out_dir / "skill_evolution.json", payload)
    (out_dir / "skill_evolution.md").write_text(
        "# Skill And Documentation Evolution\n\n"
        f"- {line}\n"
        f"- Failure owner counts: `{json.dumps(counts, sort_keys=True)}`\n",
        encoding="utf-8",
    )
    return payload


def stage_failed(rows: list[dict[str, Any]] | dict[str, Any]) -> bool:
    if isinstance(rows, dict):
        return rows.get("status") not in PASS_STATUSES
    return any(row.get("status") not in PASS_STATUSES for row in rows)


def case_final_status(state: CaseState, emitted_stage_ids: set[str]) -> str:
    if state.failure_stage:
        return "fail"
    if "linxcoremodel-execution" not in emitted_stage_ids:
        return "pending"
    model_row = state.stages.get("linxcoremodel-execution")
    if not model_row:
        return "pending"
    return model_row.get("status", "pending")


def case_summary(state: CaseState, emitted_stage_ids: set[str]) -> dict[str, Any]:
    final_status = case_final_status(state, emitted_stage_ids)
    return {
        "id": state.case.id,
        "kind": state.case.kind,
        "suite": state.case.suite,
        "tier": state.case.tier,
        "final_status": final_status,
        "failure_stage": state.failure_stage,
        "failure_owner": state.failure_owner,
        "failure_evidence": state.failure_evidence,
        "artifacts": state.artifacts,
        "stages": state.stages,
    }


def write_manifest(
    root: Path,
    out_dir: Path,
    *,
    flow: dict[str, Any],
    profile: str,
    tiers: set[int],
    dry_run: bool,
    paths: dict[str, str],
    cases: list[Case],
) -> None:
    submodules = [
        "compiler/llvm",
        "emulator/qemu",
        "tools/LinxCoreModel",
        "tools/model",
        "workloads/pto_kernels",
        "workloads/SuperNPUBench",
        "skills/linx-skills",
    ]
    payload = {
        "schema_version": 1,
        "generated_at_utc": utc_now(),
        "flow_id": flow.get("flow_id"),
        "profile": profile,
        "tiers": sorted(tiers),
        "dry_run": dry_run,
        "repo_root": str(root),
        "tools": tool_manifest(paths),
        "submodules": {rel: submodule_sha(root, rel) for rel in submodules},
        "cases": [
            {
                "id": case.id,
                "kind": case.kind,
                "suite": case.suite,
                "tier": case.tier,
                "sources": [relpath(root, p) for p in case.source_paths],
                "manifest": relpath(root, case.manifest_path) if case.manifest_path else None,
                "model_eligible": case.model_eligible,
                "produces_elf": case.produces_elf,
                "expected": case.expected,
                "metadata": case.metadata,
            }
            for case in cases
        ],
    }
    write_json(out_dir / "manifest.json", payload)


def write_report(
    out_dir: Path,
    *,
    flow: dict[str, Any],
    profile: str,
    tiers: set[int],
    dry_run: bool,
    stages: list[dict[str, Any]],
    states: list[CaseState],
    skill_evolution: dict[str, Any] | None,
) -> None:
    emitted_stage_ids = {stage["id"] for stage in stages}
    case_summaries = [case_summary(state, emitted_stage_ids) for state in states]
    payload = {
        "schema_version": 1,
        "generated_at_utc": utc_now(),
        "flow_id": flow.get("flow_id"),
        "profile": profile,
        "tiers": sorted(tiers),
        "dry_run": dry_run,
        "ok": all(summary["final_status"] in PASS_STATUSES for summary in case_summaries),
        "stages": stages,
        "cases": case_summaries,
        "skill_evolution": skill_evolution,
    }
    write_json(out_dir / "report.json", payload)


def write_summary(
    out_dir: Path,
    states: list[CaseState],
    skill_evolution: dict[str, Any] | None,
    stages: list[dict[str, Any]],
) -> None:
    emitted_stage_ids = {stage["id"] for stage in stages}
    summaries = [case_summary(state, emitted_stage_ids) for state in states]
    total = len(states)
    failures = [s for s in states if s.failure_stage]
    pending = [summary for summary in summaries if summary["final_status"] == "pending"]
    final_green = [
        s
        for s in states
        if not s.failure_stage
        and s.stages.get("linxcoremodel-execution", {}).get("status") == "pass"
    ]
    lines = [
        "# AI Workload Bring-Up Summary",
        "",
        f"- Generated (UTC): `{utc_now()}`",
        f"- Cases selected: `{total}`",
        f"- Final model green: `{len(final_green)}`",
        f"- Failed cases: `{len(failures)}`",
        f"- Pending cases: `{len(pending)}`",
        "",
        "| Case | Kind | Tier | Final | First Owner | Evidence |",
        "|---|---:|---:|---|---|---|",
    ]
    for state, summary in zip(states, summaries, strict=True):
        evidence = (summary.get("failure_evidence") or "").replace("|", "\\|")
        lines.append(
            f"| `{state.case.id}` | `{state.case.kind}` | `{state.case.tier}` | "
            f"`{summary['final_status']}` | `{summary.get('failure_owner') or '-'}` | {evidence or '-'} |"
        )
    if skill_evolution:
        lines += ["", "## Skill Evolution", "", f"- {skill_evolution['skill_evolve']}"]
    (out_dir / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def print_stage_list(stages: list[dict[str, Any]], cases: list[Case]) -> None:
    for idx, stage in enumerate(stages, start=1):
        hard = "hard-break" if stage.get("hard_break", True) else "non-blocking"
        print(f"{idx}. {stage['id']} [{stage.get('owner', 'unknown')}/{hard}]")
        if stage.get("why"):
            print(f"   {stage['why']}")
    print()
    for case in cases:
        print(f"{case.id} [{case.kind}/tier-{case.tier}] {case.suite}")


def main(argv: list[str]) -> int:
    root = repo_root()
    ap = argparse.ArgumentParser(
        description="Run the AI workload hard-break flow through Linx LLVM, QEMU, and LinxCoreModel."
    )
    ap.add_argument("--flow", default=str(default_flow_path(root)))
    ap.add_argument("--profile", default="smoke")
    ap.add_argument("--tier", type=int, action="append", default=[], help="Override profile tiers; may repeat")
    ap.add_argument(
        "--case",
        action="append",
        default=[],
        help="Select cases whose id/suite/kind contains this text; prefix with '=' for an exact id/suite/kind match; may repeat",
    )
    ap.add_argument("--kind", action="append", choices=["avs_pto", "pto_kernel", "supernpu"], default=[])
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--stage", action="append", default=[], help="Run one stage id; may repeat")
    ap.add_argument("--start-at", default=None)
    ap.add_argument("--stop-after", default=None)
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--continue-on-fail", action="store_true")
    ap.add_argument("--run-id", default=default_run_id())
    ap.add_argument("--out-dir", default="")
    ap.add_argument("--clang", default="")
    ap.add_argument("--clangxx", default="")
    ap.add_argument("--lld", default="")
    ap.add_argument("--llvm-objdump", default="")
    ap.add_argument("--llvm-objcopy", default="")
    ap.add_argument("--qemu", default="")
    ap.add_argument("--model-root", default="")
    ap.add_argument("--gfsim", default="")
    ap.add_argument("--model-smoke-elf", default="")
    ap.add_argument("--skip-model-build", action="store_true")
    ap.add_argument("--skill-evolve-note", default="", help="Emit `skill-evolve: update <note>` in the run closeout")
    ap.add_argument("--compile-timeout", type=int, default=900)
    ap.add_argument("--qemu-timeout", type=int, default=240)
    ap.add_argument("--model-timeout", type=int, default=600)
    ap.add_argument("--model-build-timeout", type=int, default=3600)
    args = ap.parse_args(argv)

    flow_path = Path(args.flow).resolve()
    flow = load_flow(flow_path)
    stages = selected_stages(flow, args.profile, args.stage, args.start_at, args.stop_after)
    tiers = profile_tiers(flow, args.profile, args.tier)
    all_cases = discover_cases(root)
    cases = filter_cases(all_cases, tiers, args.kind, args.case, args.limit)
    if not cases:
        raise SystemExit("error: no cases selected")

    if args.list:
        print_stage_list(stages, cases)
        return 0

    out_dir = Path(args.out_dir).expanduser().resolve() if args.out_dir else root / "workloads" / "generated" / args.run_id / "ai-bringup"
    out_dir.mkdir(parents=True, exist_ok=True)
    paths = tool_paths(root, args)
    states = [CaseState(case=case, case_dir=out_dir / "cases" / case.id) for case in cases]
    write_manifest(
        root,
        out_dir,
        flow=flow,
        profile=args.profile,
        tiers=tiers,
        dry_run=args.dry_run,
        paths=paths,
        cases=cases,
    )

    stage_reports: list[dict[str, Any]] = []
    failed = False
    model_stage_status = True
    skill_evolution: dict[str, Any] | None = None

    for stage in stages:
        stage_id = stage["id"]
        print(f"== {stage_id} ({stage.get('owner', 'unknown')})")
        if stage_id == "source-contract":
            rows: list[dict[str, Any]] | dict[str, Any] = source_contract(root, states, args.dry_run)
        elif stage_id == "compiler-contract":
            rows = compiler_contract(root, states, paths, args.dry_run, args.compile_timeout)
        elif stage_id == "qemu-execution":
            rows = qemu_execution(root, states, paths, args.dry_run, args.qemu_timeout)
        elif stage_id == "model-build-smoke":
            rows = model_build_smoke(
                root,
                states,
                paths,
                args.dry_run,
                args.model_build_timeout,
                args.model_timeout,
                args.skip_model_build,
                args.model_smoke_elf or None,
            )
            model_stage_status = rows.get("status") in PASS_STATUSES
        elif stage_id == "linxcoremodel-execution":
            rows = linxcoremodel_execution(
                root,
                states,
                paths,
                args.dry_run,
                args.model_timeout,
                model_stage_status,
            )
        elif stage_id == "differential-triage":
            rows = differential_triage(states)
        elif stage_id == "fix-packets":
            rows = write_fix_packets(out_dir, states)
        elif stage_id == "skill-doc-evolution":
            skill_evolution = write_skill_doc_evolution(out_dir, states, args.skill_evolve_note or None)
            rows = skill_evolution
        else:
            raise SystemExit(f"error: unsupported stage id in flow: {stage_id}")

        stage_reports.append(
            {
                "id": stage_id,
                "owner": stage.get("owner"),
                "hard_break": bool(stage.get("hard_break", True)),
                "result": rows,
            }
        )
        write_report(
            out_dir,
            flow=flow,
            profile=args.profile,
            tiers=tiers,
            dry_run=args.dry_run,
            stages=stage_reports,
            states=states,
            skill_evolution=skill_evolution,
        )
        write_summary(out_dir, states, skill_evolution, stage_reports)
        if stage_failed(rows):
            failed = True
            if stage.get("hard_break", True) and not args.continue_on_fail:
                print(f"hard-break: stopping at stage {stage_id}")
                break

    emitted_stage_ids = {stage["id"] for stage in stage_reports}
    if any(state.failure_stage for state in states) and "fix-packets" not in emitted_stage_ids:
        rows = write_fix_packets(out_dir, states)
        stage_reports.append(
            {
                "id": "fix-packets",
                "owner": "integration",
                "hard_break": False,
                "result": rows,
            }
        )

    if skill_evolution is None:
        skill_evolution = write_skill_doc_evolution(out_dir, states)
        stage_reports.append(
            {
                "id": "skill-doc-evolution",
                "owner": "docs-skills",
                "hard_break": False,
                "result": skill_evolution,
            }
        )

    write_report(
        out_dir,
        flow=flow,
        profile=args.profile,
        tiers=tiers,
        dry_run=args.dry_run,
        stages=stage_reports,
        states=states,
        skill_evolution=skill_evolution,
    )
    write_summary(out_dir, states, skill_evolution, stage_reports)

    print(f"manifest: {out_dir / 'manifest.json'}")
    print(f"report: {out_dir / 'report.json'}")
    print(f"summary: {out_dir / 'summary.md'}")
    if failed:
        return 1
    print("ok: AI workload flow complete" if not args.dry_run else "ok: AI workload dry-run complete")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
