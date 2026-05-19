# Instruction set overview

LinxISA is defined as a basic integer instruction set, called the **Basic Instruction Set**, which must be present in any implementation. The basic instruction set is Turing complete and contains all basic instructions for processing general-purpose operations. LinxISA can also contain other extensions based on the basic instruction set, which can be added by changes in instruction encoding length, or can be introduced by some special block type.

LinxISA adopts variable-length instruction encoding mode and supports 4 instruction lengths of 16-bit, 32-bit, 48-bit or 64-bit. Since the instruction lengths are all multiples of the 16-bit base, these instructions must be aligned on **16-bit boundaries**.

Instructions of different lengths are introduced as follows:

- The 16-bit length instruction is called a **compressed instruction** and is defined in [Compressed Instruction Extension] (../instset/compressInstrs.md). The naming of compression instructions uniformly uses "C." (or lowercase "c.") as the prefix.
- 32-bit length instructions are called **standard instructions**, and standard instructions are used to define [Basic Instruction Set] (../instset/baseInstrs.md), [Basic Instruction Extension] (../instset/baseExtInstrs.md) and [Standard Instruction Extension] (../instset/standardInstrs.md).
- 48-bit length instructions are called **half-length instructions** and are defined in [Enhanced Instruction Extensions] (../instset/haflLongInstrs.md). The naming of half-length instructions uniformly uses "HL." (or lowercase "hl.") as the prefix.
- Instructions with a length of 64 bits are called **long instructions** and are defined in [Very Long Instruction Extension] (../instset/longInstrs.md). Long instructions are named with "L." (or lowercase "l.") as the prefix.

Among them, 48-bit and 64-bit word length instructions are encoded using the splicing combination method of **prefix + suffix**, so as to expand the instruction space and improve the instruction expression ability. At the same time, in order to enable software or programmers to use instructions of any length to implement specified functions in one implementation, we encode instructions with four word lengths in the same set of instruction spaces. The encoding rules are as follows:

![encoding-layer1](../../figs/isa/space/encoding-layer1.png)

In the first layer of coding logic, the lowest bit represents the instruction word length Width (abbreviated as W). A Width bit coded as 0 represents a 16-bit instruction, and a Width bit coded as 1 represents a 32-bit instruction.

![encoding-layer2](../../figs/isa/space/encoding-layer2.png)

In the second layer of encoding logic, the 16bit and 32bit instruction spaces are further divided into `主指令空间`, `后缀指令空间` and `前缀指令空间` of corresponding word lengths through the Opcode field, which is used to provide combined encoding of longer instructions. The details are as follows:

| Width | Opcode | Classification | Role/Requirements |
|-------|--------|------|----------|
| 0 | [0, 6] | 16bit main instruction | Individually define instructions with specific semantics. Splicing prefix instructions are not supported for the time being |
| 0 | 7 | 16bit prefix instruction | Must match the main instruction or suffix instruction to have meaning. Often used to supplement additional information |
| 1 | [0, 5] | 32bit main instruction | Allows instructions with specific semantics to be defined separately, and prefix instructions can be spliced |
| 1 | 6 | 32bit suffix instructions | Must match the prefix instructions to have meaning, the suffix instructions alone have no meaning |
| 1 | 7 | 32bit prefix instruction | Must match the main instruction or suffix instruction to have meaning. Often used to supplement additional information |

The 48-bit and 64-bit word length instruction encoding methods are defined through effective combinations of the above types of instructions:

- **48-bit instruction**: composed of a `16位前缀` spliced into a `32位主指令` or `32位后缀指令`. The prefix part is mainly used to expand the high-bit information of the opcode and immediate data to meet the needs of long immediate data loading and complex memory operations.
- **64-bit instruction**: composed of a `32位前缀` and a `32位主指令` or `32位后缀指令`, providing enough coding space for more extreme complex operations.

For detailed space allocation of instructions with different word lengths, please refer to the section [Instruction Space Allocation] (./space.md).