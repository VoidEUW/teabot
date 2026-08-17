<div align="center">

# 🍵 TeaBot

**Selbstgehostete Management-Plattform für einen Discord-Bot.**

Ein Bot und ein Dashboard. Ein Prozess. Eine Datei als Datenbank.

[![CI](https://github.com/VoidEUW/teabot/actions/workflows/ci.yml/badge.svg)](https://github.com/VoidEUW/teabot/actions/workflows/ci.yml)
[![CodeQL](https://github.com/VoidEUW/teabot/actions/workflows/codeql.yml/badge.svg)](https://github.com/VoidEUW/teabot/actions/workflows/codeql.yml)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)

[Architektur](ARCHITECTURE.md) · [Sicherheit](SECURITY.md) · [Roadmap](docs/exec/v1.0/README.md) · [Beitragen](docs/branching.md)

</div>

---

> **Status: in Entwicklung.** Das Projekt befindet sich vor `v1.0.0`;
> Schnittstellen und Datenmodell können sich ändern. Der aktuelle Fortschritt
> steht in der [Roadmap](docs/exec/v1.0/README.md).

## Worum es geht

Die meisten Discord-Bots mit Weboberfläche bestehen aus mehreren Diensten:
Bot, API, Frontend, Datenbank, Cache. Für einen kleinen privaten Server ist
das mehr Infrastruktur als Anwendung.

TeaBot geht den anderen Weg. Bot und Dashboard laufen **im selben Prozess und
Event Loop** — dadurch entfällt die interne API zwischen beiden vollständig.
Ein Slash-Command und ein Klick im Dashboard rufen dieselbe Python-Funktion
auf. Die Datenbank ist eine SQLite-Datei, das Frontend braucht keinen
Build-Schritt, das Deployment ist ein `docker compose up`.

Das ist eine bewusste Entscheidung gegen Skalierbarkeit und für
Verständlichkeit. Die Begründung samt Alternativen steht in
[ADR 0001](docs/adr/).

## Geplanter Funktionsumfang für v1.0

| Bereich | Inhalt |
|---|---|
| 🔐 **Authentifizierung** | Login über Discord OAuth, serverseitige Sessions |
| 👥 **Rollen** | Eigenes Rollenmodell, abgeleitet aus Discord-Rollen |
| 📊 **Live-Logging** | Terminal im Browser über Server-Sent Events |
| 🤖 **Bot-Steuerung** | Start, Stop, Restart, Statusanzeige im Dashboard |
| 🎫 **Tickets** | Support-Tickets per Command und per Dashboard |
| ⚠️ **Verstöße** | Verwarnungen, Timeouts, Historie |
| 📢 **Ankündigungen** | Verfassen, senden, nachträglich bearbeiten |
| 📅 **Events** | Serverereignisse mit Teilnehmerliste |
| 💬 **Zitate** | Sammeln und abrufen |
| 🛠️ **Developer-Mode** | Debug-Ansichten und Diagnosefelder |

Jedes Feature ist ein eigenständiges Modul und lässt sich pro Server
deaktivieren.

## Technik

```
discord.py  ·  FastAPI  ·  SQLAlchemy 2.0 (async)  ·  Alembic
SQLite (WAL)  ·  Jinja2  ·  Alpine.js  ·  uv  ·  Docker
```

Kein Node, kein Bundler, kein Redis, kein separater Message Broker.

## Architektur in einem Bild

```
┌──────────────────── uvicorn · asyncio event loop ────────────────────┐
│                                                                       │
│   FastAPI ─────────┐                          ┌───────── discord.py   │
│   HTML-Routen      │                          │          Cogs         │
│                    ▼                          ▼                       │
│              ┌──────────────────────────────────────┐                │
│              │      Service Layer · Vertical Slices  │                │
│              └──────────────────────────────────────┘                │
│                              │                                        │
│                     ┌────────▼────────┐                              │
│                     │  SQLAlchemy · DB │                              │
│                     └─────────────────┘                              │
└───────────────────────────────────────────────────────────────────────┘
```

Die zentrale Regel: **Cog und Router rufen sich niemals gegenseitig auf —
beide gehen durch den Service.** Jedes Feature ist ein Vertical Slice, der
Modell, Logik und alle Einstiegspunkte in einem Ordner bündelt.

Mehr dazu in [ARCHITECTURE.md](ARCHITECTURE.md).

## Schnellstart

**Voraussetzungen:** Python 3.12+, [uv](https://docs.astral.sh/uv/), Docker
(optional), eine Discord-Anwendung mit Bot-Token.

```bash
git clone https://github.com/VoidEUW/teabot.git
cd teabot

cp .env.example .env
# .env öffnen und Discord-Token sowie OAuth-Daten eintragen

uv sync
uv run alembic upgrade head
uv run teabot
```

Dashboard unter `http://localhost:8000`.

### Mit Docker

```bash
cp .env.example .env
docker compose up --build
```

## Entwicklung

```bash
uv sync --all-extras          # inkl. Entwicklungsabhängigkeiten
uv run ruff check --fix .     # Lint
uv run ruff format .          # Format
uv run mypy src               # Typecheck
uv run pytest                 # Tests
```

Komponenten lassen sich unter `/design` in allen Zuständen ansehen — eine
Harness ohne Datenbankabhängigkeit, vergleichbar mit Storybook, aber in Jinja.

## Projektstruktur

```
src/teabot/
├── app/         Composition Root — hier wird alles zusammengesteckt
├── core/        Registry, Events, Security, Settings, Permissions
├── db/          Engine, Session, Base, Mixins
├── bot/         Discord-Client, Lifecycle, Gateway
├── web/         Layout, Dependencies, Static, Design-Harness
└── modules/     Vertical Slices — ein Ordner je Feature
```

Jeder Bereich hat eine eigene `README.md` mit Zuständigkeit, harten Regeln und
Anti-Patterns.

## Dokumentation

| Dokument | Inhalt |
|---|---|
| [ARCHITECTURE.md](ARCHITECTURE.md) | Aufbau, Schichten, harte Regeln |
| [AGENTS.md](AGENTS.md) | Vorgaben für KI-gestützte Entwicklung |
| [SECURITY.md](SECURITY.md) | Meldeweg für Sicherheitslücken |
| [docs/security-baseline.md](docs/security-baseline.md) | Sicherheitsanspruch nach OWASP ASVS |
| [docs/branching.md](docs/branching.md) | Branching, Releases, Tagging |
| [docs/exec/v1.0/](docs/exec/v1.0/README.md) | Ausführungsplan bis v1.0 |
| [docs/deployment/runner.md](docs/deployment/runner.md) | Self-hosted Runner einrichten |
| [docs/adr/](docs/adr/) | Architekturentscheidungen |

## Sicherheit

Das Projekt orientiert sich an **OWASP ASVS Level 1**, mit gezielten
Level-2-Anforderungen für Sessions, Zugriffskontrolle, Logging und den Umgang
mit Geheimnissen. Details in
[docs/security-baseline.md](docs/security-baseline.md).

Sicherheitslücken bitte **nicht** als öffentliches Issue melden — der Weg
steht in [SECURITY.md](SECURITY.md).

## Beitragen

Pull Requests sind willkommen. Vor dem ersten Beitrag lohnt ein Blick in
[ARCHITECTURE.md](ARCHITECTURE.md) und [docs/branching.md](docs/branching.md) —
die Schichtenregeln sind strikt und werden im Review geprüft.

Für Fehler und Vorschläge gibt es
[Issue-Vorlagen](.github/ISSUE_TEMPLATE/).

## Lizenz

Siehe [LICENSE](LICENSE).

---

<div align="center">
<sub>Gebaut für einen kleinen Server, auf dem alles nachvollziehbar bleiben soll.</sub>
</div>
