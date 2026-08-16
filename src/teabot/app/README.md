# `app/` — Composition Root

## Zuständigkeit

Der einzige Ort, an dem alle Teile bekannt sind und zusammengesteckt werden.
Hier entsteht die FastAPI-Anwendung, der Discord-Client, der `ClientManager`
und das `BotGateway` — und hier wird entschieden, was wovon abhängt.

Alle anderen Pakete kennen nur ihre eigenen Abhängigkeiten und bekommen sie
hereingereicht. `app/` ist damit die einzige Schicht, die nach oben *und* nach
unten sehen darf.

## Einstiegskette

```
main.py                 dünner Starter im Repo-Root
   └── teabot.py        Prozess-Einstieg: CLI, Uvicorn-Start
          └── app/      baut alles zusammen
```

`main.py` und `teabot.py` enthalten keine Konstruktionslogik. Sie starten nur.
Wer wissen will, wie TeaBot aufgebaut ist, liest `app/`.

## Was hier hineingehört

- Aufbau der FastAPI-Instanz inklusive Middleware und Exception-Handlern
- `lifespan`: Start- und Shutdown-Sequenz
- Client-Factory für `discord.py` und Aufbau des `ClientManager`
- Auswahl und Verdrahtung der `BotGateway`-Implementierung
- Ausführen der Registry und Einhängen der gefundenen Router
- Einbindung von Templates und Static Files
- Konfiguration des Logging-Baums samt Log-Bus-Handler

## Was hier nicht hineingehört

- **Geschäftslogik jeder Art.** Sobald hier eine Domänenregel steht, gehört sie
  in einen Service.
- **Routen.** Die liegen in Modulen oder in `web/`.
- **Direkter Datenbankzugriff.** `app/` baut die Engine, benutzt sie aber nicht.
- **Eine Liste aller Module.** Module werden über die Registry gefunden, nicht
  aufgezählt. Eine solche Liste hier wäre ein Bug.

## Harte Regeln

1. **Keine zirkulären Abhängigkeiten.** `app/` importiert aus `core/`, `db/`,
   `bot/`, `web/` und `modules/`. Der umgekehrte Weg ist verboten — kein
   Modul, kein Service und kein Router importiert aus `app/`.
2. **Startreihenfolge ist verbindlich:** Config validieren → Logging → DB und
   PRAGMAs → Registry → FastAPI → Client-Factory und Gateway → ClientManager →
   Uvicorn. Config zuerst, damit ein fehlender Token sofort abbricht und nicht
   erst beim ersten Discord-Connect.
3. **Shutdown in umgekehrter Reihenfolge:** erst Bot schließen, dann
   DB-Engine disposen. Andersherum laufen noch Handler auf einer toten Session.
4. **Der Bot wird als supervisierter Task gestartet**, nie als „fire and
   forget". Ohne Done-Callback stirbt ein `asyncio.Task` lautlos.
5. **Kein globaler Zustand.** Abhängigkeiten wandern über den App-State und
   über FastAPI-Dependencies, nicht über Modulvariablen.

## Anti-Patterns

- **Singleton-Client als Modulvariable.** Verhindert Restart, weil ein
  geschlossener `discord.Client` nicht wiederverwendbar ist, und macht Tests
  unmöglich. Der Client kommt aus einer Factory.
- **Import aus `app/` in einem Modul**, um „schnell an den Client zu kommen".
  Das ist der Import-Zyklus, der die Architektur aufbricht. Der Weg führt über
  das `BotGateway`.
- **Blockierende Arbeit im Lifespan.** Startet der Prozess langsam, verzögert
  das den Health-Check und lässt den Deploy fehlschlagen.
- **Try/except um den gesamten Startvorgang.** Startfehler sollen laut
  scheitern; ein Prozess, der halb hochgekommen ist, ist schlimmer als keiner.

## Referenzen

- `ARCHITECTURE.md` §3 Prozess-Topologie, §7.1 Registry, §7.7 Client-Lifecycle,
  §10 Startsequenz
- `docs/adr/` — Entscheidung zur In-Process-Architektur
