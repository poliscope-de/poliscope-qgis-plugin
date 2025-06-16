# Poliscope QGIS Plugin

Das offizielle QGIS Plugin für die Integration von Poliscope-Daten in Ihre GIS-Arbeitsumgebung.

## Über Poliscope

Poliscope revolutioniert die Informations- und Datenbeschaffung für Projektentwickler im Bereich erneuerbarer Energien durch automatisierte Analyse von Kommunalpolitik. Mit einer zentralen API bringt Poliscope Transparenz und Effizienz in die kommunalpolitische Informationslandschaft Deutschlands.

## Features

- **🗺️ Direkte QGIS-Integration**: Nahtlose Einbindung kommunaler Planungsdaten in Ihre QGIS-Arbeitsumgebung
- **🔍 Geografische Suche**: Suche nach Sitzungsdaten basierend auf dem aktuellen Kartenausschnitt
- **📍 Fokusregionen**: Definieren Sie bevorzugte Regionen für automatische Updates
- **📋 Merkliste**: Speichern und verwalten Sie wichtige Sitzungsdaten
- **🔄 Live-Datenverbindung**: Echtzeit-Zugriff auf die Poliscope-Datenbank
- **🎯 Erweiterte Filter**: Präzise Suchfilter für effiziente Datenanalyse
- **🔒 Sichere API-Anbindung**: Verschlüsselte Verbindung über persönlichen API-Key

## Systemanforderungen

- **QGIS**: Version 3.16 oder höher
- **Python**: Version 3.7+
- **Internet**: Aktive Internetverbindung erforderlich
- **Account**: Gültiger Poliscope-Account mit API-Key

## Installation

### Über QGIS Plugin Manager (Empfohlen)

1. QGIS öffnen
2. **Plugins** → **Plugins verwalten und installieren**
3. Nach **"Poliscope"** suchen
4. Plugin installieren und aktivieren

### Manuelle Installation

1. Plugin-ZIP aus dem [GitHub Repository](https://github.com/poliscope-de/poliscope-qgis-plugin) oder direkt unter [QGIS-Plugins](https://plugins.qgis.org/plugins/poliscope_qgis_plugin/) herunterladen
2. In QGIS: **Plugins** → **Plugins verwalten und installieren** → **Aus ZIP installieren**
3. ZIP-Datei auswählen und installieren

## Konfiguration

### 1. API-Key erstellen

1. Besuchen Sie die [Poliscope GIS-Plugin Seite](https://www.poliscope.de/gis-plugin)
2. Generieren Sie einen neuen API-Key
3. **Wichtig**: Speichern Sie den Key sicher ab - er wird nur einmal angezeigt!

### 2. Plugin konfigurieren

1. In QGIS das Poliscope Plugin öffnen
2. Auf das **Zahnrad-Icon** (Einstellungen) klicken
3. API-Key einfügen
4. **QGIS neu starten** (erforderlich!)

## Nutzung

### Neuigkeiten Tab
- Aktuelle Sitzungen aus Ihren Fokusregionen
- Erstellen Sie Fokusregionen auf der Poliscope-Website
- Nutzen Sie Filter zur Verfeinerung der Suche
- Klicken Sie "Aktualisieren" nach Filteränderungen

### Suche Tab
- **Viewport-Suche**: Alle Sitzungen im aktuellen Kartenausschnitt
- **Zentrale Suche**: Nur Verwaltungseinheit in der Kartenmitte
- Ideal für gezielte Suchen in einzelnen Städten

### Merkliste Tab
- Alle gespeicherten Sitzungen aus Plugin und Web-App
- Gewohnte Filterfunktionen verfügbar
- Synchronisation zwischen verschiedenen Poliscope-Anwendungen

## Tipps & Tricks

💡 **Kleiner Bildschirm**: Klappen Sie Filter zu für bessere Übersicht der Ergebnisse

💡 **Präzise Suche**: Nutzen Sie die "Zentrum-Suche"-Option für exakte geografische Abgrenzung

💡 **Automatische Updates**: Konfigurieren Sie Fokusregionen für relevante Gebiete

## Support & Feedback

- **🐛 Bugs & Features**: [GitHub Issues](https://github.com/poliscope-de/poliscope-qgis-plugin/issues)
- **❓ Allgemeine Fragen**: [Kontaktseite](https://www.poliscope.de/kontakt)
- **📧 Technischer Support**: support@poliscope.de

## Lizenz

Dieses Plugin steht unter der [GPL-3.0 license](LICENSE).

## Entwicklung

Interessiert an der Weiterentwicklung? Wir freuen uns über Contributions!

### Erstellen einer installierbaren ZIP-Datei

1. Kopiere das gesamte Plugin-Verzeichnis in einen neuen Ordner.
2. Entferne das `.git` Verzeichnis.
3. Benenne den Ordner um in `poliscope_qgis_plugin`
4. Erstelle eine ZIP-Datei aus diesem Ordner.

Punkt 1-3 sind nur für öffentliche Releases im QGIS Plugin Repository notwendig. Für lokale Installationen kann die ZIP-Datei direkt aus dem Repository erstellt werden.

## Über uns

Poliscope GmbH ist ein Technologieführer im Bereich der kommunalpolitischen Datenanalyse mit Sitz in Lüneburg. Unser Ziel ist es, den Standard für politische Transparenz und datengetriebene Entscheidungsfindung in Deutschland zu setzen.

---

**Poliscope GmbH** | Katzenstr. 1a, 21335 Lüneburg | [www.poliscope.de](https://www.poliscope.de)
