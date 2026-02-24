/*
 * linx-libc: LinxISA-specific system call stubs
 *
 * These functions provide the interface between the C library
 * and the underlying LinxISA system.
 */

#include <errno.h>
#include <linxisa_libc.h>
#include <linxisa_syscall.h>

/* File descriptors */
#define STDIN_FILENO  0
#define STDOUT_FILENO 1
#define STDERR_FILENO 2

/* QEMU virt UART + shutdown MMIO (freestanding profile). */
#define LINX_UART_BASE      0x10000000u
#define LINX_EXIT_REG_INDEX 1u

int errno;

static ssize_t linx_fail_ssize(int err)
{
    errno = err;
    return -1;
}

static int linx_fail_int(int err)
{
    errno = err;
    return -1;
}

static off_t linx_fail_off_t(int err)
{
    errno = err;
    return (off_t)-1;
}

static void *linx_fail_ptr(int err)
{
    errno = err;
    return (void *)-1;
}

/*
 * __linx_putchar - Write a character to stdout
 *
 * This is the core output function. On real hardware/emulator,
 * this would make a syscall to write to a console or UART.
 */
void __linx_putchar(int c) {
    volatile unsigned char *uart = (volatile unsigned char *)LINX_UART_BASE;
    *uart = (unsigned char)c;
}

/*
 * __linx_puts - Write a null-terminated string to stdout
 */
void __linx_puts(const char *s) {
    while (*s) {
        __linx_putchar(*s++);
    }
    __linx_putchar('\n');
}

/*
 * __linx_exit - Terminate the program
 * 
 * This should never return - the program is terminated.
 */
void __linx_exit(int code) {
    /* Exit register is at UART base + 0x4 (virt machine). */
    volatile unsigned int *mmio = (volatile unsigned int *)LINX_UART_BASE;
    mmio[LINX_EXIT_REG_INDEX] = (unsigned int)code;

    /* If exit doesn't halt, loop forever */
    while (1) {
        __asm__ volatile ("" ::: "memory");
    }
}

/*
 * __linx_read - Read from a file descriptor
 *
 * Returns the number of bytes read, or -1 on error.
 */
ssize_t __linx_read(int fd, void *buf, size_t count) {
    (void)fd;
    (void)buf;
    (void)count;
    return linx_fail_ssize(ENOSYS);
}

/*
 * __linx_write - Write to a file descriptor
 *
 * Returns the number of bytes written, or -1 on error.
 */
ssize_t __linx_write(int fd, const void *buf, size_t count) {
    if (!buf && count != 0) {
        return linx_fail_ssize(EFAULT);
    }
    if (fd == STDOUT_FILENO || fd == STDERR_FILENO) {
        const char *p = (const char *)buf;
        size_t written = 0;
        while (written < count) {
            __linx_putchar(p[written++]);
        }
        if (written > 0x7fffffffU) {
            return 0x7fffffff;
        }
        errno = 0;
        return (int)written;
    }
    return linx_fail_ssize(ENOSYS);
}

/*
 * __linx_open - Open a file
 *
 * Returns a file descriptor, or -1 on error.
 */
int __linx_open(const char *pathname, int flags, int mode) {
    (void)pathname;
    (void)flags;
    (void)mode;
    return linx_fail_int(ENOSYS);
}

/*
 * __linx_close - Close a file descriptor
 */
int __linx_close(int fd) {
    (void)fd;
    return linx_fail_int(ENOSYS);
}

/*
 * __linx_brk - Change data segment size
 */
void *__linx_brk(void *addr) {
    (void)addr;
    return linx_fail_ptr(ENOSYS);
}

off_t __linx_lseek(int fd, off_t offset, int whence)
{
    (void)fd;
    (void)offset;
    (void)whence;
    return linx_fail_off_t(ENOSYS);
}

void *__linx_mmap(void *addr, size_t length, int prot, int flags, int fd,
                  off_t offset)
{
    (void)addr;
    (void)length;
    (void)prot;
    (void)flags;
    (void)fd;
    (void)offset;
    return linx_fail_ptr(ENOSYS);
}

int __linx_munmap(void *addr, size_t length)
{
    (void)addr;
    (void)length;
    return linx_fail_int(ENOSYS);
}

int __linx_getpid(void)
{
    return linx_fail_int(ENOSYS);
}

ssize_t read(int fd, void *buf, size_t count)
{
    return __linx_read(fd, buf, count);
}

ssize_t write(int fd, const void *buf, size_t count)
{
    return __linx_write(fd, buf, count);
}

int open(const char *pathname, int flags, int mode)
{
    return __linx_open(pathname, flags, mode);
}

int close(int fd)
{
    return __linx_close(fd);
}

void *brk(void *addr)
{
    return __linx_brk(addr);
}

off_t lseek(int fd, off_t offset, int whence)
{
    return __linx_lseek(fd, offset, whence);
}

void *mmap(void *addr, size_t length, int prot, int flags, int fd,
           off_t offset)
{
    return __linx_mmap(addr, length, prot, flags, fd, offset);
}

int munmap(void *addr, size_t length)
{
    return __linx_munmap(addr, length);
}

int getpid(void)
{
    return __linx_getpid();
}
