# Architecture

Dieses Dokument beschreibt, **wie TeaBot aufgebaut ist und warum**. Es ist die
verbindliche Referenz für alle Beiträge — menschlich wie maschinell. Wenn Code
und dieses Dokument sich widersprechen, ist eines von beidem ein Bug.

Konkrete Einzelentscheidungen mit Begründung und Alternativen liegen als ADRs
unter `docs/adr/`.

---

## 1. Überblick

TeaBot ist eine selbstgehostete Management-Plattform für einen Discord-Bot auf
einem privaten Server. Sie besteht aus einem Discord-Client und einer
Web-Oberfläche, die sich **einen Prozess, einen Event Loop und eine Datenbank
teilen**.

Leitprinzipien:

1. **Kompaktheit vor Skalierbarkeit.** Zielgröße ist ein kleiner Server. Wir
   optimieren für Verständlichkeit und Deploybarkeit, nicht für Durchsatz.
2. **Etablierte Bausteine statt Eigenbau.** Wo ein gepflegtes Framework die
   Aufgabe löst, nehmen wir das Framework.
3. **Eine Wahrheit pro Regel.** Jede Geschäftsregel existiert genau einmal im
   Code, unabhängig davon, über wie viele Wege sie ausgelöst werden kann.
4. **Löschbarkeit.** Ein Feature muss sich entfernen lassen, indem man einen
   Ordner löscht.

---

## 2. Tech Stack

| Bereich       | Wahl                                | Begründung |
|---------------|-------------------------------------|------------|
| Bot           | `discord.py`                        | Referenzbibliothek, async, aktiv gepflegt |
| Web-Framework | FastAPI                             | ASGI, Dependency Injection, Pydantic-Integration |
| Server        | Uvicorn                             | Standard-ASGI-Server, hostet Web und Bot im selben Loop |
| Templates     | Jinja2                              | Serverseitiges HTML, keine Build-Pipeline |
| Interaktivität| Alpine.js                           | Progressive Enhancement ohne Bundler |
| ORM           | SQLAlchemy 2.0 (async) + `aiosqlite`| Typisiert, Migrationsökosystem |
| Migrationen   | Alembic                             | Ab der ersten Tabelle, keine Ausnahmen |
| Datenbank     | SQLite (WAL)                        | Ein Writer, kleine Last, triviales Backup |
| Config        | pydantic-settings                   | Validierung beim Start, nicht beim ersten Zugriff |
| Paketmanager  | uv                                  | Schnell, Lockfile, reproduzierbare Builds |
| Deployment    | Docker + Compose, Actions-Runner    | Self-hosted auf „Tiger" |

**Kein React, kein SvelteKit, keine separate SPA.** Das Frontend wird
serverseitig gerendert; Alpine übernimmt lokale Interaktivität.

---

## 3. Prozess-Topologie

### Entscheidung: ein Prozess (In-Process)

Bot und Web laufen im selben Python-Prozess. Der Bot ist ein supervisierter
`asyncio.Task`, der vom Lifespan der FastAPI-Anwendung gestartet und beendet
wird.

```
┌─────────────────────── uvicorn / asyncio loop ───────────────────────┐
│                                                                       │
│   FastAPI App ────┐                            ┌──── discord.Client   │
│   (HTML-Routen)   │                            │     (Cogs)           │
│                   ▼                            ▼                      │
│              ┌─────────────────────────────────────┐                 │
│              │        Service Layer (Slices)        │                 │
│              └─────────────────────────────────────┘                 │
│                              │                                        │
│                    ┌─────────▼─────────┐                             │
│                    │  SQLAlchemy / DB   │                             │
│                    └───────────────────┘                             │
└───────────────────────────────────────────────────────────────────────┘
```

**Konsequenzen — positiv**

- Keine interne REST-API, kein Bot-Token-Auth, keine Serialisierung zwischen
  Bot und Backend.
- Ein einziger SQLite-Writer. Kein Locking-Design nötig.
- Bot-Lifecycle (Start/Stop/Restart) ist Task-Verwaltung, kein Prozess-Handling.

**Konsequenzen — negativ**

- Keine parallelen Clients auf unterschiedlichen `discord.py`-Versionen.
- Ein Deploy startet alles neu.
- Ein blockierender Aufruf blockiert Bot **und** Web. Synchrone I/O ist
  deshalb verboten (siehe §5).

**Ausstiegspfad.** Der gesamte Nicht-Bot-Code spricht ausschließlich über das
`BotGateway`-Protokoll mit Discord (§7.6). Ein Wechsel auf Subprozesse
erfordert eine neue Gateway-Implementierung — nicht mehr.

Details: `docs/20260813_ARCHITECTURE.md`

---

## 4. Schichten

Vier Schichten, Abhängigkeiten fließen ausschließlich nach unten:

```
Adapter      cog.py · router.py          kennen Discord bzw. HTTP
   │
Service      service.py                   kennt weder Discord noch HTTP
   │
Modell       models.py · schemas.py       Daten und Validierung
   │
Infra        db · config · core           Engine, Session, Registry, Security
```

### Die zentrale Regel

> **Cog und Router rufen sich niemals gegenseitig auf. Beide gehen durch den
> Service.**

Ein Service:

- bekommt eine DB-Session und einfache Werte oder Pydantic-Modelle herein,
- gibt Domain-Objekte oder Pydantic-Modelle zurück,
- importiert **nie** `discord`, `fastapi` oder `starlette`,
- wirft Domain-Exceptions (`TicketNotOpen`), keine `HTTPException`.

Adapter sind dünn: Auth prüfen, Eingabe validieren, Service rufen, Antwort
formen. Enthält ein Adapter eine `if`-Verzweigung über Domänenzustand, gehört
sie in den Service.

### Warum Routen trotzdem existieren

Die HTTP-Routen sind **Frontend-Endpunkte, keine System-API**. Sie liefern
HTML — ganze Seiten oder Fragmente für Alpine. JSON gibt es nur dort, wo der
Browser Daten statt Markup braucht (Statuspolling, Log-Stream). Wir bauen
keine REST-API für einen Konsumenten, der im selben Prozess lebt.

---

## 5. Harte Regeln

Diese Punkte sind nicht verhandelbar und werden im Review geprüft:

1. **Keine synchrone I/O im Request- oder Event-Pfad.** Kein `requests`, kein
   `time.sleep`, kein blockierender Dateizugriff. Rechenintensives gehört in
   `asyncio.to_thread`.
2. **Kein Modul importiert ein anderes Modul.** Kommunikation läuft über den
   Event Bus (§7.5) oder über explizit deklarierte Abhängigkeiten in `MODULE`.
3. **Jede persistierte Tabelle hat `guild_id`.** Auch wenn aktuell nur eine
   Guild betrieben wird.
4. **Kein Schemawechsel ohne Alembic-Migration.**
5. **Keine Berechtigungslogik in Templates.** Templates fragen ein
   vorberechnetes Flag ab, sie entscheiden nicht.
6. **Keine Secrets im Repo.** Nur `.env.example` wird versioniert.
7. **Keine rohen Discord-IDs als Strings.** IDs sind `int` (Snowflakes), in der
   DB `BigInteger`.

---

## 6. Modulstruktur (Vertical Slices)

Ein Feature ist ein Ordner unter `src/teabot/modules/` mit stets derselben
inneren Form:

```
modules/tickets/
├── __init__.py      MODULE-Deskriptor (Name, Icon, Prefix, Abhängigkeiten)
├── models.py        SQLAlchemy-Modelle
├── schemas.py       Pydantic: Ein- und Ausgabe
├── service.py       Domänenlogik, framework-agnostisch
├── router.py        FastAPI-Routen (HTML/Fragmente)
├── cog.py           discord.py Commands und Listener
├── settings.py      Settings-Schema des Moduls
├── permissions.py   Actions, die dieses Modul definiert
└── templates/       Jinja-Partials des Moduls
```

Nicht jedes Modul braucht jede Datei. Fehlende Dateien werden von der Registry
ignoriert.

### Warum diese Form

Ein Ticket kann durch einen Slash-Command, einen Klick im Web oder künftig
einen Scheduler entstehen. Das sind drei Adapter auf **eine** Logik. Der Slice
hält sie zusammen und macht sichtbar, dass sie dieselbe Tür benutzen.

---

## 7. Querschnittsthemen

### 7.1 Registry

`core/registry.py` scannt beim Start `teabot.modules`, importiert jedes
Untermodul und sammelt ein, was vorhanden ist: `MODULE`, `router`, `Cog`,
`SETTINGS`, `PERMISSIONS`. Es gibt **keine** manuell gepflegte Liste.

Reihenfolge:

- Router werden einmalig beim Bau der App eingehängt.
- Cogs werden bei **jedem** Client-Aufbau neu geladen (Restart erzeugt eine
  neue Client-Instanz).
- Settings- und Permission-Schemata werden einmalig registriert.

Aus `MODULE` baut sich die Admin-Navigation automatisch.

### 7.2 Settings-Framework

Generischer Store: `(guild_id, module, key) -> value`. Jedes Modul deklariert
sein Schema (Typ, Default, Label, Hilfetext, Sichtbarkeit, `dev_only`).

Das Admin-UI rendert Einstellungsseiten aus dem Schema — keine handgeschriebene
Settings-Seite pro Feature. Zugriff im Code über einen typisierten Accessor mit
Cache, Invalidierung bei Schreibzugriff.

**Dieses Framework muss vor dem ersten fachlichen Modul stehen.**

### 7.3 Permissions

Schmales RBAC statt Discord-Rollen-Prüfung an Ort und Stelle.

- App-Rollen: `owner`, `admin`, `moderator`, `member`
- Ableitung aus einem Mapping Discord-Rolle → App-Rolle, plus explizite
  User-Overrides
- Alle Actions sind in einem zentralen Enum gesammelt, gespeist aus den
  `permissions.py` der Module (`tickets.create`, `tickets.close`, …)
- **Eine** Prüffunktion `can(user, guild, action) -> bool`

Web nutzt sie über eine FastAPI-Dependency `require(action)`, der Bot über
einen Cog-Check. Zwei Aufrufer, eine Implementierung.

### 7.4 Logging

Hierarchischer Logger-Baum nach `__name__` (`teabot.core`,
`teabot.modules.tickets`). Der `discord`-Logger wird auf `WARNING` gedeckelt.

Drei Senken:

1. **stdout** — Docker-Logs, strukturiert in Produktion
2. **Datenbank** — nur fachlich relevante Einträge, mit Retention-Policy
3. **Log-Bus** — In-Memory-Ringpuffer plus `asyncio.Queue` je verbundenem
   Client, ausgeliefert per **Server-Sent Events**

SSE, nicht WebSocket: der Logstream ist unidirektional, `EventSource`
reconnected von selbst, und wir sparen den gesamten WS-Lifecycle.

Guild-lose Systemlogs erscheinen nicht im Guild-Dashboard.

### 7.5 Event Bus

Minimaler In-Process-Pub/Sub: `publish(event)` und Decorator-Subscription.
Zweck ist ausschließlich Entkopplung — `violations` soll `logging` nicht
importieren müssen. Kein Broker, keine Persistenz, keine Zustellgarantie.
Handler-Fehler werden geloggt und schlucken nicht den Publisher.

### 7.6 BotGateway

Das einzige Tor vom Nicht-Bot-Code zu Discord:

```python
class BotGateway(Protocol):
    async def send_message(self, channel_id: int, content: str) -> int: ...
    async def edit_message(self, channel_id: int, message_id: int, content: str) -> None: ...
    async def close_channel(self, channel_id: int) -> None: ...
    async def is_ready(self) -> bool: ...
```

Die In-Process-Implementierung hält eine Referenz auf den laufenden Client. Ist
der Bot offline, wirft sie `BotUnavailable`; die Web-Schicht zeigt das als
Fehler an. Eine Outbox mit späterer Zustellung ist bewusst v1.1.

### 7.7 Client-Lifecycle

`bot/manager.py` kapselt den Lebenszyklus:

- `start()`, `stop()`, `restart()`, `status()`
- ein `asyncio.Lock` verhindert Doppelstarts durch schnelle UI-Klicks
- ein Done-Callback fängt Task-Exceptions ab, loggt sie und setzt den Status
  auf `crashed` — ein stiller Tod ist der häufigste Fehler bei diesem Muster
- `restart()` bedeutet: Task canceln, `close()` awaiten, **neue** Client-Instanz
  über die Factory bauen, Cogs neu laden. Ein geschlossener `discord.Client`
  ist nicht wiederverwendbar.

Shutdown-Reihenfolge: erst Bot schließen, dann DB-Engine disposen.

---

## 8. Datenhaltung

- SQLite im WAL-Modus, Volume unter `data/`
- Beim Connect gesetzt: `journal_mode=WAL`, `busy_timeout`, `foreign_keys=ON`,
  `synchronous=NORMAL`
- Alle Modelle erben von einer `Base` mit `id`, `created_at`, `updated_at`
- Schreibzugriffe laufen über `session_scope()` — ein Kontextmanager, der
  committet oder zurückrollt; kein manuelles `commit()` in Services verstreut
- Backup: `VACUUM INTO` per Cron; Litestream als Option für kontinuierliche
  Replikation

---

## 9. Verzeichnisstruktur

```
teabot/
├── ARCHITECTURE.md
├── AGENTS.md
├── pyproject.toml
├── Dockerfile
├── compose.yaml
├── alembic/
├── data/                       Volume: teabot.db, Uploads
├── docs/adr/
├── tests/
└── src/teabot/
    ├── main.py                 Composition Root
    ├── config.py
    ├── db/                     engine, session, Base, Mixins
    ├── core/
    │   ├── registry.py
    │   ├── events.py
    │   ├── security.py
    │   ├── logbus.py
    │   └── gateway.py
    ├── bot/
    │   ├── client.py           Factory
    │   ├── manager.py
    │   └── base.py             BaseCog
    ├── web/
    │   ├── app.py
    │   ├── deps.py
    │   ├── templates/
    │   └── static/
    └── modules/
```

---

## 10. Startsequenz

`main.py` ist die einzige Datei, die alles kennt:

1. Config laden und validieren — fehlende Pflichtwerte brechen sofort ab
2. Logging konfigurieren, Log-Bus-Handler anhängen
3. DB-Engine bauen, PRAGMAs setzen, Alembic-Head prüfen
4. Registry ausführen
5. FastAPI-App bauen, Router einhängen
6. Client-Factory und Gateway bereitstellen
7. ClientManager erzeugen, in den App-State legen
8. Uvicorn starten; Lifespan startet den Bot (falls Autostart aktiv)

---

## 11. Roadmap

| Phase | Inhalt | Ergebnis |
|-------|--------|----------|
| 0 | Skelett, Config, DB + Alembic, Registry, Docker, CI | Deploybares Nichts |
| 1 | Client, Manager, Logging + SSE-Terminal | Bot läuft und ist sichtbar |
| 2 | Discord OAuth, Sessions, Permissions, Dev-Mode | Zugang |
| 3 | Guild-Sync, Settings-Framework, Admin-Shell | Gerüst |
| 4 | Tickets als Referenzmodul | Muster validiert |
| 5 | Violations, Announcements, Events, Citations | Breite |
| 6 | Backup, Dokumentation, Härtung | Release v1.0 |

Phase 3 steht vor Phase 4. Ohne Settings-Framework wird jede Einstellungsseite
Handarbeit.

**Bewusst nicht in v1.0:** LLM-gestützte Bot-Antworten. Provider-Abstraktion,
Kosten-Guard, Rate Limits und Prompt-Verwaltung sind ein eigenes Vorhaben, kein
Nebenfeature.
