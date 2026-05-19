# 0.32 version update

Date: September 28, 2023

For the path to the web version of the instruction encoding design document, please see [LinxISA Encoding-v0.32](http://dbox.huawei.com/detaildocs?oid=VR%3Awt.doc.WTDocument%3A100255827005)

The most important change in the v0.32 version is the change to the store command.

## Directive implementation changes

### Store command changes

1. Since the DecodeType decoding type of the hardware decoder does not match, the **opcode** of the Store instruction (sb/sh/sw/sd) needs to be adjusted:
    - Reg + Reg format: opcode 7'b0010110 -> 7'b0010100 /* Change the RegDst field to all zeros */
    - Reg + imm format: opcode 7'b0010111 -> 7'b0010101
2. In order to simplify the writing port of the hardware register of the Store instruction and reduce the complexity of hardware implementation. Modify the execution operation of instructions such as sb/sh/sw/sd to: do not output the destination address, that is, do not write the T register and RegDst register.
3. In order to improve the efficiency of continuous memory writing, the sb.a/sh.a/sw.a/sd.a instruction is added. Based on the corresponding sb/sh/sw/sd function, the operation of writing addresses to the destination T and RegDst registers is added.

![store-v0.33](../figs/isa/version/store-v0.32.png)

### Instruction operand increases TP/GP/CP

In v0.32, the source register of each microinstruction can index the TP/GP/CP register in system register.

- In order to improve the efficiency of hardware access to private variables, the operation of microinstruction index TP register is added.
- In order to improve the efficiency of hardware access to global variables, the operation of microinstruction index GP register has been added.
- In order to improve the efficiency of hardware state migration, the operation of microinstruction index CP register is added.

### Changes in bit operation instructions

#### In order to improve the efficiency of string library processing, new bit manipulation instructions are added

- ctzw: Count trailing zeros within the least significant word.  
- clz: Count leading zeros within the entire 64bit.  
- clzw: Count leading zeros within the least significant word.  

#### In order to reduce the complexity of hardware implementation. The bit operation instruction bfi encoding update: changed to a two-input instruction, M/N is expressed in the instruction encoding.

Before update:

![bfi-v32](../figs/isa/version/bfi-v32.png)

After update:

![bfi-v64](../figs/isa/version/bfi-v64.png)

!!! info "Coding changes bring about partial changes in instruction implementation"

    After the update, the G/L field and RegDst field are occupied by the M field, so the result is only written to the T register.  
    Before the update, it was a three-input instruction. In order to simplify the hardware implementation, SrcR was restricted to only index the block-private register. After updating to two inputs, this restriction is removed, and SrcR can index the T register and the newly added TP/GP/CPsystem register

#### In order to adapt to the modification of bfi encoding, the bxu and concat encodings have been updated:

Before update:

![bxu_concat-v32](../figs/isa/version/bxu_concat-v32.png)

After update:

![bxu_concat-v64](../figs/isa/version/bxu_concat-v64.png)

#### The bxu/bxs/bfi command implements the processing of adding winding situations.

By adding winding, these instructions can be used to implement circular shift operations (ror, rol) on the operands.

For the modified instruction implementation, please see: [bxu](../isa/inst/misa_g/BXU.md), [bxs](../isa/inst/misa_g/BXS.md), bfi.