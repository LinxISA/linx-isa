// Canonical LinxISA v0.58 Sail model entrypoint.

default Order dec

$include "state/state.sail"
$include "state/msgb_receive.sail"
$include "state/msgb_transport.sail"
$include "state/msgb_bse.sail"
$include "state/hscb_dispatch.sail"
$include "state/msgb_registers.sail"
$include "execute/execute.sail"
$include "decode/decode.sail"
$include "decode/scoped_scalar.sail"
