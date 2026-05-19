# Simpoint scheme and slicing process

This document is mainly used to briefly introduce the Simpoint solution and the slicing process of Linx Instruction Set Architecture.

## Simpoint solution

### Overview

What is it? The Simpoint solution uses parts to represent the whole, trying to use local code segments to represent the entire program.

Why use Simpoint? The CPU performance simulation model has its own limitations. The running efficiency of the model is slow. When running large-scale performance verification programs, such as SPECCPU, the running time is calculated on a monthly basis.

### Simpoint process

![Simpoint process](../figs/intro/simpoint_classic_process.png)

* Feature value: It can be understood as abstracting feature information from the entire program, and using feature information to represent the entire program.
* Clustering: It is to classify all input BBV according to their similarity.
* Selection algorithm: select the most typical one from each cluster;

## Linx Instruction Set Architecture slicing process

Trace Manager uses the partial information obtained by the Simpoint solution that can represent the whole as input, and captures the partial execution flow when QEMU is running.

![Slicing process](../figs/intro/ckpt_process.png)

### Introduction to QEMU

QEMU is simply a CPU function simulation model that only simulates functions, not performance. Although the execution efficiency is not as good as that of a physical machine, it is much faster than the performance model.

Broadly speaking, QEMU is a platform, an open source emulator and virtual machine monitor (Virtual Machine Monitor, VMM).

It mainly provides two functions for users: one is as a **user mode simulator**, using the dynamic code translation mechanism to execute code that is different from the host architecture. The second is to act as a **Virtual Machine Supervisor** to simulate the entire system and use other VMMs (Xen, KVM, etc) to use the virtualization support provided by the hardware to create virtual machines with performance close to that of the host.

### Introduction to Trace Manager

Trace Manager is a capture tool for program execution flow. It uses the API interface provided by QEMU to capture the instruction code of instruction execution, the memory address accessed and other information.