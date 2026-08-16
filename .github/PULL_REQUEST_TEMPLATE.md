# Was und warum

<!-- Was ändert sich, und welches Problem löst es? Zwei bis vier Sätze. -->

Closes #

## Art der Änderung

- [ ] Feature
- [ ] Bugfix
- [ ] Refactoring
- [ ] Infrastruktur / CI
- [ ] Dokumentation

## Architektur-Checkliste

- [ ] Domänenlogik liegt im Service, nicht im Cog oder Router
- [ ] Service importiert weder `discord` noch `fastapi`/`starlette`
- [ ] Kein Import eines anderen Moduls
- [ ] Keine synchrone I/O im Request- oder Event-Pfad
- [ ] Neue Tabellen haben `guild_id`
- [ ] Schemaänderung hat eine Alembic-Migration im selben Commit
- [ ] Neue Berechtigungen sind in `permissions.py` deklariert
- [ ] Neue Einstellungen sind als Schema deklariert, keine handgebaute Seite
- [ ] Neue Config-Werte stehen in `config.py` **und** `.env.example`

## Qualität

- [ ] `ruff check` und `ruff format --check` grün
- [ ] `mypy src` grün
- [ ] `pytest` grün, neue Logik ist getestet
- [ ] Bei Bugfix: Regressionstest vorhanden

## Migration und Deployment

- [ ] Keine Migration nötig
- [ ] Migration ist rückwärtskompatibel
- [ ] Migration transformiert Bestandsdaten — Vorgehen unten beschrieben
- [ ] Manuelle Schritte beim Deploy nötig — unten beschrieben

<!-- Falls zutreffend, hier ausführen. -->

## Nachweis

<!-- Screenshot, Ausgabe oder kurze Beschreibung, wie du getestet hast. -->

## Offene Punkte

<!-- Bewusst nicht gelöst, Folgearbeit, Diskussionsbedarf. -->
