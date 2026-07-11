# Smoke test 008 — Feature flag and rollback entrypoint

Date: 2026-07-11

## Results

| Mode | Resolver outcome | Entrypoint exit | render_allowed |
|---|---|---:|---:|
| off | not executed | 0 | true |
| advisory | underlying would block | 0 | true |
| enforce | underlying blocks impostor | 2 | false |

## YAML parsing defect caught

Unquoted `off` was initially parsed by PyYAML as boolean false. The config now quotes `"off"`, and the parser also treats boolean false as off for defensive compatibility.

## Unit suite

Five tests pass, including config-off behavior and environment override precedence.
