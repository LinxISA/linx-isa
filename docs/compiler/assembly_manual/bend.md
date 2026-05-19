# bodyEND
Each body of LinxISA uses the 'bend' instruction to mark the end of body execution. <br>

During the execution of the following body, when encountering the first bend instruction, the current body will be submitted, and microinstruction 2 will not be executed. Therefore, the position of the bend instruction is the last instruction expected to be executed. <br>
Microinstructions:<br>
```
...
...
.Lbody.bstart:
    微指令 1
    bend         /* 第一个bend */
    微指令 2
.Lbody.bstop:
    bend         /* 第二个bend */
...
...
```