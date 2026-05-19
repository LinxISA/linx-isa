# Dispatch unit (PE Dispatch)
The dispatch unit will send the decoded instructions to ISQ and ROB at the same time. A maximum of four microinstructions can be issued per beat, and the dispatch unit will allocate them to different ISQs according to different instruction types. At the same time, for instructions of the same type, the microarchitecture will dispatch microinstructions according to the remaining vacancies of each ISQ.

The ISQs that need to be allocated in the micro-architecture are as follows:

| ISQ Type | Number |Depth| Calculation Category|
| --| --- | ---|--|
|ALU 0| 1 | 8|General computing class|
|ALU 1| 1 | 8|General computing class|
|GSU | 2 | 8|PC Computing and Inter-Block Communication Category|
|LSU |2| 8|Memory access class|




Take the ALU instruction as an example: (Note: GSU instructions and LSU instructions apply to the same distribution rules)

The ALU transmission queue has two banks, ALU0 and ALU1. In the same clock cycle, up to four instructions can be written to these two banks. Assume that Free0 Free1 is the number of vacancies in the two banks of ALU0/1, and Instr0 Instr1 Instr2 Instr3 is the four instructions of the same shot and type, and the program sequence is from old to new. Where Instr0 has a higher probability of being valid than Instr1, and so on Instr0 >= Instr1 >= Instr2 >= Instr3. Based on the above conditions, instructions with a high probability of validity are given priority to banks with many vacancies. The details are as follows:

|Rules |ALU 0 Enqueue |ALU1 1 Enqueue|
|--|--|--|
|Free0 >= Free1 (the vacancy of ALU0 is greater than or equal to ALU1) |Instr0 Instr1 |Instr2 Instr3|
|Free0 < Free1 (ALU0 has less space than ALU1) |Instr2 Instr3| Instr0 Instr1|