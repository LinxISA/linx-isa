# 0.31 version update

Date: September 18, 2023

For the path to the web version of the instruction encoding design document, please see [LinxISA Encoding-v0.31](http://dbox.huawei.com/detaildocs?oid=VR%3Awt.doc.WTDocument%3A100255902243)

The v0.31 version is mainly an update to the header encoding.

## header changes

v0.31 defines 10 types of block instructionheader instruction including **standard block**, **standard super block**, **standard compression fast**, **standard super compression block**, **standard floating point block**, **standard floating point super block**, **inline block**, **control block**, **template block** and **system block**.

- Put instructions in the 16-bit encoding space into standard compression blocks and standard super compression blocks for execution.
- Add inline block to embed instructions in header.
- The concat block is removed and the LBREF block is added to realize long jump, long index and loop control.
- Delete the auxiliary block, and move the microinstructions in the original auxiliary block to the standard block for execution.

block type defined in v0.31 is as follows:

| block type | Explanation | Assembly Identification |
|---------------------|---------------------|-------------|
| Standard Block | Standard Block | b.std |
| Standard Hyper Block | Standard Hyper Block | b.stdh |
| Standard Compressd Block | Standard Compressed Block | b.stdc |
| Standard Compressd Hyper Block | Standard Compressed Hyper Block | b.stdhc |
| Floating-point Block | Standard floating-point block | b.fp |
| FP Hyper Block | Standard floating point super block | b.fph |
| Inline Block | Inline block | b.inl |
| Control Block | Control Block | See specific block instruction |
| Template Block | template block | See specific block instruction |
| System Block | System Block | b.sys |
| System Hyper Block | System Hyper Block | b.sysh |