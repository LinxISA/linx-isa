# PTO ISA 0.58.3 retired conditional branch pages

These English and Chinese pages preserve the pre-0.58.3 descriptions of
`B.EQ`, `B.NE`, `B.LT`, `B.GE`, `B.LTU`, `B.GEU`, `B.Z`, and `B.NZ` for
historical review only.

They are non-normative and are not included in either published navigation.
PTO ISA 0.58.3 removes these common forms and reserves their former encoding
space. Current code uses `SETC.*` with `BSTART COND` where block-control
condition state is required.
