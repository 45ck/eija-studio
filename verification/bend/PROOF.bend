# EIJA protected authority laws: the proofs. LAWS.bend states each law; each `def Laws.<name>` below
# proves the law of that name, and `bend PROOF.bend --verdict` is the gate.
#
# Shape of the argument (every law is a consequence of the same three ingredients):
#
#   1. Engine lemmas, written once and independent of any workflow: `step` is a guard conjunction
#      `permits` followed by `finish`, which either commits the rule's target and effects or changes
#      nothing. `step_prop` turns "prove P of a step" into "prove P when permits holds, and prove P
#      when the command is denied".
#   2. Table certificates: closed computations over the finitely many (model, action) rules. A
#      certificate is `Unit{}` exactly when the generated table satisfies the fact, so a table that
#      violates a law makes the certificate (and the proof) fail to check.
#   3. Induction over the command sequence, from an invariant that one command preserves.
#
# Nothing here is specific to the numbers in the shipped models: the same file is run against
# deliberately unsafe models (verification/bend/bend_runner.py) and must fail on them.

import Base
import ./main.bend as M
import ./LAWS.bend as Laws

# Proof kit
# ---------
# Boolean reflection: T(b) is the truth of b as a type (Unit when True, Empty when False), so a
# computed check becomes a proof by conversion.

def T(b: Bool) -> Data:
  match b:
    case True{}:
      Unit
    case False{}:
      Empty

def holds(+b: Bool, w: T(b)) -> {b == True{} : Bool}:
  match b:
    case True{}:
      {==}
    case False{}:
      Empty.absurd({False{} == True{} : Bool}, w)

def and_split(+a: Bool, -b: Bool, w: T(a && b), -P: Type,
  f: T(a) -> T(b) -> P) -> P:
  match a:
    case True{}:
      f(Unit{}, w)
    case False{}:
      Empty.absurd(P, w)

def imp_elim(+a: Bool, -b: Bool, wi: T(Laws.implies(a, b)), wa: T(a)) -> T(b):
  match a:
    case True{}:
      wi
    case False{}:
      Empty.absurd(T(b), wa)

def imp_intro(+a: Bool, -b: Bool, f: T(a) -> T(b)) -> T(Laws.implies(a, b)):
  match a:
    case True{}:
      f(Unit{})
    case False{}:
      Unit{}

def or_intro_r(+a: Bool, +b: Bool, w: T(b)) -> T(a || b):
  match a:
    case True{}:
      Unit{}
    case False{}:
      w

# from (x implies y) to (x implies (y or z))
def imp_or(+x: Bool, +y: Bool, -z: Bool, h: T(Laws.implies(x, y))) -> T(Laws.implies(x, y || z)):
  match x:
    case True{}:
      match y:
        case True{}:
          Unit{}
        case False{}:
          Empty.absurd(T(True{} && z), h)
    case False{}:
      Unit{}

# Engine lemmas
# -------------

def finish_prop(+c: Bool, +r: Maybe<&2, M.Rule>, +s: M.State, -P: M.Outcome -> Type,
  pt: T(c) -> P(M.Outcome{True{}, M.target(r, s), M.emitted(r)}),
  pf: P(M.Outcome{False{}, s, []})) -> P(M.finish(c, r, s)):
  match c:
    case True{}:
      pt(Unit{})
    case False{}:
      pf

# A property of a step follows from: (a) it holds of the committed outcome whenever the command is
# permitted, and (b) it holds of the "nothing happened" outcome.
def step_prop(+m: M.Model, +a: M.Actor, +act: M.Action, +s: M.State, -P: M.Outcome -> Type,
  pt: T(M.permits(M.rule_of(m, act), a, s)) -> P(M.Outcome{True{}, M.target(M.rule_of(m, act), s), M.emitted(M.rule_of(m, act))}),
  pf: P(M.Outcome{False{}, s, []})) -> P(M.step(m, a, act, s)):
  finish_prop(M.permits(M.rule_of(m, act), a, s), M.rule_of(m, act), s, P, pt, pf)

def permits_role(+r: Maybe<&2, M.Rule>, +a: M.Actor, +s: M.State, w: T(M.permits(r, a, s)))
  -> T(M.role_is(r, M.Actor.role(a))):
  and_split(M.role_is(r, M.Actor.role(a)), M.live(a) && (M.assign_ok(r, a) && M.from_ok(r, s)), w,
    T(M.role_is(r, M.Actor.role(a))),
    x => y => x)

def permits_from(+r: Maybe<&2, M.Rule>, +a: M.Actor, +s: M.State, w: T(M.permits(r, a, s)))
  -> T(M.from_ok(r, s)):
  and_split(M.role_is(r, M.Actor.role(a)), M.live(a) && (M.assign_ok(r, a) && M.from_ok(r, s)), w,
    T(M.from_ok(r, s)),
    x => y =>
      and_split(M.live(a), M.assign_ok(r, a) && M.from_ok(r, s), y, T(M.from_ok(r, s)),
        p => q =>
          and_split(M.assign_ok(r, a), M.from_ok(r, s), q, T(M.from_ok(r, s)),
            u => v => v)))

# LAW 1 and LAW 2: a Teacher command never enters Approved
# --------------------------------------------------------
# Certificate: for every rule of either model, if the rule belongs to the Teacher role then its
# target is not Approved (for a missing rule the first conjunct is already False).

def cert_teacher(m: M.Model, act: M.Action, +s: M.State)
  -> T(Laws.implies(M.role_is(M.rule_of(m, act), M.Teacher{}),
        Bool.not(M.State.eq(M.target(M.rule_of(m, act), s), M.Approved{})))):
  match m act:
    case M.Baseline{} M.Approve{}:
      Unit{}
    case M.Baseline{} M.Recommend{}:
      Unit{}
    case M.Baseline{} M.Reject{}:
      Unit{}
    case M.Baseline{} M.Revise{}:
      Unit{}
    case M.Baseline{} M.Submit{}:
      Unit{}
    case M.Candidate{} M.Approve{}:
      Unit{}
    case M.Candidate{} M.Recommend{}:
      Unit{}
    case M.Candidate{} M.Reject{}:
      Unit{}
    case M.Candidate{} M.Revise{}:
      Unit{}
    case M.Candidate{} M.Submit{}:
      Unit{}

def teacher_pt(+m: M.Model, +act: M.Action, +active: Bool, +assigned: Bool, +s: M.State,
  w: T(M.permits(M.rule_of(m, act), M.Actor{M.Teacher{}, active, assigned}, s)))
  -> T(Bool.not(M.State.eq(M.target(M.rule_of(m, act), s), M.Approved{}))):
  imp_elim(M.role_is(M.rule_of(m, act), M.Teacher{}),
    Bool.not(M.State.eq(M.target(M.rule_of(m, act), s), M.Approved{})),
    cert_teacher(m, act, s),
    permits_role(M.rule_of(m, act), M.Actor{M.Teacher{}, active, assigned}, s, w))

def NotApproved(o: M.Outcome) -> Type:
  T(Bool.not(M.Outcome.enters(o, M.Approved{})))

def Laws.teacher_never_approves(m, active, assigned, act, s):
  holds(Bool.not(M.Outcome.enters(M.step(m, M.Actor{M.Teacher{}, active, assigned}, act, s), M.Approved{})),
    step_prop(m, M.Actor{M.Teacher{}, active, assigned}, act, s, NotApproved,
      w => teacher_pt(m, act, active, assigned, s, w), Unit{}))

# LAW 2: the invariant "not Approved" survives every teacher command, by induction on the sequence.

def NextNotApproved(o: M.Outcome) -> Type:
  T(Bool.not(M.State.eq(M.Outcome.state(o), M.Approved{})))

def teacher_state(+m: M.Model, +act: M.Action, +active: Bool, +assigned: Bool, +s: M.State,
  hs: T(Bool.not(M.State.eq(s, M.Approved{}))))
  -> NextNotApproved(M.step(m, M.Actor{M.Teacher{}, active, assigned}, act, s)):
  step_prop(m, M.Actor{M.Teacher{}, active, assigned}, act, s, NextNotApproved,
    w => teacher_pt(m, act, active, assigned, s, w), hs)

def initial_not_approved(m: M.Model) -> T(Bool.not(M.State.eq(M.initial(m), M.Approved{}))):
  match m:
    case M.Baseline{}:
      Unit{}
    case M.Candidate{}:
      Unit{}

def replay_teacher(cmds: +List<M.Cmd>, +m: M.Model, +s: M.State,
  hb: T(Laws.all_by(cmds, M.Teacher{})), hs: T(Bool.not(M.State.eq(s, M.Approved{}))))
  -> T(Bool.not(M.State.eq(M.replay(cmds, m, s), M.Approved{}))):
  match cmds:
    case Nil{}:
      hs
    case Con{cmd, rest}:
      match cmd:
        case M.Cmd{a, +act}:
          match a:
            case M.Actor{r, +active, +assigned}:
              match r:
                case M.Teacher{}:
                  replay_teacher(rest, m, M.Outcome.state(M.step(m, M.Actor{M.Teacher{}, active, assigned}, act, s)), hb,
                    teacher_state(m, act, active, assigned, s, hs))
                case M.Registrar{}:
                  Empty.absurd(T(Bool.not(M.State.eq(M.replay(rest, m, M.Outcome.state(M.step(m, M.Actor{M.Registrar{}, active, assigned}, act, s))), M.Approved{}))), hb)
                case M.Viewer{}:
                  Empty.absurd(T(Bool.not(M.State.eq(M.replay(rest, m, M.Outcome.state(M.step(m, M.Actor{M.Viewer{}, active, assigned}, act, s))), M.Approved{}))), hb)

def Laws.teacher_sequences_never_approve(m, cmds):
  holds(Laws.implies(Laws.all_by(cmds, M.Teacher{}), Bool.not(M.State.eq(M.replay(cmds, m, M.initial(m)), M.Approved{}))),
    imp_intro(Laws.all_by(cmds, M.Teacher{}), Bool.not(M.State.eq(M.replay(cmds, m, M.initial(m)), M.Approved{})),
      hb => replay_teacher(cmds, m, M.initial(m), hb, initial_not_approved(m))))

# LAW 3 and LAW 4: Approved is entered only from Recommended (recommend_only candidate)
# -----------------------------------------------------------------------------------
# For each action of the candidate: if the rule's target is Approved, its source guard
# `from_ok` (which `permits` includes) pins the instance to Recommended; every other rule targets
# some other state.

def approve_pt(+act: M.Action, +a: M.Actor, +s: M.State, w: T(M.permits(M.rule_of(M.Candidate{}, act), a, s)))
  -> T(Laws.implies(M.State.eq(M.target(M.rule_of(M.Candidate{}, act), s), M.Approved{}), M.State.eq(s, M.Recommended{}))):
  match act:
    case M.Approve{}:
      permits_from(M.rule_of(M.Candidate{}, M.Approve{}), a, s, w)
    case M.Recommend{}:
      Unit{}
    case M.Reject{}:
      Unit{}
    case M.Revise{}:
      Unit{}
    case M.Submit{}:
      Unit{}

def EntersOnlyFromRecommended(s: M.State, o: M.Outcome) -> Type:
  T(Laws.implies(M.Outcome.enters(o, M.Approved{}), M.State.eq(s, M.Recommended{})))

def Laws.approved_only_from_recommended(active, assigned, role, act, s):
  holds(Laws.implies(M.Outcome.enters(M.step(M.Candidate{}, M.Actor{role, active, assigned}, act, s), M.Approved{}), M.State.eq(s, M.Recommended{})),
    step_prop(M.Candidate{}, M.Actor{role, active, assigned}, act, s, o => EntersOnlyFromRecommended(s, o),
      w => approve_pt(act, M.Actor{role, active, assigned}, s, w), Unit{}))

# LAW 4: the invariant "if Approved then the run has been through Recommended" survives every
# command (the run monitor records having been in Recommended before the command), by induction.

def SoundAfter(seen: Bool, s: M.State, o: M.Outcome) -> Type:
  T(Laws.sound(M.Run{M.Outcome.state(o), seen || M.State.eq(s, M.Recommended{})}))

def sound_pt(+act: M.Action, +a: M.Actor, +s: M.State, +seen: Bool,
  w: T(M.permits(M.rule_of(M.Candidate{}, act), a, s)))
  -> T(Laws.sound(M.Run{M.target(M.rule_of(M.Candidate{}, act), s), seen || M.State.eq(s, M.Recommended{})})):
  match act:
    case M.Approve{}:
      or_intro_r(seen, M.State.eq(s, M.Recommended{}), permits_from(M.rule_of(M.Candidate{}, M.Approve{}), a, s, w))
    case M.Recommend{}:
      Unit{}
    case M.Reject{}:
      Unit{}
    case M.Revise{}:
      Unit{}
    case M.Submit{}:
      Unit{}

def sound_step(+a: M.Actor, +act: M.Action, +s: M.State, +seen: Bool, h: T(Laws.sound(M.Run{s, seen})))
  -> T(Laws.sound(M.Run{M.Outcome.state(M.step(M.Candidate{}, a, act, s)), seen || M.State.eq(s, M.Recommended{})})):
  step_prop(M.Candidate{}, a, act, s, o => SoundAfter(seen, s, o),
    w => sound_pt(act, a, s, seen, w),
    imp_or(M.State.eq(s, M.Approved{}), seen, M.State.eq(s, M.Recommended{}), h))

def replay_sound(cmds: +List<M.Cmd>, r: M.Run, h: T(Laws.sound(r)))
  -> T(Laws.sound(M.replay_run(cmds, M.Candidate{}, r))):
  match cmds:
    case Nil{}:
      h
    case Con{cmd, rest}:
      match cmd:
        case M.Cmd{+a, +act}:
          match r:
            case M.Run{+s, +seen}:
              replay_sound(rest, M.Run{M.Outcome.state(M.step(M.Candidate{}, a, act, s)), seen || M.State.eq(s, M.Recommended{})},
                sound_step(a, act, s, seen, h))

def Laws.every_path_to_approved_passes_recommended(cmds):
  holds(Laws.sound(M.replay_run(cmds, M.Candidate{}, M.Run{M.initial(M.Candidate{}), False{}})),
    replay_sound(cmds, M.Run{M.initial(M.Candidate{}), False{}}, Unit{}))

# LAW 5 and LAW 6: revoked or unassigned teachers cannot recommend
# ----------------------------------------------------------------
# Decided by computation once the free variables that the guard conjunction inspects are split.

def Laws.revoked_teacher_cannot_recommend(m, assigned, s):
  match m:
    case M.Baseline{}:
      {==}
    case M.Candidate{}:
      {==}

def Laws.unassigned_teacher_cannot_recommend(m, active, s):
  match m:
    case M.Baseline{}:
      {==}
    case M.Candidate{}:
      match active:
        case True{}:
          {==}
        case False{}:
          {==}

# LAW 7: Reject only from the declared rejection source
# -----------------------------------------------------
# An accepted Reject satisfied `from_ok`, i.e. the instance was in the rule's source state, and that
# source state is the declared one.

def reject_pt(+m: M.Model, +a: M.Actor, +s: M.State, w: T(M.permits(M.rule_of(m, M.Reject{}), a, s)))
  -> T(M.State.eq(s, Laws.reject_source(m))):
  match m:
    case M.Baseline{}:
      permits_from(M.rule_of(M.Baseline{}, M.Reject{}), a, s, w)
    case M.Candidate{}:
      permits_from(M.rule_of(M.Candidate{}, M.Reject{}), a, s, w)

def RejectFromSource(m: M.Model, s: M.State, o: M.Outcome) -> Type:
  T(Laws.implies(M.Outcome.ok(o), M.State.eq(s, Laws.reject_source(m))))

def Laws.reject_only_from_declared_source(m, a, s):
  holds(Laws.implies(M.Outcome.ok(M.step(m, a, M.Reject{}, s)), M.State.eq(s, Laws.reject_source(m))),
    step_prop(m, a, M.Reject{}, s, o => RejectFromSource(m, s, o),
      w => reject_pt(m, a, s, w), Unit{}))

# LAW 8: no forbidden effect is ever emitted
# ------------------------------------------
# Certificate: no rule of either model declares a forbidden effect; a denied command emits nothing.

def cert_effects(m: M.Model, act: M.Action)
  -> T(Bool.not(Laws.any_forbidden(M.emitted(M.rule_of(m, act))))):
  match m act:
    case M.Baseline{} M.Approve{}:
      Unit{}
    case M.Baseline{} M.Recommend{}:
      Unit{}
    case M.Baseline{} M.Reject{}:
      Unit{}
    case M.Baseline{} M.Revise{}:
      Unit{}
    case M.Baseline{} M.Submit{}:
      Unit{}
    case M.Candidate{} M.Approve{}:
      Unit{}
    case M.Candidate{} M.Recommend{}:
      Unit{}
    case M.Candidate{} M.Reject{}:
      Unit{}
    case M.Candidate{} M.Revise{}:
      Unit{}
    case M.Candidate{} M.Submit{}:
      Unit{}

def NoForbidden(o: M.Outcome) -> Type:
  T(Bool.not(Laws.any_forbidden(M.Outcome.effects(o))))

def Laws.forbidden_effects_never_emitted(m, a, act, s):
  holds(Bool.not(Laws.any_forbidden(M.Outcome.effects(M.step(m, a, act, s)))),
    step_prop(m, a, act, s, NoForbidden, w => cert_effects(m, act), Unit{}))
