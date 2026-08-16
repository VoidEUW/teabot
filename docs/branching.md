# Branching und Releases

Verbindliches Arbeitsmodell für dieses Repository. Gilt für menschliche
Beiträge und für Coding-Agents gleichermaßen.

## Modell: GitHub Flow

Ein dauerhafter Branch, kurzlebige Arbeitsbranches, Releases über Tags.

```
feat/tickets-close-command ──┐
                             │  Pull Request
                             │  CI grün + CodeRabbit abgehakt
                             ▼
main ─────────────────────────────────────────────►   immer deploybar
  │
  │  git tag -a v0.3.0
  ▼
deploy.yml  ──►  Fuchs
```

**Kein `develop`, kein `latest`, kein `release/*`.** `main` *ist* der aktuelle
Stand. Die Trennung zwischen „neuester Stand" und „freigegeben" läuft nicht
über einen zweiten Branch, sondern über Tags: ein Merge nach `main` deployt
nichts, weil `deploy.yml` ausschließlich auf Tags und manuelle Auslösung
reagiert.

Ein zweiter Branch wäre nur dann gerechtfertigt, wenn `main` automatisch
deployen würde. Das ist bewusst nicht der Fall.

---

## Branches

`main` ist der einzige dauerhafte Branch. Er ist jederzeit deploybar und
geschützt.

Arbeitsbranches sind kurzlebig — ein bis wenige Tage. Wird ein Branch älter,
ist der Schnitt meist zu groß gewählt.

### Namensschema

Präfix wie beim Commit-Scope, damit Branch und Commit dieselbe Sprache
sprechen:

```
feat/tickets-close-command
fix/core-duplicate-client-start
refactor/web-permission-dependency
docs/adr-settings-framework
chore/deps-bump-discordpy
ci/self-hosted-runner-labels
```

Kleinbuchstaben, Bindestriche, kein Datum, keine Issue-Nummer im Namen — die
Verknüpfung entsteht über `Closes #12` im PR.

---

## Pull Requests

Jede Änderung an `main` läuft über einen PR. Auch alleinarbeitend, denn der PR
ist die Stelle, an der CI und CodeRabbit greifen.

Ablauf:

1. Branch von aktuellem `main` abzweigen
2. Arbeiten, Conventional Commits mit Scope
3. PR öffnen, Vorlage ausfüllen
4. CI muss grün sein
5. CodeRabbit-Anmerkungen abarbeiten oder begründet ablehnen
6. **Squash Merge** nach `main`
7. Branch löschen

### Squash Merge als Standard

Arbeitsbranches enthalten Zwischenstände, besonders wenn ein Agent daran
gearbeitet hat. Squash erzeugt pro PR genau einen Commit auf `main` mit
sauberer Conventional-Commits-Nachricht. Merge-Commits und Rebase-Merge sind
in den Repo-Einstellungen deaktiviert, damit die Entscheidung nicht bei jedem
PR neu getroffen wird.

Die Squash-Nachricht wird von Hand gesetzt — GitHubs Vorschlag ist meist die
PR-Überschrift plus Commit-Liste und damit unbrauchbar als Changelog-Quelle.

### Branch Protection auf `main`

| Einstellung | Wert |
|---|---|
| Require a pull request before merging | an |
| Require approvals | **aus** (Einzelmaintainer; die Prüfung leistet CodeRabbit) |
| Require status checks to pass | an — `quality`, `migrations`, `docker`, CodeQL |
| Require branches to be up to date | an |
| Require conversation resolution | an |
| Allow force pushes | aus |
| Allow deletions | aus |

---

## Releases

### Was einen Tag zum stabilen Stand macht

Nichts Technisches. Ein Tag ist ein Zeiger auf einen Commit — „stabil" ist
eine **Erklärung**, die du abgibst, nachdem du geprüft hast. Damit die
Erklärung etwas wert ist, gehört eine Prüfung davor und eine Markierung
danach.

### Vor dem Tag

- [ ] CI auf `main` grün, letzter Lauf nicht älter als der letzte Merge
- [ ] Alle PRs des geplanten Umfangs sind gemergt
- [ ] Migrationen auf einer **Kopie** der Produktionsdatenbank durchgelaufen
- [ ] Keine offenen kritischen CodeRabbit-Anmerkungen
- [ ] Bei sicherheitsrelevanten Änderungen: Durchgang durch
      `docs/security-baseline.md`
- [ ] Bekannte Einschränkungen notiert, die in die Release-Notes gehören

### Taggen

Annotiert, niemals leichtgewichtig — annotierte Tags tragen Autor, Datum und
Nachricht und sind ein eigenes Objekt in der Historie:

```bash
git checkout main && git pull
git tag -a v0.3.0 -m "Settings-Framework und Admin-Shell"
git push origin v0.3.0
```

Der Push löst `deploy.yml` aus.

### Pre-Releases

Wenn Unsicherheit besteht, ob der Stand trägt:

```bash
git tag -a v0.3.0-rc.1 -m "Release Candidate: Settings-Framework"
git push origin v0.3.0-rc.1
```

Der Deploy läuft ebenfalls — genau das ist der Zweck, der Stand soll ja auf
Fuchs beobachtet werden. Das zugehörige GitHub-Release wird als
**Pre-release** markiert.

Bewährt sich der Kandidat, folgt der eigentliche Tag auf denselben Commit.

### Stable markieren

GitHub-Releases kennen zwei Zustände: **Pre-release** und **Latest release**.
Das ist die Markierung für „stabil" — kein zusätzlicher Branch nötig.

- Kandidat läuft auf Fuchs → Release als *Pre-release*
- Läuft einige Tage unauffällig → Tag ohne Suffix, Release als *Latest*

Damit ist von außen maschinenlesbar, welcher Stand als stabil gilt.

**Stabilität wird rückblickend festgestellt, nicht vorausgesagt.** Ein
Release wird zum stabilen Stand erklärt, nachdem es sich bewährt hat.

### Versionsschema

Semantic Versioning, vor `1.0.0` bewusst nachsichtig gehandhabt:

| Bereich | Bedeutung |
|---|---|
| `0.x.0` | eine abgeschlossene Phase aus `ARCHITECTURE.md` §11 |
| `0.x.y` | Fehlerbehebungen innerhalb einer Phase |
| `1.0.0` | Funktionsumfang v1.0 vollständig, produktiv im Einsatz |

`0.x` signalisiert ausdrücklich, dass sich Schnittstellen und Datenmodell noch
ändern können.

---

## Rollback

Kein eigener Mechanismus nötig. `deploy.yml` nimmt über `workflow_dispatch`
einen beliebigen Ref entgegen:

**Actions → Deploy → Run workflow → ref:** `v0.2.0`

Damit läuft Fuchs wieder auf dem vorherigen Stand. Der Backup-Step des Deploys
hat vorher eine Kopie der Datenbank abgelegt.

**Achtung bei Migrationen:** Ein Rollback des Codes rollt das Datenbankschema
nicht zurück. Wurde in der fehlerhaften Version migriert, muss entweder das
Backup eingespielt oder `alembic downgrade` von Hand ausgeführt werden. Das
ist der Grund, weshalb `downgrade()` in Migrationen ernst zu nehmen ist.

---

## Hotfixes

Kein eigener Branch-Typ. Ein Fehler in Produktion wird zu einem normalen
`fix/`-Branch, der schneller durch den PR geht. Bei genau einem
Deployment-Ziel gibt es nichts zurückzuportieren.

Anschließend Patch-Tag: `v0.3.1`.

---

## Zusammenspiel mit Coding-Agents

Der übliche Ablauf in diesem Projekt:

1. Konzept ausarbeiten, Issue aus dem passenden Template anlegen — das
   ausgefüllte Issue ist das Briefing
2. Agent arbeitet auf einem `feat/`-Branch
3. PR ist die Prüfstelle: CI, CodeQL, CodeRabbit
4. Mensch entscheidet am Merge

Der Branch ist dabei die Sicherung: Was dort liegt, kann nichts beschädigen,
und ein verworfener Versuch kostet ein `git branch -D`. Genau deshalb läuft
auch Agentenarbeit nie direkt auf `main`.
