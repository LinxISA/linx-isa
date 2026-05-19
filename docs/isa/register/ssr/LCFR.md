# LCFR

Linx core features register (Linx Core Features Register)<br>
Used to describe the functional features supported by the current processor core, such as vector extension, floating point operations, etc.

![LCFR](../../../figs/bitfield/svg/Sysregs/LCFR.svg)

Each field is described as follows:

## **C flag**

The `C` bit is 1 when [Compression Command Extension] (../../instset/compressInstrs.md) is supported, otherwise it is 0;

## **G flag**

The `G` bit is 1 when the GQM instruction extension is supported, otherwise it is 0;

## **F flag**

The `F` bit is 1 when floating point instructions are supported, otherwise it is 0;

## **V flag**

The `v` bit is 1 when the vector instruction extension is supported, otherwise it is 0;

## **GroupNum field**

`GroupNum` indicates how many parallel groups there are in the core that supports the vector extension. Calculation method:

```c
    GroupNumber = 2 ^ GroupNum;
```
The valid range of GroupNum is [0, 8], so the valid value of GroupNumber is:

| GroupNum | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|----------|---|---|---|---|---|---|---|---|---|
| Number of parallel groups | 1 | 2 | 4 | 8 | 16 | 32 | 64 | 128 | 256 |

## **LaneNum field**

`LaneNum` represents the number of parallel lanes **LaneNumber** in each Group in the core that supports the vector extension. The calculation method is:

```c
    LaneNumber = 2 ^ LaneNum;
```

The valid range of LaneNum is [0, 6], so the valid value of LaneNumber is:

| LaneNum | 0 | 1 | 2 | 3 | 4 | 5 | 6 |
|----------|---|---|---|---|---|---|---|
| Number of parallel lanes | 1 | 2 | 4 | 8 | 16 | 32 | 64 |

## **TMaxSize field**

`TMaxSize` indicates the maximum range of [Tile Register] (../common/tilereg.md) allowed by the architecture **TileMaxSize**, calculation method:

```c
    TileMaxSize = 512 * (TMaxSize + 1) byte;
```

In the current version, the maximum value allowed to be set in the Tile register range is 32KB.

## **TMinSize field**

`TMinSize` indicates the minimum range **TileMinSize** of the [Tile Register] (../common/tilereg.md) that the architecture allows to apply for, and the calculation method is:

```c
    TileMinSize = 512 * (TMinSize + 1) byte;
```

In the current version, the minimum value allowed to be set in the Tile register range is 512Byte.

## Remarks

This register is **read-only (RO)** and its SSRID is **0x0024**.