// Minimal PID1 used by AVS linux boot smoke.
// It keeps userspace alive while the kernel prints its EBARG selftest result.

#include <fcntl.h>
#include <unistd.h>

int main(void)
{
    int cfd = open("/dev/console", O_RDWR);
    if (cfd >= 0) {
        (void)dup2(cfd, STDIN_FILENO);
        (void)dup2(cfd, STDOUT_FILENO);
        (void)dup2(cfd, STDERR_FILENO);
        if (cfd > STDERR_FILENO)
            (void)close(cfd);
    }

    static const char msg[] = "EBARG_INIT_START\n";
    (void)write(1, msg, sizeof(msg) - 1);

    for (;;) {
        __asm__ volatile("" ::: "memory");
    }
}
