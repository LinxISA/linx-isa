.text
.globl _start
_start:
  C.BSTART
  lui 32, ->a0
  hl.liu 1684828007, ->a1
  swi a1, [a0, 0]
  hl.liu 1982688869, ->a1
  swi a1, [a0, 4]
  hl.liu 170997813, ->a1
  swi a1, [a0, 8]
  C.BSTOP

  C.BSTART
  hl.liu 21845, ->a0
  hl.liu 268472320, ->t
  swi a0, [t#1, 0]
  C.BSTOP

.Lhang:
  C.BSTART DIRECT, .Lhang
  C.BSTOP

.section .result,"aw",@progbits
.globl cross_model_result
.type cross_model_result,@object
.size cross_model_result,12
cross_model_result:
  .zero 12
.globl cross_model_result_size
.set cross_model_result_size,12
