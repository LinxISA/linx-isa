# Version 0.50 update

Update date: May 26, 2025

For the corresponding encoding overview in this repository, see [Instruction-Set Overview](../isa/encoding/overview.md).

## Update background

Earlier proprietary AI-processor instruction-set approaches exposed repeated evolution bottlenecks. Each architecture iteration forced operator-library rewrites because the abstraction layer did not cleanly separate mechanism (for example memory access mode) from strategy (for example data blocking policy), so hardware-specification changes directly destabilized the software stack.

In this context, LinxISA is positioned as a heterogeneous computing architecture that aims to break out of the traditional GPU-only paradigm and stay competitive across artificial intelligence, graphics rendering, and high-performance computing. Existing full-stack ecosystems derive their moat not only from hardware performance, but also from long-accumulated compiler, library, and application integration. A follow-the-leader strategy would therefore inherit compatibility cost without creating differentiated architectural value.

In order for LinxISA to complete this task, it first needs to further optimize the basic scalar instructions from the perspective of static code volume and dynamic instruction number to ensure that the instruction set base can reach a relatively high level in the industry. Based on this, we will expand to the fields of artificial intelligence, graphics rendering and high-performance computing, and gradually realize the integrated computing architecture of CPU, NPU and GPU.

At present, LinxISA has reached a level similar to the ARM architecture in coding optimization, and the static code size (codesize) is approximately 0.9 times that of the ARM architecture. Although the static code has been relatively optimized, LinxISA still has about 40% more dynamic instructions than ARM. The expansion of the number of dynamic instructions directly affects execution efficiency and overall performance. Especially when facing computationally intensive tasks, the increase in the number of instructions will lead to additional processing delays and waste of computing resources. 2025 is regarded as a key year for LinxISA to be widely used in many fields. To stand out from the competition, we need an instruction set that can surpass existing mainstream architectures (such as ARM and x86) in performance, instruction count and code density. Although good progress has been made on the road to catch up, more efforts and innovation are needed to truly achieve transcendence, especially to achieve ultimate optimization in all aspects of instruction set design. Therefore, we are not satisfied with the design of v0.43. We hope that in the v0.5 version, we will focus on significantly reducing the number of dynamic instructions, further improving execution efficiency, and optimizing code density and variable-length encoding. Therefore, the core goal of this version is to reduce redundant instructions while ensuring performance and stability through targeted optimization, and ensure the efficient performance of the instruction set in practical applications.

The following is the LinxISAV0.5 version evolution plan:

![plan](../figs/isa/version/isa_plan.png){ width="800" }

## Update Summary

- Adjust the instruction encoding framework: Unify the planning of 16bit/32bit/48bit/64bit instruction formats and reasonably reserve encoding space;
- Replan the instruction space, cancel the custom space of different block type in 32bit, and simplify the hardware decoding complexity.
- Complete the scalar command function to ensure the perfection of the scalar base.
- Added 48bit command support to improve parameter configuration efficiency in AI/rendering scenarios; including: dual output commands, Long Immediate loading commands, Load Literal commands, and complex operation commands.

## Specific content

### 1. Instruction encoding

In order to solve the problem of encoding duplication in different blocks, we eliminated the encoding space in private blocks and restructured it. At the same time, the **prefix+suffix** encoding method is introduced to ensure that there is still enough instruction space and to improve the expressive ability of instructions within the block.- **48-bit instruction**: consists of a `16位前缀` plus a `32位主指令` or `32位后缀`. The prefix part is mainly used to expand the high-bit information of the opcode and immediate data to meet the needs of long immediate data loading and complex memory operations.
- **64-bit instructions**: It consists of `32位前缀` and `32位主指令` or `32位后缀`, providing sufficient coding space for more extreme complex operations.

![space](../figs/isa/version/space.png){ width="800" }

- Main directive: a directive that defines specific semantics independently without prefix.
- Main instruction + prefix instruction: The prefix instruction only completes the information of the main instruction and does not affect the instruction semantics.
- Prefix command: It must match the main command or suffix command to have meaning. Usually used to complete additional information.
- Suffix command: It must match the prefix command to have meaning. The suffix command alone has no meaning.

| Combination | 16bit instruction | 16bit prefix instruction | 32bit main instruction | 32bit suffix instruction | 32bit prefix instruction |
|------|-----------|---------------|---------------|-----------|-------------|
| 16bit instruction | - | × | - | × | × |
| 16bit prefix instruction | × | × | √ | √ | × |
| 32bit main instruction | - | × | - | × | × |
| 32bit suffix instructions | × | × | × | × | × |
| 32bit prefix instructions | × | × | √ | √ | × |

This prefix + suffix structure not only effectively avoids duplication and conflicts of encoding between different instruction blocks, but also makes the instruction decoding process clearer and more modular, allowing the hardware to flexibly handle instructions of different lengths during parsing.

### 2. Command naming

Distinguish instructions with different word lengths through instruction prefixes and standardize instruction naming. Easy for programmers to understand and use.

1. 16bit compression instructions are uniformly prefixed with "C." or "c.".  
2. 48bit enhanced instructions are uniformly prefixed with "HL." or "hl.".  
3. 64bit long instructions are uniformly prefixed with "L." or "l.".  

### 3. Command combination

16bit, 32bit, 48bit and 64bit instructions with different word lengths are allowed to be mixed. All instructions use the same encoding space for encoding, so they can be mixed.

### 4.16bit instruction

1. Overall adjustment of 16bit instruction encoding
2. Delete the B.NEXT.C instruction, and the long jump of header is encoded through the 48bit or 64bit version of the BSTART instruction.
3. The c.addpc instruction was renamed to c.setret. The modification to c.setret is more consistent with the instruction semantics and is easier for programmers to use and understand.
4. Delete the instruction c.addtpc and add the 48bit Load/Store PC-Relative instruction to replace this instruction function.

![16bit](../figs/isa/version/16bit.png){ width="800" }

This version adds a 48-bit Load/Store PC-relative instruction, which can replace the combination of c.addtpc and load/store instructions to load symbols, so this instruction is deleted.

The way to load symbols in previous versions:
```asm
    c.addtpc %hi(symbol), ->t
    ldi [t#1, %lo(symbol)], ->t
```
Current version:
```asm
    hl.ld.pcr [symbol], ->t
```

### 5.32bitheader instruction1. The BSTART instruction **removes the EX bit** and the BlockType field is expanded to 5 bits. Subsequently, the 48bit and 64bit versions of the long jump headerBSTART are added, so the B.NEXT instruction is no longer needed. The 32bit version of the BSTART instruction does not need to use the EX bit to indicate the jump distance and splicing with B.NEXT.
2. Delete the B.NEXT instruction
3. The block input/output instruction B.IO is renamed to B.IOR to distinguish other B.IO instructions that will be expanded later.
4. Add EBREAK instruction to provide software breakpoint function

![bstart](../figs/isa/version/bstart.png){ width="800" }

### 6.32bit microinstructions

The modified instructions in this version are as follows:

1. The addpc command is renamed to setret and the code is reused with addtpc. Multiplexing encoding with addtpc can save Opcode space and reserve more space for subsequent expansion.
2. Adjust the semantics of ctz and clz instructions, and add M and N parameters in assembly (compatible with the functions of ctzw and clzw). After the modification, the instruction implementation is more flexible, and the encoding method of bit operation instructions tends to be unified.
3. rev16, rev32 and rev64 are combined into one rev instruction. The encoding format is unified, and the instruction implementation is more flexible.
4. Add the bcnt instruction to supplement the scalar instruction function, which is used to count the number of bits in the register that are 1.
5. The third input SrcR of the csel instruction adds the ".neg" optional parameter. After adding this parameter, the cneg operation can be implemented, and a register original value or a negative value can be selected according to conditions. The benefit of reducing the number of dynamic instructions can be obtained in the 525 subkey.
6. Added 7 Load PC-Relative instructions and 4 Store PC-Relative instructions. Improve the efficiency of symbolic address loading, and further improve the performance and code density of the instruction set by reducing the frequency of use of the T register.
7. The far parameter is added to the atomic instruction, and the encoding of the high-order command ID field is modified to provide atomic operations on a specific cache level.
8. Add the bwt instruction in the system block to wake up the thread after waiting for the specified time.
9. The parameter encoding position of the acrc and acre instructions has been adjusted, and the target ACR parameter of the acre instruction is deleted. The target ACR of the privilege level switch triggered by the acre instruction is specified by the ECSTATE register.
10. The cvt instructions in the floating point block are split into fcvt, scvtf, ucvtf, fcvta, fcvtm, fcvtn, fcvtp, fcvtz and other instructions. Corresponding rounding modes are provided for different data format conversion scenarios.
11. Add the BSTART.CALL instruction, specifically the pseudo-instruction expressed by the combination of the C.BSTART.CALL instruction and c.setret.

After upgrading to version 0.50, the list of deleted 32bit instructions is as follows:

| Command List | Description |
|----------|-----------|
| b.eq, b.ne, b.lt, b.ge, b.ltu, b.geu, j, jr | Intra-block jumps are not supported for the time being. Jump scenarios are uniformly implemented using inter-block jumps. (Reserve coding space if needed for subsequent verification) |
| b.feq, b.fne, b.flt, b.fge | Intra-block jumps are not supported at the moment |
| fsin, fcos, fclass, flog | The previous version has design content and is officially deleted. |

Moved to 48bit extended space instruction list| Category | Command List | Description |
|------|----------|---------|
| 1. store.a class | sb.a, sh.a, sw.a sd.a, sh.ua, sw.ua, sd.ua<br> sbi.a, shi.a, swi.a sdi.a, shi.ua, swi.ua, sdi.ua | Supplement the destination register encoding and add the flag bit of Pre/Post Index by adding 16bit prefix. |
| 2. system register access | ssrrd, ssrwr renamed to hl.ssrget and hl.ssrset. | Expand the SSR ID expression space by adding a 16-bit prefix. |
| 3. With immediate multiplication and addition/subtraction | miadd, misub | Expand the range of immediate numbers by adding a 16bit prefix. |
| 4. Bit operations | bfi, ccat, ccatw | Express dual output or extended parameter domain by adding 16bit prefix. |
| 5. Prefetch operation | prf, prf.a, prfi.u, prfi.ua | By adding a 16-bit prefix, the field indicating the prefetch target cache can be uniformly encoded. |
| 6. General queue management | qmt, qpush, qpop | By adding a 16bit prefix, dual output can be encoded. |
| 7. Atomic comparison exchange | casb, cash, casw, casd | By adding a 16bit prefix, more register inputs can be encoded. |

### 7. Add 48bit instructions| Category | Instruction List |
|------|----------|
| 1. Enhanced version of BSTART | HL.BSTART |
| 2. CALL block header | HL.BSTART.CALL |
| 3. Long immediate data loading | hl.lis, hl.liu, hl.lui |
| 4. Multiplication double output | hl.mul, hl.mulu, hl.madd, hl.maddw |
| 5. ALUI class | hl.addi, hl.subi, hl.andi, hl.ori, hl.xori |
| 6. ALUWI class | hl.addiw, hl.subiw, hl.andiw, hl.oriw, hl.xoriw |
| 7. CMPI class | hl.cmp.eqi, hl.cmp.nei, hl.cmp.andi, hl.cmp.ori, hl.cmp.lti, hl.cmp.gei, hl.cmp.ltui, hl.cmp.geui |
| 8. SETCI class | hl.setc.eqi, hl.setc.nei, hl.setc.andi, hl.setc.ori, hl.setc.lti, hl.setc.gei, hl.setc.ltui, hl.setc.geui |
| 9. TPC-Relative | hl.addtpc, hl.setret |
| 10. Divide remainder | hl.div, hl.divu, hl.divw, hl.divuw, hl.rem, hl.remu, hl.remw, hl.remuw |
| 11. Load long immediate offset | hl.lbi, hl.lhi, hl.lwi, hl.ldi, hl.lbui, hl.lhui, hl.lwui, hl.lhi.u, hl.lwi.u, hl.ldi.u, hl.lhui.u, hl.lwui.u |
| 12. Load Pair (register base address + register offset) | hl.lbp, hl.lhp, hl.lwp, hl.ldp, hl.lbup, hl.lhup, hl.lwup |
| 13. Load Pair (register base address + immediate offset) | hl.lbip, hl.lhip, hl.lwip, hl.ldip, hl.lbuip, hl.lhuip, hl.lwuip, hl.lhip.u, hl.lwip.u, hl.ldip.u, hl.lhuip.u, hl.lwuip.u |
| 14. Load Pre-Index (register base address + register offset) | hl.lb.pr, hl.lh.pr, hl.lw.pr, hl.ld.pr, hl.lbu.pr, hl.lhu.pr, hl.lwu.pr |
| 15. Load Pre-Index (register base address + immediate offset) | hl.lbi.pr, hl.lhi.pr, hl.lwi.pr, hl.ldi.pr, hl.lbui.pr, hl.lhui.pr, hl.lwui.pr, hl.lhi.upr, hl.lwi.upr, hl.ldi.upr, hl.lhui.upr, hl.lwui.upr |
| 16. Load Post-Index (register base address + register offset) | hl.lb.po, hl.lh.po, hl.lw.po, hl.ld.po, hl.lbu.po, hl.lhu.po, hl.lwu.po || 17. Load Post-Index (register base address + immediate offset) | hl.lbi.po, hl.lhi.po, hl.lwi.po, hl.ldi.po, hl.lbui.po, hl.lhui.po, hl.lwui.po, hl.lhi.upo, hl.lwi.upo, hl.ldi.upo, hl.lhui.upo, hl.lwui.upo |
| 18. Load PC-Relative addressing instructions | hl.lb.pcr, hl.lh.pcr, hl.lw.pcr, hl.ld.pcr, hl.lbu.pcr, hl.lhu.pcr, hl.lwu.pcr |
| 19. Store long immediate offset | hl.sbi, hl.shi, hl.swi, hl.sdi, hl.shi.u, hl.swi.u, hl.sdi.u |
| 17. Store Pair (register base address + register offset) | hl.sbp, hl.shp, hl.swp, hl.sdp, hl.shp.u, hl.swp.u, hl.sdp.u |
| 18. Store Pair (register base address + immediate offset) | hl.sbip, hl.ship, hl.swip, hl.sdip, hl.ship.u, hl.swip.u, hl.sdip.u |
| 13. Store Pre-Index (register base address + register offset) | hl.sb.pr, hl.sh.pr, hl.sw.pr, hl.sd.pr, hl.sh.upr, hl.sw.upr, hl.sd.upr |
| 14. Store Pre-Index (register base address + immediate offset) | hl.sbi.pr, hl.shi.pr, hl.swi.pr, hl.sdi.pr, hl.shi.upr, hl.swi.upr, hl.sdi.upr |
| 15. Store Post-Index (register base address + register offset) | hl.sb.po, hl.sh.po, hl.sw.po, hl.sd.po, hl.sh.upo, hl.sw.upo, hl.sd.upo |
| 16. Store Post-Index (register base address + immediate offset) | hl.sbi.po, hl.shi.po, hl.swi.po, hl.sdi.po, hl.shi.upo, hl.swi.upo, hl.sdi.upo |
| 21. Store PC-Relative | hl.sb.pcr, hl.sh.pcr, hl.sw.pcr, hl.sd.pcr |

### 64bit instruction

This version does not modify the 64-bit instructions in the original SIMT block for the time being, and will be modified uniformly in the subsequent version 0.51.| Classification | Command | Description |
|------|-------|------|
| 1. Added long jump header | L.BSTART | Used in ultra-long jump scenarios, supporting 42-bit jump offset. |
| 2. Added CALL block header | L.BSTART.CALL | Provides a wider range of return address offsets than the HL.BSTART.CALL instruction |
| 3. Add long immediate addition instruction | l.addli | Used in combination with hl.lui to load 64-bit long immediate. |
| 4. Added Load PC-Relative addressing instructions | l.lb.pcr, l.lh.pcr, l.lw.pcr, l.ld.pcr, l.lbu.pcr, l.lhu.pcr, l.lwu.pcr | Improve the efficiency of symbol address loading and reduce the frequency of use of T register. Provides longer offset distance than 32bit and 48bit versions. |
| 5. Added Store PC-Relative addressing instructions | l.sb.pcr, l.sh.pcr, l.sw.pcr, l.sd.pcr | Provide longer offset distance than 32bit and 48bit versions. |
| 6. Added atomic comparison and exchange instructions | l.casbp, l.cashp, l.caswp, l.casdp | Provide atomic comparison and exchange operations for two elements |