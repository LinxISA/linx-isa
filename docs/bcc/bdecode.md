# Block parsing unit (Block Decode)

The block parsing unit is mainly responsible for parsing a 128-bit block instruction retrieved by the BFU, and obtaining the input, output, microinstruction code offset, block type, block characteristics and other information. This information will be used in its downstream modules.

## BlockID generation

Since the Block ROB is divided into each PE, the micro-architecture needs to set up a centralized module in the parsing unit to generate a globally continuous Block ROBID and pass it to the downstream and each PE.