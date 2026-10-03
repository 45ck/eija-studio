# Symbols of application.formal

# Constants

* [application.formal.BLOCKING](BLOCKING.md) - Constant `BLOCKING` in `application/formal`.
* [application.formal.READS_REPORTS](READS_REPORTS.md) - Constant `READS_REPORTS` in `application/formal`.
* [application.formal.WHAT_IF_FAULTS](WHAT_IF_FAULTS.md) - Constant `WHAT_IF_FAULTS` in `application/formal`.

# Functions

* [application.formal.attach](attach.md) - Sealed receipts for every registered kind the source returned, skipping an exact repeat of the latest one.
* [application.formal.for_pack](for_pack.md) - Artifacts of a kind this pack does not verify from the reports become one NOT_RUN artifact with the pack's reason.
* [application.formal.pack_not_run](pack_not_run.md) - Why ``kind`` is NOT_RUN for ``pack`` (None when the pack verifies it from the checkout's reports).
* [application.formal.packet_view](packet_view.md) - The formal part of the review packet: per-kind claims, blockers, the full evidence list, explanations, and (with a pack) the pack's declared verifiers, so a kind no registered evidence covers (a TLC check) is shown NOT_…
* [application.formal.verifier_view](verifier_view.md) - Every verifier the pack declares, with the status its mode implies before any evidence is read: a kind that is not produced for this pack (``not_run``) is NOT_RUN with the reason, never absent and never a pass.
* [application.formal.what_if_model](what_if_model.md) - The workflow an unsupported interpretation would produce, or None (supported, unknown, or no transactions).
