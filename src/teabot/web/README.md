# `web/` — Weboberfläche

## Zuständigkeit

Alles, was das Dashboard ausmacht und keinem Modul gehört: Basis-Layout,
gemeinsame Dependencies, Fehlerseiten, Static Files und die Design-Harness
unter `/design`.

Modulspezifische Routen und Templates leben **nicht** hier, sondern im
jeweiligen Modul.

## Bestandteile

| Pfad | Aufgabe |
|---|---|
| `deps.py` | `get_db`, `current_user`, `require(action)` |
| `templates/` | `base.html`, Layout, gemeinsame Komponenten, Fehlerseiten |
| `static/css/tokens.css` | Design-Tokens: Farben, Typografie, Abstände, Motion |
| `static/css/base.css` | Reset und Grundtypografie |
| `static/css/layout.css` | Seitengerüst, Navigation, Raster |
| `static/css/components/` | eine Datei je Komponente |
| `design/` | Harness unter `/design` zur Sichtprüfung |

## Die Routen sind kein API

Endpunkte liefern **HTML** — ganze Seiten oder Fragmente, die Alpine ins DOM
setzt. JSON nur dort, wo der Browser Daten statt Markup braucht (Statuspolling,
SSE-Logstream).

Es wird **keine** REST-API gebaut. Bot und Web laufen im selben Prozess; eine
API für einen Konsumenten im selben Prozess wäre reiner Aufwand.

## Design-Harness (`/design`)

Rendert alle Komponenten mit Fixture-Daten, ohne echte Datenbank. Zweck:
Zustände sichtbar machen, die im Betrieb selten auftreten — leere Listen,
Fehlerzustände, sehr lange Namen, fehlende Avatare.

Neue Komponente heißt: Eintrag in `design/templates/design/components.html`
mit allen relevanten Zuständen. Das ist die Sichtprüfung vor dem PR.

Die Harness ist im Produktivbetrieb deaktiviert oder an die Developer-Mode-
Berechtigung gebunden.

## Harte Regeln

1. **Keine Berechtigungslogik in Templates.** Der Router übergibt fertige
   Flags. Ein `can()`-Aufruf im Template ist ein Verstoß.
2. **Ausgeblendete UI-Elemente sind kein Schutz.** Jede Route prüft
   serverseitig, unabhängig davon, ob der Button sichtbar war.
3. **Autoescaping bleibt an.** `|safe` und `Markup()` nur mit dokumentierter
   Begründung im PR — niemals auf Daten aus Nutzereingaben.
4. **Farben, Abstände und Schriftgrößen kommen aus `tokens.css`.** Feste Werte
   in Komponenten-CSS sind ein Verstoß.
5. **Kein Build-Schritt.** Kein Bundler, kein Preprocessor, kein npm. Alpine und
   CSS werden direkt ausgeliefert.
6. **Fragment-Antworten sind normale Templates ohne `extends`.**
7. **Session-Cookies** mit `HttpOnly`, `Secure`, `SameSite=Lax`.

## Anti-Patterns

- **Datenbankzugriff im Router.** Gehört in den Service.
- **Modulspezifische Templates in `web/templates/`.** Sie gehören ins Modul,
  sonst zerfällt der Slice.
- **Globaler Alpine-Store für alles.** Zustand bleibt lokal an der Komponente,
  solange nichts anderes zwingend ist.
- **Zweites Icon-Set.** Es gilt ein einziges; Mischung erzeugt sichtbare
  Stilbrüche.
- **Inline-`<style>` in Templates.** Umgeht die Tokens.
- **Neue Komponente ohne Eintrag in der Harness.** Dann ist sie nie in ihren
  Randzuständen gesehen worden.

## Offen

`docs/frontend-design.md` stammt aus der Zeit vor dem Stackwechsel und ist auf
SvelteKit und Tailwind gemünzt. Die Tokens und das Komponenteninventar sind
weiter gültig, die technische Umsetzung nicht. Abgleich steht aus.

## Referenzen

- `ARCHITECTURE.md` §4 Schichten, §7.4 Logging (SSE-Terminal)
- `docs/frontend-design.md` — Tokens und Komponenteninventar
- `docs/security-baseline.md` — Session Management, Ausgabe
