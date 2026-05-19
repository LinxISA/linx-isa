## Background introduction

In the process of BISA's continuous deduction, we found that appropriately combining some Blocks into one Hyper Block will produce performance or Codesize benefits. The decision: which Blocks to merge into Hyper Blocks does not only rely on static analysis of the program, but more, we need some runtime data to support the decision of making Blocks Hyper. To this end, this article will discuss a BISA language extension: when the programmer knows enough about the application, or has used analysis tools such as pref to know which piece of C code is suitable for merging into a Hyper Block, how to give compiler hints at the C source code level, and ultimately obtain performance or Codesize benefits.

**Note**: This article does not discuss why Hyper Block should be introduced; in what scenarios it is optimal to use Hyper Block; whether Blocks Hyperization can be completely implemented by the compiler through xxx methods, so that programmers are not aware of it, etc. Only discuss:
**When the programmer knows which piece of C code is suitable to be merged into a Hyper Block, how to modify the C source code to give the compiler a prompt** is this proposition.

## Scheme description (the current pragma scheme is not supported on 0.50 yet)

Refer to openMP, which uses pragma guidance to give compiler prompts in the C source code. The keyword `block { }` indicates that the domain indicated by the curly braces is compiled into a Hyper Block, for example:
```c
int arr[10] = {1,2,3,4,5,6,7,8,9,0};
void test(int n, int a) {
  #pragma linx block
  {
  for (int i = 0; i < n; ++i) {
    arr[i] += a;
  }
  }

  arr[4] -= a;

  #pragma linx block
  {
    if (arr[3] > a)
      arr[3] -= a;
    else
      arr[3] += a;
  }
}
```

## Constraints and Limitations

### Entry 1
The curly braces `{ }` in `#pragma linx block { }` are the standard syntax of domain/compound statements in C language, which need to meet the syntax rules of C language itself: for example, variables defined in `{ }` cannot be accessed externally.

### Entry 2
One function is allowed to have multiple fields to be compiled into Hyper Blocks; nested Hyper Block fields are meaningless, and the compiler will report an error;

### Entry 3
Due to the following limitations of the Hyper Block design itself:

- Top single entry: Caller is not allowed to jump to an instruction inside the Hyper Block
- Single out at the bottom: Hyper Block cannot be jumped out inside

Therefore, `#pragma linx block { }` does not allow:

- There is a statement similar to `goto`, which jumps directly to the interior of the `block { }` domain.
- There are statements similar to `goto`/`return`, which jump directly to the outside in the `block { }` domain.
> Note: `break` is supported in the `for/switch` statement. Because essentially these `break` and the termination of the statement block point to the same position (that is, the end of the statement block).
- Function Call exists inside Hyper Block