# Sicherheit

## Lücken melden

**Bitte keine öffentlichen Issues für Sicherheitsprobleme.**

Nutze stattdessen **Security → Report a vulnerability** in diesem Repository
(GitHub Private Vulnerability Reporting). Das erzeugt einen privaten Kanal,
in dem sich das Problem besprechen lässt, bevor es bekannt wird.

Hilfreich sind: betroffene Version oder Commit, Reproduktionsschritte,
mögliche Auswirkung und — falls vorhanden — ein Vorschlag zur Behebung.

Dies ist ein privat betriebenes Freizeitprojekt. Ich bemühe mich um eine
Rückmeldung innerhalb von sieben Tagen, kann aber keine festen Fristen
zusagen.

## Unterstützte Versionen

Nur der jeweils aktuelle Release-Stand auf `main` wird gepflegt. Ältere Tags
erhalten keine Sicherheitsupdates.

## Geltungsbereich

**Im Geltungsbereich:** Anwendungscode unter `src/`, Authentifizierung und
Autorisierung, Umgang mit Discord-Tokens und OAuth-Daten, Datenbankzugriff,
Templates, CI- und Deployment-Konfiguration.

**Außerhalb:** Discord selbst, Schwachstellen in Abhängigkeiten Dritter
(bitte dort melden — hier gern ein Hinweis, wenn eine Aktualisierung nötig
ist), sowie Fehlkonfigurationen einzelner Installationen.

## Sicherheitsanspruch

Das Projekt orientiert sich an **OWASP ASVS 5.0, Level 1**, mit gezielten
Level-2-Anforderungen für Session Management, Zugriffskontrolle und Logging.
Die konkrete Ableitung auf diesen Stack steht in
[`docs/security-baseline.md`](docs/security-baseline.md).

## Bekannte Betriebsrisiken

Der Deploy läuft über einen self-hosted Runner mit Docker-Socket-Zugriff.
Deploy-Workflows sind deshalb ausschließlich über Tag-Push und manuelle
Auslösung erreichbar, niemals über Pull Requests. `pull_request_target` wird
in diesem Repository nicht verwendet.
