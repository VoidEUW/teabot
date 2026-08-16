# `tests/` — Teststrategie

## Zuständigkeit

Alle automatisierten Tests. Die Ebenen sind hier definiert, auch wenn viele
davon erst mit den Feature-Modulen entstehen.

## Ebenen

| Ebene | Testet | Braucht |
|---|---|---|
| **Unit** | Services, reine Funktionen | nichts — kein Discord, kein HTTP |
| **Integration** | Router gegen die App, Migrationen, Permissions | In-Memory-DB, `httpx.AsyncClient` |
| **End-to-End** | vollständiger Start, Health, Registry | den gebauten Prozess |

Schwerpunkt liegt auf Unit- und Integrationstests. E2E bleibt dünn: ein Start
ohne Fehler, `/health` antwortet, Registry findet alle Module.

## Der Lackmustest

> **Braucht ein Service-Test einen Discord-Mock oder einen HTTP-Client, ist die
> Schichtung verletzt.**

Das ist kein Teststil, sondern eine Architekturprüfung. Services sind
framework-agnostisch; lässt sich das nicht testen, stimmt etwas nicht.

## Verbindlich

1. **Jede Bugfix-PR bringt einen Regressionstest.** Ohne Ausnahme.
2. **Negative Tests für Zugriffskontrolle sind Pflicht**, sobald das
   Permission-Modell steht:
   - Nutzer ohne Berechtigung erhält 403
   - Zugriff auf ein Objekt einer **fremden Guild** scheitert, auch bei
     korrekter ID
   - Route ohne Auth-Dependency wird erkannt (Deny by default)
3. **Migrationen laufen im Test von leer bis `head` durch.**
4. **Keine Secrets in Fixtures**, auch keine erfundenen, die echten Tokens
   ähneln.
5. **Tests sind unabhängig und in beliebiger Reihenfolge lauffähig.**

Punkt 2 stammt aus `docs/security-baseline.md` und ist kein Feature-Test,
sondern eine Sicherheitsanforderung.

## Aufbau

```
tests/
├── conftest.py          gemeinsame Fixtures: Engine, Session, App-Client
├── unit/
│   └── modules/<name>/  Service-Tests je Modul
├── integration/
│   ├── modules/<name>/  Router- und Permission-Tests
│   └── test_migrations.py
└── e2e/
```

Fixtures: In-Memory-SQLite pro Test, PRAGMAs wie in Produktion (besonders
`foreign_keys=ON` — sonst laufen Tests durch, die produktiv scheitern).

## Anti-Patterns

- **Service-Tests mit Discord-Mocks.** Siehe Lackmustest.
- **Discord selbst testen.** `discord.py` ist getestet; getestet wird das
  eigene Parsing.
- **Tests gegen die Produktionsdatenbank.**
- **Nur der Erfolgsfall.** Gerade bei Berechtigungen ist der Fehlerfall der
  eigentliche Test.
- **Zeitabhängige Tests ohne fixierte Zeit.** `freezegun` oder injizierte
  Zeitquelle.
- **Abdeckungsquote als Ziel.** Ein Test, der nichts belegt, aber Zeilen
  abdeckt, verschleiert die Lücke.

## Befehle

```bash
uv run pytest
uv run pytest -k tickets
uv run pytest tests/unit
uv run pytest --cov=teabot --cov-report=term-missing
```

## Offen

Konkrete Testfälle entstehen mit den Modulen. Festgelegt sind bereits die
Ebenen, die Pflicht zu negativen Berechtigungstests und die Regel zum
Regressionstest.

## Referenzen

- `AGENTS.md` — Testerwartungen bei Agentenarbeit
- `docs/security-baseline.md` — Anforderungen an Zugriffskontrolle
