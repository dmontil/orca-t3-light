---
name: orca-t3-light
description: Aplica la estética clara minimalista de T3 Code (fondo #fafafa, sidebar unificado) al terminal de Orca en macOS editando su profile-state.db con backup y verificación.
---

# Orca con estética T3 Code Light

## Cuándo usarla

Cuando el usuario pida el tema claro estilo T3 Code para Orca, o cuando quiera volver de
`orca-t3-dark` a un tema claro.

## Dónde vive realmente la configuración (verificado en macOS)

**No** hay `settings.json`. Orca guarda todo en una SQLite:

```
~/Library/Application Support/orca/profiles/<profile>/profile-state.db
  tabla: profile_state_documents
  domain: 'settings'          <- acá está el tema
  columnas: payload (JSON), content_hash, revision, updated_at, domain_version
```

Reglas que la tabla impone:

- `content_hash` debe ser **`sha256(payload)`** (verificado: coincide exacto).
- `revision` debe **incrementarse** en 1.
- Orca mantiene el payload **en memoria** y lo reescribe al salir: hay que **cerrar Orca
  con `Cmd + Q` antes de escribir**, o el cambio se pierde.

## Las claves reales del tema

Dentro del JSON de `payload`:

| Clave | Valor para light |
|---|---|
| `theme` | `"light"` |
| `leftSidebarAppearanceMode` | `"match-terminal"` |
| `leftSidebarTintColor` | `#e4e4e7` |
| `leftSidebarTintOpacity` | `0.08` |
| `terminalColorOverrides` | objeto con los 23 colores de abajo |

Ojo: la clave es **`terminalColorOverrides`**, no `colorOverrides`. Y no existe
`leftSidebarAppearance` como booleano.

## Los 23 colores

| Grupo | Claves |
|---|---|
| Base | `background` `#fafafa` · `foreground` `#18181b` · `cursor` `#18181b` · `cursorAccent` `#fafafa` · `selectionBackground` `#e4e4e7` · `selectionForeground` `#18181b` · `bold` `#09090b` |
| ANSI normal | `black` `#18181b` · `red` `#dc2626` · `green` `#16a34a` · `yellow` `#ca8a04` · `blue` `#2563eb` · `magenta` `#9333ea` · `cyan` `#0891b2` · `white` `#e4e4e7` |
| ANSI bright | `brightBlack` `#71717a` · `brightRed` `#ef4444` · `brightGreen` `#22c55e` · `brightYellow` `#eab308` · `brightBlue` `#3b82f6` · `brightMagenta` `#a855f7` · `brightCyan` `#06b6d4` · `brightWhite` `#ffffff` |

## Procedimiento

```bash
# 1. Cerrar Orca (Cmd+Q) y confirmar que no corre
pgrep -x Orca && echo "CERRÁ ORCA PRIMERO" && exit 1

# 2. Backup de la DB antes de tocarla
DB="$HOME/Library/Application Support/orca/profiles/local-default/profile-state.db"
cp "$DB" "$DB.bak.$(date +%Y%m%d-%H%M%S)"

# 3. Aplicar (el script hace merge, actualiza revision y content_hash)
python3 scripts/apply_theme.py light

# 4. Verificar que quedó escrito y el JSON es válido
python3 scripts/apply_theme.py show

# 5. Abrir Orca y comprobar a ojo
open -a Orca
```

`scripts/apply_theme.py` acepta `dark`, `light` o `show`, y `--dry-run` para ver qué
cambiaría sin escribir. Es idempotente: aplicar el mismo tema dos veces no rompe nada.

## Verificación

```bash
python3 -c "
import sqlite3,hashlib
c=sqlite3.connect('$DB')
p,h=c.execute(\"select payload,content_hash from profile_state_documents where domain='settings'\").fetchone()
print('hash OK' if hashlib.sha256(p.encode()).hexdigest()==h else 'HASH MISMATCH')
"
```

Si el hash no coincide, Orca descartará el cambio en el próximo arranque.

## Errores conocidos

- **Cambio que no aparece**: Orca estaba abierta y sobrescribió al salir. Cerrarla, reaplicar.
- **`no 'settings' row`**: el nombre del profile no es `local-default`. Listar
  `~/Library/Application Support/orca/profiles/` y ajustar la ruta.
- **Sin efecto en el sidebar**: revisar `leftSidebarAppearanceMode`; debe ser `match-terminal`.
