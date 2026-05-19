# 获取消息模板-GETMSG

## 说明

读取消息缓存寄存器(*Get Message Buffer*)  
硬件中指令模板**CT-CodeTemplate**单元获取到NUM和BCC的唤醒信号后，会触发GETMSG模板产生将MessageBuffer信息搬运到Global GPR的指令：

指令序列如下：

```asm
    ssrget 0X0831, ->s1        # 读取MSGBD1 寄存器值至Global R12
    ssrget 0X0832, ->s2        # 读取MSGBD2 寄存器值至Global R13
    ssrget 0X0833, ->s3        # 读取MSGBD3 寄存器值至Global R14
    ssrget 0X0834, ->s4        # 读取MSGBD4 寄存器值至Global R15
    ssrget 0X0835, ->s5        # 读取MSGBD5 寄存器值至Global R16
    ssrget 0X0836, ->s6        # 读取MSGBD6 寄存器值至Global R17
    ssrget 0X0837, ->s7        # 读取MSGBD7 寄存器值至Global R18
    ssrget 0X0838, ->s8        # 读取MSGBD8 寄存器值至Global R19
    ssrget 0X0839, ->x0        # 读取MSGBD9 寄存器值至Global R20
    ssrget 0X083A, ->x1        # 读取MSGBD10寄存器值至Global R21
```

## 特殊注意

本模版块会占用全局寄存器s1至s8以及x0至x1，因此收消息前请确保这些寄存器是空闲，否则将会覆盖原有的有效内容。
