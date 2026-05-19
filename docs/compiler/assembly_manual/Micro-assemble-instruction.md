# Microinstruction assembly instructions

For the assembly syntax of microinstructions, please see: [LinxISA Manual] (https://openx.huawei.com/mkdocs/project/1410/blockisa-doc/docs/site/docs/). The following is a detailed description based on public microinstructions and private microinstructions: public microinstructions refer to those that can be used in all basic block type, and private microinstructions refer to those that can only be used in the corresponding block type.

**Note**: In the description of microinstruction assembly syntax<br>

- SrcL represents the left source operation object, the syntax type is a register, which may be either LL_GPR or UL_GPR<br>
- SrcR represents the right source operation object, the syntax type is a register, which may be either LL_GPR or UL_GPR<br>
- shamt represents the offset value, and the syntax type is immediate.
- simm represents signed immediate value, and the syntax type is expression (immediate value or label)
- uimm represents unsigned immediate value, and the syntax type is expression (immediate value or label)