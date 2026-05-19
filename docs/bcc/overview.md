# Block Control Core (BCC)

The block control core is the processing and distribution unit of header. It delivers instruction blocks to each PE out of order, allowing each PE to process different instruction blocks in parallel, thus utilizing inter-block parallelism (Block Parallelism) to the maximum extent. In the block control core, the overall hardware processing is block instruction (Block Header). Like ordinary processors, the block control core is also divided into front and rear ends:

## Block Control Core Frontend Pipeline (BCC Frontend)

It includes block instruction [branch prediction unit] (./bp.md), [fetch unit] (./bifu.md), [decoding] (./bdecode.md), [scheduling unit] (./bdispatch.md), etc. Mainly responsible for fetching instructions header instruction and distributing blocks to appropriate execution engines through algorithms.

## Block Control Core Backend Pipeline (BCC Backend)

It includes [general-purpose register rename] (./bren.md), [reorder cache] (./brob.md), emission pipeline, [general-purpose register heap] (ZXM DLINK6QXZ), [Block Address Cache] (./bhcache.md), [PE Execution Engine] (../pe/ope.md), etc., are responsible for the processing and efficient execution of block instruction.

In order to effectively expand the number of back-end execution engines and effectively reduce hardware wiring costs, the microarchitecture decouples the back-end logic of BCC to each execution engine as much as possible in the block dimension and binds it to the execution engine. The bound structure is called **PE Tile**. Therefore, the architecture presents the structure of an overall block control core front-end pipeline and N block control core back-end pipelines. The details are as follows:

![Architecture BCC](../figs/uArch/bcc_overview.png){ width="800" }

## BCC overall pipeline

![BCC overall pipeline](../figs/model/BCC.png)