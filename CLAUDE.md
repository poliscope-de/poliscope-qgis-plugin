# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Poliscope QGIS Plugin integrates municipal planning data from German council information systems (Ratsinformationssysteme) into QGIS. It provides semantic and keyword search, focus regions with new-results tracking, and bookmarking for council meetings, proposals, and documents.

**Requirements:** QGIS 3.0+, Python 3.7+, valid Poliscope API key

## Architecture

### Core Components

- **`poliscope_plugin.py`** — Main plugin class (`PoliscopePlugin`). Handles QGIS integration, UI event binding, and coordinates between API and UI. Contains three tabs: Fokusregionen, Suche, Merkliste.

- **`api/poliscopeAPI.py`** — API client (`PoliscopeAPI`) and typed data models. Communicates with `api.poliscope.de/v2` using Bearer token auth. Returns `ResultGroup` / `ChunkHit` objects from the vector search API.

- **`ui/`** — Qt widgets loaded from `.ui` files via `uic.loadUi()`. Main dockwidget defined in `poliscope_plugin_dockwidget_base.ui`.

- **`utils/utils.py`** — Static utility methods for coordinate transforms (EPSG:4326), date formatting, score display, breadcrumb building, and SVG rendering.

### Key Patterns

- Settings stored via `QSettings("PoliscopePlugin")` — API key persists in QGIS settings
- Tab-specific state: each tab maintains `results_*` (full result list), `displayedCount_*` (how many shown), separate filter state
- Client-side batching: API returns all results at once; "Mehr laden" reveals next 50 from the cached list
- Coordinate transforms use `QgsCoordinateTransform` between project CRS and EPSG:4326 for API calls

### Data Model

The v2 API uses a grouped result structure:

- `ResultGroup` — one source item (meeting, proposal, or document), contains top 3 `ChunkHit`s and a `ResultContext`
- `ChunkHit` — a matching text chunk with score, text, chunkType, and optional highlights (character offset pairs for keyword matches)
- `ResultContext` — entity name, level, parents[], location, date, and a reference to the source meeting/proposal/document
- `Focusregion` — saved search subscription with team membership, `lastVisit`, and `newResultsCount`
- `Meeting` / `Proposal` — full detail objects returned by `get_meeting()` / `get_proposal()`

### API

Base URL: `https://api.poliscope.de/v2`  
Auth: `Authorization: Bearer {api_key}` header

Key endpoints:
- `GET /search` — semantic/keyword search, returns `ResultGroup[]` + `MapPoint[]`
- `GET /focusregions/{id}/results` — run a saved focus region search
- `POST /focusregions/{id}/visit` — mark visited, resets `newResultsCount`
- `GET /meetings/{id}?detail=full` — full meeting detail including agenda items and documents
- `GET /proposals/{id}?detail=full` — full proposal detail
- `GET /meetings/bookmarked` — user's bookmarked meetings
- `POST /meetings/{id}/bookmark` / `DELETE /meetings/{id}/bookmark` — add/remove bookmark
- `GET /health` — returns `minCompatibleClientVersions.qgis-plugin` (minimum compatible plugin version)

### Version Check

On startup, `get_qgis_plugin_version()` fetches the minimum compatible version from `/v2/health` (`minCompatibleClientVersions.qgis-plugin`). It is compared against the local version in `metadata.txt` using semver tuple comparison. If outdated, all three tab lists show `ListWrongPluginVersionErrorWidget` and all refresh buttons are disabled.

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

### UI Files

UI layout is defined in Qt Designer (`.ui` files). Python code uses `uic.loadUi()` to load them at runtime — never edit `.ui` files by hand. Widget names referenced in Python must match `objectName` in Qt Designer exactly.

### Testing

Tests are in `test/` using QGIS test infrastructure with a mock `QgisInterface` (`qgis_interface.py`). Manual testing in QGIS is required for UI behaviour — reload the plugin via Plugin Reloader, then close and reopen the panel to trigger `run()` fresh.
