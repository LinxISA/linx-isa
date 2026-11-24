# LinxISA Sail Model 0.59.1

The canonical entry is `model/linxisa_v0591.sail`. Its state and execute
definitions are maintained in this directory. The exporter adds the shared
scalar and message components and generates the decoder from the 0.59.1
catalog. Decode rejects instructions in the ten reserved PTO ranges before
reading operands or producing instruction effects.

Run `python3 tools/isa/check_v0591_candidate_dispatch_sail.py` from the
repository root with Sail 0.20.2 on PATH. The check builds the C backend and
executes the scoped dispatch and reserved-encoding tests.
