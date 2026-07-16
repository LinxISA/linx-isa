#include <errno.h>
#include <fcntl.h>
#include <stdio.h>
#include <stdlib.h>
#include <sys/reboot.h>
#include <sys/wait.h>
#include <unistd.h>

static void setup_stdio(void)
{
    int fd = open("/dev/ttyS0", O_RDWR);

    if (fd < 0)
        return;
    for (int target = STDIN_FILENO; target <= STDERR_FILENO; ++target) {
        if (fd != target)
            (void)dup2(fd, target);
    }
    if (fd > STDERR_FILENO)
        (void)close(fd);
}

int main(void)
{
    char *const argv[] = {"/bench", NULL};
    char *const envp[] = {"PATH=/bin:/sbin:/usr/bin:/usr/sbin", NULL};
    int status = 0;
    pid_t child;
    pid_t waited;
    int code = 126;

    setup_stdio();
    puts("LINX_BENCH_START");
    fflush(stdout);

    child = fork();
    if (child == 0) {
        execve(argv[0], argv, envp);
        perror("LINX_BENCH_EXEC_FAIL");
        _exit(127);
    }
    if (child < 0) {
        perror("LINX_BENCH_FORK_FAIL");
    } else {
        do {
            waited = waitpid(child, &status, 0);
        } while (waited < 0 && errno == EINTR);
        if (waited == child && WIFEXITED(status))
            code = WEXITSTATUS(status);
        else if (waited == child && WIFSIGNALED(status))
            code = 128 + WTERMSIG(status);
        else
            perror("LINX_BENCH_WAIT_FAIL");
    }

    printf("LINX_BENCH_EXIT rc=%d\n", code);
    fflush(stdout);
    sync();
    (void)reboot(RB_POWER_OFF);
    _exit(code == 0 ? 125 : code);
}
