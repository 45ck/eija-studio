# Symbols of application.scxml

# Constants

* [application.scxml.FORMAT](FORMAT.md) - Constant `FORMAT` in `application/scxml`.
* [application.scxml.NAMESPACE](NAMESPACE.md) - Constant `NAMESPACE` in `application/scxml`.

# Functions

* [application.scxml.event_data](event_data.md) - What the sender of an event attaches: the actor as the directory knows it (None if unknown), the version, the record's value of each guarded attribute in `attributes`, and, for a `timed` model, how long it has been in i…
* [application.scxml.guard_condition](guard_condition.md) - The transition's `cond`: the actor checks of `runtime.check_actor`, its guards over record values and the version check, over the event data.
* [application.scxml.scxml_id](scxml_id.md) - An XML/SCXML-safe id for a state or event name.
* [application.scxml.to_scxml](to_scxml.md) - The model as an SCXML document.
