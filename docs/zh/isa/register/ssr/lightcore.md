## 轻核子系统自定义寄存器

本章节介绍轻核子系统自定义的系统寄存器，这些寄存器使用0x0800-0x08ff范围的空间。

## 线程寄存器

|  SSR ID  |   简称   |    Name                    |    名称         |
|----------|----------|----------------------------|------------------|
|  0x0800  |  TR1  |  Thread Register 1  |  线程私有寄存器1，每个线程独立一个 |
|  0x0801  |  TR2  |  Thread Register 2  |  线程私有寄存器2，每个线程独立一个 |

## 时钟寄存器

|  SSR ID  |   简称   |    Name                    |    名称         |
|----------|----------|----------------------------|------------------|
|  0x0810  |  SYSCNT   |  System Counter  |  本地时间戳  |

## 动态配置寄存器

|  SSR ID  |   简称   |    Name                    |    名称         |
|----------|----------|----------------------------|------------------|
|  0x0820  |  CW  |  Canary Word  |  随机状态寄存器  |

## 消息缓存寄存器

|  SSR ID  |   简称   |    Name                    |    名称         |
|----------|----------|----------------------------|------------------|
| 0x0830 | MSGBCR | Message Buffer Ctrl Register | 消息控制寄存器 |
| 0x0831 | MSGBD1 | Message Buffer Data Register 1 | 消息数据寄存器1 |
| 0x0832 | MSGBD2 | Message Buffer Data Register 2 | 消息数据寄存器2 |
| 0x0833 | MSGBD3 | Message Buffer Data Register 3 | 消息数据寄存器3 |
| 0x0834 | MSGBD4 | Message Buffer Data Register 4 | 消息数据寄存器4 |
| 0x0835 | MSGBD5 | Message Buffer Data Register 5 | 消息数据寄存器5 |
| 0x0836 | MSGBD6 | Message Buffer Data Register 6 | 消息数据寄存器6 |
| 0x0837 | MSGBD7 | Message Buffer Data Register 7 | 消息数据寄存器7 |
| 0x0838 | MSGBD8 | Message Buffer Data Register 8 | 消息数据寄存器8 |
| 0x0839 | MSGBD9 | Message Buffer Data Register 9 | 消息数据寄存器9 |
| 0x083a | MSGBD10 | Message Buffer Data Register 10 | 消息数据寄存器10 |
