# 0.50版本更新

更新日期：2025年5月26日

指令编码设计文档网页版路径请见[LinxISA Encoding-0.50](https://dbox.huawei.com/detaildocs?oid=VR:wt.doc.WTDocument:100973044043)

## 更新背景

厂商昇腾AI处理器及其达芬奇指令集面临了众多产品的挑战，在多种场合已经遇到了演进瓶颈。AI Core每代架构迭代均需重写算子库，根源在于计算抽象层未实现机制（如内存访问模式）与策略（如数据分块策略）的解耦，导致硬件规格变动直接冲击软件栈稳定性。

在此背景下，公司领导将核架构的演进任务交给了灵犀指令集。他们希望构建自主可控的异构计算架构体系，突破传统GPU的范式桎梏，实现在人工智能、图形渲染及高性能计算领域的跨代际竞争力。NVIDIA的CUDA生态已形成“硬件-编译器-算子库-应用框架”的全栈闭环，其护城河不仅在于硬件性能，更在于十余年累积的开发者粘性。厂商若采用跟随策略，既面临专利壁垒与兼容性成本，也难以在既有生态中实现差异化价值。

灵犀指令集要完成该任务，首先需要从静态代码量和动态指令数的角度对基础标量指令进行进一步调优，保障指令集基座能够达到业内相对较高的水平。并以此为基础，进而针对人工智能、图形渲染及高性能计算领域进行扩展，逐步实现CPU、NPU和GPU的融合计算架构。

目前，灵犀指令集在编码优化上已达到了与ARM架构相似的水平，静态代码大小（codesize）大约是ARM架构的0.9倍。虽然静态代码已经相对优化，但在动态指令数上，灵犀指令集仍然比ARM多出约40%。动态指令数的膨胀，直接影响了执行效率和整体性能，尤其是在面对计算密集型任务时，指令数的增加会导致额外的处理延迟和计算资源的浪费。2025年被视为灵犀指令集在多个领域广泛应用的关键年份。为了在竞争中脱颖而出，我们需要一款能够在性能、指令数和代码密度上超越现有主流架构（如ARM和x86）的指令集。虽然追赶的路上已经取得了不错的进展，但要真正实现超越，尤其是在指令集设计的各个方面做到极致优化，还需要付出更多的努力与创新。因此，我们并不满足于v0.43的设计，我们希望在v0.5版本上，聚焦于显著降低动态指令数，进一步提升执行效率，并对代码密度和变长编码进行优化。因此这一版本的核心目标是通过针对性优化，在保证性能和稳定性的前提下，减少冗余指令，并确保指令集在实际应用中的高效表现。

下面是灵犀指令集V0.5版本演进计划：

![plan](../figs/isa/version/isa_plan.png){ width="800" }

## 更新概要

- 调整指令编码框架：统一规划 16bit / 32bit / 48bit / 64bit 指令格式，并合理预留编码空间；
- 重新规划指令空间，取消32bit中不同块类型的自定义空间，简化硬件解码复杂度。
- 补齐标量指令功能，保证标量基座的完善。
- 新增48bit指令支持，用于提升AI/渲染场景下参数配置效率；其中包括：双输出指令，Long Immediate加载指令，Load Literal指令，复杂操作指令。

## 具体内容

### 1.指令编码

为了解决不同块内编码重复问题，我们取消了对私有块内的编码空间，并对其进行了重新构建。同时引入**前缀+后缀**的编码方式，以保证仍有足够的指令空间以及提升块内指令的表达能力。 

- **48位指令**：由一个 `16位前缀` 加上一个 `32位主指令` 或 `32位后缀` 构成。前缀部分主要用于扩展操作码 和 立即数的高位信息，从而满足长立即数加载和复杂内存操作的需求。
- **64位指令**：则由 `32位前缀` 和 `32位主指令` 或 `32位后缀` 组成，为更极端的复杂操作提供足够的编码空间。

![space](../figs/isa/version/space.png){ width="800" }

- 主指令：无前缀单独定义特定语义的指令。
- 主指令+前缀指令：前缀指令只是对主指令进行信息补全，不影响指令语义。
- 前缀指令：必须匹配主指令或后缀指令，才有含义。通常用于额外信息补齐。
- 后缀指令：必须匹配前缀指令才有含义，单独后缀指令无含义。

| 组合 | 16bit指令 | 16bit前缀指令 | 32bit主指令 | 32bit后缀指令 | 32bit前缀指令 |
|------|-----------|--------------|---------------|-----------|-------------|
| 16bit指令 | - | × | - | × | × |
| 16bit前缀指令 | × | × | √ | √ | × |
| 32bit主指令 | - | × | - | × | × |
| 32bit后缀指令 | × | × | × | × | × |
| 32bit前缀指令 | × | × | √ | √ | × |

这种前缀+后缀结构不仅有效避免了不同指令块之间编码的重复和冲突，还使得指令解码过程更加清晰和模块化，便于硬件在解析时灵活处理不同长度指令。

### 2.指令命名  

通过指令前缀区别不同字长指令，规范指令命名。便于程序员理解和使用。

1. 16bit 压缩指令统一以"C."或 "c."作为前缀。  
2. 48bit 增强指令统一以"HL."或 "hl."作为前缀。  
3. 64bit 长指令统一以"L."或 "l."作为前缀。  

### 3.指令组合

16bit、32bit、48bit和64bit不同字长指令允许混编，所有指令使用同一套编码空间进行编码，因此可以进行混编。

### 4.16bit指令

1. 16bit指令编码整体调整
2. 删除B.NEXT.C指令，块头的长跳转改为通过48bit或64bit版本的BSTART指令编码。
3. c.addpc指令改名为c.setret，修改为c.setret后更符合指令语义，便于程序员使用和理解。
4. 删除指令c.addtpc，增加了48bit的Load/Store PC-Relative指令，可代替该指令功能。

![16bit](../figs/isa/version/16bit.png){ width="800" }

本版本增加了48bit的Load/Store PC-relative指令，可以代替c.addtpc与load/store指令组合加载symbol的方式，因此删除该指令。

以前版本加载symbol的方式：
```asm
    c.addtpc %hi(symbol), ->t
    ldi [t#1, %lo(symbol)], ->t
```
当前版本：
```asm
    hl.ld.pcr [symbol], ->t
```

### 5.32bit块头指令

1. BSTART指令**删除EX位**，BlockType字段扩展为5bit。后续增加48bit和64bit版本长跳转块头BSTART，因此不再需要B.NEXT指令，32bit版本的BSTART指令中也不需要通过EX位指示跳转距离与B.NEXT拼接。
2. 删除B.NEXT指令
3. 块输入输出指令B.IO改名为B.IOR，区分后续扩展的其他B.IO类指令
4. 增加EBREAK指令，提供软件断点功能

![bstart](../figs/isa/version/bstart.png){ width="800" }

### 6.32bit微指令

本版本修改的指令如下：

1. addpc指令改名为setret并与addtpc复用编码。与addtpc复用编码后可节省Opcode空间，预留更多空间给后续扩展。
2. ctz，clz指令语义调整，汇编中增加M和N参数（兼容ctzw, clzw的功能）。修改后指令实现更灵活，比特位操作指令编码方式趋于统一。
3. rev16，rev32和rev64合并为一条rev指令。统一编码格式，并且指令实现更灵活。
4. 增加bcnt指令  补充标量指令功能，用于计数寄存器中比特位为1的位数。
5. csel指令的第三个输入SrcR增加”.neg”可选参数。增加该参数后可以实现cneg操作，根据条件选择一个寄存器原值或负值。在525子项中可以获得减少动态指令数的收益。
6. 增加7条Load PC-Relative指令和4条Store PC-Relative指令。提高符号地址加载的效率，并通过减少对T寄存器的使用频率，进一步提升了指令集的性能和代码密度。
7. 原子指令增加far参数，并对高位command ID字段编码有修改，用于提供对特定Cache层级的原子操作。
8. 系统块内增加bwt指令，等待指定时间后唤醒线程。
9. acrc和acre指令的参数编码位置有调整，删除acre指令的目标ACR参数。acre指令激发的特权级切换的目标ACR由ECSTATE寄存器指定。
10. 浮点块内cvt指令拆分为fcvt，scvtf, ucvtf, fcvta, fcvtm, fcvtn, fcvtp, fcvtz等指令。对于不同数据格式转换场景提供对应的舍入模式。
11. 增加BSTART.CALL指令，具体为C.BSTART.CALL指令加c.setret组合表达的伪指令。

升级到0.50版本后，删除32bit指令列表如下：

| 指令列表 | 说明 |
|----------|-----------|
| b.eq, b.ne, b.lt, b.ge, b.ltu, b.geu, j, jr | 暂时不支持块内跳转，跳转场景统一使用块间跳转实现。（预留编码空间，如果后续验证需要再合入） |
| b.feq, b.fne, b.flt, b.fge |  暂时不支持块内跳转  |
| fsin, fcos, fclass, flog | 上个版本过设计内容，正式删除。 |

移至48bit扩展空间指令列表

| 分类 | 指令列表 | 说明 |
|------|----------|---------|
| 1. store.a类 | sb.a, sh.a, sw.a sd.a, sh.ua, sw.ua, sd.ua<br> sbi.a, shi.a, swi.a sdi.a, shi.ua, swi.ua, sdi.ua | 通过增加16bit前缀，补充目的寄存器编码以及加入Pre/Post Index的标志位。|
| 2. 系统寄存器访问 | ssrrd, ssrwr改名为hl.ssrget 和 hl.ssrset。| 通过增加16bit前缀，扩展SSR ID表达空间。 |
| 3. 带立即数乘加/减 | miadd, misub | 通过增加16bit前缀，扩展立即数范围。 |
| 4. 比特位操作   | bfi, ccat, ccatw  | 通过增加16bit前缀，表达双输出或扩展参数域。 |
| 5. 预取操作     | prf, prf.a, prfi.u, prfi.ua | 通过增加16bit前缀，可统一编码指示预取目标cache的字段。 |
| 6. 通用队列管理 | qmt, qpush, qpop | 通过增加16bit前缀，可编码双输出。 |
| 7. 原子比较交换 | casb, cash, casw, casd | 通过增加16bit前缀，可编码更多的寄存器输入。 |

### 7.增加48bit指令

| 分类 | 指令列表 |
|------|----------|
| 1. 增强版本的BSTART  |  HL.BSTART |
| 2. CALL块块头 | HL.BSTART.CALL |
| 3. 长立即数加载 | hl.lis, hl.liu, hl.lui |
| 4. 乘法双输出 | hl.mul, hl.mulu, hl.madd, hl.maddw |
| 5. ALUI类 | hl.addi, hl.subi, hl.andi, hl.ori, hl.xori |
| 6. ALUWI类 | hl.addiw, hl.subiw, hl.andiw, hl.oriw, hl.xoriw |
| 7. CMPI类 | hl.cmp.eqi, hl.cmp.nei, hl.cmp.andi, hl.cmp.ori, hl.cmp.lti, hl.cmp.gei, hl.cmp.ltui, hl.cmp.geui |
| 8. SETCI类 | hl.setc.eqi, hl.setc.nei, hl.setc.andi, hl.setc.ori, hl.setc.lti, hl.setc.gei, hl.setc.ltui, hl.setc.geui |
| 9. TPC-Relative | hl.addtpc, hl.setret |
| 10. 除法求余 | hl.div, hl.divu, hl.divw, hl.divuw, hl.rem, hl.remu, hl.remw, hl.remuw |
| 11. Load长立即数偏移 | hl.lbi, hl.lhi, hl.lwi, hl.ldi, hl.lbui, hl.lhui, hl.lwui, hl.lhi.u, hl.lwi.u, hl.ldi.u, hl.lhui.u, hl.lwui.u |
| 12. Load Pair（寄存器基址+寄存器偏移） | hl.lbp, hl.lhp, hl.lwp, hl.ldp, hl.lbup, hl.lhup, hl.lwup |
| 13. Load Pair（寄存器基址+立即数偏移） | hl.lbip, hl.lhip, hl.lwip, hl.ldip, hl.lbuip, hl.lhuip, hl.lwuip, hl.lhip.u, hl.lwip.u, hl.ldip.u, hl.lhuip.u, hl.lwuip.u |
| 14. Load Pre-Index（寄存器基址+寄存器偏移） | hl.lb.pr, hl.lh.pr, hl.lw.pr, hl.ld.pr, hl.lbu.pr, hl.lhu.pr, hl.lwu.pr |
| 15. Load Pre-Index（寄存器基址+立即数偏移） | hl.lbi.pr, hl.lhi.pr, hl.lwi.pr, hl.ldi.pr, hl.lbui.pr, hl.lhui.pr, hl.lwui.pr, hl.lhi.upr, hl.lwi.upr, hl.ldi.upr, hl.lhui.upr, hl.lwui.upr |
| 16. Load Post-Index（寄存器基址+寄存器偏移） | hl.lb.po, hl.lh.po, hl.lw.po, hl.ld.po, hl.lbu.po, hl.lhu.po, hl.lwu.po |
| 17. Load Post-Index（寄存器基址+立即数偏移） | hl.lbi.po, hl.lhi.po, hl.lwi.po, hl.ldi.po, hl.lbui.po, hl.lhui.po, hl.lwui.po, hl.lhi.upo, hl.lwi.upo, hl.ldi.upo, hl.lhui.upo, hl.lwui.upo |
| 18. Load PC-Relative寻址指令 | hl.lb.pcr, hl.lh.pcr, hl.lw.pcr, hl.ld.pcr, hl.lbu.pcr, hl.lhu.pcr, hl.lwu.pcr |
| 19. Store长立即数偏移 | hl.sbi, hl.shi, hl.swi, hl.sdi, hl.shi.u, hl.swi.u, hl.sdi.u | 
| 17. Store Pair（寄存器基址+寄存器偏移） | hl.sbp, hl.shp, hl.swp, hl.sdp, hl.shp.u, hl.swp.u, hl.sdp.u |
| 18. Store Pair（寄存器基址+立即数偏移） | hl.sbip, hl.ship, hl.swip, hl.sdip, hl.ship.u, hl.swip.u, hl.sdip.u |
| 13. Store Pre-Index（寄存器基址+寄存器偏移） | hl.sb.pr, hl.sh.pr, hl.sw.pr, hl.sd.pr, hl.sh.upr, hl.sw.upr, hl.sd.upr |
| 14. Store Pre-Index（寄存器基址+立即数偏移） | hl.sbi.pr, hl.shi.pr, hl.swi.pr, hl.sdi.pr, hl.shi.upr, hl.swi.upr, hl.sdi.upr |
| 15. Store Post-Index（寄存器基址+寄存器偏移） | hl.sb.po, hl.sh.po, hl.sw.po, hl.sd.po, hl.sh.upo, hl.sw.upo, hl.sd.upo |
| 16. Store Post-Index（寄存器基址+立即数偏移） | hl.sbi.po, hl.shi.po, hl.swi.po, hl.sdi.po, hl.shi.upo, hl.swi.upo, hl.sdi.upo |
| 21. Store PC-Relative | hl.sb.pcr, hl.sh.pcr, hl.sw.pcr, hl.sd.pcr |

### 64bit指令

本版本暂不修改原SIMT块内64bit指令，后序0.51版本统一修改。

| 分类 | 指令 | 说明 |
|------|-------|------|
| 1. 增加长跳转块头 | L.BSTART | 用于超长距离跳转场景，支持42位跳转偏移。 |
| 2. 增加CALL块块头 | L.BSTART.CALL | 相比HL.BSTART.CALL指令提供更大范围返回地址偏移 |
| 3. 增加长立即数加法指令 | l.addli | 用于与hl.lui组合，实现加载64位长立即数。 |
| 4. 增加Load PC-Relative寻址指令 | l.lb.pcr, l.lh.pcr, l.lw.pcr, l.ld.pcr, l.lbu.pcr, l.lhu.pcr, l.lwu.pcr | 提高符号地址加载的效率，并通过减少对T寄存器的使用频率。相比32bit和48bit版本提供更长的偏移距离。 |
| 5. 增加Store PC-Relative寻址指令 | l.sb.pcr, l.sh.pcr, l.sw.pcr, l.sd.pcr | 相比32bit和48bit版本提供更长的偏移距离。 |
| 6. 增加原子比较交换指令 | l.casbp, l.cashp, l.caswp, l.casdp | 提供双元素的原子比较交换操作 |
