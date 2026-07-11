# Feature-flagged entrypoint

Use `tools/fontdb_entry.py` as the only integration point. TP03 should not call the internal resolver directly.

## Modes

| Mode | FontDB runs | Can block renderer | Intended use |
|---|---:|---:|---|
| off | no | no | instant rollback |
| advisory | yes | no | shadow evaluation |
| enforce | yes | yes | production gate |

The committed default is `off`.

## Change mode

Configuration:

```yaml
mode: "advisory"
```

Or override without editing files:

```bash
FONTDB_MODE=off python tools/fontdb_entry.py -- ...
```

Environment takes precedence over the configuration file.

## Off-mode contract

```json
{
  "fontdb": {"enabled": false, "mode": "off"},
  "render_allowed": true,
  "bypass": true,
  "selected": null,
  "warnings": ["fontdb_disabled_existing_renderer_unchanged"]
}
```

The caller must preserve its pre-FontDB renderer path when `bypass=true`.
