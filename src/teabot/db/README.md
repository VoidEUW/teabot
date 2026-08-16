# `db/` — Persistenzschicht

## Zuständigkeit

Engine, Session-Verwaltung, `Base` samt Mixins und die SQLite-spezifische
Konfiguration. Kein einziges fachliches Modell — die leben in den Modulen.

## Bestandteile

| Datei | Aufgabe |
|---|---|
| `engine.py` | Async-Engine, PRAGMA-Hook beim Connect |
| `session.py` | `session_scope()`, FastAPI-Dependency `get_db` |
| `base.py` | Declarative Base, Naming Convention für Constraints |
| `mixins.py` | `id`, `created_at`, `updated_at`, `GuildScopedMixin` |

## SQLite-Konfiguration

Bei jedem Connect gesetzt:

| PRAGMA | Wert | Grund |
|---|---|---|
| `journal_mode` | `WAL` | Leser blockieren den Writer nicht |
| `foreign_keys` | `ON` | SQLite prüft sonst **keine** Fremdschlüssel |
| `busy_timeout` | 5000 ms | wartet statt sofort „database is locked" |
| `synchronous` | `NORMAL` | mit WAL ausreichend, deutlich schneller |

`foreign_keys=ON` ist kein Detail: ohne dieses PRAGMA akzeptiert SQLite
verwaiste Referenzen stillschweigend.

## Was hier nicht hineingehört

- **Fachliche Modelle.** `models.py` liegt im jeweiligen Modul.
- **Queries.** Abfragen leben in den Services.
- **Migrationen.** Die liegen in `alembic/`.

## Harte Regeln

1. **Schreibzugriffe laufen über `session_scope()`.** Der Kontextmanager
   committet oder rollt zurück — kein verstreutes `commit()` in Services.
2. **Kein Schemawechsel ohne Alembic-Migration im selben Commit.** CI prüft das
   mit `alembic check`.
3. **Discord-Snowflakes sind `BigInteger`.** Sie überschreiten 32 Bit; `Integer`
   führt zu stillen Fehlern.
4. **Jede persistierte Tabelle hat `guild_id`** — auch bei aktuell einer Guild.
   Nachrüsten ist teuer.
5. **Eine Naming Convention für Constraints** in der `Base`. Ohne sie erzeugt
   Alembic bei SQLite unbenannte Constraints, die sich später nicht ändern
   lassen.
6. **Nur `aiosqlite`.** Ein synchroner Treiber blockiert Bot und Web zugleich.

## Anti-Patterns

- **Langlebige Session über mehrere Anfragen.** Sessions sind kurzlebig, eine
  pro Anfrage oder pro Bot-Event.
- **Session an einen Service **außerhalb** von `session_scope()` reichen** und
  dort committen. Die Transaktionsgrenze gehört dem Aufrufer.
- **Lazy Loading nach Verlassen des Scopes.** Async-SQLAlchemy wirft dort;
  Beziehungen explizit mit `selectinload` laden.
- **`ALTER TABLE`-Erwartungen wie bei PostgreSQL.** SQLite kann kaum Spalten
  ändern; Alembic baut Tabellen neu. Migrationen entsprechend prüfen.
- **Backup per `cp` bei laufendem Betrieb.** Ergibt möglicherweise eine
  beschädigte Datei. Richtig ist `VACUUM INTO`.

## Referenzen

- `ARCHITECTURE.md` §8 Datenhaltung
- `docs/deployment/runner.md` — Backup im Deploy-Ablauf
