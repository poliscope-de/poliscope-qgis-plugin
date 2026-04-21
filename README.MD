# Poliscope QGIS Plugin

Das offizielle QGIS Plugin für die Integration von Poliscope-Daten in Ihre GIS-Arbeitsumgebung.

## Über Poliscope

Poliscope revolutioniert die Informations- und Datenbeschaffung für Projektentwickler im Bereich erneuerbarer Energien durch automatisierte Analyse von Kommunalpolitik. Mit einer zentralen API bringt Poliscope Transparenz und Effizienz in die kommunalpolitische Informationslandschaft Deutschlands.

## Features

- **🗺️ Direkte QGIS-Integration**: Nahtlose Einbindung kommunaler Planungsdaten in Ihre QGIS-Arbeitsumgebung
- **🔍 KI-basierte Suche**: Semantische und Keyword-Suche nach Sitzungen, Vorlagen und Dokumenten
- **📍 Fokusregionen**: Gespeicherte Suchabonnements mit Neuigkeitenzähler und automatischen Updates
- **📋 Merkliste**: Gespeicherte Sitzungen synchronisiert zwischen Plugin und Web-App
- **🔄 Live-Datenverbindung**: Echtzeit-Zugriff auf die Poliscope-Datenbank
- **🎯 Erweiterte Filter**: Verwaltungsebene, Quellen, Suchmodus und Suchtiefe
- **🔒 Sichere API-Anbindung**: Verschlüsselte Verbindung über persönlichen API-Key

## Systemanforderungen

- **QGIS**: Version 3.0 oder höher
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

1. Plugin-ZIP aus dem [GitHub Repository](https://github.com/poliscope-de/poliscope-qgis-plugin) herunterladen
2. In QGIS: **Plugins** → **Plugins verwalten und installieren** → **Aus ZIP installieren**
3. ZIP-Datei auswählen und installieren

## Konfiguration

### API-Key einrichten

1. Besuchen Sie die [Poliscope GIS-Plugin Seite](https://poliscope.de/app/gis-plugin) und erstellen Sie einen API-Key
2. In QGIS das Poliscope Plugin öffnen
3. Auf das **Zahnrad-Icon** (Einstellungen) klicken
4. API-Key einfügen und bestätigen

## Nutzung

### Fokusregionen Tab

- Zeigt Neuigkeiten aus Ihren gespeicherten Fokusregionen
- Fokusregion auswählen und **Liste aktualisieren** klicken, um Ergebnisse zu laden und den Neuigkeitenzähler zurückzusetzen
- Fokusregionen werden auf [poliscope.de/app/focusregions](https://poliscope.de/app/focusregions) verwaltet
- Filter nach Verwaltungsebene, Quellen und Datum

### Suche Tab

- **Kartenausschnitt Suche**: Alle Ergebnisse im aktuellen Kartenausschnitt
- **Kartenzentrum Suche**: Nur Verwaltungseinheit in der Kartenmitte
- Suchmodus: **Semantisch** (bedeutungsbasiert) oder **Keyword** (exakte Treffer)
- Suchtiefe: Schnellsuche / Tiefenrecherche / Umfassend
- Filter nach Verwaltungsebene, Quellen und Datum

### Merkliste Tab

- Alle gespeicherten Sitzungen aus Plugin und Web-App
- Räumliche Filter: Kartenausschnitt, Kartenzentrum oder Fokusregion
- Synchronisation zwischen verschiedenen Poliscope-Anwendungen

## Tipps & Tricks

💡 **Kleiner Bildschirm**: Klappen Sie Filter zu für bessere Übersicht der Ergebnisse

💡 **Präzise Suche**: Nutzen Sie den Keyword-Modus für exakte Begriffe

💡 **Automatische Updates**: Konfigurieren Sie Fokusregionen für relevante Gebiete und prüfen Sie den Neuigkeitenzähler

## Support & Feedback

- **🐛 Bugs & Features**: [GitHub Issues](https://github.com/poliscope-de/poliscope-qgis-plugin/issues)
- **❓ Allgemeine Fragen**: [Kontaktseite](https://www.poliscope.de/kontakt)
- **📧 Technischer Support**: support@poliscope.de

## Lizenz

Dieses Plugin steht unter der [GPL-2.0 license](LICENSE).

## Erstellen einer installierbaren ZIP-Datei

1. Kopiere das gesamte Plugin-Verzeichnis in einen neuen Ordner `poliscope_qgis_plugin`
2. Entferne das `.git` Verzeichnis
3. Erstelle eine ZIP-Datei aus diesem Ordner

---

**Poliscope GmbH** | Katzenstr. 1a, 21335 Lüneburg | [www.poliscope.de](https://www.poliscope.de)
