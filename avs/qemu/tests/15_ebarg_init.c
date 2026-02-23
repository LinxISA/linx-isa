// Minimal PID1 used by AVS linux boot smoke.
// It keeps userspace alive while the kernel prints its EBARG selftest result.

#include <unistd.h>

int main(void)
{
    static const char msg[] = "EBARG_INIT_START\n";
    (void)write(1, msg, sizeof(msg) - 1);

    for (;;) {
        __asm__ volatile("" ::: "memory");
    }
}
