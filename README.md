# FontDB

A semantic typography reference and resolver for Chinese-first card generation.

FontDB does **not** treat every visual treatment as a standalone font. It separates:

1. **Archetype** — the structural family (sans, serif, handwritten, display, etc.).
2. **Treatment** — stroke, shadow, texture, deformation, spacing, and composition.
3. **Font stack** — real font families, fallbacks, coverage, source, and license.
4. **Usage profile** — where the combination is safe and useful.

## Status

`v0.3-draft` — 21 semantic profiles cover the initial montage; four profiles now have verified open-font stacks, while the industrial condensed recipe remains provisional pending render tests.

## Repository map

- `catalog/profiles.yaml` — canonical semantic profiles
- `catalog/sources.yaml` — verified font sources, releases, licenses, and coverage limits
- `schema/profile.schema.json` — machine-readable profile schema
- `docs/TAXONOMY.md` — classification rules
- `docs/RESOLVER.md` — selection and fallback logic
- `docs/SOURCE_POLICY.md` — evidence, licensing, and reference-image policy
- `references/README.md` — how to register visual references without pretending they are fonts
- `tools/glyph_preflight.py` — executable ordered-stack Unicode coverage resolver
- `tests/` — deterministic render and glyph stress-test records

## Core rule

A generated-looking label such as “liquid future font” or “explosive headline font” is a **style reference**, not a verified font identity. A profile becomes production-ready only after its real font stack, CJK coverage, source URL, and license are verified.

## Intended integration

FontDB is designed to sit beside Seed Resolver:

- Seed controls the overall visual language.
- FontDB resolves typography role and treatment.
- The renderer applies a verified font stack when deterministic text rendering is available.
- Image generation receives a constrained visual description, never a fabricated font name.

## Versioning

- `draft`: semantic role exists, but implementation or license is incomplete.
- `verified`: real fonts, source, license, and CJK coverage checked.
- `tested`: verified and passed layout stress tests.
- `deprecated`: retained only for backward compatibility.
