"""
Poliscope API v2 client.

Provides the PoliscopeAPI class for communicating with the Poliscope REST API
(https://api.poliscope.de/v2). All endpoints use Bearer token authentication.

Data classes defined here map raw API JSON responses to typed Python objects.
Each class implements a from_dict() classmethod for parsing API responses.

Usage:
    api = PoliscopeAPI(api_key="your_key")
    result_groups, map_points, meta = api.search("Windpark")
    meeting = api.get_meeting("some-id")
"""
from dataclasses import dataclass
from typing import List, Tuple, Optional, Dict, Any
import requests

# ---------------------------------------------------------------------------
# DATA MODELS
# ---------------------------------------------------------------------------
# Each class maps one API response schema to typed Python attributes.
# Use from_dict() to parse a raw JSON dict returned by the API.
# ---------------------------------------------------------------------------

@dataclass
class FileSummary:
    """
    Metadata for a file attachment, including its download URL.
    Used inside DocumentSummary to reference downloadable files.

    Fields:
        id           — unique file identifier
        file_name    — original file name. Optional.
        mime_type    — MIME type (e.g. "application/pdf"). Optional.
        download_url — direct download URL for the file.
    """
    id: str
    file_name: Optional[str]
    mime_type: Optional[str]
    download_url:str

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'FileSummary':
        return cls(
            id = data.get('id', ""),
            file_name = data.get('fileName'),
            mime_type = data.get('mimeType'),
            download_url= data.get("downloadUrl", "")
        )

@dataclass
class UserSummary:
    """
    A lightweight user reference, used to identify who bookmarked a meeting.

    Fields:
        id         — unique user identifier
        first_name — user's first name. Optional.
        last_name  — user's last name. Optional.
    """
    id: str
    first_name: Optional[str]
    last_name: Optional[str]

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UserSummary':
        return cls(
            id = data.get("id", ""),
            first_name= data.get('firstName'),
            last_name=data.get('lastName')
        )
@dataclass
class MapPoint:
    """
    A single geo-located point for map rendering.

    Returned alongside search results to place result groups on the map.
    Each MapPoint corresponds to exactly one ResultGroup and represents
    the geographic location of its source entity. Scores are normalised
    to 0–1 regardless of search mode, making them suitable for controlling
    visual rendering (e.g. dot size or opacity) but not for comparing
    relevance across results.

    Fields:
        location    — geographic coordinates {"lat", "lon"} of the source
                      entity in WGS84.
        score       — normalised relevance score (0–1), intended for visual
                      rendering. Not comparable to ChunkHit scores.
        entity_id   — Regionalschlüssel (RS code) of the source entity.
        entity_name — display name of the source entity.
        group_key   — unique group key matching the corresponding ResultGroup
                      in data[]. Use this to cross-reference map points with
                      search results.
    """
    location: Dict[str, float]
    score: float
    entity_id: str
    entity_name: str
    group_key: str

    @classmethod
    def from_dict(cls, data:Dict[str, Any]) -> 'MapPoint':
        return cls(
            location = data.get('location', {}),
            score = data.get('score', 0.0),
            entity_id = data.get('entityId', ""),
            entity_name = data.get('entityName', ""),
            group_key = data.get('groupKey', "")

        )    

@dataclass
class ChunkHit:
    """
    A single matching text chunk within a search result group.

    The v2 API segments source documents, agenda items, and proposals into
    discrete text chunks and searches across them. Each ChunkHit represents
    one such chunk that matched the search query. A ResultGroup contains
    up to 3 ChunkHits, sorted by relevance score descending.

    Fields:
        id             — composite chunk identifier in the format 'groupKey:index'
        score          — relevance score. Semantic mode: 0–1 (higher is more
                         relevant). Keyword mode: unbounded. Scores are not
                         comparable across modes.
        text           — full text of the matching chunk
        chunk_type     — content category of this chunk. One of:
                         'agendaItemTitle', 'agendaItemDescription',
                         'proposalTitle', 'proposalDescription', 'document'
        highlights     — character offset pairs [startOffset, endOffset] within
                         text, marking literal query term matches. Optional —
                         only present when query terms appear literally in text.
        agenda_item_id — ID of the source agenda item, if applicable. Optional.
        document_id    — ID of the source document, if applicable. Optional.
        proposal_id    — ID of the source proposal, if applicable. Optional.
        poliscope_url  — relative URL path to view this hit in the Poliscope
                         web app. Optional.
    """
    id: str
    score: float
    text: str
    chunk_type: str
    highlights: Optional[List[Tuple[int, int]]]
    agenda_item_id: Optional[str]
    document_id: Optional[str]
    proposal_id: Optional[str]
    poliscope_url: Optional[str]

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ChunkHit':
        return cls(
            id=data.get('id', ""),
            score=data.get('score', 0.0),
            text=data.get('text', ""),
            chunk_type=data.get('chunkType', ""),
            highlights=data.get('highlights'),
            agenda_item_id=data.get('agendaItemId'),
            document_id=data.get("documentId"),                                                                                                       
            proposal_id=data.get("proposalId"),                                                                                                       
            poliscope_url=data.get("poliscopeUrl")
        )
    
@dataclass
class ResultContext:
    """
    Contextual metadata for a search result group.

    Provides the administrative and geographic context of a ResultGroup,
    identifying the source entity (municipality, district, etc.) and the
    specific item (meeting, proposal, or document) the result originates from.
    Exactly one ResultContext is present per ResultGroup.

    Fields:
        date         — datetime of the source item (ISO 8601). Optional.
        entity_name  — display name of the administrative entity
                       (e.g. "Gemeinde Freren")
        entity_level — administrative level of the entity:
                       0=Deutschland, 10=Bundesland, pr=Planungsregion,
                       40=Landkreis, 50=Verbandsgemeinde, 60=Kommune
        entity_id    — Regionalschlüssel (RS code) uniquely identifying the
                       administrative entity (e.g. "03404")
        parents      — ordered list of parent entities (e.g. Landkreis,
                       Bundesland), each as {"id", "name", "level"}.
                       Used to construct breadcrumb navigation.
        location     — geographic coordinates {"lat", "lon"} of the entity
                       in WGS84. Optional. Used for map rendering.
        meeting      — populated when groupType is 'meeting'. Contains
                       id, title, date, url, committee, bookmarks.
        proposal     — populated when groupType is 'proposal'. Contains
                       id, title, type, url, reference.
        document     — populated when groupType is 'document'. Contains
                       id, title, type, url.
    """
    date: Optional[str]
    entity_name: str
    entity_level: str
    entity_id: str
    parents: List[Dict[str, str]]
    location: Optional[Dict[str, float]]
    meeting: Optional[Dict[str, Any]]
    proposal: Optional[Dict[str, Any]]
    document: Optional[Dict[str, Any]]

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ResultContext':
        return cls(
            date = data.get('date'),
            entity_name = data.get('entityName', ""),
            entity_level = data.get('entityLevel', ""),
            entity_id = data.get('entityId', ""),
            parents = data.get('parents', []),
            location = data.get('location'),
            meeting = data.get('meeting'),
            proposal = data.get('proposal'),
            document = data.get('document')
        )

@dataclass
class ResultGroup:
    """
    A grouped search result representing one source item (meeting, proposal, or document).

    The v2 API groups matching text chunks by their source item. Each ResultGroup
    contains the top 3 matching ChunkHits for that item, the overall relevance
    score, and a ResultContext describing where and when the item originates from.
    Results are sorted by score descending.

    Fields:
        group_key           — unique identifier for this group, e.g.
                              'meeting:0f91effc-7d62-4e24-b4af-f887b08e65f7'.
                              Can be used to cross-reference with mapPoints[].
        group_type          — type of the source item: 'meeting', 'proposal',
                              or 'document'. Determines which detail endpoint
                              to call and how to render the detail dialog.
        group_creation_date — ISO 8601 datetime when this item was first
                              ingested into the search index. Optional.
        score               — highest relevance score among all hits in this
                              group. Groups are sorted by this value descending.
        hits                — top matching ChunkHits (max 3, sorted by score
                              descending). Use hits[0].text for the preview.
        total_hits          — total number of matching chunks found for this
                              group before the per-group limit of 3 is applied.
        context             — contextual metadata (entity, location, date,
                              meeting/proposal/document info). See ResultContext.
    """

    group_key: str
    group_type: str
    group_creation_date: Optional[str]
    score: float
    hits: List[ChunkHit]
    total_hits: int
    context: ResultContext

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ResultGroup':
        return cls(
            group_key = data.get('groupKey', ""),
            group_type = data.get('groupType', ""),
            group_creation_date = data.get('groupCreationDate'),
            score = data.get('score', 0.0),
            hits = [ChunkHit.from_dict(h) for h in data.get('hits', [])],
            total_hits = data.get('totalHits', 0),
            context = ResultContext.from_dict(data.get('context', {}))
        )
    
@dataclass
class DocumentSummary:
    """
    A reference to a document attached to a meeting or agenda item.

    Contains the document's ID, type, and an optional file attachment.
    Used inside Meeting and AgendaItem. For downloading the file, use
    the FileSummary.download_url field.

    Fields:
        id           — unique document identifier
        type         — document category (e.g. 'invitation', 'protocol'). Optional.
        original_url — original source URL of the document. Optional.
        file         — file attachment metadata including download URL. Optional —
                       not all documents have an associated file.
    """
    id: str
    type: Optional[str]
    original_url: Optional[str]
    file: Optional[FileSummary]

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DocumentSummary':
        return cls(
            id = data.get('id', ""),
            type = data.get('type'),
            original_url = data.get('originalUrl'),
            file = FileSummary.from_dict(data['file']) if data.get('file') else None
        )


@dataclass
class MeetingSummary:
    """
    Lightweight meeting reference used inside AgendaItem.

    A reduced version of Meeting containing only the fields needed to
    identify and locate a meeting without loading full detail. Used when
    an AgendaItem needs to reference its parent meeting.

    Fields:
        id         — unique meeting identifier
        title      — meeting title. Optional.
        date       — meeting datetime (ISO 8601, no timezone). Optional.
        location   — geographic coordinates {"lat", "lon"} of the meeting's
                     entity. Required by the spec.
        created_at — record creation timestamp (ISO 8601). Optional.
    """
    id: str
    title: Optional[str]
    date: Optional[str]
    location: Optional[Dict[str, float]]
    created_at: Optional[str]

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MeetingSummary':
        return cls(
            id=data.get('id', ""),
            title=data.get('title'),
            date=data.get('date'),
            location=data.get('location'),
            created_at=data.get('createdAt')
        )


@dataclass
class AgendaItem:
    """
    A single agenda item (Tagesordnungspunkt) within a meeting.

    Agenda items are the individual topics discussed in a meeting. Each
    can have a title, description, voting result, attached documents, and
    a reference back to its parent meeting.

    Fields:
        id          — unique agenda item identifier
        number      — display number within the meeting (e.g. "3.2"). Optional.
        title       — agenda item title. Optional.
        description — full text description. Optional.
        url         — source URL in the RIS. Optional.
        voting      — voting result and resolution text as a dict. Optional.
                      Contains 'result' (yes/no/abstain/recusal counts) and
                      'resolution' (text of the resolution passed).
        documents   — list of attached documents.
        meeting     — reference to the parent meeting. Optional — only present
                      when the agenda item is returned outside of a full Meeting.
    """
    id: str
    number: Optional[str]
    title: Optional[str]
    description: Optional[str]
    url: Optional[str]
    voting: Optional[Dict[str, Any]]
    documents: List[DocumentSummary]
    meeting: Optional[MeetingSummary]

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AgendaItem':
        return cls(
            id=data.get('id', ""),
            number=data.get('number'),
            title=data.get('title'),
            description=data.get('description'),
            url=data.get('url'),
            voting=data.get('voting'),
            documents=[DocumentSummary.from_dict(d) for d in data.get('documents', [])],
            meeting=MeetingSummary.from_dict(data['meeting']) if data.get('meeting') else None
        )


@dataclass
class Meeting:
    """
    Full meeting detail, returned by GET /meetings/{id}.

    Represents a council meeting (Sitzung) with all its metadata, agenda
    items, documents, and bookmarks. This is the detail object loaded when
    a user clicks a meeting result in the plugin.

    Fields:
        id           — unique meeting identifier
        title        — meeting title. Optional.
        date         — meeting datetime (ISO 8601, no timezone). Optional.
        location     — geographic coordinates {"lat", "lon"}. Optional.
        created_at   — record creation timestamp (ISO 8601). Optional.
        description  — meeting description text. Optional.
        ris          — RIS metadata including the list of associated entities.
                       Always present. Contains 'entities' array with id/name/level.
        documents    — list of documents attached directly to the meeting.
        agenda_items — list of agenda items (Tagesordnungspunkte).
        bookmarks    — list of users who bookmarked this meeting.
    """
    id: str
    title: Optional[str]
    date: Optional[str]
    location: Optional[Dict[str, float]]
    created_at: Optional[str]
    description: Optional[str]
    ris: Dict[str, Any]
    documents: List[DocumentSummary]
    agenda_items: List[AgendaItem]
    bookmarks: List[UserSummary]

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Meeting':
        return cls(
            id=data.get('id', ""),
            title=data.get('title'),
            date=data.get('date'),
            location=data.get('location'),
            created_at=data.get('createdAt'),
            description=data.get('description'),
            ris=data.get('ris', {}),
            documents=[DocumentSummary.from_dict(d) for d in data.get('documents', [])],
            agenda_items=[AgendaItem.from_dict(a) for a in data.get('agendaItems', [])],
            bookmarks=[UserSummary.from_dict(u) for u in data.get('bookmarks', [])]
        )


@dataclass
class Proposal:
    """
    Full proposal detail, returned by GET /proposals/{id}.

    Represents a legislative proposal (Vorlage) with its metadata, attached
    documents, and related agenda items. Loaded when a user clicks a proposal
    result in the plugin.

    Fields:
        id             — unique proposal identifier
        title          — proposal title. Optional.
        type           — proposal category (e.g. 'Beschlussvorlage'). Optional.
        url            — source URL in the RIS. Optional.
        description    — full proposal text. Optional.
        reference      — official reference number. Optional.
        case_reference — case reference number. Optional.
        documents      — list of attached documents.
        agenda_items   — list of agenda items this proposal appears in.
        external_id    — external system identifier. Optional.
    """
    id: str
    title: Optional[str]
    type: Optional[str]
    url: Optional[str]
    description: Optional[str]
    reference: Optional[str]
    case_reference: Optional[str]
    documents: List[DocumentSummary]
    agenda_items: List[AgendaItem]
    external_id: Optional[str]

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Proposal':
        return cls(
            id=data.get('id', ""),
            title=data.get('title'),
            type=data.get('type'),
            url=data.get('url'),
            description=data.get('description'),
            reference=data.get('reference'),
            case_reference=data.get('caseReference'),
            documents=[DocumentSummary.from_dict(d) for d in data.get('documents', [])],
            agenda_items=[AgendaItem.from_dict(a) for a in data.get('agendaItems', [])],
            external_id=data.get('externalId')
        )
    

@dataclass
class Entity:
    """
    An administrative entity (Verwaltungseinheit) such as a municipality,
    district, or planning region.

    Returned by GET /entities. Field availability depends on the 'detail'
    level requested: summary returns only id, name, level. standard and full
    return all fields.

    Fields:
        id           — Regionalschlüssel (RS code) uniquely identifying the entity
        name         — display name (e.g. "Aachen, Stadt")
        level        — administrative level: "10"=Bundesland, "pr"=Planungsregion,
                       "40"=Landkreis, "50"=Verbandsgemeinde, "60"=Kommune
        population   — population count. Optional.
        area         — area in km². Optional.
        postal_code  — postal code. Optional.
        city         — city name. Optional.
        street       — street address. Optional.
        location     — geographic coordinates {"lat", "lon"} in WGS84. Optional.
        ris          — RIS metadata including provider and associated entities. Optional.
        parent       — RS code of the parent entity. Optional.
        state        — RS code of the Bundesland this entity belongs to. Optional.
        weblinks     — list of related web links. Optional.
        ai_summary   — AI-generated summary text. Optional.
        ai_summary_date — date the AI summary was generated (ISO 8601). Optional.
    """
    id: str
    name: str
    level: str
    population: Optional[int]
    area: Optional[float]
    postal_code: Optional[str]
    city: Optional[str]
    street: Optional[str]
    location: Optional[Dict[str, float]]
    ris: Optional[Dict[str, Any]]
    parent: Optional[str]
    state: Optional[str]
    weblinks: Optional[List[Dict[str, Any]]]
    ai_summary: Optional[str]
    ai_summary_date: Optional[str]

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Entity':
        return cls(
            id = data.get('id', ""),
            name = data.get('name', ""),
            level = data.get('level', "10"),
            population = data.get('population'),
            area = data.get('area'),
            postal_code = data.get('postalCode'),
            city = data.get('city'),
            street = data.get('street'),
            location = data.get('location'),
            ris = data.get('ris'),
            parent = data.get('parent'),
            state = data.get('state'),
            weblinks = data.get('weblinks'),
            ai_summary = data.get('aiSummary'),
            ai_summary_date = data.get('aiSummaryDate')
        )


class PoliscopeAPI:
    """
    HTTP client for the Poliscope API v2.                                                                                                                                                
    Handles authentication and provides one method per API endpoint.                                                                                            
    All methods return typed Python objects built from the data classes                                                                                         
    defined above.

    Usage:
        api = PoliscopeAPI(api_key="your_key")
        results = api.search("Windpark")
    """
    BASE_URL = "https://api.poliscope.de/v2"

    def __init__(self, api_key: str):
        self.headers = {
            "Authorization": f"Bearer {api_key}"
        }

    def get_qgis_plugin_version(self) -> Optional[str]:
        """
        Fetch the minimum required QGIS plugin version from the API health endpoint.
        Used at startup to check whether the installed plugin version is still compatible.
        Returns the version string (e.g. "2.1.0") or None on error.
        """
        try:    
            response = requests.get(f"{self.BASE_URL}/health", headers=self.headers)
            if response.status_code == 200:
                data = response.json()
                return data.get("version")
            else:
                print(f"[Fehler] Status {response.status_code}: {response.text}")
                return None
        except Exception as e:
            print(f"[Exception] Fehler beim Abrufen der Plugin-Version: {e}")
        return None

    
    def get_entity(self, id: str, detail=None):
        """
        Fetch a single administrative entity by its Regionalschlüssel (RS code).
        Returns an Entity object, or None on error or if not found.

        Parameters:
            id     — Regionalschlüssel of the entity (e.g. "083355001001"). Required.
            detail — response detail level: "summary", "standard" (default), or "full"
        """
        params = {}
        if detail is not None:
            params["detail"] = detail

        try:
            response = requests.get(f"{self.BASE_URL}/entities/{id}", headers=self.headers, params=params)
            if response.status_code == 200:
                data = response.json()
                return Entity.from_dict(data["data"])
            else:
                print(f"[Fehler] Status {response.status_code}: {response.text}")
                return None
        except Exception as e:
            print(f"[Exception] Fehler beim Abrufen der Verwaltungseinheit: {e}")
        return None
    
    def get_file(self, id: str):
        """
        Fetch file metadata by ID, including the download URL.
        Returns a FileSummary object, or None on error or if not found.

        Parameters:
            id — unique file identifier. Required.
        """
        try:
            response = requests.get(f"{self.BASE_URL}/files/{id}", headers=self.headers)
            if response.status_code == 200:
                data = response.json()
                return FileSummary.from_dict(data["data"])
            else:
                print(f"[Fehler] Status {response.status_code}: {response.text}")
                return None
        except Exception as e:
            print(f"[Exception] Fehler beim Abrufen der Datei: {e}")
        return None
    
    def get_focusregion_counts(self):
        """
        Fetch the number of new search results per focus region for the authenticated user.
        Counts are based on each focus region's saved query and the user's last visit timestamp.
        Returns a dict mapping focus region ID to count (e.g. {"7adfa2c6-...": 5}),
        or None on error.
        """
        try:
            response = requests.get(f"{self.BASE_URL}/focusregions/counts", headers=self.headers)
            if response.status_code == 200:
                data = response.json()
                return data["data"]
            else:
                print(f"[Fehler] Status {response.status_code}: {response.text}")
                return None
        except Exception as e:
            print(f"[Exception] Fehler beim Abrufen der Fokusregionanzahl: {e}")
        return None
    
    def get_focusregion_results(self, id: str, new_since=None):
        """
        Execute a saved focus region search and return results.
        The authenticated user must be a member of the focus region's team.
        Returns a tuple (list[ResultGroup], list[MapPoint], meta), or (None, None, None) on error.

        Parameters:
            id        — focus region ID. Required.
            new_since — only return results ingested since this date (ISO 8601, e.g. "2024-01-01").
                        Useful for polling new content since the last check. Optional.
        """
        params = {}
        if new_since is not None:
            params["newSince"] = new_since

        try:
            response = requests.get(f"{self.BASE_URL}/focusregions/{id}/results", headers=self.headers, params=params)
            if response.status_code == 200:
                data = response.json()
                result_groups = [ResultGroup.from_dict(r) for r in data["data"]]
                map_points = [MapPoint.from_dict(m) for m in data["mapPoints"]]
                meta = data["meta"]
                return result_groups, map_points, meta
            else:
                print(f"[Fehler] Status {response.status_code}: {response.text}")
                return None, None, None
        except Exception as e:
            print(f"[Exception] Fehler beim Abrufen der Fokusregionergebnisse: {e}")
        return None, None, None
    
    def get_meeting(self, id: str, detail=None):
        """
        Fetch a single meeting by ID, including its agenda items, documents, and bookmarks.
        Returns a Meeting object, or None on error or if not found.

        Parameters:
            id     — unique meeting identifier. Required.
            detail — response detail level: "summary", "standard" (default), or "full"
        """

        params = {}
        if detail is not None:
            params["detail"] = detail

        try:
            response = requests.get(f"{self.BASE_URL}/meetings/{id}", headers=self.headers, params=params)
            if response.status_code == 200:
                data = response.json()
                return Meeting.from_dict(data["data"])
            else:
                print(f"[Fehler] Status {response.status_code}: {response.text}")
                return None
        except Exception as e:
            print(f"[Exception] Fehler beim Abrufen der Sitzung: {e}")
        return None
    
    def get_proposal(self, id: str, detail=None):
        """
        Fetch a single proposal by ID, including its documents and agenda items.
        Returns a Proposal object, or None on error or if not found.

        Parameters:
            id     — unique proposal identifier. Required.
            detail — response detail level: "summary", "standard" (default), or "full"
        """

        params = {}
        if detail is not None:
            params["detail"] = detail

        try:
            response = requests.get(f"{self.BASE_URL}/proposals/{id}", headers=self.headers, params=params)
            if response.status_code == 200:
                data = response.json()
                return Proposal.from_dict(data["data"])
            else:
                print(f"[Fehler] Status {response.status_code}: {response.text}")
                return None
        except Exception as e:
            print(f"[Exception] Fehler beim Abrufen der Vorlage: {e}")
        return None
    
    def list_entities(self, q=None, level=None, parent_id=None, state_id=None, limit=None, offset=None, detail=None):
        """
        List administrative entities with optional filtering and pagination.
        Returns a tuple (list[Entity], meta) where meta contains pagination info,
        or (None, None) on error.

        Parameters:
            q         — filter by name (case-insensitive substring)
            level     — filter by administrative level ("10", "40", "50", "60", "pr")
            parent_id — filter by parent entity RS code
            state_id  — filter by Bundesland RS code
            limit     — max results to return (default 10, max 500)
            offset    — pagination offset (default 0)
            detail    — response detail level: "summary", "standard", or "full"
        """
        params = {
            "q": q,
            "level": level,
            "parentId": parent_id,
            "stateId": state_id,
            "limit": limit,
            "offset": offset,
            "detail": detail
        }
        params = {k: v for k, v in params.items() if v is not None}

        try:
            response = requests.get(f"{self.BASE_URL}/entities", headers=self.headers, params=params)
            if response.status_code == 200:
                data = response.json()
                entities = [Entity.from_dict(item) for item in data["data"]]
                meta = data["meta"]
                return entities, meta
            else:
                print(f"[Fehler] Status {response.status_code}: {response.text}")
                return (None, None)
        except Exception as e:
            print(f"[Exception] Fehler beim Abrufen der Verwaltungseinheiten: {e}")
        return (None, None)
    
    def list_meetings(self, limit=None, offset=None, detail=None, entity_ids=None, from_date=None, to_date=None):
        """
        List meetings with optional filtering and pagination.
        For text search, use search() instead.
        Returns a tuple (list[Meeting], meta) where meta contains pagination info,
        or (None, None) on error.

        Parameters:
            limit      — max results to return (API default 10, max 500)
            offset     — pagination offset (API default 0)
            detail     — response detail level: "summary" (API default), "standard", or "full"
            entity_ids — comma-separated RS codes to filter by entity, supports * prefix matching
                         (e.g. "01*" for all of Schleswig-Holstein)
            from_date  — filter meetings from this date inclusive (ISO 8601, e.g. "2024-01-01")
            to_date    — filter meetings up to this date inclusive (ISO 8601)
        """
        params={
            "limit": limit,
            "offset": offset,
            "detail": detail,
            "entityIds": entity_ids,
            "fromDate": from_date,
            "toDate": to_date
        }
        params = {k: v for k, v in params.items() if v is not None}

        try:
            response = requests.get(f"{self.BASE_URL}/meetings", headers=self.headers, params=params)
            if response.status_code == 200:
                data = response.json()
                meetings = [Meeting.from_dict(item) for item in data["data"]]
                meta = data["meta"]
                return meetings, meta
            else:
                print(f"[Fehler] Status {response.status_code}: {response.text}")
                return (None, None)
        except Exception as e:
            print(f"[Exception] Fehler beim Abrufen der Sitzungsliste: {e}")
        return (None, None)
    
    def search(self, q: str, mode=None, types=None, entity_ids=None, bbox=None, levels=None, date_from=None, date_to=None, new_since=None, limit=None, score_threshold=None):
        """
        Universal search across meetings, proposals, and documents.
        Returns a tuple (list[ResultGroup], list[MapPoint], meta), or (None, None, None) on error.

        Parameters:
            q               — search phrase. Supports OR-separated sub-queries (max 5). Required.
            mode            — "semantic" (API default, meaning-based) or "keyword" (exact match)
            types           — comma-separated chunkType filter: "agendaItemTitle",
                              "agendaItemDescription", "proposalTitle", "proposalDescription",
                              "document"
            entity_ids      — comma-separated RS codes, supports * prefix matching (e.g. "01*").
                              Mutually exclusive with bbox.
            bbox            — bounding box as "west,south,east,north" (lon/lat).
                              Mutually exclusive with entity_ids.
            levels          — administrative level filter: "10", "pr", "40", "50", "60"
            date_from       — filter results from this date inclusive (ISO 8601, e.g. "2024-01-01")
            date_to         — filter results up to this date inclusive (ISO 8601)
            new_since       — only return results ingested since this date (ISO 8601)
            limit           — max result groups to return (API default 50, max 500)
            score_threshold — minimum relevance score (0.05–1). Semantic mode only;
                              ignored in keyword mode. API default 0.35.
        """
        params={
            "q": q,
            "mode": mode,
            "types": types,
            "entityIds": entity_ids,
            "bbox": bbox,
            "levels": levels,
            "dateFrom": date_from,
            "dateTo": date_to,
            "newSince": new_since,
            "limit": limit,
            "scoreThreshold": score_threshold
        }
        params = {k: v for k, v in params.items() if v is not None}

        try:
            response = requests.get(f"{self.BASE_URL}/search", headers=self.headers, params=params)
            if response.status_code == 200:
                data = response.json()
                result_groups = [ResultGroup.from_dict(item) for item in data["data"]]
                map_points = [MapPoint.from_dict(item) for item in data["mapPoints"]]
                meta = data["meta"]
                return result_groups, map_points, meta
            else:
                print(f"[Fehler] Status {response.status_code}: {response.text}")
                return (None, None, None)
        except Exception as e:
            print(f"[Exception] Fehler beim Abrufen der Suche: {e}")
        return (None, None, None)



            





