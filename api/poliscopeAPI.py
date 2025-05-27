from datetime import datetime
import requests
from typing import List, Dict, Any, Optional
from PyQt5.QtCore import QSettings
from PyQt5.QtWidgets import QMessageBox


class Meeting:
    """
    Modell für Meetings, das die relevanten Attribute speichert.
    """

    def __init__(self, data: Dict[str, Any]):
        self.id = data.get("id")
        self.url = data.get("url")
        self.ris_id = data.get("ris", {}).get("id")

        entities = data.get("ris", {}).get("entities", [])
        entity = entities[0] if entities else {}
        self.rs = entity.get("rs")
        self.rsName = entity.get("name")
        self.children_name = entity.get("children", [{}])[0].get(
            "name") if entity.get("children") else None

        parent = entity.get("parent") or {}
        self.parent_name = parent.get("name")
        self.parent_type = parent.get("type")
        self.parent_rs = parent.get("rs")

        grandparent = parent.get("parent") if isinstance(
            parent.get("parent"), dict) else {}
        self.grandparent_name = grandparent.get("name")
        self.grandparent_type = grandparent.get("type")
        self.grandparent_rs = grandparent.get("rs")

        great_grandparent = grandparent.get("parent") if isinstance(
            grandparent.get("parent"), dict) else {}
        self.great_grandparent_name = great_grandparent.get("name")
        self.great_grandparent_type = great_grandparent.get("type")
        self.great_grandparent_rs = great_grandparent.get("rs")

        self.topics = []
        for t in data.get("topics", []):
            topic_name = t.get("topic")
            public_proc = t.get("publicProcedure", {})
            proc_name = public_proc.get("name")
            proc_description = public_proc.get("description")

            self.topics.append({
                "topic": topic_name,
                "publicProcedureName": proc_name,
                "publicProcedureDescription": proc_description
            })

        bookmarks = data.get("bookmarks", [])
        if isinstance(bookmarks, list) and bookmarks:
            self.bookmark_id = bookmarks[0].get("user", {}).get("id")
        else:
            self.bookmark_id = None

        self.topics.sort(
            key=lambda x: 0 if "wind" in x["topic"].lower() else 1)

        self.last_status_update = data.get("lastStatusUpdate")
        self.title = data.get("title")
        self.description = data.get("description")
        self.status = data.get("status")
        self.date = data.get("date")

        self.solar_score = data.get("solarScore")
        self.wind_score = data.get("windScore")
        self.documents = data.get("documents")

        # Signale laden
        self.signals = data.get("signals", [])
        self.signals_agenda_item_ids = [
            junction.get("agendaItem_id")
            for signal in data.get("signals", [])
            for junction in signal.get("agendaItems", [])
            if "agendaItem_id" in junction
        ]

        self.agenda_items = data.get("agendaItems")
        self.relevant_agenda_items = [
            item for item in data.get("agendaItems", [])
            if not self.signals_agenda_item_ids or item.get("id") in self.signals_agenda_item_ids
        ]

        # Alle relevanten Dokumente sammeln
        self.relevant_documents = []

        # 1. Normale Dokumente
        for doc in self.documents or []:
            seen_ids = set()
            if doc.get("file"):
                file_info = doc.get("file")
                if file_info and file_info.get("type") == "application/pdf":
                    if file_info.get("id") not in seen_ids:
                        seen_ids.add(file_info.get("id"))
                        self.relevant_documents.append(doc.get("file"))

        # 2. AgendaItem-Dokumente
        self.relevant_agenda_items_relevant_documents = []
        for item in self.relevant_agenda_items or []:
            for group in item.get("documents", []):
                if group.get("file"):
                    file_info = group.get("file")
                    if file_info and file_info.get("type") == "application/pdf":

                        self.relevant_agenda_items_relevant_documents.append(
                            group.get("file"))


class MeetingsAPI:
    """
    Klasse zum Abrufen von Meetings von der API.
    """
    MEETINGS_URL = "https://api.poliscope.de/v1/meetings/query"
    MEETINGS_COUNT_URL = "https://api.poliscope.de/v1/meetings/count"
    MEETINGS_BOOKMARKED_URL = "https://api.poliscope.de/v1/meetings/bookmarked/query"
    MEETINGS_BOOKMARKED_COUNT_URL = url = "https://api.poliscope.de/v1/meetings/bookmarked/count"
    MEETINGS_BOOKMARK_URL = url = "https://api.poliscope.de/v1/meetings/{meeting_id}/bookmark"
    ENTITIES_URL = "https://api.poliscope.de/v1/entities/{rs}"

    FOCUSREGION_URL = "https://api.poliscope.de/v1/focusregions/query"
    VERSION_URL = "https://api.poliscope.de/v1/version"

    def __init__(self, api_key: str):
        self.headers = {"x-api-key": api_key,
                        "Content-Type": "application/json"}

        # Teste die API-Verbindung mit einem einfachen Request
        try:
            response = requests.post(self.MEETINGS_URL, json={
                                     "page": 1, "limit": 1}, headers=self.headers)
            if response.status_code != 200:
                raise ValueError("API-Key ungültig oder Zugriff verweigert.")
        except Exception as e:
            raise

    # type: ignore
    def get_meetings(self, filters: Optional[Dict[str, Any]] = None, entityRSCodes: Optional[str] = None, sortString: Optional[str] = None, page: Optional[int] = 1) -> List[Meeting]:
        """
        Ruft Meetings von der API mit optionalen Filtern ab und speichert die Ergebnisse zwisch.
        """
        if not filters:
            filters = {}

        payload = {"filter": filters, "fields": ["id", "url", "ris.id", "bookmarks.user.id",
                                                 "ris.entities.rs", "ris.entities.name", "ris.entities.children.name",
                                                 "ris.entities.parent.name", "ris.entities.parent.type", "ris.entities.parent.rs",
                                                 "ris.entities.parent.parent.name", "ris.entities.parent.parent.type", "ris.entities.parent.parent.rs",
                                                 "ris.entities.parent.parent.parent.name", "ris.entities.parent.parent.parent.type", "ris.entities.parent.parent.parent.rs",
                                                 "lastStatusUpdate", "title", "description", "status", "date",
                                                 "topics.publicProcedure.name", "topics.publicProcedure.description", "topics.topic",
                                                 "solarScore", "windScore", "documents.type", "documents.url", "documents.file.title", "documents.file.id", "documents.file.type", "documents.file.filesize", "signals.agendaItems.agendaItem_id", "agendaItems.id", "agendaItems.description",
                                                 "agendaItems.number", "agendaItems.title", "agendaItems.documents.url", "agendaItems.documents.file.title", "agendaItems.documents.file.filesize",
                                                 "agendaItems.documents.file.id", "agendaItems.documents.file.type",
                                                 ], "entity_rs": entityRSCodes, "sort": sortString, "page": page, "limit": 10}
        response = requests.post(
            self.MEETINGS_URL, json=payload, headers=self.headers)
        print(payload)
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list):
                return [Meeting(item) for item in data]
            return [Meeting(item) for item in data.get("data", [])]
        else:
            response.raise_for_status()

    def get_meetings_count(self, filters: Optional[Dict[str, Any]] = None, entityRSCodes: Optional[str] = None) -> int:
        """
        Ruft Meetings von der API mit optionalen Filtern ab und speichert die Ergebnisse zwisch.
        """
        if not filters:
            filters = {}

        payload = {"filter": filters, "entity_rs": entityRSCodes}
        response = requests.post(
            self.MEETINGS_COUNT_URL, json=payload, headers=self.headers)
        if response.status_code == 200:
            data = response.json()
            return data
        else:
            response.raise_for_status()

    def get_qgis_plugin_version(self,) -> Optional[str]:
        try:
            response = requests.get(self.VERSION_URL, headers=self.headers)
            if response.status_code == 200:
                data = response.json()
                return data.get("qgisPluginVersion")
            else:
                print(
                    f"[Fehler] Status {response.status_code}: {response.text}")
                return None
        except Exception as e:
            print(f"[Exception] Fehler beim Abrufen der Plugin-Version: {e}")
        return None

    def get_bookmarked_meetings(self, filters: Optional[Dict[str, Any]] = None, sortString: Optional[str] = None, page: Optional[int] = 1) -> List[Meeting]:
        """
        Ruft Meetings von der API mit optionalen Filtern ab und speichert die Ergebnisse zwisch.
        """
        if not filters:
            filters = {}

        payload = {"filter": filters, "fields": ["id", "url", "ris.id", "bookmarks.user.id",
                                                 "ris.entities.rs", "ris.entities.name", "ris.entities.children.name",
                                                 "ris.entities.parent.name", "ris.entities.parent.type", "ris.entities.parent.rs",
                                                 "ris.entities.parent.parent.name", "ris.entities.parent.parent.type", "ris.entities.parent.parent.rs",
                                                 "ris.entities.parent.parent.parent.name", "ris.entities.parent.parent.parent.type", "ris.entities.parent.parent.parent.rs",
                                                 "lastStatusUpdate", "title", "description", "status", "date",
                                                 "topics.publicProcedure.name", "topics.publicProcedure.description", "topics.topic",
                                                 "solarScore", "windScore", "documents.type", "documents.url", "documents.file.title", "documents.file.id", "documents.file.type", "documents.file.filesize", "signals.agendaItems.agendaItem_id", "agendaItems.id", "agendaItems.description",
                                                 "agendaItems.number", "agendaItems.title", "agendaItems.documents.url", "agendaItems.documents.file.title", "agendaItems.documents.file.filesize",
                                                 "agendaItems.documents.file.id", "agendaItems.documents.file.type",
                                                 ], "entity_rs": [], "sort": sortString, "page": page, "limit": 10}
        response = requests.post(
            self.MEETINGS_BOOKMARKED_URL, json=payload, headers=self.headers)
        print(payload)
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list):
                return [Meeting(item) for item in data]
            return [Meeting(item) for item in data.get("data", [])]
        else:
            response.raise_for_status()

    def get_bookmarked_meetings_count(self, filters: Optional[Dict[str, Any]] = None) -> int:

        if not filters:
            filters = {}

        payload = {"filter": filters}
        response = requests.post(
            self.MEETINGS_BOOKMARKED_COUNT_URL, json=payload, headers=self.headers)
        if response.status_code == 200:
            data = response.json()
            return data
        else:
            response.raise_for_status()

    def get_entity(self, rs: str) -> Optional[Dict[str, Any]]:
        """
        Ruft die Entität mit dem angegebenen RS-Code von der API ab.
        """
        url = self.ENTITIES_URL.format(rs=rs)
        response = requests.get(url, headers=self.headers)
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list):
                return data[0] if data else None
            return data
        else:
            response.raise_for_status()

    def get_fokusregionen(self) -> List[Dict[str, Any]]:
        """
        Ruft die Fokusregionen von der API ab und speichert die Ergebnisse zwisch.
        """
        response = requests.post(self.FOCUSREGION_URL, json={"filter": {"type": {"_eq": "core"}}, "fields": [
                                 "*", "team.paused"], "sort": "-id", "page": 1, "limit": 10}, headers=self.headers)
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list):
                return data
            return data.get("data", [])
        else:
            response.raise_for_status()

    def bookmark_meeting(self, meeting_id: str) -> bool:
        url = self.MEETINGS_BOOKMARK_URL.format(meeting_id=meeting_id)

        response = requests.put(url, headers=self.headers)
        return response.status_code == 200

    def remove_meeting_bookmark(self, meeting_id: str) -> bool:
        url = self.MEETINGS_BOOKMARK_URL.format(meeting_id=meeting_id)

        response = requests.delete(url, headers=self.headers)
        return response.status_code == 200

    @staticmethod
    def create_date_range_filter(start_date: str, end_date: str) -> Dict[str, Any]:
        dt_start_date = datetime.strptime(start_date, "%d.%m.%Y")
        start_date = dt_start_date.strftime("%Y-%m-%d")
        dt_end_date = datetime.strptime(end_date, "%d.%m.%Y")
        end_date = dt_end_date.strftime("%Y-%m-%d")
        if dt_start_date > dt_end_date:
            QMessageBox.critical(
                None, "Fehler", "Das Startdatum muss vor dem Enddatum liegen.")
            return {}
        return {"_and": [{"date": {"_gte": start_date}}, {"date": {"_lte": end_date}}]}

    @staticmethod
    def create_wind_and_solar_score_filter(wind_strength: int, solar_strength: int) -> Dict[str, Any]:
        return {
            "signals": {
                "_and": [
                    {
                        "_some": {
                            "monitor": {
                                "_eq": "39f29802-6d28-4e4b-a384-df486d84dd7c"  # Solar
                            },
                            "strength": {
                                "_gte": solar_strength
                            }
                        }
                    },
                    {
                        "_some": {
                            "monitor": {
                                "_eq": "49d66672-ed64-4f7a-8ca3-5afe51056ffe"  # Wind
                            },
                            "strength": {
                                "_gte": wind_strength
                            }
                        }
                    }
                ]
            }
        }

    @staticmethod
    def create_status_filter(status_list: List[str]) -> Dict[str, Any]:
        return {"status": {"_in": status_list}}

    @staticmethod
    def create_saved_meetings_filter() -> Dict[str, Any]:
        return {"bookmarks": {"user": {"_eq": "$CURRENT_USER"}}}

    @staticmethod
    def create_not_saved_meetings_filter() -> Dict[str, Any]:
        return {"_or": [{"bookmarks": {"directus_users_id": {"_neq": "$CURRENT_USER"}}}, {"bookmarks": {"_null": True}}]}

    @staticmethod
    def create_hidden_meetings_filter() -> Dict[str, Any]:
        return {"hidden": {"user": {"_eq": "$CURRENT_USER"}}}

    @staticmethod
    def create_exclude_hidden_meetings_filter() -> Dict[str, Any]:
        return {"_or": [{"hidden": {"_null": True}}, {"hidden": {"user": {"_neq": "$CURRENT_USER"}}}]}

    @staticmethod
    def create_bounds_filter(coords: List[List[float]]) -> Dict[str, Any]:
        """
        Erstellt einen Filter mit einem GeoJSON-Polygon aus übergebenen Koordinaten.
        Die Koordinaten müssen eine gültige Polygon-Umrisslinie bilden (geschlossen).
        """
        if coords[0] != coords[-1]:
            # Polygon schließen, falls nicht bereits geschehen
            coords.append(coords[0])

        return {
            "ris": {
                "entities": {
                    "bounds": {
                        "_intersects": {
                            "type": "Feature",
                            "geometry": {
                                "type": "Polygon",
                                # GeoJSON benötigt doppelte Verschachtelung
                                "coordinates": [coords]
                            }
                        }
                    }
                }
            }
        }
