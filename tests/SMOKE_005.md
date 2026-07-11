# Smoke test 005 — Runtime font integrity gate

Date: 2026-07-11

## Positive cases

### jf open 粉圓 2.1

- claimed family: `jf open 粉圓`
- accepted alias: `jf-openhuninn`
- name-table match: pass
- SHA-256 match: pass
- integrity: pass

### Iansui / 芫荽

- claimed family: `芫荽 Iansui`
- accepted aliases: `Iansui`, `芫荽`
- name-table match: pass
- SHA-256 match: pass
- integrity: pass

## Impostor case

File: locally instantiated `NotoSansTC-700.ttf`  
Claimed family: `Source Han Sans TC`

Result:

- actual typographic family: `Noto Sans TC`
- error: `family_name_mismatch`
- integrity: fail
- exit code: 3

## Additional finding

fontTools variable-font instancing correctly changed `OS/2.usWeightClass` to 700, while legacy name-table records remained `Thin` in the generated file. Weight verification must therefore use the OS/2 numeric weight class rather than trusting the filename or style label alone.

## Exit contract

- 0: all requested integrity checks pass
- 3: family, digest, or weight mismatch
