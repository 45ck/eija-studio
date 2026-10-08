# Gates defined in quality/sessions/property.py

# Quality Gates

* [nox -s property_deep](property-deep.md) - The same suite with random seeds and 10x examples; failures are saved under .hypothesis/.
* [nox -s property](property.md) - Hypothesis properties + stateful differential test, ci profile (derandomized, fast).
