---------------------------- MODULE Excursion ----------------------------
(***************************************************************************)
(* EIJA Studio: formal model of the excursion workflow AND its commit      *)
(* protocol (application/runtime.py `execute`).                            *)
(*                                                                         *)
(* One preview instance is executed by commands (opId, actor, action,      *)
(* expectedVersion).  `Decide` fixes the order of the checks exactly as    *)
(* the runtime performs them:                                              *)
(*   1 action modelled?  2 actor in directory?  3 actor active?            *)
(*   4 role current?     5 assigned (when guarded)?   <- authority, NOW    *)
(*   6 operation replay lookup (binding conflict / duplicate)              *)
(*   7 CAS on version    8 state check                                     *)
(*   9 effects: state, version, audit, outbox, operation record - one step *)
(* A command that is not decided COMMITTED changes nothing (rollback).     *)
(* The actor directory (active / assigned) is changed by the environment,  *)
(* not by commands: revocation and assignment changes are environment      *)
(* steps that may interleave anywhere.                                     *)
(*                                                                         *)
(* The transition table, directory and bounds are GENERATED from the       *)
(* executable Python model (verification/tla/generate.py) into MC_*.tla    *)
(* modules; nothing in this file is edited per configuration.              *)
(*                                                                         *)
(* This model establishes safety properties of the modelled protocol      *)
(* within the declared bounds.  It does not prove the Python code correct; *)
(* agreement between model and code is a separate, measured claim         *)
(* (verification/tla/conformance.py).                                      *)
(***************************************************************************)
EXTENDS Naturals, Sequences, FiniteSets, TLC

CONSTANTS
    OpSeq,         \* operation ids (bounded), as a sequence for stable printing
    ActorSeq,      \* actors of the trusted directory
    UnknownSeq,    \* actor ids that are not in the directory
    MutableSeq,    \* directory actors the environment may change
    ActionSeq,     \* every action name a command may carry
    States,        \* workflow states
    InitialState,
    ActorRole,     \* [directory actor -> role]
    InitDir,       \* [directory actor -> [active, assigned]]
    Table,         \* [modelled action -> transition record]
    Forbidden,     \* effect names that must never be emitted
    MaxVer,        \* largest expectedVersion a command may carry
    Mutation       \* "none" or a seeded defect used only as a negative control

Range(s) == { s[i] : i \in 1..Len(s) }
OpIds == Range(OpSeq)
Actors == Range(ActorSeq)
CmdActors == Actors \cup Range(UnknownSeq)
Actions == Range(ActionSeq)

Cmds == [op : OpIds, actor : CmdActors, action : Actions, ver : 0..MaxVer]
EnvActs == [actor : Range(MutableSeq), kind : {"active", "assigned"}, val : BOOLEAN]

VARIABLES st, ver, ops, audit, outbox, dir, emitted
vars == <<st, ver, ops, audit, outbox, dir, emitted>>

Unused == [used |-> FALSE, actor |-> "-", action |-> "-", ver |-> 0, res |-> <<"-", 0>>]
Cur == [st |-> st, ver |-> ver, ops |-> ops, audit |-> audit, outbox |-> outbox, dir |-> dir, emitted |-> emitted]

InitState ==
    [st |-> InitialState, ver |-> 0, ops |-> [o \in OpIds |-> Unused], audit |-> 0,
     outbox |-> [o \in OpIds |-> 0], dir |-> InitDir, emitted |-> {}]

(* ---------------------- decision function ------------------------------ *)

Bind(c) == <<c.actor, c.action, c.ver>>

AuthCode(s, c) ==
    LET t == Table[c.action] IN
    IF c.actor \notin Actors THEN "UNKNOWN_ACTOR"
    ELSE IF ~s.dir[c.actor].active THEN "ACTOR_REVOKED"
    ELSE IF ActorRole[c.actor] # t.role THEN "ROLE_DENIED"
    ELSE IF t.needsAssigned /\ ~s.dir[c.actor].assigned THEN "ASSIGNMENT_DENIED"
    ELSE "OK"

ReplayCode(s, c) ==
    IF ~s.ops[c.op].used THEN "OK"
    ELSE IF <<s.ops[c.op].actor, s.ops[c.op].action, s.ops[c.op].ver>> # Bind(c) THEN "OPERATION_CONFLICT"
    ELSE "DUPLICATE"

CommitCode(s, c) ==
    LET t == Table[c.action] IN
    IF s.ver # c.ver THEN "STALE_VERSION"
    ELSE IF s.st # t.src THEN "STATE_DENIED"
    ELSE IF t.other # <<>> /\ Mutation # "emit_unadapted" THEN "EFFECT_DENIED"
    ELSE "COMMITTED"

Decide(s, c) ==
    IF c.action \notin DOMAIN Table THEN "ACTION_DENIED"
    ELSE IF Mutation = "replay_before_auth" THEN
        (IF ReplayCode(s, c) # "OK" THEN ReplayCode(s, c)
         ELSE IF AuthCode(s, c) # "OK" THEN AuthCode(s, c)
         ELSE CommitCode(s, c))
    ELSE IF AuthCode(s, c) # "OK" THEN AuthCode(s, c)
    ELSE IF ReplayCode(s, c) # "OK" THEN ReplayCode(s, c)
    ELSE CommitCode(s, c)

(* Successor state of a command.  Only COMMITTED changes state, except the  *)
(* seeded defect "replay_reemits" (a replay re-queues its notifications).   *)
Succ(s, c) ==
    LET o == Decide(s, c) IN
    IF o = "COMMITTED" THEN
        LET t == Table[c.action] IN
        [s EXCEPT !.st = t.dst, !.ver = s.ver + 1,
                  !.audit = s.audit + Len(t.audit),
                  !.outbox[c.op] = s.outbox[c.op] + Len(t.notify),
                  !.ops[c.op] = [used |-> TRUE, actor |-> c.actor, action |-> c.action,
                                 ver |-> c.ver, res |-> <<t.dst, s.ver + 1>>],
                  !.emitted = s.emitted \cup Range(t.audit) \cup Range(t.notify) \cup Range(t.other)]
    ELSE IF o = "DUPLICATE" /\ Mutation = "replay_reemits" THEN
        LET t == Table[c.action] IN
        [s EXCEPT !.outbox[c.op] = s.outbox[c.op] + Len(t.notify)]
    ELSE s

EnvSucc(s, e) ==
    IF e.kind = "active" THEN [s EXCEPT !.dir[e.actor].active = e.val]
    ELSE [s EXCEPT !.dir[e.actor].assigned = e.val]

(* ------------------------- specification ------------------------------ *)

Init ==
    /\ st = InitState.st /\ ver = InitState.ver /\ ops = InitState.ops
    /\ audit = InitState.audit /\ outbox = InitState.outbox /\ dir = InitState.dir
    /\ emitted = InitState.emitted

GoTo(n) == /\ st' = n.st /\ ver' = n.ver /\ ops' = n.ops /\ audit' = n.audit
           /\ outbox' = n.outbox /\ dir' = n.dir /\ emitted' = n.emitted

Execute(c) == LET n == Succ(Cur, c) IN /\ n # Cur /\ GoTo(n)
Environment(e) == LET n == EnvSucc(Cur, e) IN /\ n # Cur /\ GoTo(n)

Next == (\E c \in Cmds : Execute(c)) \/ (\E e \in EnvActs : Environment(e))
Spec == Init /\ [][Next]_vars

(* --------------------------- invariants -------------------------------- *)

AllEffects == UNION { Range(Table[a].audit) \cup Range(Table[a].notify) \cup Range(Table[a].other) : a \in DOMAIN Table }

TypeOK ==
    /\ st \in States
    /\ ver \in 0..Len(OpSeq)
    /\ audit \in Nat
    /\ outbox \in [OpIds -> Nat]
    /\ dir \in [Actors -> [active : BOOLEAN, assigned : BOOLEAN]]
    /\ \A o \in OpIds : ops[o].used \in BOOLEAN
    /\ emitted \subseteq AllEffects

Committed == { o \in OpIds : ops[o].used }

\* A committed approval was never issued by a teacher (role read from the directory, not the table).
NoTeacherApproval ==
    \A o \in Committed :
        Table[ops[o].action].dst = "Approved" => ActorRole[ops[o].actor] # "Teacher"

\* In the candidate model (recommendation enabled) approval is only taken from Recommended
\* and only after a Recommend operation has committed.
ApprovalRequiresRecommendation ==
    ("Recommend" \in DOMAIN Table) =>
        /\ \A o \in Committed : Table[ops[o].action].dst = "Approved" => Table[ops[o].action].src = "Recommended"
        /\ st = "Approved" => \E o \in Committed : ops[o].action = "Recommend"

\* Effects are queued at most once per operation id, exactly as the committed operation dictates.
OutboxAtMostOncePerOperation ==
    \A o \in OpIds : outbox[o] <= IF ops[o].used THEN Len(Table[ops[o].action].notify) ELSE 0

RECURSIVE AuditOf(_)
AuditOf(i) == IF i = 0 THEN 0
              ELSE AuditOf(i - 1) + (IF ops[OpSeq[i]].used THEN Len(Table[ops[OpSeq[i]].action].audit) ELSE 0)

\* State version, operation record and audit move together: one atomic step per commit.
AtomicCommit ==
    /\ ver = Cardinality(Committed)
    /\ audit = AuditOf(Len(OpSeq))

\* Continuing authority: no answer that depends on instance or operation history (a replayed
\* result, a binding conflict, a version or state answer, a commit) is produced for an actor
\* that is not authorised in the CURRENT directory.  Stated independently of `Decide`.
Authorised(c) ==
    /\ c.actor \in Actors
    /\ dir[c.actor].active
    /\ ActorRole[c.actor] = Table[c.action].role
    /\ Table[c.action].needsAssigned => dir[c.actor].assigned

PastAuthority == {"DUPLICATE", "OPERATION_CONFLICT", "STALE_VERSION", "STATE_DENIED", "EFFECT_DENIED", "COMMITTED"}

ReplayNeverBypassesCurrentAuthority ==
    \A c \in Cmds : (c.action \in DOMAIN Table /\ Decide(Cur, c) \in PastAuthority) => Authorised(c)

ForbiddenEffectsNeverEmitted == emitted \cap Forbidden = {}

\* Action property (PROPERTY): the version never decreases.
VersionMonotonic == [][ver' >= ver]_vars

(* ------------- state-graph dump used by conformance checking ------------ *)

BoolInt(b) == IF b THEN 1 ELSE 0
OpSig(s, o) == IF ~s.ops[o].used THEN <<>>
               ELSE <<s.ops[o].actor, s.ops[o].action, s.ops[o].ver, s.ops[o].res[1], s.ops[o].res[2]>>
Key(s) ==
    << s.st, s.ver, s.audit,
       [i \in 1..Len(OpSeq) |-> OpSig(s, OpSeq[i])],
       [i \in 1..Len(OpSeq) |-> s.outbox[OpSeq[i]]],
       [i \in 1..Len(ActorSeq) |-> <<BoolInt(s.dir[ActorSeq[i]].active), BoolInt(s.dir[ActorSeq[i]].assigned)>>] >>

CmdActorSeq == ActorSeq \o UnknownSeq
NO == Len(OpSeq)
NA == Len(CmdActorSeq)
NK == Len(ActionSeq)
NV == MaxVer + 1
CmdAt(i) == [op |-> OpSeq[(i \div (NA * NK * NV)) + 1],
             actor |-> CmdActorSeq[((i \div (NK * NV)) % NA) + 1],
             action |-> ActionSeq[((i \div NV) % NK) + 1],
             ver |-> i % NV]
CmdSeq == [i \in 1..(NO * NA * NK * NV) |-> CmdAt(i - 1)]
EnvAt(i) == [actor |-> MutableSeq[(i \div 4) + 1],
             kind |-> IF (i \div 2) % 2 = 0 THEN "active" ELSE "assigned",
             val |-> (i % 2 = 1)]
EnvSeq == [i \in 1..(4 * Len(MutableSeq)) |-> EnvAt(i - 1)]

\* One line per reachable state: its key, the outcome code of EVERY command and the successor of
\* every committing command and every environment step.  Used only by the dump configuration.
Emit ==
    /\ (Cur = InitState => PrintT(<<"HEADER",
                                 [i \in 1..Len(CmdSeq) |-> <<CmdSeq[i].op, CmdSeq[i].actor, CmdSeq[i].action, CmdSeq[i].ver>>],
                                 [i \in 1..Len(EnvSeq) |-> <<EnvSeq[i].actor, EnvSeq[i].kind, BoolInt(EnvSeq[i].val)>>]>>))
    /\ PrintT(<<"STATE", Key(Cur),
                [i \in 1..Len(CmdSeq) |-> Decide(Cur, CmdSeq[i])],
                [i \in 1..Len(CmdSeq) |-> IF Decide(Cur, CmdSeq[i]) = "COMMITTED" THEN Key(Succ(Cur, CmdSeq[i])) ELSE <<>>],
                [i \in 1..Len(EnvSeq) |-> Key(EnvSucc(Cur, EnvSeq[i]))]>>)
=============================================================================
