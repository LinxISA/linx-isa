# Floating point block microinstructions

```
Opcode Operand0,Operand1,Operand2                        /* 无输出，浮点块内跳转 */    
Opcode Operand0->{LL_GPR，UL_GPR}                        /* 输出到LL_GPR或者UL_GPR */
Opcode Operand0,Operand1,->{LL_GPR，UL_GPR}              /* 输出到LL_GPR或者UL_GPR */
Opcode Operand0,Operand1,Operand2,->{LL_GPR，UL_GPR}     /* 输出到LL_GPR或者UL_GPR */
```

These microinstructions are only used by the floating point block. Microinstruction operations include not only floating point operations, but also some integer operations. The data type involved in floating point related operations is as follows:

- '.fd' : represents 64bit double precision floating point type <br>
- '.fs': represents 32bit single precision floating point type <br>
- '.fh' : represents 16bit half-precision floating point type <br>
- '.fb' : represents 8bitlow-precision floating-point type
- '.ud': represents 64-bit unsigned long integer data <br>
- '.uw' : represents 32-bit unsigned long integer data <br>
- '.uh' : represents 16-bit unsigned long integer data <br>
- '.ub' : represents 8-bit unsigned long integer data <br>
- '.sd': represents 64-bit signed long integer data <br>
- '.sw' : represents 32-bit signed long integer data <br>
- '.sh' : represents 16-bit signed long integer data <br>
- '.sb': represents 8-bit signed long integer data <br>

See [Floating Point block instruction Set] (https://openx.huawei.com/mkdocs/project/1410/blockisa-doc/docs/site/docs/isa/blockIntro/fp_block/intro/) for all detailed microinstructions in the floating point block.

- Under normal circumstances, for floating point operations, the Opcode basically starts with **f**, and the extension after the Opcode {.fd, .fs, .fh, .fb, .ud, .uw, .uh, .ub, .sd, .sw, .sh, .sb} indicates the data type of the microinstruction operation.
- **cvt** microinstructions can be used to convert between different data type, supporting integer to integer, integer to floating point, floating point to integer, and floating point to floating point.
- The rounding mode of floating point operations is controlled by [CSTATE](https://openx.huawei.com/mkdocs/project/1410/blockisa-doc/docs/site/docs/isa/register/ssr/CSTATE/?h=cstate). The default floating point rounding mode is rounding to the nearest. If you need to switch the rounding mode, you need to configure CSTATE.

## Assembly example:

```
feq.fs t#1, a0, ->t            /*单精度浮点比较操作*/
cvt.fs2sw t#1, ->a1            /*将单精度浮点值转换成有符号32bit整型*/
b.feq.fs t#1, t#2, .Ljump      /*t#1和t#2相等时，跳转到.Ljump的位置*/
```