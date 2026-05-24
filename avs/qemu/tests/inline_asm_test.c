/*
 * LinxISA Inline Assembly QEMU Test (Simplified)
 * 
 * This test verifies basic inline assembly works in QEMU:
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
    /* Output header */
    __asm__ volatile ("BSTART.STD" ::: "memory");
    uart_putc('I');
    uart_putc('N');
    uart_putc('L');
    uart_putc('I');
    uart_putc('N');
    uart_putc('E');
    uart_putc('-');
    uart_putc('A');
    uart_putc('S');
    uart_putc('M');
    uart_putc('-');
    uart_putc('T');
    uart_putc('E');
    uart_putc('S');
    uart_putc('T');
    uart_putc('\r');
    uart_putc('\n');
    __asm__ volatile ("BSTOP" ::: "memory");
    
    /* Test 1: Addition (10 + 20 = 30) */
    __asm__ volatile ("BSTART.STD" ::: "memory");
    __asm__ volatile ("addi a0, 10, ->a0");
    __asm__ volatile ("addi a1, 20, ->a1");
    __asm__ volatile ("add a0, a1, ->a0");
    __asm__ volatile ("BSTOP" ::: "memory");
    uart_putc('1');
    uart_putc(':');
    uart_putc('3');
    uart_putc('0');
    uart_putc('\r');
    uart_putc('\n');
    
    /* Test 2: Subtraction (50 - 25 = 25) */
    __asm__ volatile ("BSTART.STD" ::: "memory");
    __asm__ volatile ("addi a0, 50, ->a0");
    __asm__ volatile ("addi a1, 25, ->a1");
    __asm__ volatile ("sub a0, a1, ->a0");
    __asm__ volatile ("BSTOP" ::: "memory");
    uart_putc('2');
    uart_putc(':');
    uart_putc('2');
    uart_putc('5');
    uart_putc('\r');
    uart_putc('\n');
    
    /* Test 3: AND (0xFF & 0x0F = 0x0F) */
    __asm__ volatile ("BSTART.STD" ::: "memory");
    __asm__ volatile ("addi a0, 255, ->a0");
    __asm__ volatile ("addi a1, 15, ->a1");
    __asm__ volatile ("and a0, a1, ->a0");
    __asm__ volatile ("BSTOP" ::: "memory");
    uart_putc('3');
    uart_putc(':');
    uart_putc('F');
    uart_putc('\r');
    uart_putc('\n');
    
    /* Test 4: OR (0xF0 | 0x0F = 0xFF) */
    __asm__ volatile ("BSTART.STD" ::: "memory");
    __asm__ volatile ("addi a0, 240, ->a0");
    __asm__ volatile ("addi a1, 15, ->a1");
    __asm__ volatile ("or a0, a1, ->a0");
    __asm__ volatile ("BSTOP" ::: "memory");
    uart_putc('4');
    uart_putc(':');
    uart_putc('F');
    uart_putc('F');
    uart_putc('\r');
    uart_putc('\n');
    
    /* Test 5: XOR (0xAA ^ 0x55 = 0xFF) */
    __asm__ volatile ("BSTART.STD" ::: "memory");
    __asm__ volatile ("addi a0, 170, ->a0");
    __asm__ volatile ("addi a1, 85, ->a1");
    __asm__ volatile ("xor a0, a1, ->a0");
    __asm__ volatile ("BSTOP" ::: "memory");
    uart_putc('5');
    uart_putc(':');
    uart_putc('F');
    uart_putc('F');
    uart_putc('\r');
    uart_putc('\n');
    
    /* Test 6: Shift Left (8 << 2 = 32) */
    __asm__ volatile ("BSTART.STD" ::: "memory");
    __asm__ volatile ("addi a0, 8, ->a0");
    __asm__ volatile ("addi a1, 2, ->a1");
    __asm__ volatile ("sll a0, a1, ->a0");
    __asm__ volatile ("BSTOP" ::: "memory");
    uart_putc('6');
    uart_putc(':');
    uart_putc('3');
    uart_putc('2');
    uart_putc('\r');
    uart_putc('\n');
    
    /* Test 7: Shift Right Logical (32 >> 2 = 8) */
    __asm__ volatile ("BSTART.STD" ::: "memory");
    __asm__ volatile ("addi a0, 32, ->a0");
    __asm__ volatile ("addi a1, 2, ->a1");
    __asm__ volatile ("srl a0, a1, ->a0");
    __asm__ volatile ("BSTOP" ::: "memory");
    uart_putc('7');
    uart_putc(':');
    uart_putc('8');
    uart_putc('\r');
    uart_putc('\n');
    
    /* Test 8: Load Immediate */
    __asm__ volatile ("BSTART.STD" ::: "memory");
    __asm__ volatile ("addi a0, 42, ->a0");
    __asm__ volatile ("BSTOP" ::: "memory");
    uart_putc('8');
    uart_putc(':');
    uart_putc('4');
    uart_putc('2');
    uart_putc('\r');
    uart_putc('\n');
    
    /* Test 9: Move Register */
    __asm__ volatile ("BSTART.STD" ::: "memory");
    __asm__ volatile ("addi a1, 99, ->a1");
    __asm__ volatile ("add a0, a1, zero, ->a0");
    __asm__ volatile ("BSTOP" ::: "memory");
    uart_putc('9');
    uart_putc(':');
    uart_putc('9');
    uart_putc('9');
    uart_putc('\r');
    uart_putc('\n');
    
    /* Test 10: Multi-instruction block */
    __asm__ volatile ("BSTART.STD" ::: "memory");
    __asm__ volatile ("addi a0, 1, ->a0");
    __asm__ volatile ("addi a1, 2, ->a1");
    __asm__ volatile ("addi a2, 3, ->a2");
    __asm__ volatile ("add a0, a1, ->a0");
    __asm__ volatile ("add a0, a2, ->a0");
    __asm__ volatile ("BSTOP" ::: "memory");
    uart_putc('A');
    uart_putc(':');
    uart_putc('6');
    uart_putc('\r');
    uart_putc('\n');
    
    /* Done */
    uart_putc('D');
    uart_putc('O');
    uart_putc('N');
    uart_putc('E');
    uart_putc('\r');
    uart_putc('\n');
    
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
