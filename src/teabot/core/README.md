# `core/` — Querschnittsdienste

## Zuständigkeit

Infrastruktur, die mehrere Module braucht, aber keinem gehört: Registry,
Event Bus, Sicherheit, Log-Bus, Gateway-Protokoll, Settings-Framework,
Permission-Modell.

Faustregel: Wenn zwei Module dasselbe brauchen und keines der beiden es
besitzen sollte, gehört es hierher. Wenn nur ein Modul es braucht, gehört es
in dieses Modul.

## Bestandteile

| Datei | Aufgabe |
|---|---|
| `registry.py` | findet Module, sammelt `MODULE`, `router`, `Cog`, `SETTINGS`, `PERMISSIONS` |
| `events.py` | In-Process-Pub/Sub zur Entkopplung von Modulen |
| `security.py` | Sessions, OAuth-Flow, `can(user, guild, action)` |
| `logbus.py` | Ringpuffer und Queues für den SSE-Logstream |
| `gateway.py` | `BotGateway`-Protokoll — das einzige Tor zu Discord |
| `settings.py` | generischer Store und Schema-Registrierung |
| `permissions.py` | Action-Enum, Rollenableitung, Prüflogik |

## Was hier nicht hineingehört

- **Fachlichkeit.** Kein Ticket, kein Verstoß, keine Ankündigung. Findet sich
  hier ein Domänenbegriff, ist die Grenze verletzt.
- **Import aus `modules/`.** `core/` kennt keine Module — nur die Registry
  kennt sie, und die lädt sie dynamisch, statt sie zu importieren.
- **Import aus `app/`.** Niemals.
- **Sammelbecken.** `core/` ist kein `utils/`. Eine Hilfsfunktion ohne
  Querschnittscharakter gehört zu ihrem Nutzer.

## Harte Regeln

1. **`gateway.py` definiert nur das Protokoll**, nie eine Implementierung mit
   `discord`-Import. Die Implementierung wohnt in `bot/`, verdrahtet wird sie
   in `app/`.
2. **`security.py` ist ASVS-Level-2-Bereich.** Änderungen dort erfordern einen
   Durchgang durch `docs/security-baseline.md` und einen expliziten Hinweis im
   PR.
3. **Deny by default.** `can()` gibt bei unbekannter Action, unbekannter Rolle
   oder fehlendem Guild-Kontext `False` zurück — niemals `True` als Fallback.
4. **Der Event Bus garantiert nichts.** Keine Zustellgarantie, keine
   Reihenfolge, keine Persistenz. Wer Verlässlichkeit braucht, ruft einen
   Service direkt auf. Ein Handler-Fehler wird geloggt und darf den Publisher
   nicht mitreißen.
5. **Guild-Scoping ist Teil jeder Prüfung.** Eine Berechtigung gilt für eine
   Guild, niemals global — außer für explizit als global markierte
   Owner-Actions.

## Anti-Patterns

- **Rollenprüfung an Ort und Stelle** (`if member.guild_permissions.administrator`).
  Umgeht das Rollenmodell und ist im Web nicht reproduzierbar. Immer `can()`.
- **Fachliche Events als Ersatz für Service-Aufrufe.** Der Event Bus entkoppelt
  Nebenwirkungen, er ersetzt keine Aufrufkette. „Ticket erstellen" ist ein
  Service-Aufruf, „Ticket wurde erstellt" ist ein Event.
- **Settings direkt aus der Datenbank lesen.** Immer über den Accessor, sonst
  greift der Cache nicht und Defaults werden umgangen.
- **Tokens oder Session-IDs ins Log.** Auch gekürzt nicht.
- **Manuell gepflegte Modulliste in der Registry.** Widerspricht ihrem Zweck.

## Referenzen

- `ARCHITECTURE.md` §7 Querschnittsthemen
- `docs/security-baseline.md` — Session Management, Zugriffskontrolle, Logging
