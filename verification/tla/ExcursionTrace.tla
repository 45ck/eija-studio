------------------------- MODULE ExcursionTrace -------------------------
(***************************************************************************)
(* Trace validation. `Traces` holds sequences OBSERVED on the real Python  *)
(* runtime (application.runtime.execute against an ephemeral SQLite        *)
(* sandbox, real commits).  Each trace is <<initialKey, steps>>; a step is *)
(*   <<"X", op, actor, action, ver, outcome, postKey>>      (a command)    *)
(*   <<"E", actor, kind, val, 0, "ENV", postKey>>           (environment)  *)
(* TLC replays the trace through the SPEC's decision procedure and flags   *)
(* any step whose outcome code or resulting state differs from what the    *)
(* runtime produced.  TLC chooses the trace in Init, so one run validates  *)
(* the whole set.  Not a proof that the runtime is correct: it shows the   *)
(* runtime's observed behaviour is a behaviour of the spec.                *)
(*                                                                         *)
(* The unread steps live in the state (`rest`): TLC re-evaluates a large   *)
(* constant at every use, so indexing `Traces` per step is quadratic.      *)
(***************************************************************************)
EXTENDS Excursion

CONSTANT Traces
VARIABLES tr, pos, rest, bad
tvars == <<vars, tr, pos, rest, bad>>

CmdOf(x) == [op |-> x[2], actor |-> x[3], action |-> x[4], ver |-> x[5]]
EnvOf(x) == [actor |-> x[2], kind |-> x[3], val |-> (x[4] = 1)]

TInit ==
    /\ tr \in 1..Len(Traces)
    /\ Init
    /\ Key(InitState) = Traces[tr][1]
    /\ rest = Traces[tr][2]
    /\ pos = 0
    /\ bad = FALSE

TStep ==
    /\ ~bad
    /\ rest # <<>>
    /\ LET x == Head(rest) IN
       IF x[1] = "X"
       THEN LET c == CmdOf(x)
                n == Succ(Cur, c)
            IN /\ bad' = ~(Decide(Cur, c) = x[6] /\ Key(n) = x[7])
               /\ GoTo(n)
       ELSE LET n == EnvSucc(Cur, EnvOf(x))
            IN /\ bad' = ~(x[6] = "ENV" /\ Key(n) = x[7])
               /\ GoTo(n)
    /\ rest' = Tail(rest)
    /\ pos' = pos + 1
    /\ UNCHANGED tr

TSpec == TInit /\ [][TStep]_tvars

\* Violated exactly when the spec and the runtime disagree on an outcome or a state.
TNoDivergence == ~bad
=============================================================================
