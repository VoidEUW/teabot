# ARCHITECTURE — Bot und Web in einem Prozess

- **Status:** akzeptiert
- **Datum:** 2026-08-13
- **Betrifft:** Prozess-Topologie, Client-Lifecycle, Datenzugriff

## Kontext

TeaBot besteht aus einem Discord-Client und einer Weboberfläche. Beide arbeiten
auf denselben Daten. Zielumgebung ist ein einzelner privater Server mit
geringer Last.

Ein Vorgängerentwurf trennte Bot und Backend in zwei Prozesse, die über eine
tokengesicherte HTTP-API und eine WebSocket-Verbindung kommunizierten. Das
funktionierte, kostete aber deutlichen Aufwand für Serialisierung,
Authentifizierung zwischen den eigenen Komponenten und Fehlerbehandlung bei
Verbindungsabbrüchen — ohne Nutzen, da beide Prozesse auf derselben Maschine
liefen.

## Optionen

**A — Ein Prozess.** Bot als supervisierter `asyncio.Task` im ASGI-Event-Loop.

**B — Bot als Subprozess.** Backend supervidiert Bot-Prozesse, Kommunikation
über Redis Pub/Sub oder lokalen Socket. Ermöglicht mehrere Clients auf
unterschiedlichen `discord.py`-Versionen.

## Entscheidung

**Option A.**

Der Nutzen von B liegt fast ausschließlich in parallelen Client-Versionen — ein
Anspruch, der für einen privaten Server nicht trägt. Die Kosten von B sind
dagegen dauerhaft: IPC, mehrere SQLite-Writer, doppelte Fehlerpfade.

## Konsequenzen

**Positiv**

- Keine interne API, keine Serialisierung, kein Bot-Token-Auth
- Genau ein SQLite-Writer
- Start/Stop/Restart ist Task-Verwaltung
- Ein Deployment-Artefakt

**Negativ**

- Keine parallelen `discord.py`-Versionen
- Ein Deploy startet alles neu
- Synchrone I/O blockiert Bot **und** Web und ist deshalb verboten
- Ein Speicherleck in einer Komponente betrifft beide

## Ausstiegspfad

Der gesamte Nicht-Bot-Code spricht ausschließlich über das
`BotGateway`-Protokoll (`core/gateway.py`) mit Discord. Services importieren
`discord` nicht. Ein Wechsel auf Option B erfordert damit:

1. eine neue `BotGateway`-Implementierung über IPC,
2. WAL plus `busy_timeout` für mehrere Writer (bereits gesetzt),
3. eine Prozess-basierte `ClientManager`-Implementierung.

Die Service- und Adapterschicht bleibt unverändert. Dieser Pfad ist der Grund,
weshalb die frühe Festlegung auf A vertretbar ist.
