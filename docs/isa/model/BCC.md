# BCC (Block Control Core)

The purpose of this chapter is to help you quickly understand the implementation of LinxISA microarchitecture.

## Main content

1. block instruction level assembly line
2. Briefly describe the functions or purposes of the main modules of BCC [[For details, see: Introduction to Block Control Core BCC]] (../../bcc/overview.md) and the code description to implement its functions.

## Description

How data flows to the next level:
(1) Write the next status of the next flow level;
(2) Write to a queue (the data entered in this queue will only be visible in the next cycle);
(3) Set a status for each flow level, and assign it to the next flow level after the work is completed.

## BCC overall pipeline

- **BCC pipeline**

![BCC pipeline](../../figs/model/model_detail/BCC.svg)

## BPC reset - execute first block

*sim->core->setBPC(start_addr);*
\=> *bctrl->interrupt(req);*
\===> *blockFetchUnit.jumpTo(req.initPC);*
\=====> *bfu->createNewF0(bpc, 0, true); // Set the first level pipeline according to BPC*

## Execution of each stage

- [View BIFU](./BIFU.md)
- [View Decode](./BCTRL.md)
- [View BRename](./BRename.md)
- [View BIssue](./BIssue.md)
- [View BROB](./BROB.md)