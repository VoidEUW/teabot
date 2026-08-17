# Ausführungsplan v1.0

Jede Datei in diesem Ordner beschreibt **einen** Abschnitt auf dem Weg zu
v1.0. Die Identität eines Abschnitts ist sein Ziel-Tag — es gibt keine
zusätzliche Phasennummerierung, damit nichts durcheinandergeht.

## Reihenfolge

| Ziel-Tag | Datei | Inhalt |
|---|---|---|
| `v0.1.0` | [bootstrap](v0.1.0-bootstrap.md) | Skelett, Config, DB, Registry, Docker, CI |
| `v0.2.0` | [bot-logging](v0.2.0-bot-logging.md) | Client, Manager, Logging, SSE-Terminal |
| `v0.3.0` | [auth](v0.3.0-auth.md) | Discord OAuth, Sessions, Permissions, Dev-Mode |
| `v0.4.0` | [settings-shell](v0.4.0-settings-shell.md) | Guild-Sync, Settings-Framework, Admin-Shell |
| `v0.5.0` | [tickets](v0.5.0-tickets.md) | Tickets als Referenzmodul |
| `v0.6.0`–`v0.9.0` | [modules](v0.6.0-modules.md) | Violations, Announcements, Events, Citations — je ein Tag |
| `v0.10.0` | [hardening](v0.10.0-hardening.md) | Backup, Dokumentation, Härtung |
| `v1.0.0` | — | Freigabe, kein eigener Plan |

## Regeln

**Die Reihenfolge ist verbindlich.** Insbesondere `v0.4.0` vor `v0.5.0`: ohne
Settings-Framework wird jede Einstellungsseite Handarbeit.

**Ein Abschnitt gilt als fertig**, wenn alle Abnahmekriterien seiner Datei
erfüllt sind — nicht wenn der Code „läuft".

**Patch-Tags haben keine eigene Datei.** `v0.3.1` ist ein Fix innerhalb des
`v0.3.0`-Abschnitts.

**Jeder Abschnitt wird in Issues zerlegt**, bevor Code entsteht. Die Datei ist
die Vorlage dafür, nicht der Ersatz.

## Aufbau der Dateien

Alle folgen demselben Schema:

- **Ziel** — was danach möglich ist, in einem Satz
- **Voraussetzungen** — was vorher stehen muss
- **Umfang** — die zu erstellenden Artefakte
- **Abnahmekriterien** — überprüfbar, nicht „funktioniert"
- **Nicht in diesem Abschnitt** — die Scope-Grenze, explizit
- **Fußangeln** — bekannte Stolperstellen
- **Referenzen**

## Referenzen

- `ARCHITECTURE.md` — Struktur und harte Regeln
- `docs/branching.md` — Tagging und Release-Ablauf
- `docs/security-baseline.md` — Sicherheitsanspruch
- `AGENTS.md` — Vorgaben für Agentenarbeit
