# BlockDISPATCH
The Block Dispatch module is responsible for distributing BFU-predicted blocks to different PEs. The distribution rules are affected by the following factors:

* Type-related: Based on the type of the block, send the block to the appropriate PE
* Dependency related: If the instruction block has multiple PEs to choose from, it will be sent first to the PE where the block with the highest dependency correlation is located.
* Load related: If the instruction block has multiple PEs to choose from, priority will be given to the PE with the smallest load, that is, the one with the smallest number of blocks being executed in BISQ