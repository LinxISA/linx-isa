# header Cache (Block Header Cache, BHC)

The header cache is a first-level cache used to temporarily store Block Header. It is consistent with the L1 Cache in the processor. They are hardware that improves memory access efficiency by utilizing spatial locality and time locality. Since the overall architecture of BFU adopts a different approach from the traditional coupling prediction and instruction fetching, BHC is also used as BTB. BHC does not currently support Hit Under Miss, that is, when a Cache Miss is encountered, subsequent requests will be blocked.

## header cache configuration

* header cache capacity is 64KB, Cacheline granularity is 64B
* Data Array supports 4 Way group associative structure. Each way has 8 single-port SRAMs, divided into 4 qwords and 8 dwords. The SRAM depth is 256 and the width is 78bit.
* Tag Array is a single-port SRAM with a depth of 256 and a bit width of 49 bits.
* Write operations are not supported yet. The only write operations come from Cacheline Fill.
* VIPT, Virtual Index Physical Tag
* ECC detection, 1-bit error self-correction, 2-bit error reporting exception


## DATA Array reading process

Data Array is divided into two paths: reading and writing. Among them, the data of the write port comes from L2 cache data backfill; the data of the read port comes from the read request of BFU; after reading the data from the Data Array, ECC judgment will be performed, and if an error occurs, the exception signal will be reported. The main processing flow is as follows:
* In the I2 pipeline, prepare data for reading and writing, and generate enable, address and other signals. For write operations, the data source is L2 data backfill. The hardware will generate write enable, address, write mask and other signals based on the backfill signal. For read operations, the signal source is BFU. The hardware will calculate the data selection and address signals for the read operation based on the input address.
* In the e1 stage, data read and write operations are implemented. When writing data, the ecc data and data data from fill are written into memory in order; when reading data, since there are 4 ways in total, each way has 4 qwords, and each qword includes two dwords, a total of 32 data will be read. The read data is read out at the e2 stage.
* In the e2 stage, first each way will select d0 and d1 data from the 8 result data read out by this way based on the qword_en signal. A total of 8 data will be selected for the four ways, and then the d0 and d1 data of a certain way will be selected based on the way_hit signal obtained from the tag.
* In the e3 stage, perform ecc_err detection on the selected pipe data, and output the err signal and correct_data.


## PLRU algorithm

Plru (Partial Least Recently Used) is an algorithm based on lru (Least Recently Used). This module uses the Tree-plru algorithm. The specific implementation is as follows:
Taking a 4-way cache as an example, 3 status bits need to be set: lvl1_node, lvl2_left, lvl2_right. The initial state is all 0, corresponding to 4 Ways respectively. The corresponding situation is shown in the figure below:

![PLRU_FIG0](../figs/uArch/PLRU0.png){ width="400" }

When a Fill operation occurs to determine the replacement of Way, the value of lvl1_node is first read, and based on the result, it is decided to continue to determine lvl2_left or lvl2_right. If the value of lvl1_node is 0, read the value of lvl2_left and ignore lvl2_right; if the value of lvl1_node is 1, read the value of lvl2_right and ignore lvl2_left, thereby selecting the replacement Way number. After replacing Way, the status of the three nodes will be updated. In addition to the replacement operation, when a Way hits, the status of the three nodes also needs to be updated.According to the above analysis, it can be seen that when the Fill operation initially occurs, since lvl1_node is 0, the value of lvl2_left will be read, and lvl2_left is also 0, so Way0 is selected for the data writing operation. In the next beat, as data is written to Way0, the status of the three nodes will be updated. The update rules are as follows:

	For lvl1_node, when Way0/1 is selected, set it to 1, and when Way2/3 is selected, set it to 0;
	For lvl2_left, when Way0 is selected, set it to 1, when Way1 is selected, set it to 0, and keep the other conditions;
	For lvl2_right, when Way2 is selected, set it to 1, when Way3 is selected, set it to 0, and keep the other conditions;

After the update, the node status is as follows:

![PLRU_FIG0](../figs/uArch/PLRU1.png){ width="400" }
 
When a fill operation occurs on this basis, way2 will be selected to write data and update the node status.