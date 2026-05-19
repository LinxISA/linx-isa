# Calling convention

This chapter describes the standard calling conventions of C/C++ compilers for Linx programs.

## data type aligned with

The following table summarizes the data type natively supported by Linx.

| C type | Description | Linx bytes |
| -- | -- | -- |
| char | character/byte value | 1 |
| short | short integer | 2 |
| int | integer | 4 |
| long | long integer | 8 |
| long long | long integer | 8 |
| void* | pointer | 8 |
| float | single precision floating point number | 4 |
| double | double precision floating point number | 8 |
| long double | extended precision floating point number | 16 |

* char and unsigned char are 8-bit unsigned integer, which are zero-extended when stored in Linx integer registers. The unsigned short is 16-bit unsigned integer, which is also zero-extended when stored in the register.
* signed char is 8-bit signed integer, which is sign-extended when stored in the register (that is, the high-order 63 to 7 bits are all filled with sign bits)
* short is 16-bit signed integer, which is sign extended when stored in the register.
* When a 32-bit type (such as int) is stored in an integer register, it will be stored as a sign extension of the 32-bit value, that is, bits 63 to 31 are the same as the sign bit. **This restriction also applies to unsigned 32-bit types**. Compilers and compliance software maintain natural alignment when storing the above data type in memory.

## Calling Convention

The Linx calling convention prefers passing arguments via registers, using up to 8 integer registers (a0–a7). If the function parameters are regarded as C structure fields with pointer alignment, the parameter register corresponds to the first 5 pointer words of the structure. However, the floating point fields in the union or array in the structure need to be passed through integer registers. In addition, floating-point arguments to variadic functions (other than explicitly declared arguments) are also passed through integer registers.

Parameters smaller than the pointer word length are stored in the low bits of the parameter register. In little-endian memory systems, such arguments passed on the stack are aligned at the lower address of the pointer word.

Basic type parameters with double pointer word length are naturally aligned when passed on the stack; when passed in an integer register, an aligned odd and even register pair needs to be occupied, and the even register stores the low bits.

Parameters that exceed double pointer word length are passed by reference. The parameters that are not passed through registers are passed through the stack, and the stack pointer sp points to the first parameter that is not passed through registers.

The function return value passes through the integer registers a0 and a1. Other values ​​up to two pointer words are returned through a0 and a1. Larger return values ​​are passed through memory: the caller allocates memory and passes the pointer through the implicit first parameter.

In the standard Linx calling convention, the stack grows downward and the stack pointer always remains 16-byte aligned.

In addition to the parameter and return value registers, the three integer registers x0–x3 may become invalid after the call and need to be saved by the caller; the eight integer registers s0–s7 are reserved registers and need to be saved by the callee. The following table details the calling convention roles of registers.| Register | ABI Name | Description |
| ------- | ----------- | ----------------------- |
| r0 | zero | zero register |
| r1 | sp | stack pointer register |
| r2 | a0 | function parameter 0 |
| r3 | a1 | function parameter 1 |
| r4 | a2 | function parameter 2 |
| r5 | a3 | function parameter 3 |
| r6 | a4 | function parameter 4 |
| r7 | a5 | function parameter 5 |
| r8 | a6 | function parameter 6 |
| r9 | a7 | Function parameter 7 |
| r10 | ra | Return address register |
| r11 | fp(s0) | Frame register/sub-function register 0 |
| r12 | s1 | Sub-function register 1 |
| r13 | s2 | Sub-function register 2 |
| r14 | s3 | Sub-function register 3 |
| r15 | s4 | Sub-function register 4 |
| r16 | s5 | Sub-function register 5 |
| r17 | s6 | Sub-function register 6 |
| r18 | s7 | Subfunction register 7 |
| r19 | s8 | Subfunction register 8 |
| r20 | x0 | The parent function saves other registers 0 |
| r21 | x1 | The parent function saves other registers 1 |
| r22 | x2 | The parent function saves other registers 2 |
| r23 | x3 | The parent function saves other registers 3 |