/* Canonical direct-boot entry; the platform supplies the initial stack. */
extern int main(void);
extern void __linx_exit(int code) __attribute__((noreturn));

void _start(void) __attribute__((noreturn, section(".text.startup")));

void _start(void)
{
    __linx_exit(main());
}
