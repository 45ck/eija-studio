# Gates defined in quality/sessions/interop.py

# Quality Gates

* [nox -s interop_mermaid](interop-mermaid.md) - Mermaid's own parser reads every Mermaid export as PlayIDE does; its negative controls are caught.
* [nox -s interop_plantuml](interop-plantuml.md) - PlantUML reads every PlantUML export as PlayIDE does; its negative controls are caught.
* [nox -s interop_roundtrip](interop-roundtrip.md) - The committed UML exports are current, and every export reads back as exactly the model it came from.
