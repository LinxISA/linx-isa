# Hint Interface for HW/SW co-design

Existing research works that require new architectural support for SW guidance (or hints) tend to approach the problem in an ad-hoc manner, typically using a combination of new instructions and new architecturally-exposed registers that serve only the purpose of the proposed optimization. The challenge of providing a general-purpose HW/SW interface for a variety of hint use-cases appears to be a new one.

A proper hint abstraction must be able to support an arbitrary amount of data, metadata and instructions associated with each hint. The integration of hints should orthogonalize with the existing ISA as much as possible – i.e., hints should not disrupt the encoding or operation of existing instructions.

One potential abstraction for hints is a dedicated hint instruction embedded in the regular instruction stream by the compiler at the hint trigger point, which contains control bits and a pointer to a memory region containing all of the code and (meta)data required by the hint. Execution of the hint instruction can direct fetch or (meta)data loads, depending on the control bits, to the region pointed to by the hint instruction. However, we note that while this abstraction appears promising, there needs to be a robust understanding of the various potential use-cases for hints, which can then drive the actual ISA design.

