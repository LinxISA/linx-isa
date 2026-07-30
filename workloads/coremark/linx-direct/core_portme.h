/*
 * Freestanding LinxISA CoreMark port for semantic direct-boot validation.
 *
 * This port intentionally exposes a deterministic synthetic timer. Results
 * prove workload correctness only; they are not CoreMark performance scores.
 */
#ifndef CORE_PORTME_H
#define CORE_PORTME_H

#include <stddef.h>
#include <stdint.h>

#ifndef HAS_FLOAT
#define HAS_FLOAT 0
#endif
#ifndef HAS_TIME_H
#define HAS_TIME_H 0
#endif
#ifndef HAS_STDIO
#define HAS_STDIO 1
#endif
#ifndef HAS_PRINTF
#define HAS_PRINTF 1
#endif
#ifndef MULTITHREAD
#define MULTITHREAD 1
#endif
#ifndef USE_PTHREAD
#define USE_PTHREAD 0
#endif
#ifndef USE_FORK
#define USE_FORK 0
#endif
#ifndef USE_SOCKET
#define USE_SOCKET 0
#endif
#ifndef MAIN_HAS_NOARGC
#define MAIN_HAS_NOARGC 0
#endif
#ifndef MAIN_HAS_NORETURN
#define MAIN_HAS_NORETURN 0
#endif
#ifndef SEED_METHOD
#define SEED_METHOD SEED_VOLATILE
#endif
#ifndef MEM_METHOD
#define MEM_METHOD MEM_STATIC
#endif

#define COMPILER_VERSION "LinxISA Clang direct-boot"
#ifndef FLAGS_STR
#define FLAGS_STR "semantic direct-boot"
#endif
#define COMPILER_FLAGS FLAGS_STR
#ifndef MEM_LOCATION
#define MEM_LOCATION "STATIC"
#endif

typedef signed short ee_s16;
typedef unsigned short ee_u16;
typedef signed int ee_s32;
typedef double ee_f32;
typedef unsigned char ee_u8;
typedef unsigned int ee_u32;
typedef uintptr_t ee_ptr_int;
typedef size_t ee_size_t;
typedef ee_u32 CORE_TICKS;

#define align_mem(x) (void *)(4 + (((ee_ptr_int)(x) - 1) & ~(ee_ptr_int)3))

typedef struct CORE_PORTABLE_S {
    ee_u8 portable_id;
} core_portable;

extern ee_u32 default_num_contexts;

void portable_init(core_portable *portable, int *argc, char *argv[]);
void portable_fini(core_portable *portable);

#if !defined(PROFILE_RUN) && !defined(PERFORMANCE_RUN) && !defined(VALIDATION_RUN)
#if (TOTAL_DATA_SIZE == 1200)
#define PROFILE_RUN 1
#elif (TOTAL_DATA_SIZE == 2000)
#define PERFORMANCE_RUN 1
#else
#define VALIDATION_RUN 1
#endif
#endif

#endif
