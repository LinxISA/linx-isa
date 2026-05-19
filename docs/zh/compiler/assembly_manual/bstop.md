# 块头/块体结束指令：**BSTOP**

```
BSTOP               /*指示块结束的位置*/

C.BSTOP             /*BSTOP的压缩形式*/
```

**Note**:

非PAR块类型的分离块块体的结束指令当前待定。

对于一体块来说，块头指令和微指令是顺序排布的，不需要进一步指示块头块体的位置。块结束由下一个块的'BSTART'或者'BSTOP'指示，如下所示：

```
.Lblock1
BSTART
...
BSTART COND, .Lblock1      /* 用静态汇编上下一个块的BSTART来表示当前块的结束 */
微指令
BSTART                     /* 用BSTOP指令表达块的结束 */
微指令
BSTOP
...
```

对于分离块来说，块体必须用'bstop'来描述块体结束，而块头结束大部分场景下用下一个块的'BSTART'来描述，小部分场景需要'BSTOP'来表达。
示例：<br>

块头：<br>

```
...
BSTART.PAR fall     /* 用静态汇编上下一个块的bstart来表示当前块头的结束 */
B.TEXT .Lbody1
BSTART               /* 用bstop指令表达块头的结束 */
微指令
BSTOP
```

微指令：<br>

```
...
...
.Lbody1:
    微指令
    BSTOP      /* 当前块体内可能被执行到的最后的bstop指令 */
...
...
```
