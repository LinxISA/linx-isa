// PTO 0.59.1 candidate. The platform owns scoped memory and GM ordering.

enum scalar_shareability = { ScalarPrivate, ScalarIntraCore, ScalarInterCore }
enum scoped_scalar_start = {
  ScopedPrepared, ScopedIllegal, ScopedBundleFault, ScopedUnimplemented, ScopedBusy
}
enum scoped_memory_completion = {
  ScopedMemoryCommitted, ScopedMemoryBlocked, ScopedMemoryAlignment, ScopedMemoryPageFault,
  ScopedMemorySecondAlignment, ScopedMemorySecondPageFault
}
enum scoped_agu_update = { ScopedNoWriteback, ScopedPreIndex, ScopedPostIndex }

struct scoped_agu_index = {
  reg : bits(5),
  modifier : bits(2),
  shift : bits(6)
}

struct scoped_agu = {
  is_store : bool,
  pcr : bool,
  base_reg : bits(5),
  data_reg : bits(5),
  second_reg : option(bits(5)),
  offset : bits(64),
  index : option(scoped_agu_index),
  update : scoped_agu_update,
  writeback_reg : bits(5),
  size : bits(4),
  signed_load : bool
}

struct scoped_memory_request = {
  token : int,
  core : int,
  agent : int,
  invocation : int,
  acr : bits(4),
  instruction : bits(64),
  source_tpc : bits(64),
  shareability : scalar_shareability,
  address : bits(64),
  size : bits(4),
  is_store : bool,
  store_data : bits(64),
  second : option((bits(64), bits(64)))
}

struct scoped_scalar_attempt = {
  request : scoped_memory_request,
  destination : bits(5),
  second_destination : option(bits(5)),
  signed_load : bool,
  writeback : option((bits(5), bits(64))),
  issued : bool
}

$include "scoped_scalar_agu.sail"

register scoped_scalar_next_token : int = 0
register scoped_scalar_pending : option(scoped_scalar_attempt) = None()

function scoped_load_value(value : bits(64), size : bits(4), signed_load : bool) -> bits(64) = {
  match size {
    0x1 => if signed_load then sail_sign_extend(value[7..0], 64) else sail_zero_extend(value[7..0], 64),
    0x2 => if signed_load then sail_sign_extend(value[15..0], 64) else sail_zero_extend(value[15..0], 64),
    0x4 => if signed_load then sail_sign_extend(value[31..0], 64) else sail_zero_extend(value[31..0], 64),
    _ => value
  }
}

function scoped_data_register_supported(reg : bits(5), is_store : bool) -> bool = {
  if is_store then scalar_gpr_source_supported(reg)
  else scalar_gpr_or_discard_destination_supported(reg)
}

function prepare_scoped_scalar(inst : bits(64), core : int, agent : int,
    invocation : int, applicable : bool) -> scoped_scalar_start = {
  if not_bool(is_none(scoped_scalar_pending)) then return ScopedBusy;
  let id = decode_pto_scoped_scalar(inst);
  if id == 0xFF then {
    trap_illegal_inst(tpc);
    return ScopedIllegal
  };
  if not_bool(applicable) then {
    raise_trap(trapnum_block_trap(), sail_zeros(24), tpc, 0b0);
    return ScopedBundleFault
  };
  match decode_scoped_agu(id, inst[63..16]) {
    None() => ScopedUnimplemented,
    Some(agu) => {
      let data_supported = scoped_data_register_supported(agu.data_reg, agu.is_store);
      let second_supported : bool = match agu.second_reg {
        Some(reg) => scoped_data_register_supported(reg, agu.is_store),
        None() => true
      };
      let index_supported : bool = match agu.index {
        Some(index) => scalar_gpr_source_supported(index.reg),
        None() => true
      };
      if not_bool(scalar_gpr_source_supported(agu.base_reg) & data_supported & second_supported & index_supported &
          scalar_gpr_or_discard_destination_supported(agu.writeback_reg)) then
        return ScopedUnimplemented;
      let base = if agu.pcr then tpc & 0xFFFFFFFFFFFFFFFC else read_reg5(agu.base_reg);
      let offset : bits(64) = match agu.index {
        Some(index) => sail_shiftleft(apply_address_srcrtype64(index.modifier, read_reg5(index.reg)),
                                    unsigned(index.shift)),
        None() => agu.offset
      };
      let updated = base + offset;
      let address : bits(64) = match agu.update { ScopedPostIndex => base, _ => updated };
      let writeback : option((bits(5), bits(64))) = match agu.update {
        ScopedNoWriteback => None(),
        _ => Some((agu.writeback_reg, updated))
      };
      let data = if agu.is_store then scoped_load_value(read_reg5(agu.data_reg), agu.size, false)
        else 0x0000000000000000;
      let second : option((bits(64), bits(64))) = match agu.second_reg {
        Some(reg) => {
          let second_data = if agu.is_store then scoped_load_value(read_reg5(reg), agu.size, false)
            else 0x0000000000000000;
          Some((address + sail_zero_extend(agu.size, 64), second_data))
        },
        None() => None()
      };
      let scope : scalar_shareability = match inst[9..8] {
        0b01 => ScalarIntraCore,
        0b10 => ScalarInterCore,
        _ => ScalarPrivate
      };
      let request : scoped_memory_request = struct {
        token = scoped_scalar_next_token, core = core, agent = agent, invocation = invocation,
        acr = current_acr_id(), instruction = inst, source_tpc = tpc,
        shareability = scope, address = address, size = agu.size,
        is_store = agu.is_store, store_data = data, second = second
      };
      scoped_scalar_next_token = scoped_scalar_next_token + 1;
      scoped_scalar_pending = Some(struct {
        request = request, destination = agu.data_reg, signed_load = agu.signed_load,
        second_destination = if agu.is_store then None() else agu.second_reg,
        writeback = writeback, issued = false
      });
      ScopedPrepared
    }
  }
}

// The platform must hold the issuing execution context until completion.
function issue_scoped_scalar(gm_permits : bool) -> option(scoped_memory_request) = {
  match scoped_scalar_pending {
    Some(attempt) if gm_permits & not_bool(attempt.issued) &
        (attempt.request.source_tpc == tpc) & (attempt.request.acr == current_acr_id()) => {
      scoped_scalar_pending = Some({ attempt with issued = true });
      Some(attempt.request)
    },
    _ => None()
  }
}

// Committed means the backend has completed the obligation and any store.
// Blocked means no access took effect and the captured request may be reissued.
function complete_scoped_scalar_response(token : int, completion : scoped_memory_completion,
    data : bits(64), second_data : option(bits(64)), paired : bool) -> bool = {
  match scoped_scalar_pending {
    Some(attempt) if attempt.issued & (attempt.request.token == token) &
        (attempt.request.source_tpc == tpc) & (attempt.request.acr == current_acr_id()) => {
      let request = attempt.request;
      if paired != not_bool(is_none(request.second)) then return false;
      let second_fault : bool = match completion {
        ScopedMemorySecondAlignment => true,
        ScopedMemorySecondPageFault => true,
        _ => false
      };
      let fault_address : bits(64) = if second_fault then match request.second {
        Some((address, _)) => address,
        None() => return false
      } else request.address;
      scoped_scalar_pending = None();
      match completion {
        ScopedMemoryCommitted => {
          if not_bool(request.is_store) then write_scalar_gpr_or_discard(attempt.destination,
            scoped_load_value(data, request.size, attempt.signed_load));
          match (attempt.second_destination, second_data) {
            (Some(reg), Some(value)) => write_scalar_gpr_or_discard(reg,
              scoped_load_value(value, request.size, attempt.signed_load)),
            _ => ()
          };
          match attempt.writeback {
            Some((reg, value)) => write_scalar_gpr_or_discard(reg, value),
            None() => ()
          };
          tpc = request.source_tpc + 8
        },
        ScopedMemoryBlocked => scoped_scalar_pending = Some({ attempt with issued = false }),
        ScopedMemoryAlignment => raise_trap(0b100010, sail_zeros(24), fault_address, 0b0),
        ScopedMemorySecondAlignment => raise_trap(0b100010, sail_zeros(24), fault_address, 0b0),
        ScopedMemoryPageFault => trap_data_page_fault(fault_address),
        ScopedMemorySecondPageFault => trap_data_page_fault(fault_address)
      };
      true
    },
    _ => false
  }
}

function complete_scoped_scalar(token : int, completion : scoped_memory_completion,
    data : bits(64)) -> bool = {
  complete_scoped_scalar_response(token, completion, data, None(), false)
}

function complete_scoped_scalar_pair(token : int, completion : scoped_memory_completion,
    first_data : bits(64), second_data : bits(64)) -> bool = {
  complete_scoped_scalar_response(token, completion, first_data, Some(second_data), true)
}
