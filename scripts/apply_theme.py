#!/usr/bin/env python3
"""Apply an Orca terminal theme by editing the profile state SQLite.

Orca stores settings in ~/Library/Application Support/orca/profiles/<profile>/profile-state.db,
table profile_state_documents, domain 'settings', payload = JSON text.
content_hash is sha256(payload) and revision must increase.

Usage: apply_theme.py {dark|light|show} [--dry-run]
Requires Orca to be closed: it caches the payload in memory and rewrites on exit.
"""
import hashlib, json, pathlib, sqlite3, sys, time

DB = pathlib.Path.home() / "Library/Application Support/orca/profiles/local-default/profile-state.db"

BASE = {
    "background": "#0a0a0a", "foreground": "#ededed", "cursor": "#ededed",
    "cursorAccent": "#0a0a0a", "selectionBackground": "#27272a",
    "selectionForeground": "#ffffff", "bold": "#ffffff",
    "black": "#18181b", "red": "#f87171", "green": "#4ade80", "yellow": "#facc15",
    "blue": "#60a5fa", "magenta": "#c084fc", "cyan": "#22d3ee", "white": "#e4e4e7",
    "brightBlack": "#52525b", "brightRed": "#fca5a5", "brightGreen": "#86efac",
    "brightYellow": "#fde047", "brightBlue": "#93c5fd", "brightMagenta": "#d8b4fe",
    "brightCyan": "#67e8f9", "brightWhite": "#ffffff",
}

LIGHT = {
    "background": "#fafafa", "foreground": "#18181b", "cursor": "#18181b",
    "cursorAccent": "#fafafa", "selectionBackground": "#e4e4e7",
    "selectionForeground": "#18181b", "bold": "#09090b",
    "black": "#18181b", "red": "#dc2626", "green": "#16a34a", "yellow": "#ca8a04",
    "blue": "#2563eb", "magenta": "#9333ea", "cyan": "#0891b2", "white": "#e4e4e7",
    "brightBlack": "#71717a", "brightRed": "#ef4444", "brightGreen": "#22c55e",
    "brightYellow": "#eab308", "brightBlue": "#3b82f6", "brightMagenta": "#a855f7",
    "brightCyan": "#06b6d4", "brightWhite": "#ffffff",
}

THEMES = {
    "dark": {"theme": "dark", "overrides": BASE, "tint": "#18181b", "tintOpacity": 0.08},
    "light": {"theme": "light", "overrides": LIGHT, "tint": "#e4e4e7", "tintOpacity": 0.08},
}


def load(conn):
    row = conn.execute(
        "select payload, revision from profile_state_documents where domain='settings'"
    ).fetchone()
    if not row:
        sys.exit("ERROR: no 'settings' row")
    return json.loads(row[0]), row[1], row[0]


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    dry = "--dry-run" in sys.argv
    if not args or args[0] not in ("dark", "light", "show"):
        sys.exit(__doc__)
    if not DB.exists():
        sys.exit(f"ERROR: {DB} not found")

    conn = sqlite3.connect(f"file:{DB}?mode={'ro' if (dry or args[0]=='show') else 'rw'}", uri=True)
    settings, revision, raw = load(conn)

    if args[0] == "show":
        o = settings.get("terminalColorOverrides") or {}
        print(f"theme={settings.get('theme')} overrides={len(o)} keys")
        print(json.dumps(o, indent=1))
        return

    spec = THEMES[args[0]]
    before = dict(settings)
    settings["theme"] = spec["theme"]
    settings["leftSidebarAppearanceMode"] = "match-terminal"
    settings["leftSidebarTintColor"] = spec["tint"]
    settings["leftSidebarTintOpacity"] = spec["tintOpacity"]
    settings["terminalColorOverrides"] = spec["overrides"]

    payload = json.dumps(settings)
    new_hash = hashlib.sha256(payload.encode()).hexdigest()
    print(f"{args[0]}: {len(spec['overrides'])} colour keys, payload {len(raw)} -> {len(payload)} bytes")
    changed = [k for k in settings if before.get(k) != settings[k]]
    print("changed keys:", ", ".join(changed))

    if dry:
        print("(dry run, nothing written)")
        return

    conn.execute(
        "update profile_state_documents set payload=?, revision=?, updated_at=?, content_hash=? "
        "where domain='settings'",
        (payload, revision + 1, int(time.time() * 1000), new_hash),
    )
    conn.commit()
    print(f"written: revision {revision} -> {revision + 1}, sha256={new_hash[:12]}")


if __name__ == "__main__":
    main()
