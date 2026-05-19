# TPC

## Description

The microinstruction pointer register (**Temporal Program Counter**, referred to as **TPC**) is used to indicate the address of the microinstruction within the block being executed.

## Initialization

**TPC** will be initialized to the first microinstruction address in header every time block instruction starts. TPC indicates the microinstruction currently executing and is incrementally incremented during block instruction execution.

## Release

When block instruction is submitted, the TPC status is released by the hardware, and the TPC register is available again for the next block instruction.

## Features

**Private**: TPC is only valid within the current block instruction, other block instruction cannot access the current TPC status.

## Access properties

This register is read-only (RO).