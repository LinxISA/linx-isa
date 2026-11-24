// LinxISA 0.59.1 architectural model.

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
$include "execute/scoped_scalar.sail"

$include "execute/v0591_candidate_dispatch.sail"
