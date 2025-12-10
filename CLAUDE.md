# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Poliscope QGIS Plugin integrates municipal planning data from German council information systems (Ratsinformationssysteme) into QGIS. It provides geographic search, focus regions, and bookmarking for meetings related to renewable energy planning (wind and solar).

**Requirements:** QGIS 3.0+, Python 3.7+, valid Poliscope API key

## Architecture

### Core Components

- **`poliscope_plugin.py`** - Main plugin class (`PoliscopePlugin`). Handles QGIS integration, UI event binding, and coordinates between API and UI. Contains three main tabs: Neuigkeiten (News), Suche (Search), Merkliste (Watchlist).

- **`api/poliscopeAPI.py`** - API client (`MeetingsAPI`) and data model (`Meeting`). Communicates with `api.poliscope.de/v1/`. Contains filter builders for dates, scores, status, bounds, and bookmarks.

- **`ui/`** - Qt widgets loaded from `.ui` files via `uic.loadUiType()`. Main dockwidget defined in `poliscope_plugin_dockwidget_base.ui`.

- **`utils/utils.py`** - Static utility methods for coordinate transforms (EPSG:4326), date formatting, score display, and string operations.

### Key Patterns

- Settings stored via `QSettings("PoliscopePlugin")` - API key persists in QGIS settings
- Tab-specific state: each tab maintains separate pagination (`currPage_*`), filters (`filter_*`), and sort strings (`sortString_*`)
- Infinite scroll: `check_scroll_position_*` methods load more results at 90% scroll
- Coordinate transforms use `QgsCoordinateTransform` between project CRS and EPSG:4326 for API

### API Filter System

Filters are built using static methods on `MeetingsAPI`:
- `create_date_range_filter()` - date range
- `create_wind_and_solar_score_filter()` - energy relevance scores (1-3)
- `create_status_filter()` - meeting status (termin/vorlage/beschluss)
- `create_bounds_filter()` - geographic polygon intersection
- `create_saved_meetings_filter()` / `create_hidden_meetings_filter()` - user preferences

## Development

### Building Resources

Compile Qt resources after modifying `resources.qrc`:
```bash
pyrcc5 resources.qrc -o resources_rc.py
```

### Creating Release ZIP

1. Copy plugin directory to folder named `poliscope_qgis_plugin`
2. Remove `.git` directory
3. Create ZIP from that folder

### Testing

Tests are in `test/` using QGIS test infrastructure with a mock `QgisInterface` (`qgis_interface.py`).

### Version Compatibility

Plugin checks API version at startup via `/v1/version` endpoint. Compares first 3 characters of local version (from `metadata.txt`) with API's `qgisPluginVersion`.
