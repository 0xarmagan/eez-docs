#!/usr/bin/env python3
"""Transfer eez-core-protocol/docs specs into the eez-docs Docusaurus site.

Source of truth: https://github.com/eez-association/eez-core-protocol/tree/main/docs
Pinned at upstream commit a7a0d7e (2026-09-03).

Re-runnable: wipes docs/spec/ and regenerates it from /tmp/eez-core-docs.
"""
import os
import re
import shutil

SRC = "/tmp/eez-core-docs"
SITE = "/Users/armagan/eez-docs"
OUT = os.path.join(SITE, "docs", "spec")
UPSTREAM = "https://github.com/eez-association/eez-core-protocol/blob/main/docs"

# The upstream commit these pages were generated from. Update alongside SRC
# whenever the mirror is regenerated against a newer upstream.
PIN_COMMIT = "a7a0d7e"
PIN_DATE = "2026-08-14"

# ---------------------------------------------------------------- doc refs
# Inline code-span references to sibling spec files -> real site links.
DOC_LINKS = {
    "CORE_PROTOCOL_SPEC.md": "/spec/core-protocol/",
    "EXECUTION_ENTRY_SPEC.md": "/spec/execution-entries",
    "MULTI_PROVER_SPEC.md": "/spec/multi-prover",
    "STATIC_ENTRY.md": "/spec/static-entries",
    "CAVEATS.md": "/spec/caveats",
    "BLOB_FORMAT_SPEC.md": "/spec/blobs/blob-format",
    "U256_COMPRESSED_CODEC.md": "/spec/blobs/u256-codec",
    "FUTURE_OPTIMIZATIONS.md": "/spec/blobs/future-optimizations",
}

# Core protocol spec sections A-I -> page slugs.
SECTIONS = [
    ("A", "a-data-model", "A. Data Model", "Data Model",
     "Core structs, storage layout, and transient execution variables."),
    ("B", "b-protocol-functions", "B. Core Protocol Functions", "Protocol Functions",
     "Function-by-function reference for EEZ.sol, EEZL2.sol, and CrossChainProxy.sol."),
    ("C", "c-action-hash", "C. Action Hash Computation", "Action Hash",
     "How crossChainCallHash is derived at every keying site."),
    ("D", "d-execution-model", "D. Execution Model", "Execution Model",
     "Forward-scan entry consumption, flat calls, reentrant calls, and revert spans."),
    ("E", "e-rolling-hash", "E. Rolling Hash", "Rolling Hash",
     "The integrity backbone: hash-chain semantics, static sub-hashes, worked examples."),
    ("F", "f-static-entry-resolution", "F. Static Entry Resolution", "Static Entry Resolution",
     "How read-only cross-chain calls resolve against static entries."),
    ("G", "g-entry-lifecycle", "G. Execution Entry Lifecycle", "Entry Lifecycle",
     "From L1 posting through L2 loading, consumption, and table clearing."),
    ("H", "h-invariants", "H. Invariants", "Invariants",
     "The nine invariants the protocol enforces on every batch."),
    ("I", "i-security-considerations", "I. Security Considerations", "Security",
     "Trust model, reentrancy, access control, and proxy identity."),
]

# No motion graphics are injected into spec pages. Only visuals authored in the
# upstream source itself (ASCII diagrams, mermaid, code blocks) appear here.
DIAGRAMS = {}


def split_fences(text):
    """Yield (is_fence, chunk) so replacements can skip fenced code.

    Fences also appear nested inside blockquotes as `> ```c`, so the opening
    and closing markers may carry a quote prefix. Missing that prefix means
    treating real code as prose and rewriting inside it.
    """
    fence_re = re.compile(r"(?m)^(?P<q>(?:> ?)*)```")
    chunks, pos = [], 0
    while True:
        opener = fence_re.search(text, pos)
        if not opener:
            chunks.append((False, text[pos:]))
            break
        chunks.append((False, text[pos : opener.start()]))
        # Close on the next marker sharing this fence's quote prefix.
        closer = re.compile(
            r"(?m)^" + re.escape(opener.group("q")) + r"```[ \t]*$"
        ).search(text, opener.end())
        end = closer.end() if closer else len(text)
        chunks.append((True, text[opener.start() : end]))
        pos = end
        if not closer:
            break
    return chunks


def transform_prose(text):
    """Rewrite cross-doc refs and neutralise MDX hazards, outside code fences."""
    out = []
    for is_fence, chunk in split_fences(text):
        if is_fence:
            out.append(chunk)
            continue

        # `SPEC_NAME.md` -> markdown link. Handles the `docs/NAME.md` form too.
        for name, target in DOC_LINKS.items():
            chunk = chunk.replace(f"`docs/{name}`", f"[`{name}`]({target})")
            chunk = chunk.replace(f"`{name}`", f"[`{name}`]({target})")

        # Relative repo links -> site links.
        chunk = re.sub(
            r"\]\(\./(BLOB_FORMAT_SPEC|U256_COMPRESSED_CODEC|FUTURE_OPTIMIZATIONS)\.md\)",
            lambda m: f"]({DOC_LINKS[m.group(1) + '.md']})",
            chunk,
        )
        # The JSON test-vector file is not transferred; point at upstream.
        chunk = chunk.replace(
            "](./U256_COMPRESSED_CODEC_VECTORS.json)",
            f"]({UPSTREAM}/blobs/U256_COMPRESSED_CODEC_VECTORS.json)",
        )

        out.append(chunk)
    return "".join(out)


def demote_headings(text):
    """Shift h2+ down one level; the page title lives in frontmatter."""
    out = []
    for is_fence, chunk in split_fences(text):
        if is_fence:
            out.append(chunk)
            continue
        chunk = re.sub(r"(?m)^(#{2,5}) ", lambda m: "#" * (len(m.group(1)) - 1) + " ", chunk)
        out.append(chunk)
    return "".join(out)


def frontmatter(title, sidebar_label, description, extra=""):
    return (
        "---\n"
        f'title: "{title}"\n'
        f'sidebar_label: "{sidebar_label}"\n'
        f'description: "{description}"\n'
        f"{extra}"
        "---\n\n"
    )


# Provenance is recorded once on the spec Overview page (PIN_NOTE below) and in
# the site's GitHub nav link — not as a per-page banner.
SOURCE_NOTE = ""

PIN_NOTE = (
    "*These pages mirror "
    "[eez-core-protocol/docs](https://github.com/eez-association/eez-core-protocol/tree/main/docs) "
    f"at commit [`{PIN_COMMIT}`](https://github.com/eez-association/eez-core-protocol/commit/{PIN_COMMIT}) "
    f"({PIN_DATE}). The upstream repository is canonical.*\n\n"
)


def _motion_tag(clip, caption, alt):
    return (
        "<DiagramMotion\n"
        f'  src="/motion/{clip}.webm"\n'
        f'  poster="/motion/{clip}-poster.png"\n'
        f'  alt="{alt}"\n'
        f'  caption="{caption}"\n'
        "/>\n\n"
    )


def diagram_import(slug):
    if not DIAGRAMS.get(slug):
        return ""
    return "import DiagramMotion from '@site/src/components/DiagramMotion';\n\n"


def diagram_block(slug):
    """Clips with no anchor — these open the page."""
    return "".join(
        _motion_tag(c, cap, alt)
        for c, cap, alt, *rest in DIAGRAMS.get(slug, [])
        if not (rest and rest[0])
    )


def place_anchored(slug, body):
    """Insert anchored clips directly after the heading they illustrate."""
    for clip, caption, alt, *rest in DIAGRAMS.get(slug, []):
        anchor = rest[0] if rest else None
        if not anchor:
            continue
        pattern = re.compile(r"(?m)^(#{1,4} " + re.escape(anchor) + r")\s*$")
        m = pattern.search(body)
        if not m:
            raise SystemExit(f"anchor not found on {slug}: {anchor!r}")
        tag = "\n\n" + _motion_tag(clip, caption, alt).rstrip("\n") + "\n"
        body = body[: m.end()] + tag + body[m.end() :]
    return body


def write(path, body):
    full = os.path.join(OUT, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w") as fh:
        fh.write(body)
    return path


def read_src(name):
    with open(os.path.join(SRC, name)) as fh:
        return fh.read()


def strip_h1(text):
    """Strip the source's own front matter, h1 title, and [TOC] marker.

    U256_COMPRESSED_CODEC.md ships MkDocs-style front matter and a [TOC]
    directive; both would otherwise render as body text under the front
    matter this generator adds.
    """
    text = re.sub(r"\A---\n.*?\n---\n+", "", text, count=1, flags=re.S)
    text = re.sub(r"\A#\s+.*?\n+", "", text, count=1)
    text = re.sub(r"(?m)^\[TOC\]\s*\n+", "", text, count=1)
    return text


def body_of(name, slug, upstream_path):
    """Whole-file page: strip the h1 (it is the title), keep h2+ as authored."""
    return transform_prose(strip_h1(read_src(name))), upstream_path


# ------------------------------------------------------------------ build
if os.path.isdir(OUT):
    shutil.rmtree(OUT)
os.makedirs(OUT)

written = []

# ---- Core Protocol Spec: preamble + sections A-I ----
core = transform_prose(read_src("CORE_PROTOCOL_SPEC.md"))
core = strip_h1(core)

# Preamble is everything before '## A. Data Model'.
split_at = core.index("\n## A. Data Model")
preamble = core[:split_at]
# Replace the in-document TOC with links to the split pages.
preamble = re.sub(r"## Table of Contents.*?(?=\n---)", "", preamble, flags=re.S)
preamble = preamble.replace("\n---\n\n\n---\n", "\n---\n")

toc = "## Sections\n\n"
for letter, slug, full_title, _label, desc in SECTIONS:
    toc += f"- **[{full_title}](/spec/core-protocol/{slug})** — {desc}\n"

index_body = (
    frontmatter(
        "Core Protocol Specification",
        "Overview",
        "Formal reference for the EEZ core protocol: data model, functions, hashing, "
        "execution model, invariants, and security considerations.",
        extra="slug: /spec/core-protocol/\n",
    )
    + PIN_NOTE
    + SOURCE_NOTE
    + demote_headings(preamble).strip()
    + "\n\n"
    + toc
)
written.append(write("core-protocol/index.mdx", index_body))

# Each A-I section becomes its own page.
bounds = []
for letter, slug, full_title, label, desc in SECTIONS:
    marker = f"\n## {full_title}"
    bounds.append((core.index(marker), slug, full_title, label, desc))
bounds.append((len(core), None, None, None, None))

for i in range(len(SECTIONS)):
    start, slug, full_title, label, desc = bounds[i]
    end = bounds[i + 1][0]
    section = core[start:end]
    # Drop the section's own '## X. Title' heading — it is the page title.
    section = re.sub(r"\A\n## .*?\n", "", section, count=1)
    section = section.strip("\n").rstrip("-\n ")
    body = (
        frontmatter(full_title, label, desc)
        + SOURCE_NOTE
        + diagram_import(slug)
        + diagram_block(slug)
        + place_anchored(slug, demote_headings(section))
        + "\n"
    )
    written.append(write(f"core-protocol/{slug}.mdx", body))

# ---- standalone specs ----
STANDALONE = [
    ("EXECUTION_ENTRY_SPEC.md", "execution-entries.mdx", "execution-entries",
     "Execution Entry Specification", "Execution Entries",
     "Entry structure, action hashes, call tables, state deltas, and the flow patterns "
     "every cross-rollup interaction is built from."),
    ("STATIC_ENTRY.md", "static-entries.mdx", "static-entries",
     "Static Entry Specification", "Static Entries",
     "The unified reentrant table and top-level StaticExecutionEntry pool that resolve "
     "read-only cross-chain calls."),
    ("MULTI_PROVER_SPEC.md", "multi-prover.mdx", "multi-prover",
     "Multi-Prover Specification", "Multi-Prover",
     "Per-rollup proof-system thresholds, two-stage public inputs, per-rollup queues, "
     "and the trust model."),
    ("CAVEATS.md", "caveats.mdx", "caveats",
     "Caveats", "Caveats",
     "Known edge cases in the current protocol implementation."),
]
for name, path, slug, title, label, desc in STANDALONE:
    text, _ = body_of(name, slug, name)
    body = (
        frontmatter(title, label, desc)
        + SOURCE_NOTE
        + diagram_import(slug)
        + diagram_block(slug)
        + place_anchored(slug, text.strip())
        + "\n"
    )
    written.append(write(path, body))

# ---- blob specs ----
BLOBS = [
    ("blobs/BLOB_FORMAT_SPEC.md", "blobs/blob-format.mdx", "blob-format",
     "Standardized Message Format", "Blob Format",
     "The wire format for the cross-chain message stream: framing, message types, "
     "encoding, and validity rules."),
    ("blobs/U256_COMPRESSED_CODEC.md", "blobs/u256-codec.mdx", "u256-codec",
     "A Compact Byte Encoding for 256-bit Integers", "u256 Codec",
     "The single-byte-prefix codec that compresses common 256-bit values, with the full "
     "format table and a reference implementation."),
    ("blobs/FUTURE_OPTIMIZATIONS.md", "blobs/future-optimizations.mdx", "future-optimizations",
     "Future Optimizations", "Future Optimizations",
     "Blob-encoding optimizations under consideration but not yet part of the format."),
]
for name, path, slug, title, label, desc in BLOBS:
    text, _ = body_of(name, slug, name)
    body = (
        frontmatter(title, label, desc)
        + SOURCE_NOTE
        + diagram_import(slug)
        + diagram_block(slug)
        + place_anchored(slug, text.strip())
        + "\n"
    )
    written.append(write(path, body))

for p in written:
    print(p)
print(f"\n{len(written)} pages written to {OUT}")
