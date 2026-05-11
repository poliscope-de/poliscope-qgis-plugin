# Handover Notes

## Dokumente-Filter aktivieren

The "Dokumente" checkboxes in the Suche and Fokusregion tabs are intentionally disabled — the API did not yet support document search at the time of development. All code is already in place.

**What's done:**
- Both checkboxes are wired up in `poliscope_plugin.py`:
  - Suche tab: registered at lines 314–315, mapped to `"document"` at line 684
  - Fokusregion tab: registered at lines 228–229, mapped to `"document"` at line 1225
- The type string `"document"` is passed to `GET /search?types=...` exactly like the other source types — no Python changes needed

**To enable once the API supports it:**
1. Open `ui/poliscope_plugin_dockwidget_base.ui` in Qt Designer
2. Find `cbDokumente_search` and `cbDokumente_focusregion`, set their `enabled` property to `true`
3. Save the `.ui` file — done

**If the API response structure for documents differs from meetings/proposals**, check `setResultsToList()` in `poliscope_plugin.py` and the `ResultGroup` / `ChunkHit` models in `api/poliscopeAPI.py`.

---

## Qt Designer workflow

- All UI layout is defined in `.ui` files under `ui/` — **better not to edit these by hand**, but to use Qt Designer
- Widget `objectName` values in Qt Designer must exactly match the names used in `findChild()` calls in `poliscope_plugin.py`
- To test changes in QGIS: reload via Plugin Reloader, then close and reopen the panel to trigger `run()` fresh
