# 0.30 version update

Date: August 18, 2023

For the path to the web version of the instruction encoding design document, please see [LinxISA Encoding-v0.30](http://dbox.huawei.com/detaildocs?oid=VR%3Awt.doc.WTDocument%3A100255877291)

### 32bit encoding format changes

v0.30 reconstructs the 32bit encoding format. Reasons for reconstruction:

- The current coding of BISA microinstructions is not optimal, and CodeSize and fetching FootPrint are too large.
- BISA is about to be officially commercialized. An optimal and universal instruction code needs to be determined as soon as possible, and no major changes will be made in the future.
- To upgrade BISA to 1.0, you need to reserve instruction space and lay out the 32bit encoding space in advance.

Coding format changes:

- In an encoding format, the source register can be expressed as a T register or a block-private register (flag bit judgment).
- Add additional destination register, which can be block-private register or shared architectural register (flag bit judgment).
- Improved the encoding space of immediate data.

### Directive implementation changes

- Most instructions are merged with the set/set.g instructions, the results are selectively updated to the destination register, and the design of writing the results to the T register by default remains unchanged.
- The multiplication instruction writes the high and low bits of the result to the destination T register and destination register respectively.
- The division/remainder instruction writes the quotient and remainder to the destination T register and destination register respectively.
- The load class instruction writes the loaded data and access address to the destination T register and destination register respectively.

### Add new command

#### Jump class within block

- b.eq: jump when equal
- b.ne: jump without waiting
- b.lt: jump when less than (signed comparison)
- b.ge: Jump when greater than or equal to (signed comparison)
- b.ltu: jump if less than (unsigned comparison)
- b.geu: jump when greater than or equal to (unsigned comparison)

#### Integer general calculation class:

- addc: addition with carry;
- subc: borrow subtraction;

#### Memory access class

- PRF: Prefetch memory (first fetch the memory block containing the access address into the cache).

#### Bit operation class

- ctz: Count the number of zeros following the least significant bit in the register;
- concat: concatenation (circular shift)

#### Floating point calculation class

- fmadd: floating-point multiply-accumulate instruction;
- fabs: find the absolute value of floating point;

#### Immediate type

- lui: high-bit immediate data loading.

#### Block input/output Class

- bend: used as an instruction to end the execution of block instruction. It belongs to the input/output instruction in the standard block.

#### System command class- BSE: After the current block is submitted, custom event information is sent to the external system.
- BC.IVA: The virtual address corresponding to the memory address of invalid SrcL in Block Header Cache.
- BC.IALL: Invalidate all Cachelines in Block Cache.
- IC.IVA: The virtual address corresponding to the memory address of invalid SrcL in the Instruction Cache.
- IC.IALL: Invalidate all Cachelines in the Instruction Cache.
- DC.IVA: The virtual address corresponding to the memory address of invalid SrcL in Data Cache.
- DC.CVA: Write the virtual address corresponding to the memory address of SrcL in the Data Cache back to the next level cache or the main processor.
- DC.CIVA: Write the virtual address corresponding to the memory address of SrcL in the Data Cache back to the next level cache or the main processor, and mark the corresponding Cacheline as invalid.
- DC.ISW: The Cacheline corresponding to the Set/Way indicated in the invalid SrcL in the Data Cache.
- DC.CSW: Write the Cacheline corresponding to the Set/Way indicated in SrcL in the Data Cache back to the next level cache or main processor.
- DC.CISW: Write the Cacheline corresponding to the Set/Way indicated in SrcL in the Data Cache back to the next level cache or main processor, and mark the corresponding Cacheline as invalid.
- TLBGET: Privilege level: Read the page table and set the corresponding SSR register.
- TLBSET: Privilege level: Read the SSR register and set the corresponding page table.
- TLBI: Clear the page table corresponding to the ASID stored in Src in the TLB.
- FENCE.D: Data barrier.
- FENCE.I: Command barrier.

### Other changes

- Added `基址寄存器+变址寄存器` addressing mode to memory access instructions;
- The sel command is changed to **csel** (conditional selection command)
- Floating point instructions are merged (for example: fdiv.h, fdiv.s, fdiv.d are changed into one instruction fdiv) to achieve the same operation of different precision operands in one instruction.
- The fget instruction adds conversion between 64-bit unsigned long integer and [half/single/double] precision floating point numbers, and the name of the fget instruction is changed to **fcvt**.
- Microinstructions in the system block: SSRGET, SSRSET, lr.d, lr.w, sc.d, sc.w are retained; trap, wfe, wfi, fence, fence.i are merged into SSRCRLT instructions.
- Change the CARG.FLAG field of the submission parameter register to a 1-bit flag. The setc.eq class instruction sets CARG.FLAG.
- Support the ssrget instruction in the standard block, that is, read-only system register is implemented in the standard block.
- Changes to multiplication instructions:

Previous versions used mul,mulh,mulhsu,mulhu,mulw; v0.30 used mul,mulu,mulw,muluw,mulh,mulhu. At the same time, the output of the destination T register of the mul/mulu instruction and the RegDst register are changed to be consistent (the low bits of the multiplication result are retained).