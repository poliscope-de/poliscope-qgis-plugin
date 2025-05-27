import os
from datetime import datetime
from PyQt5 import QtGui
from qgis.utils import iface
from qgis.core import QgsCoordinateTransform, QgsProject, QgsCoordinateReferenceSystem
from PyQt5.QtGui import QPixmap, QPainter
from PyQt5.QtSvg import QSvgRenderer
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QFrame, QLabel, QPushButton
from PyQt5.QtWidgets import QLayout
import re
import unicodedata
from pathlib import Path
import math


from ..api.poliscopeAPI import Meeting


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
    def format_last_status_update(date_str: str) -> str:
        wochentage = ['Montag', 'Dienstag', 'Mittwoch',
                      'Donnerstag', 'Freitag', 'Samstag', 'Sonntag']
        monate = ['Januar', 'Februar', 'März', 'April', 'Mai', 'Juni',
                  'Juli', 'August', 'September', 'Oktober', 'November', 'Dezember']

        dt = datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%S')
        wochentag = wochentage[dt.weekday()]
        tag = dt.day
        monat = monate[dt.month - 1]
        jahr = dt.year
        image = '<img src="data:image/png;base64,{PD94bWwgdmVyc2lvbj0iMS4wIiBlbmNvZGluZz0iVVRGLTgiIHN0YW5kYWxvbmU9Im5vIj8+CjxzdmcKICAgeG1sbnM6ZGM9Imh0dHA6Ly9wdXJsLm9yZy9kYy9lbGVtZW50cy8xLjEvIgogICB4bWxuczpjYz0iaHR0cDovL2NyZWF0aXZlY29tbW9ucy5vcmcvbnMjIgogICB4bWxuczpyZGY9Imh0dHA6Ly93d3cudzMub3JnLzE5OTkvMDIvMjItcmRmLXN5bnRheC1ucyMiCiAgIHhtbG5zOnN2Zz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciCiAgIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyIKICAgeG1sbnM6c29kaXBvZGk9Imh0dHA6Ly9zb2RpcG9kaS5zb3VyY2Vmb3JnZS5uZXQvRFREL3NvZGlwb2RpLTAuZHRkIgogICB4bWxuczppbmtzY2FwZT0iaHR0cDovL3d3dy5pbmtzY2FwZS5vcmcvbmFtZXNwYWNlcy9pbmtzY2FwZSIKICAgd2lkdGg9IjI0IgogICBoZWlnaHQ9IjI0IgogICB2aWV3Qm94PSIwIDAgMjQgMjQiCiAgIGZpbGw9Im5vbmUiCiAgIHN0cm9rZT0iY3VycmVudENvbG9yIgogICBzdHJva2Utd2lkdGg9IjIiCiAgIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIKICAgc3Ryb2tlLWxpbmVqb2luPSJyb3VuZCIKICAgY2xhc3M9ImZlYXRoZXIgZmVhdGhlci1hY3Rpdml0eSIKICAgdmVyc2lvbj0iMS4xIgogICBpZD0ic3ZnMzc2MiIKICAgc29kaXBvZGk6ZG9jbmFtZT0iYWN0aXZpdHkuc3ZnIgogICBpbmtzY2FwZTp2ZXJzaW9uPSIwLjkyLjUgKDIwNjBlYzFmOWYsIDIwMjAtMDQtMDgpIj4KICA8bWV0YWRhdGEKICAgICBpZD0ibWV0YWRhdGEzNzY4Ij4KICAgIDxyZGY6UkRGPgogICAgICA8Y2M6V29yawogICAgICAgICByZGY6YWJvdXQ9IiI+CiAgICAgICAgPGRjOmZvcm1hdD5pbWFnZS9zdmcreG1sPC9kYzpmb3JtYXQ+CiAgICAgICAgPGRjOnR5cGUKICAgICAgICAgICByZGY6cmVzb3VyY2U9Imh0dHA6Ly9wdXJsLm9yZy9kYy9kY21pdHlwZS9TdGlsbEltYWdlIiAvPgogICAgICA8L2NjOldvcms+CiAgICA8L3JkZjpSREY+CiAgPC9tZXRhZGF0YT4KICA8ZGVmcwogICAgIGlkPSJkZWZzMzc2NiIgLz4KICA8c29kaXBvZGk6bmFtZWR2aWV3CiAgICAgcGFnZWNvbG9yPSIjZmZmZmZmIgogICAgIGJvcmRlcmNvbG9yPSIjNjY2NjY2IgogICAgIGJvcmRlcm9wYWNpdHk9IjEiCiAgICAgb2JqZWN0dG9sZXJhbmNlPSIxMCIKICAgICBncmlkdG9sZXJhbmNlPSIxMCIKICAgICBndWlkZXRvbGVyYW5jZT0iMTAiCiAgICAgaW5rc2NhcGU6cGFnZW9wYWNpdHk9IjAiCiAgICAgaW5rc2NhcGU6cGFnZXNoYWRvdz0iMiIKICAgICBpbmtzY2FwZTp3aW5kb3ctd2lkdGg9IjM0NDAiCiAgICAgaW5rc2NhcGU6d2luZG93LWhlaWdodD0iMTM1MSIKICAgICBpZD0ibmFtZWR2aWV3Mzc2NCIKICAgICBzaG93Z3JpZD0iZmFsc2UiCiAgICAgaW5rc2NhcGU6em9vbT0iOS44MzMzMzMzIgogICAgIGlua3NjYXBlOmN4PSItMjMuNDkxNTI1IgogICAgIGlua3NjYXBlOmN5PSIxMiIKICAgICBpbmtzY2FwZTp3aW5kb3cteD0iLTkiCiAgICAgaW5rc2NhcGU6d2luZG93LXk9Ii05IgogICAgIGlua3NjYXBlOndpbmRvdy1tYXhpbWl6ZWQ9IjEiCiAgICAgaW5rc2NhcGU6Y3VycmVudC1sYXllcj0ic3ZnMzc2MiIgLz4KICA8cG9seWxpbmUKICAgICBwb2ludHM9IjIyIDEyIDE4IDEyIDE1IDIxIDkgMyA2IDEyIDIgMTIiCiAgICAgaWQ9InBvbHlsaW5lMzc2MCIKICAgICBzdHlsZT0ic3Ryb2tlOiM3MzdmOTU7c3Ryb2tlLW9wYWNpdHk6MSIgLz4KPC9zdmc+Cg==}" width="12" height="12">'
        return f"{image} Aktualisiert am {wochentag}, {tag}. {monat} {jahr}"

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
    def buildRISBreadcrumbs(meeting: Meeting) -> str:
        breadcrumbs = []
        if meeting.great_grandparent_name and meeting.great_grandparent_type not in ["0"]:
            breadcrumbs.append(Utils.convertRSTypes(
                meeting.great_grandparent_type)+": "+meeting.great_grandparent_name)
        if meeting.grandparent_name and meeting.grandparent_type not in ["0"]:
            breadcrumbs.append(Utils.convertRSTypes(
                meeting.grandparent_type)+": "+meeting.grandparent_name)
        if meeting.parent_name and meeting.parent_type not in ["0"]:
            breadcrumbs.append(Utils.convertRSTypes(
                meeting.parent_type)+": "+meeting.parent_name)
        return " > ".join(breadcrumbs)

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
    def convertSortStringToAPI(sortString):
        if sortString == "Aktuellste Neuigkeiten zuerst":
            return "-lastStatusUpdate"
        elif sortString == "Zukünftige Sitzungen zuerst":
            return "-date"
        elif sortString == "Älteste Sitzung zuerst":
            return "date"
        elif sortString == "Älteste Neuigkeiten zuerst":
            return "lastStatusUpdate"
        else:
            return ""

    @staticmethod
    def setPVScore(uiItem, pvScore):
        if pvScore == 1:
            uiItem.pbPVScore1.setChecked(True)
        elif pvScore == 2:
            uiItem.pbPVScore1.setChecked(True)
            uiItem.pbPVScore2.setChecked(True)
        elif pvScore == 3:
            uiItem.pbPVScore1.setChecked(True)
            uiItem.pbPVScore2.setChecked(True)
            uiItem.pbPVScore3.setChecked(True)

    @staticmethod
    def setWindScore(uiItem, windScore):
        if windScore == 1:
            uiItem.pbWindScore1.setChecked(True)
        elif windScore == 2:
            uiItem.pbWindScore1.setChecked(True)
            uiItem.pbWindScore2.setChecked(True)
        elif windScore == 3:
            uiItem.pbWindScore1.setChecked(True)
            uiItem.pbWindScore2.setChecked(True)
            uiItem.pbWindScore3.setChecked(True)

    @staticmethod
    def setLineIcon(uiItem, status):
        plugin_dir = os.path.dirname(os.path.abspath(__file__))
        line1Pixmap = Utils.load_svg_high_quality(os.path.join(
            plugin_dir, "../resources/icons/Line/1_items.svg"),380, 24)
        line2Pixmap = Utils.load_svg_high_quality(os.path.join(
            plugin_dir, "../resources/icons/Line/2_items.svg"),380, 24)
        line3Pixmap = Utils.load_svg_high_quality(os.path.join(
            plugin_dir, "../resources/icons/Line/3_items.svg"),380, 24)

        if status == "termin":
            uiItem.lLine.setPixmap(QtGui.QPixmap(line1Pixmap))
        if status == "vorlage":
            uiItem.lLine.setPixmap(QtGui.QPixmap(line2Pixmap))
        if status == "beschluss":
            uiItem.lLine.setPixmap(QtGui.QPixmap(line3Pixmap))

    @staticmethod
    def format_bytes(bytes_value: int) -> str:
        if bytes_value < 1024:
            return f"{bytes_value} B"
        elif bytes_value < 1024 ** 2:
            kb = bytes_value // 1024
            return f"{kb} KB"
        else:
            mb = bytes_value // (1024 ** 2)
            return f"{mb} MB"

    @staticmethod
    def slugify(text: str) -> str:
        # Unicode normalisieren (z.B. ä → ä)
        text = unicodedata.normalize("NFKD", text)
        # Diakritische Zeichen entfernen (z.B. ä → a)
        text = text.encode("ascii", "ignore").decode("ascii")
        # Nur alphanumerische Zeichen und Leerzeichen zulassen
        text = re.sub(r"[^a-zA-Z0-9\s-]", "", text)
        # Leerzeichen und Doppelte Bindestriche durch einen Bindestrich ersetzen
        text = re.sub(r"[\s-]+", "-", text)
        # Alles kleinschreiben
        return text.strip("-").lower()

    @staticmethod
    def get_current_canvas_bbox_polygon_epsg4326(iface):
        # 1. Karte prüfen
        canvas = iface.mapCanvas()
        if not canvas or not canvas.extent():
            print("Keine Karte sichtbar.")
            return None

        # 2. Aktuellen Extent und CRS holen
        extent = canvas.extent()
        source_crs = canvas.mapSettings().destinationCrs()
        target_crs = QgsCoordinateReferenceSystem("EPSG:4326")
        transform = QgsCoordinateTransform(
            source_crs, target_crs, QgsProject.instance())

        # 3. BoundingBox transformieren
        transformed = transform.transformBoundingBox(extent)

        # 4. Eckpunkte des Rechtecks berechnen
        xmin, ymin = transformed.xMinimum(), transformed.yMinimum()
        xmax, ymax = transformed.xMaximum(), transformed.yMaximum()

        # 5. Polygon als Liste von Punkten (gegen den Uhrzeigersinn + geschlossen)
        polygon = [
            [round(xmin, 2), round(ymin, 2)],  # unten links
            [round(xmin, 2), round(ymax, 2)],  # oben links
            [round(xmax, 2), round(ymax, 2)],  # oben rechts
            [round(xmax, 2), round(ymin, 2)],  # unten rechts
            [round(xmin, 2), round(ymin, 2)]   # zurück zu unten links
        ]
        # Prüfen auf Default BBox
        if polygon == [[-3.5, -1.0], [-3.5, 1.0], [3.5, 1.0], [3.5, -1.0], [-3.5, -1.0]]:
            return None

        return polygon
    
    @staticmethod
    def get_current_canvas_bbox_center_epsg4326(iface):
        # 1. Karte prüfen
        canvas = iface.mapCanvas()
        if not canvas or not canvas.extent():
            print("Keine Karte sichtbar.")
            return None

        # 2. Extent und Transformation vorbereiten
        extent = canvas.extent()
        source_crs = canvas.mapSettings().destinationCrs()
        target_crs = QgsCoordinateReferenceSystem("EPSG:4326")
        transform = QgsCoordinateTransform(source_crs, target_crs, QgsProject.instance())
        transformed = transform.transformBoundingBox(extent)

        # 3. Mittelpunkt berechnen
        center_lon = (transformed.xMinimum() + transformed.xMaximum()) / 2
        center_lat = (transformed.yMinimum() + transformed.yMaximum()) / 2

        # 4. Umrechnen von ~1m in Grad
        meter_in_deg_lat = 1 / 111320  # ca. 1m in Breitengrad
        meter_in_deg_lon = 1 / (111320 * math.cos(math.radians(center_lat)))  # ca. 1m in Längengrad

        # 5. Rechteck um Mittelpunkt bauen (~1m² Fläche)
        dx = meter_in_deg_lon / 2
        dy = meter_in_deg_lat / 2

        polygon = [
            [round(center_lon - dx, 8), round(center_lat - dy, 8)],  # unten links
            [round(center_lon - dx, 8), round(center_lat + dy, 8)],  # oben links
            [round(center_lon + dx, 8), round(center_lat + dy, 8)],  # oben rechts
            [round(center_lon + dx, 8), round(center_lat - dy, 8)],  # unten rechts
            [round(center_lon - dx, 8), round(center_lat - dy, 8)]   # zurück zu unten links
        ]

        return polygon

    @staticmethod
    def get_plugin_version():
        plugin_dir = str(Path(__file__).parent.parent)
        print("Plugin Directory: ", plugin_dir)
        metadata_path = os.path.join(plugin_dir, "metadata.txt")

        if not os.path.exists(metadata_path):
            return "unknown"

        with open(metadata_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.startswith("version="):
                    return line.strip().split("=")[1]

        return "unknown"
