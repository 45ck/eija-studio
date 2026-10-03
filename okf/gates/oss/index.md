# Gates defined in quality/sessions/oss.py

# Quality Gates

* [nox -s community_files](community-files.md) - Community files exist; CITATION.cff agrees with pyproject; roadmap covers every reserved ADR block.
* [nox -s docs_links](docs-links.md) - Relative links and heading anchors in README, community files and docs/ resolve (offline).
* [nox -s docs](docs.md) - Build the MkDocs Material site with --strict.
* [nox -s pr_status](pr-status.md) - Pull-request states claimed in the roadmap and lane hubs equal GitHub's.
* [nox -s readme_diagram](readme-diagram.md) - The README's before/after state diagram equals a fresh render of domain.policy.
