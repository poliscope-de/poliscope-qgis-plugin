import os
from datetime import datetime
from qgis.utils import iface
from qgis.core import QgsCoordinateTransform, QgsProject, QgsCoordinateReferenceSystem, QgsRectangle
from PyQt5.QtGui import QPixmap, QPainter
from PyQt5.QtSvg import QSvgRenderer
from PyQt5.QtCore import Qt
from pathlib import Path
import math


from ..api.poliscopeAPI import ResultContext


class Utils:
    @staticmethod
    def load_svg_high_quality(path: str, width: int, height: int) -> QPixmap:
        renderer = QSvgRenderer(path)
        pixmap = QPixmap(width, height)
        pixmap.fill(Qt.transparent)

        painter = QPainter(pixmap)
        renderer.render(painter)
        painter.end()

        return pixmap

    @staticmethod
    def format_date(date_str: str) -> str:
        wochentage = ['Montag', 'Dienstag', 'Mittwoch',
                      'Donnerstag', 'Freitag', 'Samstag', 'Sonntag']
        monate = ['Januar', 'Februar', 'März', 'April', 'Mai', 'Juni',
                  'Juli', 'August', 'September', 'Oktober', 'November', 'Dezember']

        dt = datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%S')
        wochentag = wochentage[dt.weekday()]
        tag = dt.day
        monat = monate[dt.month - 1]
        jahr = dt.year
        image = '<img src="data:image/png;base64,{PD94bWwgdmVyc2lvbj0iMS4wIiBlbmNvZGluZz0iVVRGLTgiIHN0YW5kYWxvbmU9Im5vIj8+CjxzdmcKICAgeG1sbnM6ZGM9Imh0dHA6Ly9wdXJsLm9yZy9kYy9lbGVtZW50cy8xLjEvIgogICB4bWxuczpjYz0iaHR0cDovL2NyZWF0aXZlY29tbW9ucy5vcmcvbnMjIgogICB4bWxuczpyZGY9Imh0dHA6Ly93d3cudzMub3JnLzE5OTkvMDIvMjItcmRmLXN5bnRheC1ucyMiCiAgIHhtbG5zOnN2Zz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciCiAgIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyIKICAgeG1sbnM6c29kaXBvZGk9Imh0dHA6Ly9zb2RpcG9kaS5zb3VyY2Vmb3JnZS5uZXQvRFREL3NvZGlwb2RpLTAuZHRkIgogICB4bWxuczppbmtzY2FwZT0iaHR0cDovL3d3dy5pbmtzY2FwZS5vcmcvbmFtZXNwYWNlcy9pbmtzY2FwZSIKICAgd2lkdGg9IjI0IgogICBoZWlnaHQ9IjI0IgogICB2aWV3Qm94PSIwIDAgMjQgMjQiCiAgIGZpbGw9Im5vbmUiCiAgIHN0cm9rZT0iY3VycmVudENvbG9yIgogICBzdHJva2Utd2lkdGg9IjIiCiAgIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIKICAgc3Ryb2tlLWxpbmVqb2luPSJyb3VuZCIKICAgY2xhc3M9ImZlYXRoZXIgZmVhdGhlci1jbG9jayIKICAgdmVyc2lvbj0iMS4xIgogICBpZD0ic3ZnNDU5MSIKICAgc29kaXBvZGk6ZG9jbmFtZT0iY2xvY2suc3ZnIgogICBpbmtzY2FwZTp2ZXJzaW9uPSIwLjkyLjUgKDIwNjBlYzFmOWYsIDIwMjAtMDQtMDgpIj4KICA8bWV0YWRhdGEKICAgICBpZD0ibWV0YWRhdGE0NTk3Ij4KICAgIDxyZGY6UkRGPgogICAgICA8Y2M6V29yawogICAgICAgICByZGY6YWJvdXQ9IiI+CiAgICAgICAgPGRjOmZvcm1hdD5pbWFnZS9zdmcreG1sPC9kYzpmb3JtYXQ+CiAgICAgICAgPGRjOnR5cGUKICAgICAgICAgICByZGY6cmVzb3VyY2U9Imh0dHA6Ly9wdXJsLm9yZy9kYy9kY21pdHlwZS9TdGlsbEltYWdlIiAvPgogICAgICA8L2NjOldvcms+CiAgICA8L3JkZjpSREY+CiAgPC9tZXRhZGF0YT4KICA8ZGVmcwogICAgIGlkPSJkZWZzNDU5NSIgLz4KICA8c29kaXBvZGk6bmFtZWR2aWV3CiAgICAgcGFnZWNvbG9yPSIjZmZmZmZmIgogICAgIGJvcmRlcmNvbG9yPSIjNjY2NjY2IgogICAgIGJvcmRlcm9wYWNpdHk9IjEiCiAgICAgb2JqZWN0dG9sZXJhbmNlPSIxMCIKICAgICBncmlkdG9sZXJhbmNlPSIxMCIKICAgICBndWlkZXRvbGVyYW5jZT0iMTAiCiAgICAgaW5rc2NhcGU6cGFnZW9wYWNpdHk9IjAiCiAgICAgaW5rc2NhcGU6cGFnZXNoYWRvdz0iMiIKICAgICBpbmtzY2FwZTp3aW5kb3ctd2lkdGg9Ijc4MCIKICAgICBpbmtzY2FwZTp3aW5kb3ctaGVpZ2h0PSI0ODAiCiAgICAgaWQ9Im5hbWVkdmlldzQ1OTMiCiAgICAgc2hvd2dyaWQ9ImZhbHNlIgogICAgIGlua3NjYXBlOnpvb209IjkuODMzMzMzMyIKICAgICBpbmtzY2FwZTpjeD0iMTIiCiAgICAgaW5rc2NhcGU6Y3k9IjEyIgogICAgIGlua3NjYXBlOndpbmRvdy14PSIwIgogICAgIGlua3NjYXBlOndpbmRvdy15PSIwIgogICAgIGlua3NjYXBlOndpbmRvdy1tYXhpbWl6ZWQ9IjAiCiAgICAgaW5rc2NhcGU6Y3VycmVudC1sYXllcj0ic3ZnNDU5MSIgLz4KICA8Y2lyY2xlCiAgICAgY3g9IjEyIgogICAgIGN5PSIxMiIKICAgICByPSIxMCIKICAgICBpZD0iY2lyY2xlNDU4NyIKICAgICBzdHlsZT0ic3Ryb2tlOiM3MzdmOTU7c3Ryb2tlLW9wYWNpdHk6MSIgLz4KICA8cG9seWxpbmUKICAgICBwb2ludHM9IjEyIDYgMTIgMTIgMTYgMTQiCiAgICAgaWQ9InBvbHlsaW5lNDU4OSIKICAgICBzdHlsZT0ic3Ryb2tlOiM3MzdmOTU7c3Ryb2tlLW9wYWNpdHk6MSIgLz4KPC9zdmc+Cg==\}" width="12" height="12">'
        return f"{image} {wochentag}, {tag}. {monat} {jahr}"

    @staticmethod
    def getLocationString(location: str) -> str:
        image = '<img src="data:image/png;base64,{PD94bWwgdmVyc2lvbj0iMS4wIiBlbmNvZGluZz0iVVRGLTgiIHN0YW5kYWxvbmU9Im5vIj8+CjxzdmcKICAgeG1sbnM6ZGM9Imh0dHA6Ly9wdXJsLm9yZy9kYy9lbGVtZW50cy8xLjEvIgogICB4bWxuczpjYz0iaHR0cDovL2NyZWF0aXZlY29tbW9ucy5vcmcvbnMjIgogICB4bWxuczpyZGY9Imh0dHA6Ly93d3cudzMub3JnLzE5OTkvMDIvMjItcmRmLXN5bnRheC1ucyMiCiAgIHhtbG5zOnN2Zz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciCiAgIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyIKICAgeG1sbnM6c29kaXBvZGk9Imh0dHA6Ly9zb2RpcG9kaS5zb3VyY2Vmb3JnZS5uZXQvRFREL3NvZGlwb2RpLTAuZHRkIgogICB4bWxuczppbmtzY2FwZT0iaHR0cDovL3d3dy5pbmtzY2FwZS5vcmcvbmFtZXNwYWNlcy9pbmtzY2FwZSIKICAgd2lkdGg9IjI0IgogICBoZWlnaHQ9IjI0IgogICB2aWV3Qm94PSIwIDAgMjQgMjQiCiAgIGZpbGw9Im5vbmUiCiAgIHN0cm9rZT0iY3VycmVudENvbG9yIgogICBzdHJva2Utd2lkdGg9IjIiCiAgIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIKICAgc3Ryb2tlLWxpbmVqb2luPSJyb3VuZCIKICAgY2xhc3M9ImZlYXRoZXIgZmVhdGhlci1tYXAtcGluIgogICB2ZXJzaW9uPSIxLjEiCiAgIGlkPSJzdmc1MTU4IgogICBzb2RpcG9kaTpkb2NuYW1lPSJtYXAtcGluLnN2ZyIKICAgaW5rc2NhcGU6dmVyc2lvbj0iMC45Mi41ICgyMDYwZWMxZjlmLCAyMDIwLTA0LTA4KSI+CiAgPG1ldGFkYXRhCiAgICAgaWQ9Im1ldGFkYXRhNTE2NCI+CiAgICA8cmRmOlJERj4KICAgICAgPGNjOldvcmsKICAgICAgICAgcmRmOmFib3V0PSIiPgogICAgICAgIDxkYzpmb3JtYXQ+aW1hZ2Uvc3ZnK3htbDwvZGM6Zm9ybWF0PgogICAgICAgIDxkYzp0eXBlCiAgICAgICAgICAgcmRmOnJlc291cmNlPSJodHRwOi8vcHVybC5vcmcvZGMvZGNtaXR5cGUvU3RpbGxJbWFnZSIgLz4KICAgICAgPC9jYzpXb3JrPgogICAgPC9yZGY6UkRGPgogIDwvbWV0YWRhdGE+CiAgPGRlZnMKICAgICBpZD0iZGVmczUxNjIiIC8+CiAgPHNvZGlwb2RpOm5hbWVkdmlldwogICAgIHBhZ2Vjb2xvcj0iI2ZmZmZmZiIKICAgICBib3JkZXJjb2xvcj0iIzY2NjY2NiIKICAgICBib3JkZXJvcGFjaXR5PSIxIgogICAgIG9iamVjdHRvbGVyYW5jZT0iMTAiCiAgICAgZ3JpZHRvbGVyYW5jZT0iMTAiCiAgICAgZ3VpZGV0b2xlcmFuY2U9IjEwIgogICAgIGlua3NjYXBlOnBhZ2VvcGFjaXR5PSIwIgogICAgIGlua3NjYXBlOnBhZ2VzaGFkb3c9IjIiCiAgICAgaW5rc2NhcGU6d2luZG93LXdpZHRoPSI3ODAiCiAgICAgaW5rc2NhcGU6d2luZG93LWhlaWdodD0iNDgwIgogICAgIGlkPSJuYW1lZHZpZXc1MTYwIgogICAgIHNob3dncmlkPSJmYWxzZSIKICAgICBpbmtzY2FwZTp6b29tPSI5LjgzMzMzMzMiCiAgICAgaW5rc2NhcGU6Y3g9IjEyIgogICAgIGlua3NjYXBlOmN5PSIxMiIKICAgICBpbmtzY2FwZTp3aW5kb3cteD0iMCIKICAgICBpbmtzY2FwZTp3aW5kb3cteT0iMCIKICAgICBpbmtzY2FwZTp3aW5kb3ctbWF4aW1pemVkPSIwIgogICAgIGlua3NjYXBlOmN1cnJlbnQtbGF5ZXI9InN2ZzUxNTgiIC8+CiAgPHBhdGgKICAgICBkPSJNMjEgMTBjMCA3LTkgMTMtOSAxM3MtOS02LTktMTNhOSA5IDAgMCAxIDE4IDB6IgogICAgIGlkPSJwYXRoNTE1NCIKICAgICBzdHlsZT0ic3Ryb2tlOiM3MzdmOTU7c3Ryb2tlLW9wYWNpdHk6MSIgLz4KICA8Y2lyY2xlCiAgICAgY3g9IjEyIgogICAgIGN5PSIxMCIKICAgICByPSIzIgogICAgIGlkPSJjaXJjbGU1MTU2IgogICAgIHN0eWxlPSJzdHJva2U6IzczN2Y5NTtzdHJva2Utb3BhY2l0eToxIiAvPgo8L3N2Zz4K}" width="12" height="12">'
        return f"{image} {location}"

    @staticmethod
    def getDocumentsCountString(count: int) -> str:
        image = '<img alt="" src="data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyNCIgaGVpZ2h0PSIyNCIgdmlld0JveD0iMCAwIDI0IDI0IiBmaWxsPSJub25lIiBzdHJva2U9ImN1cnJlbnRDb2xvciIgc3Ryb2tlLXdpZHRoPSIyIiBzdHJva2UtbGluZWNhcD0icm91bmQiIHN0cm9rZS1saW5lam9pbj0icm91bmQiIGNsYXNzPSJmZWF0aGVyIGZlYXRoZXItZmlsZSI+PHBhdGggZD0iTTEzIDJINmEyIDIgMCAwIDAtMiAydjE2YTIgMiAwIDAgMCAyIDJoMTJhMiAyIDAgMCAwIDItMlY5eiI+PC9wYXRoPjxwb2x5bGluZSBwb2ludHM9IjEzIDIgMTMgOSAyMCA5Ij48L3BvbHlsaW5lPjwvc3ZnPg==" width="12" height="12"/> '
        if count == 1:
            text = f"{count} Dokument vorhanden"
        elif count > 1:
            text = f"{count} Dokumente vorhanden"
        else:
            text = "0 Dokumente vorhanden"
        return f"{image} {text}"

    @staticmethod
    def buildRISBreadcrumbs(context: ResultContext) -> str:
        breadcrumbs = []
        for parent in context.parents:
            if parent["level"] != "0":
                breadcrumbs.append(Utils.convertRSTypes(parent["level"]) + ": " + parent["name"])
        return " > ".join(reversed(breadcrumbs))

    @staticmethod
    def convertRSTypes(rs_type):
        if rs_type == "0":
            return "Bund"
        elif rs_type == "10":
            return "BL"  # Bundesland
        elif rs_type == "pr":
            return "PR"  # Planungsregion
        elif rs_type == "40":
            return "LK"  # Landkreis
        elif rs_type == "50":
            return "Verband"
        elif rs_type == "60":
            return "Gemeinde"
        else:
            return ""

    @staticmethod
    def build_highlighted_text(text: str, highlights, max_chars: int = 400) -> str:
        truncated = len(text) > max_chars
        snippet = text[:max_chars] if truncated else text
        if truncated:
            last_space = snippet.rfind(' ')
            if last_space > max_chars // 2:
                snippet = snippet[:last_space]
        suffix = '…' if truncated else ''

        if not highlights:
            return snippet + suffix
        result = []
        pos = 0
        for h in sorted(highlights, key=lambda x: x[0]):
            start, end = h[0], min(h[1], len(snippet))
            if start >= len(snippet):
                break
            if pos < start:
                result.append(snippet[pos:start]
                    .replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;'))
            result.append('<b>')
            result.append(snippet[start:end]
                .replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;'))
            result.append('</b>')
            pos = end
        if pos < len(snippet):
            result.append(snippet[pos:]
                .replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;'))
        result.append(suffix)
        return ''.join(result)

    @staticmethod
    def format_score(score: float) -> str:
        return f"{round(score * 100)}%"

    @staticmethod
    def get_current_canvas_bbox_polygon_epsg4326(iface):
        canvas = iface.mapCanvas()
        if not canvas or not canvas.extent():
            return None

        extent = canvas.extent()
        source_crs = canvas.mapSettings().destinationCrs()
        target_crs = QgsCoordinateReferenceSystem("EPSG:4326")
        transform = QgsCoordinateTransform(
            source_crs, target_crs, QgsProject.instance())

        transformed = transform.transformBoundingBox(extent)

        xmin, ymin = transformed.xMinimum(), transformed.yMinimum()
        xmax, ymax = transformed.xMaximum(), transformed.yMaximum()

        polygon = [
            [round(xmin, 2), round(ymin, 2)],
            [round(xmin, 2), round(ymax, 2)],
            [round(xmax, 2), round(ymax, 2)],
            [round(xmax, 2), round(ymin, 2)],
            [round(xmin, 2), round(ymin, 2)]
        ]
        if polygon == [[-3.5, -1.0], [-3.5, 1.0], [3.5, 1.0], [3.5, -1.0], [-3.5, -1.0]]:
            return None

        return polygon

    @staticmethod
    def get_current_canvas_bbox_center_epsg4326(iface):
        canvas = iface.mapCanvas()
        if not canvas or not canvas.extent():
            return None

        extent = canvas.extent()
        source_crs = canvas.mapSettings().destinationCrs()
        target_crs = QgsCoordinateReferenceSystem("EPSG:4326")
        transform = QgsCoordinateTransform(source_crs, target_crs, QgsProject.instance())
        transformed = transform.transformBoundingBox(extent)

        center_lon = (transformed.xMinimum() + transformed.xMaximum()) / 2
        center_lat = (transformed.yMinimum() + transformed.yMaximum()) / 2

        meter_in_deg_lat = 1 / 111320
        meter_in_deg_lon = 1 / (111320 * math.cos(math.radians(center_lat)))

        dx = meter_in_deg_lon / 2
        dy = meter_in_deg_lat / 2

        polygon = [
            [round(center_lon - dx, 8), round(center_lat - dy, 8)],
            [round(center_lon - dx, 8), round(center_lat + dy, 8)],
            [round(center_lon + dx, 8), round(center_lat + dy, 8)],
            [round(center_lon + dx, 8), round(center_lat - dy, 8)],
            [round(center_lon - dx, 8), round(center_lat - dy, 8)]
        ]

        return polygon

    @staticmethod
    def build_web_url(result_group) -> str:
        entity_id = result_group.context.entity_id
        item_id = result_group.group_key.split(":", 1)[1] if ":" in result_group.group_key else ""
        if result_group.group_type == "meeting" and entity_id and item_id:
            url = f"https://poliscope.de/app/entity/{entity_id}/meeting/{item_id}"
            if result_group.hits and result_group.hits[0].agenda_item_id:
                url += f"/agenda-item/{result_group.hits[0].agenda_item_id}"
            return url
        elif result_group.group_type == "proposal" and entity_id and item_id:
            return f"https://poliscope.de/app/entity/{entity_id}/proposal/{item_id}"
        return None

    @staticmethod
    def zoom_to_point(lat, lon):
        canvas = iface.mapCanvas()
        target_crs = QgsCoordinateReferenceSystem("EPSG:4326")
        transform = QgsCoordinateTransform(
            target_crs, canvas.mapSettings().destinationCrs(), QgsProject.instance())
        extent = QgsRectangle(lon - 0.2, lat - 0.2, lon + 0.2, lat + 0.2)
        canvas.setExtent(transform.transformBoundingBox(extent))
        canvas.refresh()

    @staticmethod
    def get_plugin_version():
        plugin_dir = str(Path(__file__).parent.parent)
        metadata_path = os.path.join(plugin_dir, "metadata.txt")

        if not os.path.exists(metadata_path):
            return "unknown"

        with open(metadata_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.startswith("version="):
                    return line.strip().split("=")[1]

        return "unknown"
