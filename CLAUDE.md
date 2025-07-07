# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a QGIS plugin for Poliscope, a service that provides AI-based crawling of municipal council information systems in Germany for renewable energy project developers. The plugin enables direct integration of municipal planning data into QGIS workflows.

## Key Architecture

- **Main Plugin**: `poliscope_plugin.py` - Core plugin class implementing QGIS plugin interface
- **UI Components**: `ui/` directory contains PyQt5 UI widgets and dialogs
  - `poliscope_plugin_dockwidget.py` - Main dockable widget interface
  - `list_item_widget.py` - Individual result item display
  - `detail_dialog.py` - Detailed session information dialog
  - Error widgets for API key and version issues
- **API Layer**: `api/poliscopeAPI.py` - Handles communication with Poliscope backend
- **Utilities**: `utils/utils.py` - Helper functions
- **Resources**: `resources.py` - Compiled Qt resource file (auto-generated)

## Build and Development Commands

### Primary Build Tool
Use `pb_tool` (Plugin Builder Tool) for most operations:
```bash
pb_tool deploy    # Deploy plugin to QGIS
pb_tool zip       # Create installable ZIP package
pb_tool compile   # Compile resources
```

### Alternative Make Commands
```bash
make compile      # Compile Qt resources (resources.py from resources.qrc)
make test         # Run test suite with nosetests
make deploy       # Deploy to local QGIS plugins directory
make zip          # Create plugin ZIP package
make pylint       # Run pylint code analysis
make pep8         # Run PEP8 style checking
make doc          # Build documentation using Sphinx
```

### Resource Compilation
Qt resources must be compiled after changes:
```bash
pyrcc5 -o resources.py resources.qrc
```

### Testing
```bash
make test         # Full test suite
# For QGIS module issues, first run:
source scripts/run-env-linux.sh <path-to-qgis>
```

### Translation Management
```bash
make transup      # Update translation files
make transcompile # Compile .ts files to .qm
```

## Development Notes

- Plugin requires QGIS 3.0+ and Python 3.7+
- Uses PyQt5 for UI components
- API key required for Poliscope service integration
- Plugin deployment path: `AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins` (Windows)
- All UI files are in `.ui` format and loaded dynamically (not compiled)
- Resources are compiled from `resources.qrc` to `resources.py`

## Plugin Structure

The plugin follows standard QGIS plugin architecture:
- Implements dockable widget interface
- Provides three main tabs: News, Search, and Bookmarks
- Integrates with QGIS map canvas for geographical searches
- Handles API authentication and version compatibility
- Supports both viewport-based and center-point searches