ENTRY(_start)

PHDRS {
  text PT_LOAD FLAGS(5);
  data PT_LOAD FLAGS(6);
}

SECTIONS {
  . = 0x00010000;
  .text : {
    KEEP(*(.text.startup))
    *(.text*)
  } :text
  .rodata : { *(.rodata*) } :text

  . = ALIGN(0x1000);
  .data : { *(.data*) } :data
  .bss (NOLOAD) : {
    __bss_start = .;
    *(.bss*)
    *(COMMON)
    __bss_end = .;
  } :data

  . = ALIGN(16);
  .bootstack (NOLOAD) : {
    __start_init_stack = .;
    . += 0x10000;
    __end_init_stack = .;
  } :data
}
