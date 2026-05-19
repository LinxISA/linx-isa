# header/body end command: **BSTOP**

```
BSTOP               /*指示块结束的位置*/

C.BSTOP             /*BSTOP的压缩形式*/
```

**Note**:

The end command for the split block body other than PARblock type is currently pending.

For an integrated block, header instruction and microinstructions are arranged sequentially, and there is no need to further indicate the position of headerbody. The end of a block is indicated by 'BSTART' or 'BSTOP' of the next block, as shown below:

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

For separate blocks, body must use 'bstop' to describe the end of body, while the end of header is described by 'BSTART' of the next block in most scenarios, and a small number of scenarios require 'BSTOP' to express.
Example:<br>

header：<br>

```
...
BSTART.PAR fall     /* 用静态汇编上下一个块的bstart来表示当前ZXTERMZH39QXZ的结束 */
B.TEXT .Lbody1
BSTART               /* 用bstop指令表达ZXTERMZH39QXZ的结束 */
微指令
BSTOP
```

Microinstructions:<br>

```
...
...
.Lbody1:
    微指令
    BSTOP      /* 当前ZXTERMZH40QXZ内可能被执行到的最后的bstop指令 */
...
...
```