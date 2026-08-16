# `modules/` — Vertical Slices

## Zuständigkeit

Jedes Feature von TeaBot ist ein Ordner hier. Ein Modul enthält **alle**
Einstiegspunkte in seine Domäne — Discord, Web, Automatik — plus Modell,
Logik, Berechtigungen, Einstellungen und Templates.

Das ist der wichtigste Vertrag im Projekt. Wer ein neues Modul anlegt, liest
diese Datei zuerst.

## Aufbau

```
modules/tickets/
├── __init__.py      MODULE-Deskriptor
├── models.py        SQLAlchemy-Modelle
├── schemas.py       Pydantic: Ein- und Ausgabe
├── service.py       Domänenlogik, framework-agnostisch
├── router.py        FastAPI-Routen (HTML/Fragmente)
├── cog.py           discord.py Commands und Listener
├── settings.py      Settings-Schema
├── permissions.py   Actions dieses Moduls
└── templates/       Jinja-Partials
```

Nicht jedes Modul braucht jede Datei. Fehlende Dateien ignoriert die Registry.

## Die zentrale Regel

> **`cog.py` und `router.py` rufen sich niemals gegenseitig auf. Beide gehen
> durch `service.py`.**

Ein Ticket kann per Slash-Command, per Klick im Web oder künftig per Scheduler
entstehen. Das sind drei Adapter auf **eine** Implementierung. Wer Logik in
einem Adapter unterbringt, dupliziert sie beim nächsten Einstiegspunkt — und
fixt Bugs künftig nur an einer der beiden Stellen.

## Schichten im Modul

| Datei | darf importieren | darf **nicht** |
|---|---|---|
| `service.py` | `db`, `core`, eigene `models`/`schemas` | `discord`, `fastapi`, `starlette` |
| `router.py` | `fastapi`, eigener Service, `web.deps` | `discord`, fremde Module |
| `cog.py` | `discord`, eigener Service, `bot.base` | `fastapi`, fremde Module |
| `models.py` | `db`, SQLAlchemy | alles Fachfremde |

## Harte Regeln

1. **Kein Modul importiert ein anderes Modul.** Kommunikation über den Event
   Bus oder über eine in `MODULE` deklarierte Abhängigkeit.
2. **Services werfen Domain-Exceptions**, keine `HTTPException`. Die
   Übersetzung in HTTP-Status oder Discord-Antwort ist Aufgabe des Adapters.
3. **Jede Tabelle hat `guild_id`**; jede Abfrage filtert danach.
4. **Berechtigungen laufen über `can()`** beziehungsweise die
   `require()`-Dependency — niemals über direkte Rollenabfragen.
5. **Einstellungen werden deklariert, nicht gebaut.** Ein Schema in
   `settings.py` genügt; das Admin-UI entsteht daraus.
6. **Modelländerung und Migration im selben Commit.**
7. **Keine synchrone I/O.** Bot und Web teilen einen Event Loop.

## Reihenfolge beim Anlegen

1. `models.py` schreiben, Migration erzeugen, `alembic upgrade head` prüfen
2. `service.py` mit Tests — **vor** jedem Adapter
3. `permissions.py` und `settings.py` deklarieren
4. `router.py` und/oder `cog.py` als dünne Adapter
5. Templates

Die Registrierung passiert automatisch. Es gibt keine zentrale Liste, in die
etwas eingetragen wird.

## Anti-Patterns

- **Logik im Cog.** Fühlt sich beim Schreiben natürlich an und ist der
  häufigste Verstoß in diesem Projekt.
- **`from teabot.modules.tickets import ...` in einem anderen Modul.** Bricht
  den Bounded Context. Wird ein gemeinsamer Begriff gebraucht, gehört er nach
  `core/` oder die Abhängigkeit wird explizit deklariert.
- **`discord` im Service importieren**, um „nur schnell" eine Nachricht zu
  senden. Dafür existiert das `BotGateway`.
- **Berechtigungslogik im Template.** Templates fragen vorberechnete Flags ab.
- **Ein Modul, das alles kann.** Wächst ein Slice über seine Domäne hinaus,
  wird geteilt.
- **Fremde Tabellen mitlesen**, statt über den Event Bus zu kommunizieren.

## Referenzen

- `ARCHITECTURE.md` §4 Schichten, §5 harte Regeln, §6 Modulstruktur
- `.github/ISSUE_TEMPLATE/module_proposal.yml` — Briefing-Vorlage für ein neues
  Modul
- `AGENTS.md` — Vorgaben für Agentenarbeit
