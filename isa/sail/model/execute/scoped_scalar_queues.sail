// Candidate Reg5 queue state for the selected platform context.

struct scoped_queue_context = {
  core : int,
  agent : int,
  invocation : int,
  acr : bits(4)
}

register scoped_queue_binding : option(scoped_queue_context) = None()
register scoped_t_queue : vector(4, option(bits(64))) = vector_init(4, None())
register scoped_u_queue : vector(4, option(bits(64))) = vector_init(4, None())

function bind_scoped_scalar_queues(core : int, agent : int, invocation : int,
    t_queue : vector(4, option(bits(64))), u_queue : vector(4, option(bits(64)))) -> bool = {
  if not_bool(is_none(scoped_scalar_pending)) then return false;
  scoped_queue_binding = Some(struct { core = core, agent = agent, invocation = invocation,
    acr = current_acr_id() });
  scoped_t_queue = t_queue;
  scoped_u_queue = u_queue;
  true
}

function scoped_queues_bound(core : int, agent : int, invocation : int) -> bool = {
  match scoped_queue_binding {
    Some(context) => (context.core == core) & (context.agent == agent) &
                     (context.invocation == invocation) & (context.acr == current_acr_id()),
    None() => false
  }
}

function scoped_queue_source(selector : bits(5)) -> option(bits(64)) = {
  let index = unsigned(selector[1..0]);
  if selector[2] == 0b0 then scoped_t_queue[index] else scoped_u_queue[index]
}

function scoped_source_available(selector : bits(5)) -> bool = {
  scalar_gpr_source_supported(selector) | not_bool(is_none(scoped_queue_source(selector)))
}

function read_scoped_reg5(selector : bits(5)) -> bits(64) = {
  if scalar_gpr_source_supported(selector) then read_reg5(selector)
  else match scoped_queue_source(selector) {
    Some(value) => value,
    None() => 0x0000000000000000 // Availability is checked before capture.
  }
}

function push_scoped_queue(queue : vector(4, option(bits(64))), value : bits(64))
    -> vector(4, option(bits(64))) = {
  let updated = vector_update(queue, 0, Some(value));
  let updated = vector_update(updated, 1, queue[0]);
  let updated = vector_update(updated, 2, queue[1]);
  vector_update(updated, 3, queue[2])
}

function write_scoped_reg5(selector : bits(5), value : bits(64)) -> unit = {
  match selector {
    0b11110 => scoped_u_queue = push_scoped_queue(scoped_u_queue, value),
    0b11111 => scoped_t_queue = push_scoped_queue(scoped_t_queue, value),
    _ => write_scalar_gpr_or_discard(selector, value)
  }
}
