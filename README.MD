# Poliscope QGIS Plugin

Das **Poliscope QGIS Plugin** ermöglicht es, Sitzungsdaten aus Ratsinformationssystemen (RIS) per API direkt in QGIS zu nutzen.
Dadurch können kommunale Entscheidungsprozesse geografisch visualisiert und analysiert werden.

## 🔍 Funktionen

- Abruf von Sitzungsdaten aus verschiedenen RIS über standardisierte APIs
- Integration der Daten als Layer in QGIS
- Geografische Visualisierung von kommunalen Entscheidungsprozessen
- Unterstützung für mehrere Städte und Gemeinden

## 🚀 Installation

### Voraussetzungen

- QGIS 3.10 oder höher
- Python 3.7 oder höher

### Installation über QGIS Plugin-Manager

1. Öffne QGIS.
2. Gehe zu `Erweiterungen` > `Erweiterungen verwalten und installieren...`.
3. Suche nach `Poliscope`.
4. Klicke auf `Installieren`.

### Manuelle Installation

1. Repository klonen:
   ```bash
   git clone https://github.com/poliscope-de/poliscope-qgis-plugin.git
   ```

2. Den Ordner `poliscope-qgis-plugin` in das QGIS-Plugin-Verzeichnis kopieren:
   - Windows:
     ```
     C:\Users\<Benutzername>\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\
     ```
   - macOS/Linux:
     ```
     ~/.local/share/QGIS/QGIS3/profiles/default/python/plugins/
     ```

3. QGIS neu starten und das Plugin unter `Erweiterungen` aktivieren.

## 🛠️ Nutzung

1. Aktiviere das Plugin in QGIS.
2. Wähle im Plugin-Menü die gewünschte Stadt oder Gemeinde aus.
3. Die Sitzungsdaten werden als Layer in dein QGIS-Projekt geladen.
4. Nutze die QGIS-Werkzeuge, um die Daten zu analysieren und zu visualisieren.

## 📂 Projektstruktur

- `api/` – Schnittstellen zu verschiedenen RIS
- `resources/` – Icons und Ressourcen
- `scripts/` – Hilfsskripte
- `ui/` – Benutzeroberflächen
- `utils/` – Hilfsfunktionen


## 📞 Kontakt

Für Fragen oder Anregungen: [info@poliscope.de](mailto:info@poliscope.de)

---

*Hinweis: Dieses Plugin befindet sich in der aktiven Entwicklung. Funktionen können sich ändern.*
