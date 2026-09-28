# syntax=docker/dockerfile:1.7
#
# Bend 2 proof checker for EIJA's formal lane (ADR-0025).
#
# Bend 2 supports Linux, macOS and WSL, not native Windows, so the gate runs the checker in this
# image. Everything that decides a verdict is pinned:
#
#   * the base image by digest (ubuntu 24.04 LTS, linux/amd64);
#   * Bend by release version, git commit and the archive sha256 that the official installer
#     (https://bend-lang.com/install.sh, VER=2.0.32) itself checks. That installer always installs
#     the *latest* release, so it is not run verbatim; the `bend` stage performs its steps
#     (download the archive, check its sha256, place bin/bend, bend2/ and guide/ side by side)
#     against a fixed version instead;
#   * Lean by release and archive sha256. `bend --verdict` rechecks every def with BendTT, a small
#     kernel whose soundness is proven in Lean (bend2/bendtt.lean). The `kernel` stage compiles
#     that file exactly as bend2/safe.ts does (`lean -c` then `leanc -O3 -DNDEBUG`), and only the
#     resulting binary reaches the final image, via $BENDTT.
#
# The final image carries no compiler: `bend PROOF.bend` only type-checks, and clang is needed only
# to build native Bend binaries (the kernel stage uses the clang bundled with Lean's leanc). The gate
# runs the container with `--network none`; BEND_NO_TELEMETRY stops the daily version check.
# Bump BEND_* and LEAN_* values together with the checksums below.

FROM ubuntu:24.04@sha256:496754492fb28b4d3049432f2ca787449331e23fb14f0dd3fffea86bf5a93eb4 AS bend

ADD --checksum=sha256:5c365ddb12954d0933cef751802e0f7d9875f842edcb80f9661f89cd1a9ff7b6 \
    https://github.com/bendlang/bend/releases/download/v2.0.32/bend-2.0.32-linux-x64.tar.gz \
    /tmp/bend.tar.gz

RUN mkdir -p /tmp/bend-x /opt/bend/bin \
 && tar -xzf /tmp/bend.tar.gz -C /tmp/bend-x \
 && mv /tmp/bend-x/bend/bend2 /tmp/bend-x/bend/guide /opt/bend/ \
 && mv /tmp/bend-x/bend/bin/bend /opt/bend/bin/bend \
 && rm -rf /tmp/bend-x /tmp/bend.tar.gz


FROM bend AS kernel

RUN apt-get update \
 && apt-get install -y --no-install-recommends zstd \
 && rm -rf /var/lib/apt/lists/*

ADD --checksum=sha256:caaa98356098c85dc0fcbbd28e1ec66f39eb6551829972b752ff20e1286b646b \
    https://github.com/leanprover/lean4/releases/download/v4.34.0/lean-4.34.0-linux.tar.zst \
    /tmp/lean.tar.zst

RUN mkdir -p /opt/lean /opt/bendtt \
 && tar --zstd -xf /tmp/lean.tar.zst -C /opt/lean --strip-components=1 \
 && rm /tmp/lean.tar.zst \
 && cp /opt/bend/bend2/bendtt.lean /opt/bendtt/ \
 && cd /opt/bendtt \
 && /opt/lean/bin/lean -c bendtt.c bendtt.lean \
 && /opt/lean/bin/leanc -O3 -DNDEBUG bendtt.c -o bendtt \
 && sha256sum bendtt.lean bendtt > /opt/bendtt/SHA256SUMS


FROM ubuntu:24.04@sha256:496754492fb28b4d3049432f2ca787449331e23fb14f0dd3fffea86bf5a93eb4

ARG BEND_VERSION=2.0.32
# git tag v2.0.32 of github.com/bendlang/bend
ARG BEND_COMMIT=573002f01ec6c52416d44489543f69a9625facf8
ARG LEAN_VERSION=4.34.0

COPY --from=bend /opt/bend /opt/bend
COPY --from=kernel /opt/bendtt/bendtt /opt/bendtt/SHA256SUMS /opt/bendtt/

ENV BENDTT=/opt/bendtt/bendtt \
    BEND_NO_TELEMETRY=1 \
    PATH=/opt/bend/bin:$PATH

RUN useradd --create-home --uid 10001 bender

LABEL org.opencontainers.image.title="eija-bend-checker" \
      org.opencontainers.image.source="https://github.com/45ck/eija-studio" \
      org.opencontainers.image.licenses="Apache-2.0" \
      dev.eija.bend.version="${BEND_VERSION}" \
      dev.eija.bend.commit="${BEND_COMMIT}" \
      dev.eija.lean.version="${LEAN_VERSION}"

USER bender
WORKDIR /work
ENTRYPOINT ["bend"]
