# Smoke test 007 — Self-contained unit suite

Date: 2026-07-11

## Local result

```text
Ran 4 tests in 0.019s
OK
```

## Covered invariants

1. versioned and hyphenated family aliases normalize consistently
2. exact family, digest, and OS/2 weight pass
3. impostor family fails
4. ordered fallback resolves missing primary glyphs
5. unresolved emoji blocks rendering
6. locale prefix matching works
7. over-limit titles are rejected

## Fixture strategy

Tests generate tiny TrueType fonts at runtime with FontTools. Production font binaries are not committed, and CI does not depend on fonts installed by the operating system.

## CI

GitHub Actions runs the same suite on Python 3.12 for every push to main and every pull request.
