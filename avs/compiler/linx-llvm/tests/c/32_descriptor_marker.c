// Emit a canonical B.ARG descriptor header opcode so mnemonic coverage includes
// descriptor-only metadata instructions in strict v0.56.
void emit_barg_marker(void) {
  __asm__ volatile(".long 0x180221a3" ::: "memory");
}
