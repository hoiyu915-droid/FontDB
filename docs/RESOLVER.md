# Resolver contract

## Inputs

```yaml
locale: zh-Hant
role: cover_title
voice: authoritative
seed_id: SEED14
density: medium
title_chars: 10
renderer: deterministic | image_generation
```

## Selection order

1. Reject profiles that do not support the requested locale or functional role.
2. Reject profiles whose `max_title_chars` is exceeded.
3. Prefer an exact voice match, then compatible voices.
4. Apply Seed compatibility only as a preference; it must not override legibility.
5. For deterministic rendering, require a verified font stack.
6. For image generation, emit archetype and treatment constraints—not an invented font name.
7. If no production profile survives, fall back to `knowledge_sans`.

## Output

```yaml
profile_id: editorial_ming
confidence: verified
font_stack: [...]
prompt_constraints: [...]
warnings: []
```

## Safety constraints

- Body copy cannot use display, blackletter, outline-only, distressed, or high-glow profiles.
- Warning typography must preserve character skeletons and pass contrast requirements.
- Traditional Chinese requests must not silently fall back to Simplified-only glyph coverage.
- Generated text remains visually non-deterministic; final copy should be overlaid by a text renderer when exact wording matters.
