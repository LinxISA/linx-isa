# IEXDispatch

## Function

1. Distribute the renamed microinstructions to each isq

![iex_dispatch](../../figs/model/model_detail/iex_dispatch.svg)

## Data structure

* pe_iex_alu_array
Function: The arithmetic instructions issued by each PE renaming stage will be sent to pe_iex_alu_array first, and then distributed to an aluIQ using a load balancing strategy.
Implementation: Queue of SimQueue

* pe_iex_lda_array
Function: The load command issued by each PE renaming stage will be sent to pe_iex_alu_array first, and then distributed to an ldaIQ according to the load balancing strategy.
Implementation: Queue of SimQueue

* pe_iex_sta_array
Function: The store(addr) command issued in each PE renaming stage will be sent to pe_iex_alu_array first, and then distributed to a certain staIQ according to the load balancing strategy.
Implementation: Queue of SimQueue

* pe_iex_std_array
Function: The store(data) command issued by each PE renaming stage will be sent to pe_iex_alu_array first, and then distributed to a stdIQ according to the load balancing strategy.
Implementation: Queue of SimQueue

* pe_iex_bru_array
Function: The branch instructions issued in each PE renaming stage will be sent to pe_iex_alu_array first, and then distributed to a certain bruIQ using a load balancing strategy.
Implementation: Queue of SimQueue

## Execution process

1. Call OPE::insertToPEArray() to insert the microinstructions after the rename stage into each pe_iex_q
2. Then call DispatchUnit::dispatch() to distribute the instructions in pe_iex_array to an IQ using a load balancing strategy.