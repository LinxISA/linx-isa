## Light core subsystem custom register

This chapter introduces the custom system register of the light core subsystem. These registers use the space in the range of 0x0800-0x08ff.

## Thread register

| SSR ID | Abbreviation | Name | Name |
|----------|----------|----------------------------------|------------------|
| 0x0800 | TR1 | Thread Register 1 | Thread private register 1, one independent for each thread |
| 0x0801 | TR2 | Thread Register 2 | Thread private register 2, one independent for each thread |

## Clock register

| SSR ID | Abbreviation | Name | Name |
|----------|----------|----------------------------------|------------------|
| 0x0810 | SYSCNT | System Counter | Local Timestamp |

## Dynamic configuration register

| SSR ID | Abbreviation | Name | Name |
|----------|----------|----------------------------------|------------------|
| 0x0820 | CW | Canary Word | Random Status Register |

## Message cache register| SSR ID | Abbreviation | Name | Name |
|----------|----------|----------------------------------|------------------|
| 0x0830 | MSGBCR | Message Buffer Ctrl Register | Message Control Register |
| 0x0831 | MSGBD1 | Message Buffer Data Register 1 | Message Data Register 1 |
| 0x0832 | MSGBD2 | Message Buffer Data Register 2 | Message Data Register 2 |
| 0x0833 | MSGBD3 | Message Buffer Data Register 3 | Message Data Register 3 |
| 0x0834 | MSGBD4 | Message Buffer Data Register 4 | Message Data Register 4 |
| 0x0835 | MSGBD5 | Message Buffer Data Register 5 | Message Data Register 5 |
| 0x0836 | MSGBD6 | Message Buffer Data Register 6 | Message Data Register 6 |
| 0x0837 | MSGBD7 | Message Buffer Data Register 7 | Message Data Register 7 |
| 0x0838 | MSGBD8 | Message Buffer Data Register 8 | Message Data Register 8 |
| 0x0839 | MSGBD9 | Message Buffer Data Register 9 | Message Data Register 9 |
| 0x083a | MSGBD10 | Message Buffer Data Register 10 | Message Data Register 10 |