# Splitable Block core

# background
In the CPU of portable devices, we usually see a structure of large cores and small cores. Among them, when the device requires a large amount of calculations, the large core will play a role in improving performance.
When the device has no performance requirements, the small core will assume the role of reasonable performance and reduced energy consumption. In the architecture of Apple and Intel, the large and small cores are called P-Core (Performance Core) respectively.
With E-Core (Efficent Core), in the ARM architecture, this approach is called Big.Little architecture.

In mobile phone chips, we also adopt the same strategy. As shown below:

![Overall architecture diagram](../figs/uArch/GFU_TOP_kirincore.png)

That is, the solution of 1 large core + 3 medium cores + 4 small cores. However, in most scenarios, the large core will not work, but it also occupies a considerable part of the area. This method is not efficient. To solve this problem,
The best way is to design a hardware that can be dynamically configured. When the device has high performance requirements, it can be transformed into a high-performance large core. It can also be used while the device is sleeping or working on simple tasks.
Convert to several small cores to save energy consumption.

## Difficulties in CPU splitting

The above splitting idea is not feasible in the existing CPU architecture. The main reason is that many hardware logics in the CPU architecture are inseparable. The same problem will be encountered when the CPU supports multi-threading, usually
The CPU needs to copy some logic to ensure correct functionality, such as INSTQ, CMAP, SMAP, Branch Predictor, etc. Secondly, the CPU requires quite complex logic to ensure that each small core after splitting
In terms of memory consistency, architectural state and other functions are correct.

## Advantages of Block ISA

However, splitting and merging are exception simple for Block ISA cores.

Since the block in Block ISA is defined as an instruction, the micro-architecture can abstract the small core into the execution unit of block instruction.
And design the "big core" in a higher dimension. Based on this, most Block ISA cores are designed as a processor with a small core as the execution unit.


At the same time, due to the definition of a block in Block ISA as a collection of microinstructions, each block can be dimensionally reduced into a program or a thread. The execution unit of the block has the ability to execute the complete program independently.
Based on this, each small core in the Block ISA core can become a "small core" that can run independently. This is also the advantage of LinxISA at the microarchitecture level and its ease of being split into multiple small cores or fused into one large core.

![Architecture logic diagram](../figs/uArch/GFU_TOP_logicBcore.png)

The large core architecture diagram is as follows:

![Architecture large core diagram](../figs/uArch/GFU_TOP_bigcore.png)

After the big core is separated from the small core, the architecture diagram is as follows:

![Architecture small core diagram](../figs/uArch/GFU_TOP_littlecore.png)


As shown in the figure above, Block core splitting only requires the following points:

1. Split the shared ROB, Issue Queue, and Rename logic, and each block only serves one PE.

2. Each PE becomes an independent small core. Each PE will only access the GRF within that PE, and the channel for mutual access to the GRF between PEs is disabled.

3. Each PE has an exclusive LSU unit and disables the MDU channel.

4. exceptioninterrupt and other logic are handed over to the ROB after the block processing. Rollback, Replay and other processing only affect this PE.

What can be seen is that after splitting the small core, all logic except the MDU works normally as before, there is no non-working hardware, and a relatively high area utilization is achieved.