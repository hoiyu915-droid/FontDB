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
- `tools/resolve_typography.py` — semantic profile selection plus glyph-safe render-run compiler
- `tools/font_integrity.py` — name-table, SHA-256, and OS/2 weight verification
- `tests/` — deterministic render and glyph stress-test records


## Canonical card-generation lock

All generated TA/TP image-card JSON must load `catalog/card_generation_lock.json`.
The active lock is `FONTDB_CARD_ZH_HANT_KNOWLEDGE_SANS_V1`:

- Traditional Chinese, English, and numerals all use `Source Han Sans TC`;
- title and section weight `700`, body `600`, label `700`, caption `500`;
- profile switching, font substitution, handwritten/display faces, and mixed-family rendering are forbidden;
- a missing, partial, or conflicting lock blocks queue sealing or image dispatch.

This lock is intentionally stricter than normal FontDB semantic selection. It
prioritizes cross-card stability for generated medical and evidence cards.

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

## Minimal resolver call

```bash
python tools/resolve_typography.py \
  --catalog catalog/profiles.yaml \
  --sources catalog/sources.yaml \
  --text '親子課程：臺語𩵚也要正確顯示' \
  --locale zh-Hant --role title --voice friendly \
  --bind 'jf open 粉圓=/path/jf-openhuninn-2.1.ttf' \
  --fallback 'NotoSansTC=/path/NotoSansTC.ttf'
```

## Why FontDB matters

Multilingual generation systems often confuse visual treatments with real font identities and fail silently when a font lacks required CJK glyphs. FontDB makes typography selection machine-readable, verifies font provenance and coverage, and provides deterministic, fail-closed inputs for downstream renderers.

FontDB is actively maintained by the repository owner. Maintenance includes issue triage, pull-request review, catalog and schema changes, regression checks, and downstream integration work.

## Maintainer workflow and Codex

Codex may assist with repository inspection, pull-request preparation, contract validation, regression repair, documentation, and release integration. Maintainers review all changes and retain responsibility for correctness, provenance, licensing, and merge decisions.

## Contributing and security

See [`CONTRIBUTING.md`](CONTRIBUTING.md) for contribution and validation expectations. Report vulnerabilities through the private process in [`SECURITY.md`](SECURITY.md).

## Adoption and impact

FontDB is intended for Chinese-first and multilingual rendering pipelines that need auditable font selection, glyph coverage, and licensing metadata. No unverified download, deployment, or adoption figures are claimed. Users may document integrations through an issue or pull request so public impact can be measured.

## License

Code, tools, tests, schemas, and executable configuration are licensed under Apache-2.0. Documentation and semantic catalog content are licensed under CC BY 4.0. See [`LICENSE`](LICENSE), [`LICENSE-ASSETS.md`](LICENSE-ASSETS.md), and [`NOTICE.md`](NOTICE.md) for boundaries and third-party exclusions.

## Roadmap

See [`ROADMAP.md`](ROADMAP.md) for current priorities and proposed stabilization work.

## Citation

Use [`CITATION.cff`](CITATION.cff) and cite the exact commit or release used.
