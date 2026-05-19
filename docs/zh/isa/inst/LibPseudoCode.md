# 指令实现伪代码函数

该篇用来介绍微指令执行过程中使用的通用伪代码函数。

## <span id="locationA">解析参数</span>

```c
// UInt()
// ======

integer UInt(bits(width) x)
    integer index = 0;
    for i = 0 to width-1
        if x<i> == 1 then index += 2^i;     // 2^i：表示2的i次方
    return index;
```

## <span id="locationB">通用寄存器读写函数</span>

```c
// R[] - 通用寄存器读
// ==================
// 从一个通用寄存器中读 32 或 64 位值。

bits(width) R[integer index, integer width]
    assert index >= 0 && index <= 31;
    assert width in {32, 64};

    if index <= 23 then
        return R[index]<width-1 : 0>;    //全局的R寄存器
    else if index <= 27 then
        return TR[index-23]<width-1 : 0>;    // 块内T队列寄存器
    else
        return UR[index-27]<width-1 : 0>;    // 块内U队列寄存器

// R[] - 通用寄存器写
// ==================
// 向一个通用寄存器中写 32 或 64 位值。

R[integer index, integer width] = bits(width) value
    assert index >= 0 && index <= 31;
    assert width in {32, 64};

    if 0 < index && index <= 23 then
        R[index] = SignExtend(value);
    else if index == 30 then
        UR[id] = SignExtend(value);
    else if index == 31 then
        TR[id] = SignExtend(value);
    else
        return;
```

## <span id="locationC">系统寄存器读写函数</span>

```c
// SSR[] - 系统寄存器读
// =====================
// 从一个系统寄存器中读 32 或 64 位值。
bits(width) SSR[bits(16) SSR_ID, integer width]
    return System_Register[SSR_ID]<width-1 : 0>;

// SSR[] - 系统寄存器写
// ====================
// 向一个系统寄存器中写 32 或 64 位值。
bits(width) SSR[bits(16) SSR_ID, integer width] = bits(width) value
    System_Register[SSR_ID] = SignExtend(value);
```

## <span id="locationD">系统寄存器读函数-特定指令</span>

```c
// SSRRD[] - 系统寄存器读
// ======================
// 从一个系统寄存器中读 32 或 64 位值。

bits(width) SSRRD[integer index, integer width]
    assert index >= 0 && index <= 31;
    assert width in {32, 64};

    when index == 0
        return System_Register[0x0010]<width-1 : 0>;    // TP
    when index == 1
        return System_Register[0x0011]<width-1 : 0>;    // GP
    when index == 2
        return System_Register[0x0012]<width-1 : 0>;    // EBSTATEP
    when index >=3 
        return 0;
```

## <span id="locationE">将操作数左移</span>

```c
// LeftShift()
// ============

bits(width) LeftShift(bits(width) value, integer shift)
    assert shift >= 0;
    return (value << shift)<width-1 : 0>;
```

## <span id="locationF">对操作数符号扩展</span>

```c
// SignExtend()
// =============

bits(width) SignExtend(bits(N) value)
    integer width = 64;
    for i = N to width-1
        value<i> = value<N-1>;
    return value<width-1 : 0>;
```

## <span id="locationG">对操作数无符号扩展</span>

```c
// ZeroExtend()
// =============

bits(width) ZeroExtend(bits(N) value)
    integer width = 64;
    for i = N to width-1
        value<i> = 0;
    return value<width-1 : 0>;
```

## <span id="locationH">对操作数按位取反</span>

```c
// Not()
// =====

bits(width) Not(bits(width) value){
    for i = 0 to width-1
        if value<i> == 0 then value<i> = 1;
        else value<i> = 0;
    return value<width-1 : 0>;
}
```

## <span id="locationI">对操作数按位取反加一</span>

```c
// Negative()
// ============

bits(width) Negative(bits(width) value){
    bits(width) result = Not(value) + 1;
    return result<width-1 : 0>;
}
```

## <span id="locationJ">获取操作数置位最高位</span>

```c
// HighestSetBit()
// ===============

bit HighestSetBit(bits(width) value):
    for i = width-1 to 0
        if value<i> == 1 then return i;
    return -1;
```

## <span id="locationK">解析逻辑立即数</span>

```c
// DecodeImm()
// ===========

bits(width) DecodeImm(bit N, bits(6) imms, bits(6) immr)
    integer length;
    if N == 1 then
        length = 6;
    else
        length = HighestSetBit((~imms)&0x3f);

    if length < 1 then undefined;

    integer esize = 1<<length           // 模式串长度
    integer setBits = imms&(esize-1)    // 连续的置1位数
    if setBits == esize-1 then undefined;

    bits(esize) elem = (1<<(setBits+1))-1    // 模式串
    integer r = immr&(esize-1)               // 有效的循环右移位数
    bits(esize) nelem = ((elem>>r)|(elem<<(esize-r)))&((1<<esize)-1)    // 循环右移

    while esize < 64    // 扩展到64bit
        nelem |= nelem<<esize
        esize = esize<<1
    nelem &= (1<<64)-1

    return nelem;
```

## <span id="locationL">解析整型输入参数</span>

```c
// DecodeINT()
// ============

{integer, DataType} DecodeINT(bits(10) x)
    integer index = 0;
    DataType datatype;

    for i = 0 to 6
        if x<i> == 1 then index += 2^i;     // 2^i：表示2的i次方
    
    when x[9:7] == 000 : datatype = Unsigned INT64;
    when x[9:7] == 001 : datatype = Unsigned INT32;
    when x[9:7] == 010 : datatype = Unsigned INT16;
    when x[9:7] == 011 : datatype = Unsigned INT8;
    when x[9:7] == 100 : datatype = Signed INT64;
    when x[9:7] == 101 : datatype = Signed INT32;
    when x[9:7] == 110 : datatype = Signed INT16;
    when x[9:7] == 111 : datatype = Signed INT8;

    return {index, datatype};
```

## <span id="locationM">解析浮点型输入参数</span>

```c
// DecodeFP()
// ==========

{integer, DataType} DecodeFP(bits(10) x)
    integer index = 0;
    DataType datatype;

    for i = 0 to 6
        if x<i> == 1 then index += 2^i;     // 2^i：表示2的i次方
    
    when x[9:7] == 000 : datatype = FP64;
    when x[9:7] == 001 : datatype = FP32;
    when x[9:7] == 010 : datatype = FP16;
    when x[9:7] == 011 : datatype = FP8;
    when x[9:7] == 100 : datatype = undefined;
    when x[9:7] == 101 : datatype = undefined;
    when x[9:7] == 110 : datatype = BF16;
    when x[9:7] == 111 : datatype = FP8.1;

    return {index, datatype};
```

## <span id="locationN">解析输出参数</span>

```c
// DecodeDst()
// ============

{integer, integer} DecodeDst(bits(10) x)
    integer index = 0;
    integer datawidth;

    for i = 0 to 6
        if x<i> == 1 then index += 2^i;     // 2^i：表示2的i次方
    
    when x[8:7] == 00 : datawidth = 64;
    when x[8:7] == 01 : datawidth = 32;
    when x[8:7] == 10 : datawidth = 16;
    when x[8:7] == 11 : datawidth = 8;

    return {index, datawidth};
```

<!-- 

## 寄存器读写函数

```c
// DecodeWidth()
// ===============
// 解码并行块内整型操作指令的源寄存器域，返回操作数。

integer DecodeWidth(bits(2) wid)
    integer width;
    case coding[8:7] of:
        when 00 then width = 64;
        when 01 then width = 32;
        when 10 then width = 16;
        when 11 then width =  8;
    return width;
```
 -->

<!-- ```c
// DecodeINT[]
// ============
// 解码并行块内整型操作指令的源寄存器域，返回操作数。

bits(64) DecodeINT[bits(10) coding]
    assert coding in [0, 1023];
    integer index = UInt(coding[6:0]);
    integer width = 64;

    case coding[8:7] of:
        when 00 then width = 64;
        when 01 then width = 32;
        when 10 then width = 16;
        when 11 then width =  8;

    bits(width) value = V[index, width];
    if coding[9] == 0 then 
        return ZeroExtend(value);
    else
        return SignExtend(value);

// DecodeFP[]
// ============
// 解码并行块内浮点指令的源寄存器域，返回操作数。

DataType DecodeFP[bits(10) coding]
    assert coding in [0, 1023];
    integer index = UInt(coding[6:0]);
    integer width = 64;

    enum FloatType{
        FP8,FP16,FP32,FP64,FP8.1,BF16
    } DataType;

    Case coding[9:7] of:
        when 000 then DataType = FP64, width = 64;
        when 001 then DataType = FP32, width = 32;
        when 010 then DataType = FP16, width = 16;
        when 011 then DataType = FP8,  width =  8;
        when 100 then undefined;
        when 101 then undefined;
        when 110 then DataType = BF16,  width = 16;
        when 111 then DataType = FP8.1, width =  8;

    DataType value = V[index, width];
    return value;
``` -->

```c
// V[] - 寄存器读
// ===============
// 从一个全局寄存器或并行块私有寄存器中读 8, 16, 32 或 64 位值。

bits(width) V[integer index, integer width]
    assert index in [0, 127];
    assert width in {8, 16, 32, 64};

    if      index in [0, 7]   then return TR[index+1]<width-1:0>;    // 块内T寄存器队列
    else if index in [8, 15]  then return UR[index-7]<width-1:0>;    // 块内U寄存器队列
    else if index in [16, 23] then return MR[index-15]<width-1:0>;   // 块内M寄存器队列
    else if index in [24, 31] then return NR[index-23]<width-1:0>;   // 块内N寄存器队列
    else if index in [32, 55] then return  R[index-32]<width-1:0>;   // 全局的R寄存器
    else if index == 64 then return SSR[0x0020]<width-1:0>;          // LC0
    else if index == 65 then return SSR[0x0021]<width-1:0>;          // LB0
    else if index == 68 then return SSR[0x0024]<width-1:0>;          // LC1
    else if index == 69 then return SSR[0x0025]<width-1:0>;          // LB1
    else if index == 72 then return SSR[0x0028]<width-1:0>;          // LC2
    else if index == 73 then return SSR[0x0029]<width-1:0>;          // LB2
    else undefined;

// V[] - 寄存器写
// ===============
// 向一个全局寄存器或并行块私有寄存器中写 8, 16, 32 或 64 位值。

V[integer index, integer dstwidth] = bits(width) value
    assert index in [0, 55];
    assert dstwidth in {8, 16, 32, 64};

    if      index == 0 then TR[id]<dstwidth-1:0> = value<dstwidth-1:0>;    // 块内T寄存器队列
    else if index == 1 then UR[id]<dstwidth-1:0> = value<dstwidth-1:0>;    // 块内U寄存器队列
    else if index == 2 then MR[id]<dstwidth-1:0> = value<dstwidth-1:0>;    // 块内M寄存器队列
    else if index == 3 then NR[id]<dstwidth-1:0> = value<dstwidth-1:0>;    // 块内N寄存器队列
    else if index in [33, 55] then R[index-32]<63:0> = value<63:0>;    // 全局R寄存器
    else undefined;
```

## <span id="locationO">浮点类型判断</span>

```c
// FP_Class
// =========
// 结果返回浮点数类型与符号位

(fptype, sign) FP_Class(Type value)
    assert Type in {fp8, fp16, fp32, fp64, fp8.1, bf16};

    bit sign;                                 // 符号位
    exponent;                                 // 指数部分
    fraction;                                 // 尾数部分

    when type == fp64 : 
        sign = value<63>;
        bits(11) exponent = value<62:52>;
        bits(52) fraction = value<51:0>;
    when type == fp32 :
        sign = value<31>;
        bits(8)  exponent = value<30:23>;
        bits(23) fraction = value<22:0>;
    when type == fp16 :
        sign = value<15>;
        bits(5)  exponent = value<14:10>;
        bits(10) fraction = value<9:0>;
    when type == bf16 :
        sign = value<15>;
        bits(8) exponent = value<14:7>;
        bits(7) fraction = value<6:0>;
    when type == fp8 :
        sign = value<7>;
        bits(4) exponent = value<6:3>;
        bits(3) fraction = value<2:0>;
    when type == fp8.1 :
        sign = value<7>;
        bits(5) exponent = value<6:2>;
        bits(2) fraction = value<1:0>;

    // 指数全部为0
    if exponent == 0 then
        if fraction == 0 then return (FP_Zero, sign);    // 尾数全部为0，表示0.0
        else return (FP_Subnormal, sign);                // 尾数不为0，表示非规格数
    // 指数全部为1
    else if exponent == -1 then
        if fraction == 0 then return (FP_INF, sign);     // 尾数全部为0，表示无穷数
        else                                             // 尾数非0，表示非数
            if fraction<XLEN> == 0 then return (FP_SNaN, -);   // 尾数最高位为0，表示发信非数
            else return (FP_QNaN, -);                          // 尾数最高位为1，表示静默非数
    else
        return (FP_Normal, sign);     // 其他情况为规格数Normal
```

## <span id="locationP">浮点求倒数函数</span>

```c
// FRECIP()
// =========

bits(width) FRECIP(Type value, integer width)
    assert width in {8, 16, 32, 64};
    assert Type in {fp8, fp16, fp32, fp64, fp8.1, bf16};

    bits(width) result;
    (fptype, sign) = FP_Class(Type value);     // 判断浮点数据类型

    if fptype == FP_Zero then
        if sign == 0 then result = +infinity;   // 输入为+0，返回正无穷大
        else result = -infinity;                // 输入为-0，返回负无穷大
    else if fptype == FP_INF then
        if sign == 0 then result = +0;    // 输入为正无穷大，返回+0
        else result = -0;                 // 输入为负无穷大，返回-0
    else if fptype == FP_Normal then
        result = 1.0 / value;    // 输入为规格化浮点数，返回其倒数
    else if fptype == FP_QNaN then
        result = value;          // 输入为静默非数，返回原值
    else if fptype == FP_SNaN then
        result = value;
        case Type of:                       // 输入为发信非数，返回尾数最高位置1的静默非数
            when fp8   then result<2> = 1;
            when fp8.1 then result<1> = 1;
            when fp16  then result<9> = 1;
            when bf16  then result<6> = 1;
            when fp32  then result<22> = 1;
            when fp64  then result<51> = 1;
        // 输入为发信非数，根据SSR寄存器的Enables位决定是否产生异常
        ProcessException(InvalidOp, Enables);    
    else undefined;

    return result;
```
