"""`python -m demos pr-gif ...`: GIFs for pull requests (docs/engineering/PR-STANDARD.md, ADR-0142).

* `browser`  records a real Studio interaction (a registered scenario, the ephemeral Studio, or a URL plus steps).
* `terminal` runs real commands, captures their real output with timing and replays it as a terminal page.
* `convert`  turns an existing video into a GIF that fits the limits.
* `publish`  commits a GIF to the orphan `pr-media` branch under `pr/<n>/` without touching the caller's worktree.

Every recording is converted by the same ffmpeg palettegen/paletteuse pipeline and fitted to the limits in
`demos.prgif.fit` (1280 px wide, 20 s, 5 MB) by lowering the frame rate and width automatically.
"""
