/*
 * Minimal LinxISA QEMU Test with BSTART
 * 
 * This test verifies that QEMU can:
 * 1. Load and execute an ELF .o file
 * 2. Execute basic LinxISA instructions
 * 3. Exit cleanly without hanging
 */

#include <stdint.h>

/* UART addresses */
#define UART_BASE          0x10000000
#define TEST_FINISHER_MMIO 0x10009000
#define UART_DR            (*(volatile uint32_t *)(UART_BASE + 0x00))
#define TEST_FINISHER      (*(volatile uint32_t *)(TEST_FINISHER_MMIO))
#define FINISHER_PASS      0x5555u

/* Output a character */
static inline void uart_putc(char c) {
    UART_DR = (uint32_t)(unsigned char)c;
}

/* _start - Entry point with BSTART */
void _start(void) {
    /* Output 'OK' to UART - wrapped in block */
    __asm__ volatile ("BSTART.STD" ::: "memory");
    uart_putc('O');
    uart_putc('K');
    uart_putc('\r');
    uart_putc('\n');
    __asm__ volatile ("BSTOP" ::: "memory");
    
    /* Exit with success code */
    __asm__ volatile (
        "BSTART.STD\n"
        "lui 65545, ->u\n"
        "lui 5, ->t\n"
        "addi t#1, 1365, ->t\n"
        "c.swi t#1, [u#1, 0]\n"
        "BSTOP\n"
        ::: "memory");
    while (1) {}
}
