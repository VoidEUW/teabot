# `bot/` — Discord-Client und Lifecycle

## Zuständigkeit

Alles, was den Discord-Client betrifft: seine Konstruktion, sein Lebenszyklus
und die konkrete Umsetzung des `BotGateway`.

Dies ist neben den `cog.py` der Module der **einzige** Ort, an dem `discord`
importiert werden darf.

## Bestandteile

| Datei | Aufgabe |
|---|---|
| `client.py` | Factory: baut eine frische `TeaBot`-Instanz samt Intents |
| `manager.py` | `start()`, `stop()`, `restart()`, `status()` |
| `base.py` | `BaseCog` mit gemeinsamen Checks und Logging |
| `gateway.py` | In-Process-Implementierung des `BotGateway`-Protokolls |

## Was hier nicht hineingehört

- **Fachlichkeit.** Slash-Commands leben in den `cog.py` der Module, nicht hier.
- **Routen oder Templates.**
- **Direkter Datenbankzugriff.** Der Manager verwaltet einen Prozesszustand,
  keine Daten.

## Harte Regeln

1. **Der Client entsteht ausschließlich über die Factory.** Ein geschlossener
   `discord.Client` lässt sich nicht wiederverwenden — `restart()` heißt: Task
   canceln, `close()` awaiten, **neue Instanz** bauen, Cogs neu laden.
2. **Cogs kommen bei jedem Client-Aufbau aus der Registry.** `bot/` fragt die
   Registry; die Registry kennt `bot/` nicht.
3. **Jeder Task braucht einen Done-Callback**, der Exceptions loggt und den
   Status auf `crashed` setzt. Ein Task, dessen Ergebnis niemand abruft,
   stirbt lautlos — und das Dashboard zeigt weiterhin „online".
4. **`asyncio.Lock` um alle Lifecycle-Operationen.** Zwei schnelle Klicks im UI
   dürfen keine zwei Clients erzeugen.
5. **Das Gateway wirft `BotUnavailable`, wenn der Client nicht bereit ist.**
   Kein stilles Verschlucken, keine Warteschleife — die Web-Schicht zeigt den
   Fehler an.
6. **Intents explizit und minimal.** Nur anfordern, was gebraucht wird;
   privilegierte Intents nur mit dokumentiertem Grund.

## Anti-Patterns

- **Client als globale Variable.** Verhindert Restart und Tests.
- **`bot.run()`** — blockiert den Event Loop und damit den Webserver.
  Verwendet wird `await bot.start()` in einem Task.
- **Geschäftslogik im Gateway.** Es ist ein Transport: Kanal-ID rein, Nachricht
  raus. Wer hier eine Bedingung einbaut, hat den Service umgangen.
- **`close()` ohne anschließenden Neuaufbau.** Der Manager landet in einem
  Zustand, aus dem kein Start mehr möglich ist.
- **Reconnect von Hand nachbauen.** `discord.py` erledigt das; ein zweiter
  Mechanismus stört nur.

## Referenzen

- `ARCHITECTURE.md` §3 Prozess-Topologie, §7.6 BotGateway, §7.7 Client-Lifecycle
- `bot/AGENTS.md` — zusätzliche Vorgaben für Agentenarbeit in diesem Bereich
