# SPECINT program analysis

## The proportion of blocks containing Store instructions in SPECINT subitems

```plotly
{"file_path": "docs/figs/bitfield/json/Summarize/SPECINT子项含Store指令的块占比.json"}
```

- **Description**: In all slices of each sub-item, the sum of the number of blocks with Store instructions is divided by the total number of blocks.
- **Analysis**: The microarchitecture requires header to prompt whether body contains Store instructions, but one header encoding is not enough. Statistics found that the proportion of blocks containing Store instructions in most sub-items is within 30%. It is acceptable to add Concatheader to prompt whether header contains Store instructions.

## Statistics on the number of interval blocks read after writing to all block shared registers of the SPECINT sub-item

```plotly
{"file_path": "docs/figs/bitfield/json/Summarize/SPECINT子项全部块共享寄存器写后读的间隔块数统计.json"}
```

- **Description**: In all slices of each sub-item, after the value is written to the shared register, before the next write, the difference between the block id that accesses the shared register and the block id that is written to the shared register is used as the dependency distance. The frequency of different dependency distances is counted, and finally a cumulative frequency curve that is less than or equal to the dependency distance is obtained.
- **Analysis**: A large proportion of scenarios have a dependency distance within 6, indicating that adjacent block registers are heavily dependent on each other during runtime.

## Statistics on the number of blocks read after writing to all block shared registers of the SPECINT sub-item

```plotly
{"file_path": "docs/figs/bitfield/json/Summarize/SPECINT子项全部块共享寄存器写后读的块数统计.json"}
```

- **Description**: In all slices of each sub-item, after the value is written to the shared register, before the next write, count the frequency of the number of blocks accessing the shared register, and draw the number of blocks with higher frequency separately.
- **Analysis**: After the value is written to the shared register, before the next write, the number of accessed blocks of the shared register is within 3, accounting for a large proportion of the scenarios. Among them, 1 block has the largest proportion of accesses, and some registers have not been accessed after being written.

## SPECINT sub-item all block shared register value statistics

```plotly
{"file_path": "docs/figs/bitfield/json/Summarize/SPECINT子项全部块共享寄存器值统计.json"}
```

- **Description**: Among all slices of each sub-item, count the frequency of the shared register value accessed by each block, and draw the values with higher frequency separately.
- **Analysis**: The values ​​that appear more frequently in the shared register are 0 and 1, and other single values ​​are less frequent.