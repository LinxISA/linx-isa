# Decode-Group Dispatch

Dispatch consumes the four-lane D1 decode group after D2 resource-demand
calculation and D3 atomic admission.

It routes admitted uops to the appropriate scalar, memory, vector, tile, or
engine issue structures according to decoded execution class and available
capacity. Prediction is not a dispatch payload source: B-SIDE predicts control
flow, while D1/D2/D3 establish instruction semantics, block ownership, and
resource identities.

The group is accepted atomically or not at all. No lane may advance its
RID/BID/rename/IQ/memory-order state when another required lane or resource is
blocked.
