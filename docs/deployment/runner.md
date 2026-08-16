# Self-hosted Runner einrichten (Fuchs)

Nativer GitHub-Actions-Runner als systemd-Dienst unter eigenem Systemnutzer.
Host: `fuchs`. Repo: öffentlich.

**Aufgabenteilung der Workflows**

| Workflow | Runner | Warum |
|---|---|---|
| `ci.yml` | `ubuntu-latest` (GitHub-gehostet) | Fork-PRs führen fremden Code aus — der gehört auf Wegwerf-Maschinen. Bei öffentlichen Repos kostenlos. |
| `deploy.yml` | `[self-hosted, fuchs]` | Braucht Zugriff auf Docker und Daten. Nur durch Tag-Push und manuelle Auslösung erreichbar, nicht durch Forks. |

Alles unten betrifft ausschließlich den Deploy-Runner.

---

## Schritt 1 — Systemnutzer anlegen

```bash
sudo useradd --system --create-home \
     --home-dir /srv/github-actions \
     --shell /bin/bash \
     actrunner
```

`--system` erzeugt einen Account ohne Passwort-Login und mit niedriger UID.
Login-Shell ist trotzdem `/bin/bash`, weil `config.sh`, `svc.sh` und `run.sh`
Bash-Skripte sind — mit `nologin` scheitert die Installation.

Home ist `/srv/github-actions`, darunter kommt pro Repo ein Ordner. Damit
bleibt Platz für weitere Runner, ohne dass etwas im Weg steht.

**Warum nicht dein eigener Benutzer:** ein Workflow auf diesem Runner läuft mit
den Rechten des Runner-Nutzers. Bei deinem Account wären das deine SSH-Keys,
Dotfiles und alles andere im Home. Der Systemnutzer begrenzt den Schaden.

---

## Schritt 2 — Verzeichnisse anlegen

```bash
sudo mkdir -p /srv/github-actions/teabot
sudo mkdir -p /srv/teabot/{data,backups}

sudo chown -R actrunner:actrunner /srv/github-actions
sudo chown -R actrunner:actrunner /srv/teabot
```

Zwei getrennte Bäume mit unterschiedlicher Lebensdauer:

| Pfad | Inhalt | Bei Neuinstallation |
|---|---|---|
| `/srv/github-actions/teabot` | Runner-Installation, Checkouts | wegwerfbar |
| `/srv/teabot` | SQLite-DB, Backups, `.env` | **unbedingt sichern** |

---

## Schritt 3 — Docker-Zugriff geben

```bash
sudo usermod -aG docker actrunner
```

Notwendig, weil der Deploy `docker compose` ausführt.

> Das gibt `actrunner` faktisch Root-Rechte auf Fuchs: Über den Docker-Socket
> lässt sich ein Container mit beliebigem Host-Mount starten. Das ist bei
> jedem self-hosted Runner so, der Docker nutzt. Tragbar, solange auf diesem
> Runner ausschließlich Workflows laufen, die Forks nicht auslösen können —
> genau deshalb steht `deploy.yml` nur auf `push: tags` und
> `workflow_dispatch`.

---

## Schritt 4 — Systemwerkzeuge prüfen

```bash
sudo apt update
sudo apt install -y curl sqlite3 jq
```

`sqlite3` braucht der Backup-Step (`VACUUM INTO`), `curl` den Health-Check.
Fehlt eines, bricht der Deploy mit einer Meldung ab, die nicht auf die Ursache
zeigt.

Prüfen:

```bash
sqlite3 --version && curl --version | head -1 && docker compose version
```

---

## Schritt 5 — Runner herunterladen

Aktuelle Version unter <https://github.com/actions/runner/releases> nachsehen.

```bash
VERSION=2.321.0

sudo -u actrunner bash -c "cd /srv/github-actions/teabot && \
  curl -fsSL -o runner.tar.gz \
    'https://github.com/actions/runner/releases/download/v${VERSION}/actions-runner-linux-x64-${VERSION}.tar.gz' && \
  tar xzf runner.tar.gz && rm runner.tar.gz && ls"
```

Sichtbar sein sollten unter anderem `config.sh`, `run.sh`, `svc.sh`, `bin/`,
`externals/`.

Wichtig ist, dass die Dateien `actrunner` gehören — deshalb der Download unter
diesem Nutzer und nicht als root mit nachträglichem `chown`.

---

## Schritt 6 — Registrieren

Token holen: **Repo → Settings → Actions → Runners → New self-hosted runner**.
Es gilt etwa eine Stunde und wird beim Registrieren verbraucht.

```bash
sudo bash -c 'cd /srv/github-actions/teabot && sudo -u actrunner ./config.sh \
  --url https://github.com/VoidEUW/teabot \
  --token <REGISTRATION_TOKEN> \
  --name fuchs \
  --labels self-hosted,fuchs \
  --work _work \
  --replace'
```

`OWNER` durch den tatsächlichen Kontonamen ersetzen — die Schreibweise steht in
`git remote -v`. Wird der Platzhalter übersehen, antwortet GitHub mit **404
Not Found**, weil die URL auf ein nicht existierendes Repository zeigt.

`--unattended` ist hier bewusst weggelassen: interaktiv sieht man, an welcher
Stelle es hakt, und der Runner bestätigt am Ende den Erfolg.

Die Labels müssen zu `runs-on: [self-hosted, fuchs]` in `deploy.yml` passen.
`self-hosted` wird automatisch vergeben; `fuchs` kommt hier dazu und sorgt
dafür, dass der Job auf genau dieser Maschine landet, falls später ein zweiter
Runner existiert.

Es entstehen `.runner`, `.credentials` und `.credentials_rsa`. Die letzte ist
ein privater Schlüssel — niemals kopieren, teilen oder sichern.

**Es gibt keine Konfigurationsdatei zum Bearbeiten.** Name und Labels stehen in
`.runner` und werden nur durch erneutes Registrieren geändert:

```bash
sudo -i
cd /srv/github-actions/teabot
./svc.sh stop
sudo -u actrunner ./config.sh remove --token <REMOVE_TOKEN>
sudo -u actrunner ./config.sh --url ... --token ... --labels ...   # neu
./svc.sh start
exit
```

---

## Schritt 7 — Als Dienst installieren

`svc.sh` muss **als root** laufen (es schreibt nach `/etc/systemd/system/` und
ruft `daemon-reload` auf) und **aus dem Runner-Verzeichnis heraus** (es sucht
`.runner` und seine Vorlagen relativ zum Arbeitsverzeichnis).

Beides zusammen ist der Haken: `/srv/github-actions` gehört `actrunner` und hat
`0750`, dein eigener Benutzer darf also nicht einmal hineinwechseln — `cd`
scheitert, bevor `sudo` überhaupt greift.

Lösung: das `cd` mit unter root ausführen lassen.

```bash
sudo bash -c 'cd /srv/github-actions/teabot && ./svc.sh install actrunner'
sudo bash -c 'cd /srv/github-actions/teabot && ./svc.sh start'
sudo bash -c 'cd /srv/github-actions/teabot && ./svc.sh status'
```

Alternativ eine Root-Shell, wenn mehrere Befehle anstehen:

```bash
sudo -i
cd /srv/github-actions/teabot
./svc.sh install actrunner
./svc.sh start
./svc.sh status
exit
```

Das Argument `actrunner` bei `install` legt fest, unter welchem Nutzer der
Dienst später läuft. Der Befehl selbst wird deshalb **nicht** als `actrunner`
ausgeführt.

Die Verzeichnisrechte bleiben bei `0750`. Ein `chmod 755` würde das Problem
scheinbar lösen, macht aber `.credentials_rsa` — einen privaten Schlüssel —
für alle lesbar.

`svc.sh install` erzeugt die systemd-Unit und aktiviert den Autostart. Der
Dienst heißt `actions.runner.OWNER-teabot.fuchs.service`.

Kontrolle:

```bash
systemctl status actions.runner.OWNER-teabot.fuchs.service
journalctl -u actions.runner.OWNER-teabot.fuchs.service -f
```

In der Weboberfläche unter **Settings → Actions → Runners** muss `fuchs` als
*Idle* erscheinen. Steht dort *Offline*, hat der Dienst ein Problem — Journal
lesen.

---

## Schritt 8 — Repo-Variablen setzen

**Settings → Secrets and variables → Actions → Variables:**

| Name | Wert |
|---|---|
| `DEPLOY_DIR` | `/srv/teabot` |
| `APP_PORT` | Port, unter dem `/health` erreichbar ist |

Variables, nicht Secrets — es sind keine Geheimnisse, und in Logs sichtbar zu
sein hilft bei der Fehlersuche.

---

## Schritt 9 — Deploy-Umgebung vorbereiten

`/srv/teabot/.env` enthält die Laufzeit-Secrets des Bots (Discord-Token,
OAuth-Client-Secret). Sie wird **einmalig von Hand** angelegt und niemals aus
dem Repo erzeugt. Der Deploy-Workflow prüft nur ihre Existenz und bricht sonst
sofort ab.

```bash
sudo -u actrunner touch /srv/teabot/.env
sudo chmod 600 /srv/teabot/.env
sudo -u actrunner nano /srv/teabot/.env
```

Ebenfalls nach `/srv/teabot` gehört später die `compose.yaml` — der Deploy
führt dort `docker compose` aus. Am einfachsten per Symlink auf den Checkout,
sobald der Workflow einmal gelaufen ist; alternativ eine Kopie, die du bei
Änderungen mitziehst.

---

## Schritt 10 — Runner testen, bevor Code existiert

Da noch keine Zeile geschrieben ist, kann `deploy.yml` nicht durchlaufen. Der
Runner lässt sich trotzdem verifizieren. Lege temporär
`.github/workflows/runner-check.yml` an:

```yaml
name: Runner check
on: workflow_dispatch

jobs:
  check:
    runs-on: [self-hosted, fuchs]
    steps:
      - run: hostname && whoami && pwd
      - run: docker version --format '{{.Server.Version}}'
      - run: sqlite3 --version
      - run: test -d "${{ vars.DEPLOY_DIR }}" && echo "DEPLOY_DIR ok"
```

Über **Actions → Runner check → Run workflow** starten. Läuft das grün, sind
Registrierung, Labels, Docker-Zugriff, Werkzeuge und Variablen korrekt. Danach
die Datei wieder löschen.

Das ist der Moment, an dem die Infrastruktur abgenommen ist — ab hier kann
Code entstehen.

---

## Betrieb

```bash
# Status und Logs
systemctl status actions.runner.OWNER-teabot.fuchs.service
journalctl -u actions.runner.OWNER-teabot.fuchs.service -f

# Steuern
cd /srv/github-actions/teabot
sudo ./svc.sh stop
sudo ./svc.sh start

# Entfernen
sudo ./svc.sh uninstall
sudo -u actrunner ./config.sh remove --token <REMOVE_TOKEN>
```

Der Runner aktualisiert sich selbst. Ein manuelles Update: Dienst stoppen,
neues Archiv über die Installation entpacken, Dienst starten — `.runner` und
`.credentials` bleiben erhalten.

---

## Fehlerbehebung

### `cd: Permission denied` auf `/srv/github-actions/teabot`

Erwartet. Das Verzeichnis gehört `actrunner` und hat `0750`. Statt die Rechte
zu lockern, das `cd` mit unter root ausführen:

```bash
sudo bash -c 'cd /srv/github-actions/teabot && ./svc.sh status'
```

### Passwortabfrage bei `su actrunner`

`actrunner` ist ein Dienstkonto ohne Passwort — eine Anmeldung ist unmöglich
und auch nicht vorgesehen. `su` funktioniert deshalb nie. Richtig ist
`sudo -u actrunner …`; die Abfrage dort gilt dem **eigenen** Passwort, nicht
dem des Dienstkontos.

### `actrunner is not in the sudoers file`

Du bist noch in der Shell von `actrunner`. Mit `exit` zurück zum eigenen
Benutzer, dann erneut. Das Dienstkonto bekommt bewusst keine sudo-Rechte.

### 404 Not Found bei der Registrierung

```
Http response code: NotFound from 'POST https://api.github.com/actions/runner-registration'
{"message":"Not Found","status":"404"}
```

Kein Netzwerk- oder Firewall-Problem — der Runner baut nur ausgehende
HTTPS-Verbindungen auf, und eine strukturierte JSON-Antwort beweist, dass die
Verbindung steht. GitHub antwortet mit 404 statt 401, um nicht preiszugeben,
ob ein Repository existiert.

Ursachen nach Häufigkeit:

1. Platzhalter `OWNER` in der URL nicht ersetzt
2. Registrierungstoken abgelaufen (ca. 1 Stunde) oder bereits verbraucht
3. Organisations-Token mit Repo-URL kombiniert oder umgekehrt
4. Personal Access Token statt Registrierungstoken verwendet

Vor einem neuen Versuch halbfertige Reste entfernen:

```bash
sudo bash -c 'cd /srv/github-actions/teabot && rm -f .runner .credentials .credentials_rsa'
```

### `svc.sh install` schlägt fehl

Setzt eine erfolgreiche Registrierung voraus — der Dienstname wird aus
`.runner` gelesen. Prüfen:

```bash
sudo bash -c 'ls -la /srv/github-actions/teabot/.runner /srv/github-actions/teabot/.credentials'
```

Fehlen die Dateien, zuerst Schritt 6 abschließen.

---

## Fallstricke

**Docker-Gruppe wirkt erst nach Neustart des Dienstes.** Laufende Prozesse
übernehmen neue Gruppenzugehörigkeiten nicht. Nach `usermod -aG` immer
`sudo ./svc.sh stop && sudo ./svc.sh start`.

**Ein Runner, ein Job.** Genau das ist hier erwünscht: zwei gleichzeitige
`alembic upgrade` auf derselben SQLite-Datei wären ein Problem.

**Rechte auf `/srv/teabot`.** Gehört das Verzeichnis nicht `actrunner`,
scheitern Backup und Compose-Aufrufe an Berechtigungen.

**`_work` wächst.** Jeder Job legt dort einen Checkout an. Gelegentlich prüfen,
bei gestopptem Dienst leeren.

**`pull_request_target` niemals verwenden.** Der Trigger läuft mit den Secrets
des Base-Repos und im Kontext eines fremden Branches — der klassische Weg,
über den öffentliche Repos kompromittiert werden.

**Registrierungstoken ist kurzlebig**, das daraus entstehende `.credentials`
dagegen dauerhaft. Wird der Server neu aufgesetzt, brauchst du ein neues
Registrierungstoken.
