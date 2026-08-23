// Emit canonical B.DATR NORM/FP32/Zero defaults so mnemonic coverage includes
// descriptor-only metadata instructions in strict v0.58.3.
void emit_bdatr_marker(void) {
  __asm__ volatile(".long 0x00001023" ::: "memory");
}
