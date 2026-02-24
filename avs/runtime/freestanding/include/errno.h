#ifndef _LINX_ERRNO_H
#define _LINX_ERRNO_H

/* Minimal errno set for freestanding runtime bring-up. */
#define EPERM    1
#define ENOENT   2
#define EBADF    9
#define EFAULT   14
#define EBUSY    16
#define EEXIST   17
#define ENODEV   19
#define EINVAL   22
#define ENOSPC   28
#define ENOSYS   38

extern int errno;

#endif /* _LINX_ERRNO_H */
