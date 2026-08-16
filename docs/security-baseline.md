# Sicherheits-Baseline

Verbindlicher Sicherheitsanspruch für TeaBot. Dieses Dokument übersetzt einen
allgemeinen Standard in prüfbare Anforderungen an *diesen* Stack. Es ist die
Referenz für Reviews, für die PR-Checkliste und für die Beauftragung von
Coding-Agents.

## Gewählter Standard

**OWASP ASVS (Application Security Verification Standard), Level 1** als
Grundanspruch — mit gezielt angehobenen Bereichen auf **Level 2**:

| Bereich | Level | Begründung |
|---|---|---|
| Session Management | 2 | Sessions schützen Zugriff auf Moderationsfunktionen |
| Zugriffskontrolle | 2 | Rollenmodell ist Kern des Produkts |
| Logging | 2 | Logs enthalten Nutzeraktionen und sind selbst ein Angriffsziel |
| Umgang mit Geheimnissen | 2 | Discord-Token = vollständige Bot-Kontrolle |
| Alle übrigen Kapitel | 1 | Angemessen für ein privates Deployment |

**Warum ASVS:** Der Katalog besteht aus einzeln prüfbaren Anforderungen. Man
kann ihn abarbeiten und im Review konkret referenzieren, statt auf ein
diffuses „sollte sicher sein" zu verweisen.

**Warum nicht Level 2 durchgängig:** Ein Anspruch, der nie geprüft wird, ist
schädlicher als ein niedrigerer, der eingehalten wird. Level 1 vollständig ist
mehr wert als Level 2 auf dem Papier.

**Ergänzend:** OpenSSF Scorecard misst die Repo-Hygiene automatisch
(Branch Protection, gepinnte Actions, Token-Rechte). SLSA-Provenance für das
Docker-Image ist nach v1.0 sinnvoll, jetzt nicht.

---

## Ableitung auf diesen Stack

### Authentifizierung (Discord OAuth)

- OAuth-Flow **muss** einen `state`-Parameter verwenden und serverseitig
  validieren — CSRF-Schutz beim Login
- Redirect-URI wird serverseitig gegen eine Allowlist geprüft, nie aus der
  Anfrage übernommen
- Access- und Refresh-Tokens von Discord werden verschlüsselt gespeichert oder
  gar nicht persistiert, falls sie nach dem Login nicht mehr gebraucht werden
- Bei Discord-Fehlern kein Fallback auf einen unauthentifizierten Zustand:
  fail closed

### Session Management (Level 2)

- Session-Cookie mit `HttpOnly`, `Secure`, `SameSite=Lax`
- Session-ID nach erfolgreichem Login **rotieren** (Session Fixation)
- Serverseitige Invalidierung beim Logout; ein Cookie zu löschen genügt nicht
- Absolute und Idle-Timeouts definiert und durchgesetzt
- Session-Bezeichner sind kryptografisch zufällig, keine ableitbaren Werte

### Zugriffskontrolle (Level 2)

- **Deny by default:** eine Route ohne explizite Berechtigungsprüfung ist ein
  Fehler, kein „öffentlich"
- Alle Prüfungen laufen über die zentrale `can(user, guild, action)` — keine
  Rollenabfrage an Ort und Stelle
- Prüfung **serverseitig** bei jeder Anfrage; ausgeblendete UI-Elemente sind
  kein Schutz
- Guild-Scoping ist Teil jeder Prüfung: Zugriff auf Objekte einer fremden
  Guild muss scheitern, auch bei erratener ID
- Developer-Mode-Funktionen sind an eine eigene Berechtigung gebunden, nicht
  an ein Konfigurations-Flag allein

### Eingabevalidierung und Ausgabe

- Alle Eingaben aus HTTP und Discord über Pydantic-Schemata
- Datenbankzugriff ausschließlich über SQLAlchemy-Konstrukte; rohes SQL nur
  parametrisiert
- Jinja-Autoescaping bleibt aktiv; `|safe` ist ohne dokumentierte Begründung
  ein Verstoß
- Nutzergenerierte Inhalte in Discord-Nachrichten ohne unbeabsichtigte
  Mentions ausgeben (`allowed_mentions` restriktiv setzen)

### Umgang mit Geheimnissen (Level 2)

- Keine Secrets im Repository, auch nicht in Tests oder Fixtures
- Konfiguration ausschließlich über Umgebungsvariablen bzw. `.env` auf dem Host
- Token dürfen niemals in Logs erscheinen — auch nicht gekürzt
- Vergleiche von Geheimnissen mit `secrets.compare_digest`
- `gitleaks` läuft im PR-Review

### Logging (Level 2)

- Sicherheitsrelevante Ereignisse werden protokolliert: Login, Logout,
  fehlgeschlagene Autorisierung, Berechtigungsänderung, Änderung von
  Einstellungen
- Logs enthalten **keine** Tokens, Passwörter, Session-IDs oder vollständigen
  personenbezogenen Datensätze
- Zugriff auf das Log-Terminal ist selbst berechtigungspflichtig
- Retention definiert; Logs wachsen nicht unbegrenzt

### Fehlerbehandlung

- Keine Stacktraces oder internen Pfade in Antworten an Nutzer
- Generische Fehlermeldungen nach außen, Details ins Log
- Bei Autorisierungsfehlern keine Auskunft darüber, ob ein Objekt existiert

### Datenhaltung

- SQLite-Datei außerhalb des Web-Roots, nicht ausliefertbar
- Backups (`/srv/teabot/backups`) sind ebenso schützenswert wie die Datenbank
- Datei-Uploads, falls später vorhanden: Typprüfung, Größenlimit, Ablage
  außerhalb des statisch ausgelieferten Bereichs

### Lieferkette und Build

- Abhängigkeiten über Lockfile fixiert
- Dependabot wöchentlich, Sicherheitsupdates sofort
- GitHub Actions auf Version gepinnt
- Docker-Image läuft als Nicht-Root-Nutzer
- `pull_request_target` wird nicht verwendet
- Self-hosted Runner nur für Workflows, die Forks nicht auslösen können

---

## Prüfung

| Wann | Wodurch |
|---|---|
| Bei jedem PR | CodeRabbit mit den `path_instructions` aus `.coderabbit.yaml` |
| Bei jedem PR | Ruff, Mypy, gitleaks, actionlint |
| Wöchentlich | Dependabot |
| Vor Release | Durchgang durch diese Liste, dokumentiert im Release-Issue |

Automatisierte Prüfung ersetzt das Nachdenken nicht — insbesondere
Zugriffskontrolle und Guild-Scoping lassen sich nur durch Tests belegen, die
den Fehlerfall explizit prüfen. Das ist beim Aufsetzen der Testebenen
mitzudenken.

## Offene Punkte

- Testebenen (Unit, Integration, End-to-End) sind noch nicht definiert. Für
  Zugriffskontrolle sind negative Integrationstests verpflichtend, sobald das
  Permission-Modell steht.
- Rate Limiting für Login und schreibende Endpunkte ist noch nicht entschieden.
- Verschlüsselung gespeicherter Discord-Tokens: Verfahren und
  Schlüsselverwaltung offen.
