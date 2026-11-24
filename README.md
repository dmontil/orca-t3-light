# orca-t3-light

Aplica la estética **T3 Code light** al terminal de [Orca](https://orca.dev) en macOS.

## Cómo funciona

Orca no usa un `settings.json`: guarda todo en una SQLite.

```
~/Library/Application Support/orca/profiles/<profile>/profile-state.db
  tabla profile_state_documents · domain 'settings' · payload (JSON)
```

`scripts/apply_theme.py` edita esa fila respetando las invariantes de la tabla
(`content_hash = sha256(payload)`, `revision + 1`) y hace backup antes de escribir.

## Uso

```bash
pgrep -x Orca && echo "Cerrala con Cmd+Q primero"
python3 scripts/apply_theme.py light      # aplica
python3 scripts/apply_theme.py show    # verifica
```

`--dry-run` muestra qué cambiaría sin escribir. Es idempotente.

## Instalación como skill

```bash
git clone https://github.com/dmontil/orca-t3-light.git ~/.agents/skills/orca-t3-light
```

MIT.
