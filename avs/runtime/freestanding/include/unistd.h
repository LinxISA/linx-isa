#ifndef _LINX_UNISTD_H
#define _LINX_UNISTD_H

/* Minimal `unistd.h` for freestanding bring-up.
 *
 * This header exists to unblock third-party C benchmarks that include common
 * POSIX headers but do not require full OS services in the bring-up profile.
 *
 * Add declarations here only when needed by workloads.
 */

#include <stddef.h>
#include <stdint.h>

#ifndef _LINX_SSIZE_T_DEFINED
#define _LINX_SSIZE_T_DEFINED 1
typedef ptrdiff_t ssize_t;
#endif

#ifndef _LINX_OFF_T_DEFINED
#define _LINX_OFF_T_DEFINED 1
typedef int64_t off_t;
#endif

#define STDIN_FILENO  0
#define STDOUT_FILENO 1
#define STDERR_FILENO 2

#define SEEK_SET 0
#define SEEK_CUR 1
#define SEEK_END 2

#ifdef __cplusplus
extern "C" {
#endif

ssize_t read(int fd, void *buf, size_t count);
ssize_t write(int fd, const void *buf, size_t count);
int open(const char *pathname, int flags, int mode);
int close(int fd);
void *brk(void *addr);
off_t lseek(int fd, off_t offset, int whence);
void *mmap(void *addr, size_t length, int prot, int flags, int fd,
           off_t offset);
int munmap(void *addr, size_t length);
int getpid(void);
void _exit(int status) __attribute__((noreturn));

#ifdef __cplusplus
}
#endif

#endif /* _LINX_UNISTD_H */
