# interrupt

interrupt is an asynchronous event detected by the instruction pipeline. The instruction pipeline can change the current instruction sequence according to the detection strategy and transfer to other sequences to continue execution. Unlike the synchronous exception, logically interrupt does not need to interrupt the current pipeline step immediately.

In `ZXTERMZH38QXZ逻辑核`, interrupt can come from inside `ZXTERMZH38QXZ物理核` or from outside it. These interrupt are collected into a unified data structure by a set of logical objects called `Xproxy` and are uniformly scheduled by the `ZXTERMZH38QXZ逻辑核` instruction pipeline.

Before these interrupt are `响应`, these interrupt will remain in a Pending state. This state can be obtained from system register[IPENDING](../register/ssr/IPENDING.md).

The following table provides a list of all Xproxy collected interrupt types that are currently supported. Sort by priority, the higher the priority, the higher the priority:

- ACR0interrupt: interrupt bound to ACR0
   - ACR0_EI: External interrupt bound to ACR0. Used for interrupt generated outside `ZXTERMZH38QXZ物理核`.
   - ACR0_TI: Internal clock interrupt bound to ACR0. Used for timing signals in `ZXTERMZH38QXZ物理核`.
- ACR1interrupt: interrupt bound to ACR1
   - ACR1_EI: External interrupt bound to ACR1.
   - ACR1_TI: Bind to ACR1's internal clock interrupt.

Each interrupt has a default binding `ACR`. This ACR is usually used as the default destination ACR for interrupt routing, unless other routing protocols modify it.

!!! note "Attention!"

    System errors (such as RAS) are now considered a type of ACR0_EI and may be separated out if necessary in the future.

interrupt can be enabled by system register[ECONFIG](../register/ssr/ECONFIG.md) according to the interrupt type, or this ACR can be disabled by the I bit of system register[CSTATE](../register/ssr/CSTATE.md). When the Linx logic core (LxLC) can activate interrupt, among all interrupt that meet all the following rules, it selects the highest priority interrupt as the activated interrupt:

* The corresponding system register[IPENDING](../register/ssr/IPENDING.md) of interrupt is 1;
* The corresponding system register[ECONFIG](../register/ssr/ECONFIG.md) of interrupt is 1;

* Any one of the following conditions is true:

  * The target routing ACR of the interrupt is higher than the current ACR of the Linx logic core (LxLC);
  * The target route ACR of this interrupt is equal to the current ACR of the Linx logical core (LxLC), and the current CSTATE.I is 1.

For different ACRn, system register[IPENDING](../register/ssr/IPENDING.md) and system register[ECONFIG](../register/ssr/ECONFIG.md) describe the same interrupt collection data structure. Only when `n` is greater than or equal to the described bound interrupt is the corresponding bit valid; otherwise the bit is defined as "reserved". See the corresponding SSR description for details.

The Linx logic core (LxLC) executes the `ASYNC_SERVICE_REQUEST` flow when activating an interrupt. Please note:

1. In the ASYNC_SERVICE_REQUEST process, the Linx logic core (LxLC) will not detect the new interrupt, so no other cross-over interrupt processing will occur in the middle.
2. The ASYNC_SERVICE_REQUEST process may access EBSTATE. This process may cause exception. The software needs to consider effective means to avoid this possibility, otherwise the exception process may cover some public registers.

## interrupt response

The software responds to interrupt by writing the interrupt code to system register[EOIEI](../register/ssr/EOIEI.md). Before interrupt is responded to, it remains in the Pending state. If this interrupt still meets the conditions in the next interrupt detection, interrupt will be stimulated again. If Xproxy detects a new signal after the Pending status of interrupt is eliminated, it can reset this status.
