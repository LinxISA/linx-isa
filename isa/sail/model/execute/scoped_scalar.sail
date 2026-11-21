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
enum scoped_atomic_kind = {
  ScopedAtomicLoadReserved, ScopedAtomicStoreConditional,
  ScopedAtomicCompareAndSwap, ScopedAtomicReadModifyWrite
}
enum scoped_atomic_operation = {
  ScopedAtomicSwap, ScopedAtomicAdd, ScopedAtomicSub, ScopedAtomicAnd,
  ScopedAtomicOr, ScopedAtomicXor, ScopedAtomicSmin, ScopedAtomicSmax,
  ScopedAtomicUmin, ScopedAtomicUmax
}

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

struct scoped_atomic = {
  kind : scoped_atomic_kind,
  operation : scoped_atomic_operation,
  address_reg : bits(5),
  destination : option(bits(5)),
  operand_reg : option(bits(5)),
  compare_reg : option(bits(5)),
  size : bits(4),
  acquire : bool,
  release : bool,
  far : bool
}

struct scoped_atomic_transaction = {
  kind : scoped_atomic_kind,
  operation : scoped_atomic_operation,
  operand : bits(64),
  compare : bits(64),
  acquire : bool,
  release : bool,
  far : bool
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
  second : option((bits(64), bits(64))),
  atomic : option(scoped_atomic_transaction)
}

struct scoped_scalar_attempt = {
  request : scoped_memory_request,
  destination : bits(5),
  second_destination : option(bits(5)),
  signed_load : bool,
  writeback : option((bits(5), bits(64))),
  atomic_response : option((scoped_atomic_kind, bits(4), option(bits(5)))),
  issued : bool
}

$include "scoped_scalar_agu.sail"
$include "scoped_scalar_atomic.sail"

register scoped_scalar_next_token : int = 0
register scoped_scalar_pending : option(scoped_scalar_attempt) = None()

$include "scoped_scalar_queues.sail"

function scoped_load_value(value : bits(64), size : bits(4), signed_load : bool) -> bits(64) = {
  match size {
    0x1 => if signed_load then sail_sign_extend(value[7..0], 64) else sail_zero_extend(value[7..0], 64),
    0x2 => if signed_load then sail_sign_extend(value[15..0], 64) else sail_zero_extend(value[15..0], 64),
    0x4 => if signed_load then sail_sign_extend(value[31..0], 64) else sail_zero_extend(value[31..0], 64),
    _ => value
  }
}

function scoped_atomic_result(value : bits(64), size : bits(4)) -> bits(64) = {
  match size {
    0x1 => sail_zero_extend(value[7..0], 64),
    0x2 => sail_zero_extend(value[15..0], 64),
    0x4 => sail_sign_extend(value[31..0], 64),
    _ => value
  }
}

function scoped_atomic_is_load_reserved(kind : scoped_atomic_kind) -> bool = {
  match kind { ScopedAtomicLoadReserved => true, _ => false }
}

function scoped_atomic_is_store_conditional(kind : scoped_atomic_kind) -> bool = {
  match kind { ScopedAtomicStoreConditional => true, _ => false }
}

function scoped_completion_is_committed(completion : scoped_memory_completion) -> bool = {
  match completion { ScopedMemoryCommitted => true, _ => false }
}

function scoped_shareability(inst : bits(64)) -> scalar_shareability = {
  match inst[9..8] {
    0b01 => ScalarIntraCore,
    0b10 => ScalarInterCore,
    _ => ScalarPrivate
  }
}

function scoped_data_register_supported(reg : bits(5), is_store : bool) -> bool = {
  if is_store then scalar_gpr_source_supported(reg)
  else scalar_gpr_or_discard_destination_supported(reg)
}

function scoped_optional_source_supported(reg : option(bits(5))) -> bool = {
  match reg { Some(selector) => scalar_gpr_source_supported(selector), None() => true }
}

function scoped_optional_destination_supported(reg : option(bits(5))) -> bool = {
  match reg { Some(selector) => scalar_gpr_or_discard_destination_supported(selector), None() => true }
}

function scoped_optional_source_available(reg : option(bits(5))) -> bool = {
  match reg { Some(selector) => scoped_source_available(selector), None() => true }
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
    None() => match decode_scoped_atomic(id, inst[63..16]) {
      None() => ScopedUnimplemented,
      Some(atomic) => {
        let queue_needed = not_bool(scalar_gpr_source_supported(atomic.address_reg) &
            scoped_optional_source_supported(atomic.operand_reg) &
            scoped_optional_source_supported(atomic.compare_reg) &
            scoped_optional_destination_supported(atomic.destination));
        if queue_needed & not_bool(scoped_queues_bound(core, agent, invocation)) then
          return ScopedUnimplemented;
        if not_bool(scoped_source_available(atomic.address_reg) &
            scoped_optional_source_available(atomic.operand_reg) &
            scoped_optional_source_available(atomic.compare_reg)) then {
          trap_illegal_inst(tpc);
          return ScopedIllegal
        };
        let operand : bits(64) = match atomic.operand_reg {
          Some(reg) => scoped_load_value(read_scoped_reg5(reg), atomic.size, false),
          None() => 0x0000000000000000
        };
        let compare : bits(64) = match atomic.compare_reg {
          Some(reg) => scoped_load_value(read_scoped_reg5(reg), atomic.size, false),
          None() => 0x0000000000000000
        };
        let scope = scoped_shareability(inst);
        let transaction : scoped_atomic_transaction = struct {
          kind = atomic.kind, operation = atomic.operation,
          operand = operand, compare = compare, acquire = atomic.acquire,
          release = atomic.release, far = atomic.far
        };
        let request : scoped_memory_request = struct {
          token = scoped_scalar_next_token, core = core, agent = agent,
          invocation = invocation, acr = current_acr_id(), instruction = inst,
          source_tpc = tpc, shareability = scope,
          address = read_scoped_reg5(atomic.address_reg), size = atomic.size,
          is_store = not_bool(scoped_atomic_is_load_reserved(atomic.kind)),
          store_data = operand, second = None(), atomic = Some(transaction)
        };
        scoped_scalar_next_token = scoped_scalar_next_token + 1;
        scoped_scalar_pending = Some(struct {
          request = request, destination = 0b00000,
          second_destination = None(), signed_load = false,
          writeback = None(),
          atomic_response = Some((atomic.kind, atomic.size, atomic.destination)),
          issued = false
        });
        ScopedPrepared
      }
    },
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
      let queue_needed = not_bool(scalar_gpr_source_supported(agu.base_reg) & data_supported & second_supported &
        index_supported & scalar_gpr_or_discard_destination_supported(agu.writeback_reg));
      if queue_needed & not_bool(scoped_queues_bound(core, agent, invocation)) then
        return ScopedUnimplemented;
      let index_available : bool = match agu.index {
        Some(index) => scoped_source_available(index.reg),
        None() => true
      };
      if not_bool(scoped_source_available(agu.base_reg) & index_available) |
          (agu.is_store & not_bool(scoped_source_available(agu.data_reg) &
            scoped_optional_source_available(agu.second_reg))) then {
        trap_illegal_inst(tpc);
        return ScopedIllegal
      };
      let base = if agu.pcr then tpc & 0xFFFFFFFFFFFFFFFC else read_scoped_reg5(agu.base_reg);
      let offset : bits(64) = match agu.index {
        Some(index) => sail_shiftleft(apply_address_srcrtype64(index.modifier, read_scoped_reg5(index.reg)),
                                    unsigned(index.shift)),
        None() => agu.offset
      };
      let updated = base + offset;
      let address : bits(64) = match agu.update { ScopedPostIndex => base, _ => updated };
      let writeback : option((bits(5), bits(64))) = match agu.update {
        ScopedNoWriteback => None(),
        _ => Some((agu.writeback_reg, updated))
      };
      let data = if agu.is_store then scoped_load_value(read_scoped_reg5(agu.data_reg), agu.size, false)
        else 0x0000000000000000;
      let second : option((bits(64), bits(64))) = match agu.second_reg {
        Some(reg) => {
          let second_data = if agu.is_store then scoped_load_value(read_scoped_reg5(reg), agu.size, false)
            else 0x0000000000000000;
          Some((address + sail_zero_extend(agu.size, 64), second_data))
        },
        None() => None()
      };
      let scope = scoped_shareability(inst);
      let request : scoped_memory_request = struct {
        token = scoped_scalar_next_token, core = core, agent = agent, invocation = invocation,
        acr = current_acr_id(), instruction = inst, source_tpc = tpc,
        shareability = scope, address = address, size = agu.size,
        is_store = agu.is_store, store_data = data, second = second, atomic = None()
      };
      scoped_scalar_next_token = scoped_scalar_next_token + 1;
      scoped_scalar_pending = Some(struct {
        request = request, destination = agu.data_reg, signed_load = agu.signed_load,
        second_destination = if agu.is_store then None() else agu.second_reg,
        writeback = writeback, atomic_response = None(), issued = false
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
      match attempt.atomic_response {
        Some((ScopedAtomicStoreConditional, _, _)) if scoped_completion_is_committed(completion) & unsigned(data) > 1 =>
          return false,
        _ => ()
      };
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
          match attempt.atomic_response {
            Some((kind, size, destination)) => match destination {
              Some(reg) => {
                let value = if scoped_atomic_is_store_conditional(kind) then data
                  else scoped_atomic_result(data, size);
                write_scoped_reg5(reg, value)
              },
              None() => ()
            },
            None() => if not_bool(request.is_store) then
              write_scoped_reg5(attempt.destination,
                scoped_load_value(data, request.size, attempt.signed_load))
          };
          match (attempt.second_destination, second_data) {
            (Some(reg), Some(value)) => write_scoped_reg5(reg,
              scoped_load_value(value, request.size, attempt.signed_load)),
            _ => ()
          };
          match attempt.writeback {
            Some((reg, value)) => write_scoped_reg5(reg, value),
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
