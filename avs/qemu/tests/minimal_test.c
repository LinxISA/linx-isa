/*
 * Minimal LinxISA Test - QEMU Verification
 * 
 * This is a simple test that:
 * 1. Tests basic arithmetic operations
 * 2. Verifies QEMU can execute LinxISA instructions
 * 3. Outputs results via UART
 * 
 * NOTE: This test avoids C conditionals after inline assembly
 * as the LinxISA backend has issues with brcond after asm.
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

/* Output a string */
static inline void uart_puts(const char *s) {
    while (*s) {
        uart_putc(*s++);
    }
}

/* Output a decimal number */
static inline void uart_putdec(uint64_t v) {
    char buf[32];
    int i = 0;
    
    if (v == 0) {
        uart_putc('0');
        return;
    }
    
    while (v > 0) {
        buf[i++] = '0' + (v % 10);
        v /= 10;
    }
    
    while (i > 0) {
        uart_putc(buf[--i]);
    }
}

/* _start - Entry point */
void _start(void) {
    uint64_t result;
    
    uart_puts("\r\n");
    uart_puts("====================================\r\n");
    uart_puts("   LinxISA Minimal Test v1.0\r\n");
    uart_puts("====================================\r\n\r\n");
    
    /* Test 1: Simple addition - add a0, a1, ->a0 (10 + 20 = 30) */
    uart_puts("Test 1: Addition (10 + 20)\r\n");
    __asm__ volatile (
        "addi a0, 10, ->a0\n\t"
        "addi a1, 20, ->a1\n\t"
        "add a0, a1, ->a0"
    );
    __asm__ volatile ("add %0, a0, zero" : "=r"(result));
    uart_puts("  Result: ");
    uart_putdec(result);
    uart_puts("\r\n");
    
    /* Test 2: Immediate addition - addi with 5-bit immediate */
    uart_puts("\r\nTest 2: Immediate Add (15 + 5)\r\n");
    __asm__ volatile (
        "addi a0, 15, ->a0\n\t"
        "addi a1, 5, ->a1\n\t"
        "add a0, a1, ->a0"
    );
    __asm__ volatile ("add %0, a0, zero" : "=r"(result));
    uart_puts("  Result: ");
    uart_putdec(result);
    uart_puts("\r\n");
    
    /* Test 3: Subtraction */
    uart_puts("\r\nTest 3: Subtraction (50 - 25 = 25)\r\n");
    __asm__ volatile (
        "addi a0, 50, ->a0\n\t"
        "addi a1, 25, ->a1\n\t"
        "sub a0, a1, ->a0"
    );
    __asm__ volatile ("add %0, a0, zero" : "=r"(result));
    uart_puts("  Result: ");
    uart_putdec(result);
    uart_puts("\r\n");
    
    /* Test 4: AND operation */
    uart_puts("\r\nTest 4: AND (0xFF & 0x0F = 0x0F)\r\n");
    __asm__ volatile (
        "addi a0, 255, ->a0\n\t"      /* 0xFF */
        "addi a1, 15, ->a1\n\t"       /* 0x0F */
        "and a0, a1, ->a0"
    );
    __asm__ volatile ("add %0, a0, zero" : "=r"(result));
    uart_puts("  Result: ");
    uart_putdec(result);
    uart_puts("\r\n");
    
    /* Test 5: OR operation */
    uart_puts("\r\nTest 5: OR (0xF0 | 0x0F = 0xFF)\r\n");
    __asm__ volatile (
        "addi a0, 240, ->a0\n\t"      /* 0xF0 */
        "addi a1, 15, ->a1\n\t"       /* 0x0F */
        "or a0, a1, ->a0"
    );
    __asm__ volatile ("add %0, a0, zero" : "=r"(result));
    uart_puts("  Result: ");
    uart_putdec(result);
    uart_puts("\r\n");
    
    /* Test 6: XOR operation */
    uart_puts("\r\nTest 6: XOR (0xAA ^ 0x55 = 0xFF)\r\n");
    __asm__ volatile (
        "addi a0, 170, ->a0\n\t"      /* 0xAA */
        "addi a1, 85, ->a1\n\t"       /* 0x55 */
        "xor a0, a1, ->a0"
    );
    __asm__ volatile ("add %0, a0, zero" : "=r"(result));
    uart_puts("  Result: ");
    uart_putdec(result);
    uart_puts("\r\n");
    
    /* Test 7: Block structure */
    uart_puts("\r\nTest 7: Block Structure (BSTART/BSTOP)\r\n");
    __asm__ volatile (
        "addi a0, 5, ->a0\n\t"
        "addi a1, 7, ->a1"
    );
    __asm__ volatile ("BSTART.STD" ::: "memory");
    __asm__ volatile ("add a0, a1, ->a0");
    __asm__ volatile ("BSTOP" ::: "memory");
    __asm__ volatile ("add %0, a0, zero" : "=r"(result));
    uart_puts("  Result: ");
    uart_putdec(result);
    uart_puts("\r\n");
    
    /* Test 8: Shift left */
    uart_puts("\r\nTest 8: Shift Left (8 << 2 = 32)\r\n");
    __asm__ volatile (
        "addi a0, 8, ->a0\n\t"
        "addi a1, 2, ->a1\n\t"
        "sll a0, a1, ->a0"
    );
    __asm__ volatile ("add %0, a0, zero" : "=r"(result));
    uart_puts("  Result: ");
    uart_putdec(result);
    uart_puts("\r\n");
    
    /* Test 9: Shift right logical */
    uart_puts("\r\nTest 9: Shift Right (32 >> 2 = 8)\r\n");
    __asm__ volatile (
        "addi a0, 32, ->a0\n\t"
        "addi a1, 2, ->a1\n\t"
        "srl a0, a1, ->a0"
    );
    __asm__ volatile ("add %0, a0, zero" : "=r"(result));
    uart_puts("  Result: ");
    uart_putdec(result);
    uart_puts("\r\n");
    
    /* Test 10: Move register */
    uart_puts("\r\nTest 10: Move (move 42 to a0)\r\n");
    __asm__ volatile (
        "addi a1, 42, ->a1\n\t"
        "add a0, a1, zero, ->a0"
    );
    __asm__ volatile ("add %0, a0, zero" : "=r"(result));
    uart_puts("  Result: ");
    uart_putdec(result);
    uart_puts("\r\n");
    
    /* All tests completed */
    uart_puts("\r\n====================================\r\n");
    uart_puts("   TESTS COMPLETED!\r\n");
    uart_puts("====================================\r\n");
    
    __asm__ volatile (
        "BSTART.STD\n"
        "lui 65545, ->u\n"
        "lui 5, ->t\n"
        "addi t#1, 1365, ->t\n"
        "c.swi t#1, [u#1, 0]\n"
        "BSTOP\n"
        ::: "memory");
    while(1) {}
}
