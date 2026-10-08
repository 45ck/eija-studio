# Symbols of domain.sequences

# Classes

* [domain.sequences.Fragment](Fragment.md) - `class Fragment(Contract)` in `domain/sequences`.
* [domain.sequences.Interaction](Interaction.md) - `class Interaction(Contract)` in `domain/sequences`.
* [domain.sequences.Message](Message.md) - `class Message(Contract)` in `domain/sequences`.
* [domain.sequences.Operand](Operand.md) - `class Operand(Contract)` in `domain/sequences`.
* [domain.sequences.Sequences](Sequences.md) - `class Sequences(Contract)` in `domain/sequences`.

# Constants

* [domain.sequences.ACTION](ACTION.md) - Constant `ACTION` in `domain/sequences`.
* [domain.sequences.RECORD](RECORD.md) - Constant `RECORD` in `domain/sequences`.
* [domain.sequences.SEQUENCES_FILE](SEQUENCES_FILE.md) - Constant `SEQUENCES_FILE` in `domain/sequences`.

# Functions

* [domain.sequences.load_sequences](load_sequences.md) - The pack's sequences, or None when the pack has no `sequences.json`.
* [domain.sequences.messages](messages.md) - Every message, fragments' operands included, in reading order.
* [domain.sequences.parse_sequences](parse_sequences.md) - `def parse_sequences(document: Any, pack_id: str) -> Sequences` in `domain/sequences`.

# Methods

* [domain.sequences.Fragment.shape](Fragment.shape.md) - `def shape(self) -> Fragment` in `domain/sequences`.
* [domain.sequences.Interaction.known_records](Interaction.known_records.md) - `def known_records(self) -> Interaction` in `domain/sequences`.
* [domain.sequences.Interaction.record_of](Interaction.record_of.md) - `def record_of(self, message: Message) -> str` in `domain/sequences`.
* [domain.sequences.Sequences.digest](Sequences.digest.md) - `def digest(self) -> str` in `domain/sequences`.
* [domain.sequences.Sequences.unique](Sequences.unique.md) - `def unique(self) -> Sequences` in `domain/sequences`.

# Type Aliases

* [domain.sequences.Step](Step.md) - Type alias `Step` in `domain/sequences`.
