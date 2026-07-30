/*
 * Freestanding LinxISA CoreMark port for semantic direct-boot validation.
 */
#include <stddef.h>

#include "coremark.h"

#if (MEM_METHOD == MEM_MALLOC)
#include <stdlib.h>
#endif

#if VALIDATION_RUN
volatile ee_s32 seed1_volatile = 0x3415;
volatile ee_s32 seed2_volatile = 0x3415;
volatile ee_s32 seed3_volatile = 0x66;
#endif
#if PERFORMANCE_RUN
volatile ee_s32 seed1_volatile = 0x0;
volatile ee_s32 seed2_volatile = 0x0;
volatile ee_s32 seed3_volatile = 0x66;
#endif
#if PROFILE_RUN
volatile ee_s32 seed1_volatile = 0x8;
volatile ee_s32 seed2_volatile = 0x8;
volatile ee_s32 seed3_volatile = 0x8;
#endif
volatile ee_s32 seed4_volatile = ITERATIONS;
volatile ee_s32 seed5_volatile = 0;

static CORE_TICKS direct_ticks;
static CORE_TICKS start_ticks;
static CORE_TICKS stop_ticks;

ee_u32 default_num_contexts = 1;

void start_time(void)
{
    start_ticks = direct_ticks++;
}

void stop_time(void)
{
    direct_ticks = start_ticks + 10;
    stop_ticks = direct_ticks;
}

CORE_TICKS get_time(void)
{
    return stop_ticks - start_ticks;
}

secs_ret time_in_secs(CORE_TICKS ticks)
{
    return ticks;
}

void portable_init(core_portable *portable, int *argc, char *argv[])
{
    (void)argc;
    (void)argv;
    portable->portable_id = 1;
}

void portable_fini(core_portable *portable)
{
    portable->portable_id = 0;
}

void *portable_malloc(ee_size_t size)
{
#if (MEM_METHOD == MEM_MALLOC)
    return malloc(size);
#else
    (void)size;
    return NULL;
#endif
}

void portable_free(void *ptr)
{
#if (MEM_METHOD == MEM_MALLOC)
    free(ptr);
#else
    (void)ptr;
#endif
}
