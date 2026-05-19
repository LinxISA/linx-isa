## Load Result Pipe component function description

This module is responsible for aggregating the three-way data returned by L1 Data Cache, STQ and SCB bypass. After the aggregation is completed, the sign bit extension or zero extension operation is performed and the data is returned to the PE.

## Load Result Pipe component processing instructions

You need to pay attention to the following points during the write-back process:

1. The priority of data selection is: STQ bypass > SCB bypass > L1 DC return data

2. When there is a Load request with the same physical address as requests in multiple STQs, and the latest STQ request cannot completely cover the data required by the current Load request, you need to wait for the STQ request to be dequeued before repicking the Load instruction.

3. The second coverage condition above can be determined by byte mask (bytemask). STQ, SCB covers the data field segment of L1 DCache.

4. After the aggregation is completed, perform sign bit extension or zero extension and alignment operations

5. After returning the data, send the completion signal (Resolve) to the PE ROB