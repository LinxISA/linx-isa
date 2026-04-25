#include <errno.h>
#include <fcntl.h>
#include <stdint.h>
#include <stdarg.h>
#include <stdio.h>
#include <sys/mman.h>
#include <unistd.h>

static void log_line(const char *fmt, ...) {
  va_list ap;

  va_start(ap, fmt);
  vdprintf(1, fmt, ap);
  va_end(ap);
}

static void probe_map(const char *label, int fd, void *addr, size_t len,
                      int prot, int flags, off_t off) {
  errno = 0;
  void *ret = mmap(addr, len, prot, flags, fd, off);
  log_line("%s addr=%p len=%#lx prot=%#x flags=%#x off=%#lx ret=%p errno=%d\n",
           label, addr, (unsigned long)len, prot, flags, (unsigned long)off,
           ret, errno);
  if (ret != MAP_FAILED && ret != addr && addr != NULL)
    munmap(ret, len);
}

int main(void) {
  const size_t maplen = 0x161ca9;
  const uintptr_t seg0 = 0x0;
  const uintptr_t seg1 = 0x47000;
  const size_t seg0_len = 0x47000;
  const size_t seg1_len = 0x10d000;
  int console = open("/dev/console", O_RDWR);
  if (console >= 0) {
    dup2(console, 0);
    dup2(console, 1);
    dup2(console, 2);
    if (console > 2)
      close(console);
  }
  int fd = open("/lib/libc.so.6", O_RDONLY);
  if (fd < 0) {
    log_line("OPEN_FAIL errno=%d\n", errno);
    return 1;
  }

  errno = 0;
  void *base = mmap(NULL, maplen, PROT_READ, MAP_PRIVATE, fd, 0);
  log_line("RESERVE ret=%p errno=%d\n", base, errno);
  if (base == MAP_FAILED)
    return 2;

  if (munmap(base, maplen) != 0) {
    log_line("UNMAP_FAIL errno=%d\n", errno);
    return 3;
  }

  probe_map("HINT_SEG0", fd, (void *)((uintptr_t)base + seg0), seg0_len,
            PROT_READ, MAP_PRIVATE, 0);
  probe_map("HINT_SEG1", fd, (void *)((uintptr_t)base + seg1), seg1_len,
            PROT_READ | PROT_EXEC, MAP_PRIVATE, 0x46000);
  probe_map("FIXED_SEG0", fd, (void *)((uintptr_t)base + seg0), seg0_len,
            PROT_READ, MAP_PRIVATE | MAP_FIXED, 0);
  probe_map("FIXED_SEG1", fd, (void *)((uintptr_t)base + seg1), seg1_len,
            PROT_READ | PROT_EXEC, MAP_PRIVATE | MAP_FIXED, 0x46000);
#ifdef MAP_FIXED_NOREPLACE
  probe_map("NOREPLACE_SEG0", fd, (void *)((uintptr_t)base + seg0), seg0_len,
            PROT_READ, MAP_PRIVATE | MAP_FIXED_NOREPLACE, 0);
  probe_map("NOREPLACE_SEG1", fd, (void *)((uintptr_t)base + seg1), seg1_len,
            PROT_READ | PROT_EXEC, MAP_PRIVATE | MAP_FIXED_NOREPLACE, 0x46000);
#endif

  close(fd);
  log_line("MMAP_PROBE_DONE\n");
  return 0;
}
