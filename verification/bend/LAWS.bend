# EIJA protected authority laws. The human states them; PROOF.bend must prove them.
#
# The model is main.bend, generated from the executable Python Workflow: a `Baseline` and a
# `Candidate` (recommend_only) slot, a `step` function (one command against one instance state) and
# `replay` (a sequence of commands). Every law quantifies over ALL actors (any role, active or
# revoked, assigned or not), ALL actions and ALL states, and the sequence laws over ALL command
# sequences of any length. These are laws about the model, not about the Python runtime:
# docs/formal/bend.md says what is and is not established.
#
# Reading guide: `{P == True{} : Bool}` says the Bool expression P is true; `implies(a, b)` is
# "if a then b".

import Base
import ./main.bend as M

# Vocabulary of the laws
# ----------------------

def implies(a: Bool, b: Bool) -> Bool:
  Bool.not(a) || b

# The protected policy's forbidden effects (domain/policy.py FORBIDDEN).
def forbidden(e: M.Effect) -> Bool:
  match e:
    case M.PaymentCaptured{}:
      True{}
    case M.ParentDataExported{}:
      True{}
    case _:
      False{}

def any_forbidden(es: +List<M.Effect>) -> Bool:
  match es:
    case Nil{}:
      False{}
    case Con{e, rest}:
      forbidden(e) || any_forbidden(rest)

# True when every command in the sequence is issued by an actor holding this role.
def all_by(cmds: +List<M.Cmd>, +role: M.Role) -> Bool:
  match cmds:
    case Nil{}:
      True{}
    case Con{cmd, rest}:
      M.Cmd{a, act} = cmd
      M.Role.eq(M.Actor.role(a), role) && all_by(rest, role)

# The state a rejection must come from. The policy fixes the baseline (Submitted) and the shipped
# recommend_only candidate (Recommended): a registrar rejects what a teacher has recommended.
def reject_source(m: M.Model) -> M.State:
  match m:
    case M.Baseline{}:
      M.Submitted{}
    case M.Candidate{}:
      M.Recommended{}

# A run is sound when being in Approved implies the run has been through Recommended.
def sound(r: M.Run) -> Bool:
  M.Run{s, seen} = r
  implies(M.State.eq(s, M.Approved{}), seen)

# Laws
# ----

# LAW 1: whatever a Teacher does (active or not, assigned or not), in any state and in either model,
# the accepted command never leaves the instance Approved.
law teacher_never_approves:
  for +m: M.Model
  for +active: Bool
  for +assigned: Bool
  for +act: M.Action
  for +s: M.State
  {Bool.not(M.Outcome.enters(M.step(m, M.Actor{M.Teacher{}, active, assigned}, act, s), M.Approved{})) == True{} : Bool}

# LAW 2: no sequence of commands issued only by teachers can ever reach Approved from the initial state.
law teacher_sequences_never_approve:
  for +m: M.Model
  for +cmds: +List<M.Cmd>
  {implies(all_by(cmds, M.Teacher{}), Bool.not(M.State.eq(M.replay(cmds, m, M.initial(m)), M.Approved{}))) == True{} : Bool}

# LAW 3: in the recommend_only candidate, any accepted command into Approved fires from Recommended.
law approved_only_from_recommended:
  for +active: Bool
  for +assigned: Bool
  for +role: M.Role
  for +act: M.Action
  for +s: M.State
  {implies(M.Outcome.enters(M.step(M.Candidate{}, M.Actor{role, active, assigned}, act, s), M.Approved{}), M.State.eq(s, M.Recommended{})) == True{} : Bool}

# LAW 4: in the candidate, every path to Approved passes through Recommended (all sequences, any actors).
law every_path_to_approved_passes_recommended:
  for +cmds: +List<M.Cmd>
  {sound(M.replay_run(cmds, M.Candidate{}, M.Run{M.initial(M.Candidate{}), False{}})) == True{} : Bool}

# LAW 5: a revoked teacher can never recommend, whatever their assignment and whatever the state.
law revoked_teacher_cannot_recommend:
  for +m: M.Model
  for +assigned: Bool
  for +s: M.State
  {Bool.not(M.Outcome.ok(M.step(m, M.Actor{M.Teacher{}, False{}, assigned}, M.Recommend{}, s))) == True{} : Bool}

# LAW 6: an unassigned teacher can never recommend, whether or not they are active.
law unassigned_teacher_cannot_recommend:
  for +m: M.Model
  for +active: Bool
  for +s: M.State
  {Bool.not(M.Outcome.ok(M.step(m, M.Actor{M.Teacher{}, active, False{}}, M.Recommend{}, s))) == True{} : Bool}

# LAW 7: Reject is accepted only from the declared rejection source of the model.
law reject_only_from_declared_source:
  for +m: M.Model
  for +a: M.Actor
  for +s: M.State
  {implies(M.Outcome.ok(M.step(m, a, M.Reject{}, s)), M.State.eq(s, reject_source(m))) == True{} : Bool}

# LAW 8: no command, by any actor in any state, ever emits a forbidden effect.
law forbidden_effects_never_emitted:
  for +m: M.Model
  for +a: M.Actor
  for +act: M.Action
  for +s: M.State
  {Bool.not(any_forbidden(M.Outcome.effects(M.step(m, a, act, s)))) == True{} : Bool}
