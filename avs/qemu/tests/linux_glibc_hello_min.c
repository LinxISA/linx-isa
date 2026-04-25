extern int open(const char *path, int flags, ...);
extern int dup2(int oldfd, int newfd);
extern int close(int fd);
extern long write(int fd, const void *buf, unsigned long count);
extern void sync(void);
extern int reboot(int howto);

#define O_RDWR 2
#define STDIN_FILENO 0
#define STDOUT_FILENO 1
#define STDERR_FILENO 2
#define RB_POWER_OFF 0x4321fedc

static void emit_marker(const char *s)
{
    const char *p = s;
    while (*p) {
        ++p;
    }
    (void)write(STDOUT_FILENO, s, (unsigned long)(p - s));
    (void)write(STDOUT_FILENO, "\n", 1);
}

int main(void)
{
    int cfd = open("/dev/console", O_RDWR);
    if (cfd >= 0) {
        (void)dup2(cfd, STDIN_FILENO);
        (void)dup2(cfd, STDOUT_FILENO);
        (void)dup2(cfd, STDERR_FILENO);
        if (cfd > STDERR_FILENO) {
            (void)close(cfd);
        }
    }

    emit_marker("GLIBC_HELLO_START");
    emit_marker("Hello, Linx ISA Linux via QEMU (glibc)");
    emit_marker("GLIBC_HELLO_PASS");

    sync();
    reboot(RB_POWER_OFF);
    return 0;
}
