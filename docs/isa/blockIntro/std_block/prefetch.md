# Prefetch instructions

The prefetch instruction is used to prefetch a cache line of data from memory into the cache. There are two ways to calculate the memory access address: one is to add the value of register SrcL and the value of register SrcR, allowing the value of SrcR to be added before addition.
Intercept the lower 32-bit extension and left shift; the second is to add the 12-bit signed immediate value to the register SrcL. The fetch address falls within the cache line to be prefetched.

The mode field in the prf and prf.a instructions prompts the data retrieved by the hardware to fill in which level of cache. mode has 4 optional values ​​from 0 to 3. Among them, mode=0 is defined as prefetching to the first-level data cache, mode=1 is defined as prefetching to the second-level data cache, mode=2 is defined as prefetching to the third-level data cache, the meaning of mode=3 is not yet defined, and is treated as a NOP instruction when the processor executes it.

If the Cache attribute of the access address of the prefetch instruction is not cached, then the instruction cannot generate a memory access action and is treated as a NOP instruction.

| Microinstructions | Assembly format | Description |
|---------------|---------------|----------------------------------------|
| PRF | prf{.l1,.l2,.l3} \[SrcL, SrcR<{.sw,.uw}><<<shamt>\] | Using \[left operand plus right operand\] as the address, prefetch the Cacheline containing the address into the specified Cache |
| PRF.A | prf.a{.l1,.l2,.l3} \[SrcL, SrcR<{.sw,.uw}><<<shamt>\], ->{t,u,Rd} | Using \[left operand plus right operand\] as the address, prefetch the Cacheline containing the address into the specified Cache. Address written to RegDst |
| PRFI.U | prfi.u.l1 \[SrcL, simm\], ->{t,u,Rd} | Using \[left operand plus right operand\] as the address, preload the Cacheline containing the address into the L1 Cache |
| PRFI.UA | prfi.ua.l1 \[SrcL, simm\], ->{t,u,Rd} | Using \[left operand plus right operand\] as the address, preload the Cacheline containing the address into the L1 Cache, and write the address into RegDst |

![Prefetch](../../../figs/bitfield/svg/Introduction_32bit/Prefetch.svg)