# Testen — Leitfaden

Ergänzt `tests/README.md`. Dort steht, *was* getestet wird; hier steht, *wie*
man dabei denkt.

---

## 1. Die Leitfrage

> **Welche Änderung am Produktivcode würde diesen Test rot machen?**

Fällt dir keine ein, ist der Test wertlos — unabhängig davon, wie sorgfältig er
aussieht. Das ist der schnellste Filter für fremden oder maschinell erzeugten
Testcode.

```python
# Wertlos: prüft, dass eine Zuweisung funktioniert
async def test_create_ticket(db):
    t = await ticket_service.create(db, guild_id=1, author_id=42, subject="Hilfe")
    assert t.subject == "Hilfe"

# Wertvoll: prüft eine Regel, die jemand entfernen könnte
async def test_close_by_stranger_is_rejected(db, ticket, stranger):
    with pytest.raises(PermissionDenied):
        await ticket_service.close(db, ticket.id, actor=stranger)
```

Der erste Test wird nur rot, wenn SQLAlchemy kaputtgeht. Der zweite wird rot,
sobald jemand eine Berechtigungsprüfung entfernt.

---

## 2. Was getestet wird

Nicht „jede Funktion". Ergiebig sind vier Kategorien:

### Invarianten

Sätze mit *nur wenn*, *niemals*, *höchstens*. Sie stehen bereits im
Modul-Issue unter „Service-Operationen". Jeder solche Satz ist ein Test — und
zwar der **negative**: nicht dass Erlaubtes funktioniert, sondern dass
Verbotenes scheitert.

### Grenzen

Null, eins, genau am Limit, eins darüber. Bei „höchstens 5 offene Tickets"
werden das fünfte und das sechste getestet, nicht das zweite.

### Zustandsübergänge

Eine kleine Matrix: welcher Übergang ist erlaubt, welcher nicht. Jede verbotene
Zelle ist ein Test.

| von \ nach | open | assigned | closed |
|---|---|---|---|
| open | — | ✓ | ✓ |
| assigned | ✓ | — | ✓ |
| closed | ✗ | ✗ | ✗ |

### Was schon einmal kaputt war

Daher die Regel, dass jede Bugfix-PR einen Regressionstest mitbringt.

---

## 3. Aufbau eines Tests

**Arrange – Act – Assert**, sichtbar getrennt. Eine Verhaltensweise pro Test.
Mehrere `assert` sind in Ordnung, solange sie **dieselbe** Aussage stützen.

Der Name beschreibt Situation und Erwartung, nicht die Funktion:

```
test_close_by_stranger_is_rejected          gut
test_sixth_open_ticket_is_rejected          gut
test_close                                  nichtssagend
test_close_2                                schlecht
```

Ein guter Name macht die Fehlermeldung selbsterklärend — bei einem roten Test
willst du nicht erst den Code lesen müssen.

---

## 4. Attrappen: so wenig wie möglich

Ein **Mock** prüft, dass eine Funktion aufgerufen wurde. Das fesselt den Test
an die Implementierung: beim nächsten Refactoring wird er rot, ohne dass ein
Fehler vorliegt.

Ein **Fake** ist eine kleine echte Implementierung. Damit prüfst du das
Ergebnis statt des Aufrufs.

```python
class FakeGateway:
    def __init__(self):
        self.sent: list[tuple[int, str]] = []

    async def send_message(self, channel_id: int, content: str) -> int:
        self.sent.append((channel_id, content))
        return len(self.sent)

    async def is_ready(self) -> bool:
        return True


async def test_announcement_reaches_configured_channel(db, gateway):
    await announcement_service.publish(db, guild_id=1, text="Wartung", gateway=gateway)
    assert gateway.sent == [(999, "Wartung")]
```

**Der Lackmustest:** Braucht ein Service-Test einen Discord-Mock oder einen
HTTP-Client, ist nicht der Test das Problem, sondern die Schichtung. Das ist
eine Architekturprüfung, kein Teststil.

---

## 5. Qualität der Tests messen

### Coverage richtig lesen

Coverage sagt, welche Zeilen ausgeführt wurden — nicht, ob jemand hinsah. Als
Zielgröße ist sie schädlich, als Suchhilfe nützlich:

```bash
uv run pytest --cov=teabot --cov-report=term-missing
```

Interessant ist die Spalte der **fehlenden Zeilen**. Sind das Fehlerpfade und
Guard Clauses, hast du die falsche Hälfte getestet.

### Mutation Testing

Der ehrliche Test der Tests. Ein Werkzeug verändert den Code minimal — `>` zu
`>=`, `and` zu `or`, ein `raise` entfernt — und prüft, ob ein Test rot wird.
Bleibt alles grün, hat die Mutation **überlebt**: dort ist eine Lücke.

```bash
uv run mutmut run --paths-to-mutate src/teabot/modules/tickets/service.py
uv run mutmut results
```

Zu langsam für CI. Richtig ist: einmal pro Modul nach Fertigstellung des
Service, als Selbstprüfung. Die erste Anwendung auf ein eigenes Modul ist die
lehrreichste Stunde im Umgang mit Tests.

### Property-based Testing

Für Regeln, die für *alle* Eingaben gelten sollen, ist `hypothesis` stärker als
Beispiele:

```python
@given(st.lists(st.text(min_size=1), min_size=1, max_size=20))
async def test_ticket_numbers_have_no_gaps(db, subjects):
    tickets = [await ticket_service.create(db, guild_id=1, author_id=1, subject=s)
               for s in subjects]
    assert [t.number for t in tickets] == list(range(1, len(subjects) + 1))
```

Hypothesis sucht selbst nach Gegenbeispielen und verkleinert sie auf den
kleinsten Fall. Lohnt sich bei Nummernvergabe, Zeitberechnungen, Parsing — nicht
bei gewöhnlicher CRUD-Logik.

---

## 6. Häufige Fehler

| Fehler | Warum problematisch |
|---|---|
| Nur der Erfolgsfall | Der Fehlerfall ist der eigentliche Test, besonders bei Berechtigungen |
| Test spiegelt die Implementierung | Wird bei jedem Refactoring rot, ohne Fehler |
| Ein Test prüft fünf Dinge | Bei Rot ist unklar, was kaputt ist |
| Tests hängen voneinander ab | Einzeln ausgeführt schlagen sie fehl |
| Echte Zeit statt fixierter | Schlägt irgendwann nachts fehl |
| Zufallsdaten ohne Seed | Nicht reproduzierbar |
| Abdeckungsquote als Ziel | Erzeugt Tests, die nichts behaupten |
| Mock statt Fake | Prüft Aufrufe statt Ergebnisse |

---

## 7. Vorgehen bei einem neuen Modul

1. Invarianten aus dem Modul-Issue als **Testnamen** notieren — vor dem Code
2. Für jede einen negativen Test schreiben
3. Service implementieren, bis alle grün sind
4. Grenzen ergänzen: null, eins, Limit, Limit+1
5. Zustandsmatrix durchgehen, verbotene Übergänge testen
6. Guild-Scoping-Test: Zugriff auf fremde Guild scheitert
7. Berechtigungstests je Action
8. `mutmut` gegen den Service laufen lassen, überlebende Mutationen prüfen
9. Erst danach Adapter und deren Tests

Schritt 1 ist der wichtigste. Die Invarianten stehen schon in Prosa im Issue —
sie in Testnamen zu übersetzen kostet Minuten und ist der wirksamste
Kontrollpunkt gegen maschinell erzeugten Code, der plausibel aussieht und die
falsche Regel umsetzt.

---

## 8. Werkzeuge

| Werkzeug | Zweck |
|---|---|
| `pytest`, `pytest-asyncio` | Basis |
| `pytest-cov` | Coverage als Suchhilfe |
| `httpx.AsyncClient` | Router-Tests gegen die App |
| `mutmut` | Mutation Testing, manuell je Modul |
| `hypothesis` | Property-based Tests, gezielt |
| `freezegun` | fixierte Zeit |
| `polyfactory` | Testdaten aus Pydantic-Modellen |

---

## Referenzen

- `tests/README.md` — Ebenen und verbindliche Testfälle
- `docs/review.md` — Diffs lesen
- `docs/security-baseline.md` — Pflichttests für Zugriffskontrolle
