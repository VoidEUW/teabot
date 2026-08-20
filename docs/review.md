# Code Review — Leitfaden

Wie ein PR in diesem Projekt gelesen wird, insbesondere maschinell erzeugter
Code.

---

## Arbeitsteilung

| Prüft die Maschine | Prüfst nur du |
|---|---|
| Typen, Stil, Formatierung | Ob die Invariante die **richtige** ist |
| Schichten (`lint-imports`) | Ob das Datenmodell die Domäne trifft |
| Migrationen laufen durch | Ob die Tests etwas Sinnvolles behaupten |
| Tests sind grün | Ob ein Fall vergessen wurde |
| Bekannte Sicherheitsmuster (CodeQL) | Ob die Lösung angemessen ist |

Alles links sollte automatisiert sein, damit deine Aufmerksamkeit für die
rechte Spalte frei bleibt. Sie ist nicht delegierbar.

---

## Lesereihenfolge

Einen Diff **nicht** von oben nach unten lesen wie eigenen Code. Diese
Reihenfolge findet Fehler schneller:

### 1. Dateiliste vor Inhalt

Stimmt die Form? Ohne eine Zeile Code zu lesen, sichtbar:

- Service geändert, aber keine Testdatei im Diff
- Migration ohne Modelländerung oder umgekehrt
- Datei an ungewöhnlicher Stelle — Template in `web/`, das ins Modul gehört
- Modul mit `router.py`, aber ohne `permissions.py`
- Verdächtig viele Dateien für die beschriebene Aufgabe

Das sind Struktur- und Scope-Fehler. Sie zu finden kostet zehn Sekunden.

### 2. Tests vor Implementierung

Zu jedem Test: **Welche Änderung am Code würde ihn rot machen?**

Fällt nichts ein, ist er wertlos. Häufig bei maschinell erzeugtem Code: Tests,
die prüfen, dass eine Funktion zurückgibt, was sie zurückgibt.

Zweite Frage: Steht hier der **negative** Fall? Ein Modul ohne Test für
fehlende Berechtigung ist unvollständig, egal wie gut der Rest ist.

### 3. Fehlerpfade, nicht Erfolgspfade

Der Erfolgspfad ist fast immer richtig. Interessant ist:

- fehlende Berechtigung
- leeres Ergebnis, `None`, leere Liste
- Bot offline (`BotUnavailable`)
- gleichzeitiger Zugriff
- Objekt gehört zu einer anderen Guild
- Zustandsübergang, der nicht erlaubt ist

### 4. Was fehlt

Die schwierigste Frage, aber die ergiebigste — und die, bei der du im Vorteil
bist: Du hast tagelang über die Domäne nachgedacht, der Agent kennt nur den
Prompt.

- fehlende Guard Clause
- nicht behandelter Zustand
- fehlender Eintrag in der Design-Harness
- Einstellung deklariert, aber nirgends gelesen
- `guild_id` im Modell, aber nicht in der Abfrage

### 5. Erklärbarkeit

Steht im Diff eine Zeile, die du nicht erklären kannst, wird sie nicht
gemergt. Nicht weil sie falsch wäre — sondern weil du sie in drei Monaten
debuggen musst.

Das gilt besonders für elegante Lösungen, die du nicht angefragt hast.

---

## Projektspezifische Prüfpunkte

Beim Lesen mitlaufen lassen:

- [ ] Steht Domänenlogik im Service statt im Adapter?
- [ ] Importiert der Service `discord` oder `fastapi`? (fängt `lint-imports`)
- [ ] Wird ein anderes Modul importiert? (fängt `lint-imports`)
- [ ] Hat jede neue Tabelle `guild_id`, und filtert jede Abfrage danach?
- [ ] Synchrone I/O im Request- oder Event-Pfad?
- [ ] `asyncio.create_task` ohne Done-Callback?
- [ ] Zeitstempel UTC und timezone-aware?
- [ ] Domain-Exception statt `HTTPException` im Service?
- [ ] Berechtigung serverseitig geprüft, nicht nur im Template?
- [ ] Migration im selben Commit wie die Modelländerung?
- [ ] `downgrade()` sinnvoll implementiert?
- [ ] Neue Komponente in der Design-Harness eingetragen?

---

## Umfang begrenzen

Ein Agent produziert mühelos 800 Zeilen. Die kann niemand prüfen — man kann sie
nur überfliegen, und Überfliegen ist keine Prüfung.

**Ein Slice-Bestandteil pro PR:**

1. Modell und Migration
2. Service und dessen Tests
3. Berechtigungen und Einstellungen
4. Router und Templates
5. Cog

Fünf kleine PRs schlagen einen großen. Der Aufwand für den PR-Rahmen ist
gering, der Unterschied in der Prüftiefe erheblich.

---

## Umgang mit CodeRabbit

CodeRabbit prüft sprachlich, also probabilistisch. Es findet Dinge, die kein
Linter findet — und irrt gelegentlich.

- Anmerkungen werden **abgearbeitet oder begründet abgelehnt**, nicht ignoriert
- Eine Ablehnung wird als Kommentar festgehalten; das ist die Dokumentation der
  Entscheidung
- Wiederholt dieselbe falsche Anmerkung: `path_instructions` in
  `.coderabbit.yaml` schärfen
- Findet CodeRabbit regelmäßig dieselbe echte Verletzung, gehört sie in einen
  deterministischen Check (`.importlinter`, Ruff-Regel)

Der letzte Punkt ist der wichtige: Jede Regel, die sich mechanisch prüfen
lässt, sollte nicht sprachlich geprüft werden.

---

## Wenn ein Agent-PR nicht überzeugt

Nicht in Nachbesserungsschleifen gehen. Zwei Runden ohne klare Verbesserung
bedeuten meist, dass das Briefing unvollständig war — nicht, dass der nächste
Anlauf gelingt.

Dann: Branch verwerfen, Issue präzisieren, neu beauftragen. Das kostet weniger
als ein PR, der halb passt und dessen Fremdheit man später nicht mehr
zuordnen kann.

---

## Referenzen

- `ARCHITECTURE.md` §4, §5
- `docs/testing.md` — Testqualität beurteilen
- `AGENTS.md` — was Agenten selbstständig dürfen
- `.github/PULL_REQUEST_TEMPLATE.md`
