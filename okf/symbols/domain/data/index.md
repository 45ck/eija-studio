# Symbols of domain.data

# Classes

* [domain.data.Association](Association.md) - `class Association(Contract)` in `domain/data`.
* [domain.data.Attribute](Attribute.md) - `class Attribute(Contract)` in `domain/data`.
* [domain.data.DataModel](DataModel.md) - `class DataModel(Contract)` in `domain/data`.
* [domain.data.Entity](Entity.md) - `class Entity(Contract)` in `domain/data`.

# Constants

* [domain.data.ATTRIBUTE_NAME](ATTRIBUTE_NAME.md) - Constant `ATTRIBUTE_NAME` in `domain/data`.
* [domain.data.DATA_FILE](DATA_FILE.md) - Constant `DATA_FILE` in `domain/data`.
* [domain.data.NAME](NAME.md) - Constant `NAME` in `domain/data`.

# Functions

* [domain.data.check_values](check_values.md) - Validate a record's values against its entity.
* [domain.data.data_for](data_for.md) - The data model beside this pack's `pack.json`, if it has one: the one a draft holds (ADR-0202), else `data.json`.
* [domain.data.load_data](load_data.md) - The pack's data model, or None when the pack has no `data.json`.
* [domain.data.parse_data](parse_data.md) - `def parse_data(document: Any, pack_id: str) -> DataModel` in `domain/data`.

# Methods

* [domain.data.Attribute.coherent](Attribute.coherent.md) - `def coherent(self) -> Attribute` in `domain/data`.
* [domain.data.DataModel.coherent](DataModel.coherent.md) - `def coherent(self) -> DataModel` in `domain/data`.
* [domain.data.DataModel.digest](DataModel.digest.md) - `def digest(self) -> str` in `domain/data`.
* [domain.data.DataModel.entity](DataModel.entity.md) - `def entity(self, name: str) -> Entity` in `domain/data`.
* [domain.data.Entity.unique](Entity.unique.md) - `def unique(self) -> Entity` in `domain/data`.

# Type Aliases

* [domain.data.FieldType](FieldType.md) - Type alias `FieldType` in `domain/data`.
* [domain.data.Multiplicity](Multiplicity.md) - Type alias `Multiplicity` in `domain/data`.
