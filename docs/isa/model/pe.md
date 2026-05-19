# Instruction execution module

## Main content

1. pe_iex’s microinstruction pipeline
2. For the functions or purposes of the main modules of pe and iex, please refer to: [PE Introduction] (../../pe/ope.md), as well as the code descriptions for realizing their functions.

## PE and IEX Pipelines

The overall pe_iex pipeline is shown in the figure below:

![pe/iex pipeline](../../figs/model/model_detail/pe_iex_pipeline.svg "pe/iex流水线")

## PE and EX various modules

* [pe_ifu](./pe_ifu.md)

* [pe_ibp](./pe_ibp.md)

* [pe_rob](./pe_rob.md)

* [iex-dispatch](./iex_dispatch.md)

* [iex-iq](./iex_issueq.md)