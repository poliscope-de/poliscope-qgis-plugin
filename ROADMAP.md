# Poliscope Plugin v2 Rewrite — Roadmap

## Context
The plugin is being rewritten to use the new Poliscope API v2 (semantic vector search). The old API used MongoDB-style filter dicts with wind/solar scoring and status/bookmark systems. The new API uses a REST GET-based search with semantic/keyword modes, chunk-based results, and focus region saved searches. Nearly every layer of the plugin changes.

**Decisions confirmed:**
- Merkliste tab → repurposed as "Gespeicherte Suchen" (focus region setup/management)
- Search field (q) + Suchmodus + Quellen + Verwaltungsebene + Suchtiefe → Suche tab only
- Neuigkeiten tab stays slim (Focusregion results + date filter only)
- Gemeindeverbände & Gemeinden = one checkbox for levels 50+60
- No infinite scroll → single API call per search + client-side "Mehr laden" batching
- Date sort is client-side, per batch of 50, independent between batches

---

## What's Removed
- Wind/Solar score system (buttons, filters, display)
- Status filter (termin/vorlage/beschluss)
- Storage/bookmark filter (Gespeichert/Versteckt) + bookmark button in list items
- All v1 MongoDB-style filter builders in `api/poliscopeAPI.py`
- Sort dropdown → replaced by simple Relevanz / Datum toggle
- Infinite scroll

## What's Kept
- Date range filters (dateFrom / dateTo)
- Aktualisieren button (all tabs)
- BBox Suche / Zentrum Suche radio buttons → maps to `bbox` param
- Focus region selection (Neuigkeiten tab)
- API key config (gear icon → QSettings)
- `openLocationInQGIS()` zoom logic
- Coordinate transform utilities

---

## API Behaviour (v2 /search)

- **No offset/pagination parameter** — the API is purely limit-based
- One call returns up to `limit` result groups, sorted by relevance score descending
- `hasMore: true` in meta means more results likely exist beyond what was fetched
- All "load more" behaviour is **client-side only** (batching the returned results)
- `scoreThreshold` controls minimum relevance (semantic mode only); lower = broader recall

---

## Implementation Steps

### Step 1 — `api/poliscopeAPI.py` (complete rewrite)

**New base URL:** `https://api.poliscope.de/v2`
**Auth:** `Authorization: Bearer {api_key}` header (replaces query param)

**New data models:**
- `ChunkHit`: id, score, text, chunkType, highlights, agendaItemId, documentId, proposalId, poliscopeUrl
- `ResultContext`: date, entityName, entityLevel, entityId, parents[], location, meeting?, proposal?, document?
- `ResultGroup`: groupKey, groupType, score, hits (ChunkHit[]), totalHits, context (ResultContext)
- `MapPoint`: lat, lon, score, entityId, entityName, groupKey
- `MeetingDetail`: id, title, date, location, description, ris.entities[], documents[], agendaItems[]
- `ProposalDetail`: id, title, type, url, description, reference, documents[], agendaItems[]

**New API client class `PoliscopeAPI`:**
```
search(q, mode, types, entity_ids, bbox, levels, date_from, date_to, limit, score_threshold)
  → GET /search → list[ResultGroup], mapPoints[], meta{total, hasMore, ...}

get_focusregion_results(focusregion_id, new_since=None)
  → GET /focusregions/{id}/results → list[ResultGroup], mapPoints[], meta

get_focusregion_counts()
  → GET /focusregions/counts → dict[id → count]

get_meeting(id)
  → GET /meetings/{id}?detail=full → MeetingDetail

get_proposal(id)
  → GET /proposals/{id}?detail=full → ProposalDetail

list_entities(q, level, parent_id, state_id, limit, offset)
  → GET /entities → list[Entity], meta

get_focusregion(id)
  → GET /focusregions/{id} → focusregion info incl. covered entityIds (coming soon)

get_bookmarks()
  → GET /bookmarks → list of bookmarked ResultGroups (coming soon)

toggle_bookmark(meeting_id, add: bool)
  → PUT /bookmarks/{id} (add) or DELETE /bookmarks/{id} (remove) (coming soon)

get_qgis_plugin_version()
  → GET /health → version field
```

---

### Step 2 — `utils/utils.py`

**Remove:** `setPVScore()`, `setWindScore()`, `setLineIcon()`, `convertSortStringToAPI()`

**Keep (unchanged):** `get_current_canvas_bbox_polygon_epsg4326()`, `get_current_canvas_bbox_center_epsg4326()`, `format_date()`, `format_last_status_update()`, `buildRISBreadcrumbs()`, `convertRSTypes()`, `get_plugin_version()`, `load_svg_high_quality()`, `getLocationString()`, `getDocumentsCountString()`, `format_bytes()`, `slugify()`

**Update:**
- `buildRISBreadcrumbs()` → adapt to use `context.parents[]` array from v2 instead of flat grandparent fields

**Add:**
- `get_bbox_string(iface)` → returns `"west,south,east,north"` string for API `bbox` param
- `format_score(score)` → formats 0–1 float as display string (e.g. "87%")
- `convertLevelToDisplay(level)` → "10"→"Bundesland", "pr"→"Planungsregion", "40"→"Landkreis", "50"→"Verband", "60"→"Gemeinde"

---

### Step 3 — `ui/list_item_widget.ui`

**Remove:**
- 3× wind score buttons (pbWind1/2/3) + PV score buttons (pbPV1/2/3)
- Status line icon label (lStatus)
- Topics group box (gbTopics) with solar/wind keyword buttons
- Bookmark button (pbBookmark)

**Keep:** lLastStatusUpdate, lTitle, lDescription, lDate, lRISBreadcrumbs, lLocation, pbDetails, pbOpenRIS, pbWeb

**Add:**
- `lScore` label — shows relevance score (hidden in Neuigkeiten tab, visible in Suche tab)
- `lChunkType` label — shows groupType badge (Sitzung / Vorlage / Dokument)
- `lHitsPreview` label — shows first matching chunk text (truncated)

---

### Step 4 — `ui/detail_dialog.ui` + `ui/detail_dialog.py`

**Remove from UI:** wind/PV score display rows, status icon (lStatus), topics group box (gbTopics)

**Keep:** lTitle, lDate, lDescription, lRISBreadcrumbs, lLocation, tbAgendaItems, gbDocuments

**Logic changes in `detail_dialog.py`:**
- `openInDialog(result_group)` → accepts `ResultGroup` instead of `Meeting`
  - Loads full detail via `api.get_meeting(id)` or `api.get_proposal(id)` depending on `groupType`
  - Populates breadcrumbs from `context.parents[]`
  - For meetings: renders agendaItems HTML table (same structure as today)
  - For proposals: renders proposal description + documents
  - For documents: renders document metadata + download link
- Remove `setDocumentBoxes()` categories (invitation/beschluss/agenda) → simplify to single list
- Remove `setTopicToGroubbox()` entirely
- Keep `generate_agenda_html()` structure, update field names to v2
- Keep `adjustTextBrowserHeight()`

---

### Step 5 — `ui/poliscope_plugin_dockwidget_base.ui`

#### Neuigkeiten tab
Remove: score buttons (wind/PV), status filter row, storage filter row, sort dropdown (ComboBox)
Keep: date range (QgsDateTimeEdit from/to), Aktualisieren button, focus region checkboxes, collapsible filter box
Add:
- `cbxSortierung_news` — QComboBox, items: "Relevanz", "Datum (neueste zuerst)", "Datum (älteste zuerst)"
- `gbQuellen_news` — QgsCollapsibleGroupBox "Quellen" (default: open) with checkboxes:
  - `cbTOPs_news`, `cbTOPBeschreibungen_news`, `cbVorlagen_news`, `cbVorlagenBeschreibungen_news`, `cbDokumente_news` (all checked by default)
- `gbVerwaltungsebene_news` — QGroupBox "Verwaltungsebene" with checkboxes:
  - `cbPlanungsregionen_news`, `cbLandkreise_news`, `cbGemeindeverbaende_news` (all unchecked by default)
- `lblResultCount_news` — QLabel ""
- `pbMehrLaden_news` — QPushButton "Mehr laden" (hidden by default)

#### Suche tab
Remove: score buttons, status filter row, storage filter row
Keep: BBox/Zentrum Suche radio buttons, date range, Aktualisieren button
Add (inside collapsible filter box):

- `leQuery_search` — QLineEdit, placeholder "Suchbegriff eingeben…"

- `wBeliebteSuchen_search` — QWidget with Horizontal Layout (empty in Qt Designer, filled by code)
  - Code generates clickable QPushButton chips on load, click fills `leQuery_search` (editable)
  - Static list: Windkraft, Solarpark, Flächennutzungsplan, Bauleitplanung, Klimaschutz, Energiewende, Photovoltaik, Repowering, Regionalplan, Bebauungsplan

- `gbSucheinstellungen_search` — QgsCollapsibleGroupBox "Sucheinstellungen" (contains Suchmodus, Suchtiefe, Ergebnisqualität):
  - `gbSuchmodus_search` — QGroupBox "Suchmodus" with radio buttons:
    - `rbSemantisch_search` "Semantisch" (default)
    - `rbKeyword_search` "Keyword"
  - `gbSuchtiefe_search` — QGroupBox "Suchtiefe" with radio buttons:
    - `rbSchnellsuche_search` "Schnellsuche" — limit=50 (API searches ~150 candidates internally, default)
    - `rbTiefenrecherche_search` "Tiefenrecherche" — limit=250 (API searches ~750 candidates internally)
    - `rbUmfassend_search` "Umfassend" — limit=500 (API searches ~1500 candidates internally)
    - toolTip on gbSuchtiefe_search: "Höhere Suchtiefe erhöht die Ladezeit"
  - `gbErgebnisqualitaet_search` — QGroupBox "Ergebnisqualität" with radio buttons (hidden when Keyword mode active):
    - `rbTopTreffer_search` "Top-Treffer" — scoreThreshold=0.60
    - `rbAusgewogen_search` "Ausgewogen" — scoreThreshold=0.35 (API default)
    - `rbAlleTreffer_search` "Alle Treffer" — scoreThreshold=0.15
    - toolTip on gbErgebnisqualitaet_search: "Top-Treffer ≥0.60 | Ausgewogen ≥0.35 | Alle Treffer ≥0.15"

- `cbxSortierung_search` — QComboBox, items: "Relevanz", "Datum (neueste zuerst)", "Datum (älteste zuerst)"
  - Note: sort is client-side, applied per batch of 50 independently

- `gbQuellen_search` — QgsCollapsibleGroupBox "Quellen" (default: open) with checkboxes:
  - `cbTOPs_search` "TOPs" (agendaItemTitle)
  - `cbTOPBeschreibungen_search` "TOP Beschreibungen" (agendaItemDescription)
  - `cbVorlagen_search` "Vorlagen" (proposalTitle)
  - `cbVorlagenBeschreibungen_search` "Vorlagen Beschreibungen" (proposalDescription)
  - `cbDokumente_search` "Dokumente" (document)

- `gbVerwaltungsebene_search` — QGroupBox "Verwaltungsebene" with checkboxes:
  - `cbPlanungsregionen_search` "Planungsregionen" (pr)
  - `cbLandkreise_search` "Landkreise" (40)
  - `cbGemeindeverbaende_search` "Gemeindeverbände & Gemeinden" (50+60)

**Result list footer (below searchList):**
- `lblResultCount_search` — QLabel ""
- `pbMehrLaden_search` — QPushButton "Mehr laden" (hidden by default)

#### Merkliste tab
Keep bookmark list, adapt to v2.

**Confirmed with admin:**
- `GET /v2/bookmarks` — will be added (not yet live)
- Bookmark toggle `PUT`/`DELETE` — will be added (not yet live)
- `GET /v2/focusregions/{id}` — info endpoint incl. covered entityIds will be added

**Spatial filter — either/or radio buttons (all client-side after fetching all bookmarks):**
- `rbAlleAnzeigen_watchlist` — QRadioButton "Alle Anzeigen" (default, no spatial filter)
- `rbBbox_watchlist` — QRadioButton "Aktuelle Kartenansicht" → check bookmark `lat/lon` within current map bbox
- `rbZentrum_watchlist` — QRadioButton "Zentrum der Karte" → check bookmark `lat/lon` within radius of map center (haversine)
- `rbFokusregion_watchlist` — QRadioButton "Fokusregion" → shows `cbxFokusregion_watchlist` QComboBox; call `GET /focusregions/{id}` to get covered entityIds, filter bookmarks by entityId match

**Secondary filters (client-side, stacked on top of spatial filter):**
- `gbVerwaltungsebene_watchlist` — QGroupBox "Verwaltungsebene" with `cbPlanungsregionen_watchlist`, `cbLandkreise_watchlist`, `cbGemeindeverbaende_watchlist`
- `gbQuellen_watchlist` — QGroupBox "Quellen" with `cbTOPs_watchlist`, `cbTOPBeschreibungen_watchlist`, `cbVorlagen_watchlist`, `cbVorlagenBeschreibungen_watchlist`, `cbDokumente_watchlist`
- Date range: `mteBegin_watchlist` / `mteEnd_watchlist`
- `cbxSortierung_watchlist` — QComboBox: "Datum (neueste zuerst)", "Datum (älteste zuerst)"

**Result count:** reuse existing `lMeetingCount_watchlist` label — no new widget needed. No "Mehr laden" — always show all bookmarks.

**Jump to QGIS:**
- Each list item gets a small "In Karte zeigen" button → calls `openLocationInQGIS()` with bookmark's `context.location.lat/lon`

#### Hilfe tab
Update help text to reflect new tab descriptions (text provided separately).

---

### Step 6 — `poliscope_plugin.py` (major refactor)

**State variables — remove:** `filter_watchlist`, `sortString_*`, score/status/storage filter state, `currPage_*`

**State variables — add (Neuigkeiten tab, client-side only):**
- `sortMode_news` (str, default "relevanz")
- `sources_news` (list[str], default all 5 chunk types)
- `levels_news` (list[str], default empty = all levels)
- `results_news` (list[ResultGroup]) → full loaded result set, batched for display
- `displayedCount_news` (int) → how many results currently shown

**State variables — add (Suche tab):**
- `searchText_search` (str, default "")
- `searchMode_search` (str, default "semantic")
- `searchDepth_search` (str, default "schnellsuche") → limit: 50 / 250 / 500; API searches 3× internally
- `ergebnisqualitaet_search` (str, default "ausgewogen") → maps to `scoreThreshold` (0.60/0.35/0.15); ignored in keyword mode
- `sortMode_search` (str, default "relevanz")
- `sources_search` (list[str], default all 5 chunk types)
- `levels_search` (list[str], default empty = all levels)
- `results_search` (list[ResultGroup]) → full loaded result set, batched for display
- `displayedCount_search` (int) → how many results currently shown

**Method changes:**

| Method | Change |
|--------|--------|
| `run()` | swap API class to new `PoliscopeAPI` |
| `getFilters_news()` | returns `{focusregion_ids, new_since}` |
| `getFilters_search()` | returns `{q, mode, types, bbox, levels, date_from, date_to, limit, score_threshold}` |
| `btnHandlerRefresh_news()` | calls `api.get_focusregion_results()` per focusregion |
| `btnHandlerRefresh_search()` | calls `api.search()`, stores full result set, renders first 50 |
| `btnHandlerRefresh_watchlist()` | calls `api.get_bookmarks()` → stores in `results_watchlist` → applies current spatial + secondary filters → renders list |
| `spatialFilter_watchlist(results)` | new — applies bbox / zentrum / focusregion filter client-side |
| `applyFilters_watchlist()` | new — applies Verwaltungsebene + Quellen + date on top of spatial filter |
| `bookmarkButtonPressed(meeting_id)` | keep — calls `api.toggle_bookmark(meeting_id)` (TBD endpoint) |
| `openLocationInQGIS_watchlist(lat, lon)` | reuse existing `openLocationInQGIS()` logic |
| `setResultsToList()` (rename from `setMeetingsToList`) | renders a batch of ResultGroup objects |
| `loadNextBatch_search()` | new — reveals next 50 from `results_search`, sorts by date if needed |
| `sortAndSlice(results, sort_mode, offset, count)` | new — client-side sort + slice helper |
| `showDetailDialog()` | pass `ResultGroup` to DetailDialog |
| `bookmarkButtonPressed()` | remove |
| score/status/storage handlers | remove |
| `check_scroll_position_*()` | remove (infinite scroll gone) |
| `openLocationInQGIS()` | adapt to use `context.location.lat/lon` |

**"Mehr laden" logic:**
1. On Aktualisieren: fetch all results → store in `results_search` → show first 50 → update `lblResultCount`
2. If `len(results_search) > 50`: show `pbMehrLaden`
3. On "Mehr laden" click: call `loadNextBatch_search()` → append next 50 to list → update count label

---

## Files Modified

| File | Change |
|------|--------|
| `api/poliscopeAPI.py` | Complete rewrite |
| `utils/utils.py` | Remove 4 methods, add 3, update 1 |
| `ui/list_item_widget.ui` | Remove score/status/bookmark elements, add score/type/hits labels |
| `ui/detail_dialog.ui` | Remove score/topics elements |
| `ui/detail_dialog.py` | Rewrite `openInDialog()`, remove topic/score methods |
| `ui/poliscope_plugin_dockwidget_base.ui` | Remove score/status/storage; add search field, Suchmodus, Suchtiefe, Sortierung, Quellen, Verwaltungsebene, Mehr-laden footer |
| `poliscope_plugin.py` | Remove bookmark/score/status/scroll logic; add new filter + batching handlers |

## Files NOT Modified
- `ui/poliscope_plugin_dockwidget.py`
- `ui/list_item_widget.py`
- `ui/list_missing_api_key_error_widget.*`
- `ui/list_wrong_plugin_version_error_widget.*`
- `__init__.py`, `resources.qrc`, `resources_rc.py`, `metadata.txt`

---

## UI Checklist (Qt Designer)

Work through these in order. Widget names in `code` are the objectName to set in Qt Designer.

---

### 1. `poliscope_plugin_dockwidget_base.ui`

#### Tab: Neuigkeiten
- [x] Remove wind score buttons (all 3)
- [x] Remove PV/Solar score buttons (all 3)
- [x] Remove status filter row (Alle / Mit Beschlussvorlage / Nur Beschlüsse)
- [x] Remove storage filter row (Gespeichert / Nicht gespeichert / Versteckt)
- [x] Change sort dropdown: `cbxSortierung_news` — QComboBox, items: "Relevanz", "Datum (neueste zuerst)", "Datum (älteste zuerst)"
- [x] Add `gbQuellen_news` — QgsCollapsibleGroupBox "Quellen" (default: open) with:
  - [x] `cbTOPs_news` — QCheckBox "TOPs" (checked by default)
  - [x] `cbTOPBeschreibungen_news` — QCheckBox "TOP Beschreibungen" (checked by default)
  - [x] `cbVorlagen_news` — QCheckBox "Vorlagen" (checked by default)
  - [x] `cbVorlagenBeschreibungen_news` — QCheckBox "Vorlagen Beschreibungen" (checked by default)
  - [x] `cbDokumente_news` — QCheckBox "Dokumente" (checked by default)
- [x] Add `gbVerwaltungsebene_news` — QGroupBox "Verwaltungsebene" with:
  - [x] `cbPlanungsregionen_news` — QCheckBox "Planungsregionen" (unchecked by default)
  - [x] `cbLandkreise_news` — QCheckBox "Landkreise" (unchecked by default)
  - [x] `cbGemeindeverbaende_news` — QCheckBox "Gemeindeverbände & Gemeinden" (unchecked by default)
- [x] Add below `newsList` (result list footer):
  - [x] `lblResultCount_news` — QLabel ""
  - [x] `pbMehrLaden_news` — QPushButton "Mehr laden" (hidden by default)

Note: Suchmodus, Suchtiefe, Relevanz not added here — these are API-side params not supported by `/focusregions/{id}/results`

#### Tab: Suche
- [x] Remove wind score buttons (all 3)
- [x] Remove PV/Solar score buttons (all 3)
- [x] Remove status filter row
- [x] Remove storage filter row
- [x] Remove sort dropdown
- [x] Add `leQuery_search` — QLineEdit, placeholder "Suchbegriff eingeben…"
- [ ] Add `wBeliebteSuchen_search` — QWidget with Horizontal Layout (below leQuery_search)
- [x] Add `gbSucheinstellungen_search` — QgsCollapsibleGroupBox "Sucheinstellungen" containing:
  - [x] `gbSuchmodus_search` — QGroupBox "Suchmodus" with:
    - [x] `rbSemantisch_search` — QRadioButton "Semantisch" (checked by default)
    - [x] `rbKeyword_search` — QRadioButton "Keyword"
  - [x] `gbSuchtiefe_search` — QGroupBox "Suchtiefe" with:
    - [x] `rbSchnellsuche_search` — QRadioButton "Schnellsuche" (checked by default)
    - [x] `rbTiefenrecherche_search` — QRadioButton "Tiefenrecherche"
    - [x] `rbUmfassend_search` — QRadioButton "Umfassend"
    - [x] toolTip on gbSuchtiefe_search: "Höhere Suchtiefe erhöht die Ladezeit"
  - [x] `gbErgebnisqualitaet_search` — QGroupBox "Ergebnisqualität" with:
    - [x] `rbTopTreffer_search` — QRadioButton "Top-Treffer"
    - [x] `rbAusgewogen_search` — QRadioButton "Ausgewogen" (checked by default)
    - [x] `rbAlleTreffer_search` — QRadioButton "Alle Treffer"
    - [x] toolTip on gbErgebnisqualitaet_search: "Top-Treffer ≥0.60 | Ausgewogen ≥0.35 | Alle Treffer ≥0.15"
- [x] Add `cbxSortierung_search` — QComboBox, items: "Relevanz", "Datum (neueste zuerst)", "Datum (älteste zuerst)"
- [x] Add `gbQuellen_search` — QgsCollapsibleGroupBox "Quellen" (default: open) with:
  - [x] `cbTOPs_search` — QCheckBox "TOPs" (checked by default)
  - [x] `cbTOPBeschreibungen_search` — QCheckBox "TOP Beschreibungen" (checked by default)
  - [x] `cbVorlagen_search` — QCheckBox "Vorlagen" (checked by default)
  - [x] `cbVorlagenBeschreibungen_search` — QCheckBox "Vorlagen Beschreibungen" (checked by default)
  - [x] `cbDokumente_search` — QCheckBox "Dokumente" (checked by default)
- [x] Add `gbVerwaltungsebene_search` — QGroupBox "Verwaltungsebene" with:
  - [x] `cbPlanungsregionen_search` — QCheckBox "Planungsregionen" (unchecked by default)
  - [x] `cbLandkreise_search` — QCheckBox "Landkreise" (unchecked by default)
  - [x] `cbGemeindeverbaende_search` — QCheckBox "Gemeindeverbände & Gemeinden" (unchecked by default)
- [x] Add below `searchList` (result list footer):
  - [x] `lblResultCount_search` — QLabel ""
  - [x] `pbMehrLaden_search` — QPushButton "Mehr laden" (hidden by default)

#### Tab: Merkliste
- [ x] Keep existing bookmark list widget (`watchlistList`), remove old score/status/storage filter rows
- [ x] Add spatial filter section (either/or radio buttons):
  - [x ] `rbAlleAnzeigen_watchlist` — QRadioButton "Alle Anzeigen" (checked by default)
  - [ x] `rbBbox_watchlist` — QRadioButton "Aktuelle Kartenansicht"
  - [x ] `rbZentrum_watchlist` — QRadioButton "Zentrum der Karte"
  - [x ] `rbFokusregion_watchlist` — QRadioButton "Fokusregion" + `cbxFokusregion_watchlist` QComboBox (enabled only when rbFokusregion checked)
- [x ] Add `gbVerwaltungsebene_watchlist` — QGroupBox "Verwaltungsebene" with:
  - [ x] `cbPlanungsregionen_watchlist`, `cbLandkreise_watchlist`, `cbGemeindeverbaende_watchlist`
- [x ] Add `gbQuellen_watchlist` — QGroupBox "Quellen" with:
  - [ x] `cbTOPs_watchlist`, `cbTOPBeschreibungen_watchlist`, `cbVorlagen_watchlist`, `cbVorlagenBeschreibungen_watchlist`, `cbDokumente_watchlist`
- [ x] Add date range: `mteBegin_watchlist` / `mteEnd_watchlist`
- [ x] Add `cbxSortierung_watchlist` — QComboBox: "Datum (neueste zuerst)", "Datum (älteste zuerst)"
- note: `lMeetingCount_watchlist` already exists in code → reuse for count display, no new label needed
- no "Mehr laden" — Merkliste always shows all bookmarks

#### Tab: Hilfe
- [ x] Update help text to reflect new tab descriptions (Neuigkeiten / Suche / Merkliste)

---

### 2. `list_item_widget.ui`

- [ x] Remove `pbWind1`, `pbWind2`, `pbWind3` — wind score buttons
- [ x] Remove `pbPV1`, `pbPV2`, `pbPV3` — solar score buttons
- [ x] Remove `gbTopics` — topics group box (solar/wind keywords)
- [x] Keep `pbBookmark` — bookmark button (admin confirmed server-side bookmarks coming)
- [x ] Add `lScore` — QLabel (relevance score, e.g. "87%")
- [ x] Add `lChunkType` — QLabel (group type badge: "Sitzung" / "Vorlage" / "Dokument")
- [ x] Add `lHitsPreview` — QLabel (first matching chunk text, word-wrap enabled)

---

### 3. `detail_dialog.ui`

- [ ] Remove wind score button row (`pbWind1`, `pbWind2`, `pbWind3`)
- [ ] Remove PV score button row (`pbPV1`, `pbPV2`, `pbPV3`)
- [ ] Remove `lStatus` — status icon label
- [ ] Remove `gbTopics` — topics group box

---

## Open Questions
- none currently

---

## Verification Checklist
- [ ] Plugin loads in QGIS without errors
- [ ] Neuigkeiten: select focusregion + date range → results from `/focusregions/{id}/results`
- [ ] Suche: enter query, BBox Suche, Schnellsuche → results from `/search`, first 50 shown
- [ ] Suche: "Mehr laden" → next 50 appended, count label updates
- [ ] Suche: `hasMore=true` → hint label visible
- [ ] Suche: switch to "Datum" sort → current batch re-sorted by date, next batch also sorted independently
- [ ] Suche: switch Keyword mode → `mode=keyword` in request
- [ ] Suche: uncheck Quellen → `types` param reflects selection
- [ ] Suche: check Landkreise only → `levels=40` in request
- [ ] Suche: Tiefenrecherche → higher limit in request, latency warning shown
- [ ] Click result → DetailDialog shows correct groupType (Sitzung/Vorlage/Dokument)
- [ ] Merkliste: shows focus regions list with counts
- [ ] No score buttons, no bookmark button anywhere
