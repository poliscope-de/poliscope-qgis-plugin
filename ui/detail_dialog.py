from PyQt5 import uic
from qgis.PyQt.QtCore import Qt
from PyQt5.QtCore import QTimer

from PyQt5.QtWidgets import QLayout, QTextBrowser, QDialog, QGroupBox, QTabWidget, QInputDialog, QMessageBox, QDialog, QVBoxLayout, QFrame, QWidget, QLabel, QPushButton, QApplication, QSpacerItem, QSizePolicy
from qgis.PyQt.QtGui import QFont
import os
from qgis.gui import QgsCollapsibleGroupBox

from ..utils.utils import Utils


class DetailDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.plugin_dir = os.path.dirname(os.path.abspath(__file__))
        ui_path = os.path.join(self.plugin_dir, "detail_dialog.ui")
        uic.loadUi(ui_path, self)

    def openInDialog(self, meeting):
        dialog = QDialog()
        dialog.setWindowTitle(meeting.title)

        layout = QVBoxLayout(dialog)

        # Fenstergröße richtet sich nach Inhalt
        layout.setSizeConstraint(QLayout.SetFixedSize)

        # Frame mit Details
        dDialog = DetailDialog()
        dDialog.setStyleSheet("""
        QWidget {
            background-color: #FFFFFF;
            }
            """)
        dDialog.setFocusPolicy(Qt.StrongFocus)
        dDialog.setAttribute(Qt.WA_TransparentForMouseEvents, False)
        dDialog.setAttribute(Qt.WA_StyledBackground, True)

        # Details des Meetings hinzufügen
        pvScore = meeting.solar_score
        windScore = meeting.wind_score

        dDialog.lTitle.setText(meeting.title)
        if not meeting.description:
            # Entfernt das QLabel aus dem Layout & UI
            dDialog.lDescription.setParent(None)
        else:
            dDialog.lDescription.setText(meeting.description)
            dDialog.lDescription.adjustSize()

        dDialog.lDescription.setWordWrap(True)
        dDialog.lDescription.setSizePolicy(
            QSizePolicy.Preferred, QSizePolicy.Minimum)
        dDialog.lDescription.setText(meeting.description)
        dDialog.lDescription.adjustSize()

        dDialog.lDate.setText(Utils.format_date(meeting.date))
        dDialog.lLastStatusUpdate.setText(
            Utils.format_last_status_update(meeting.last_status_update))

        dDialog.lRISBreadcrumbs.setText(Utils.buildRISBreadcrumbs(meeting))

        # PV Score
        Utils.setPVScore(dDialog, pvScore)
        # Wind Score
        Utils.setWindScore(dDialog, windScore)

        # Set Line
        Utils.setLineIcon(dDialog, meeting.status)

        # Set Location
        dDialog.lLocation.setText(Utils.getLocationString(meeting.rsName))

        # Set Topics
        if meeting.topics:
            for topic in meeting.topics:
                self.setTopicToGroubbox(topic, dDialog.gbTopics)
            self.setHorizontalSpacer(dDialog.gbTopics)
        else:
            if dDialog.gbTopics:
                gblayout = dDialog.gbTopics.parent().layout()
                if gblayout:
                    gblayout.removeWidget(dDialog.gbTopics)
                dDialog.gbTopics.hide()
                dDialog.gbTopics.setParent(None)
                dDialog.gbTopics.deleteLater()
                dDialog.gbTopics = None

        layout.addWidget(dDialog)

        # Schließen-Button
        close_button = QPushButton("Schließen")
        close_button.clicked.connect(dialog.accept)
        layout.addWidget(close_button, alignment=Qt.AlignRight)

        # Documents
        self.setDocumentBoxes(meeting.documents, dDialog.gbDocuments)

        # Agenda Items
        dDialog.tbAgendaItems.setOpenExternalLinks(True)
        dDialog.tbAgendaItems.setTextInteractionFlags(
            Qt.TextBrowserInteraction)
        html = self.generate_agenda_html(meeting.relevant_agenda_items)
        dDialog.tbAgendaItems.setHtml(html)
        dDialog.tbAgendaItems.document().adjustSize()
        QTimer.singleShot(
            0, lambda: self.adjustTextBrowserHeight(dDialog.tbAgendaItems))

        dialog.exec_()

    def setDocumentBoxes(self, documents: list[dict[str, any]], parent_gb: QGroupBox) -> None:
        """
        Befüllt parent_gb mit collapsible PDFs. 
        Entfernt parent_gb komplett, wenn keine PDFs gefunden werden.
        """
        # 1) Filter & Sortierung wie gehabt
        categories = {
            "invitation": ("Einladungen", []),
            "beschluss":  ("Beschlüsse",  []),
            "agenda":     ("Tagesordnungen", []),
            "other":      ("Sonstiges",   []),
        }

        for idx, doc in enumerate(documents or []):
            if not isinstance(doc, dict):
                continue
            file_info = doc.get("file")
            if not file_info or file_info.get("type") != "application/pdf":
                continue
            key = doc.get("type", "").lower()
            if key not in categories:
                key = "other"
            categories[key][1].append(doc)

        # 2) Prüfen, ob überhaupt etwas da ist
        any_docs = any(items for _, items in categories.values())
        if not any_docs:
            # Parent-Layout der GroupBox holen und Widget entfernen
            container = parent_gb.parent()
            if container is not None and isinstance(container.layout(), QVBoxLayout):
                container.layout().removeWidget(parent_gb)
            parent_gb.deleteLater()
            parent_gb.hide()
            parent_gb.setParent(None)
            parent_gb = None
            return

        # 3) Layout der gbDocuments aufräumen oder neu anlegen
        layout = parent_gb.layout()
        if layout is None:
            layout = QVBoxLayout()
            parent_gb.setLayout(layout)
        else:
            while layout.count():
                child = layout.takeAt(0)
                if child.widget():
                    child.widget().deleteLater()

        # 4) Collapsible-Boxen anlegen
        order = ["invitation", "beschluss", "agenda", "other"]
        for key in order:
            title, items = categories[key]
            if not items:
                continue

            cgb = QgsCollapsibleGroupBox(parent_gb)
            cgb.setTitle(title)
            cgb.setCursor(Qt.PointingHandCursor)
            cgb.setFont(QFont("Lucida Sans", 10))
            cgb.setCollapsed(True)
            inner = QVBoxLayout(cgb)

            for doc in items:
                file_info = doc["file"]
                file_title = file_info.get("title") or doc.get(
                    "url", "").split("/")[-1]
                filesize = Utils.format_bytes(file_info.get("filesize", ""))
                lbl = QLabel(f'<a href="{doc["url"]}"><span style=" font-family:\'Lucida Sans\',\'sans-serif\'; font-size:10pt; text-decoration: underline; color:#4E607A;">{file_title}</span></a><span style=" font-family:\'Lucida Sans\',\'sans-serif\'; font-size:10pt; text-decoration: underline; color:#A0AEC0;"> ({filesize})</span>', cgb)
                lbl.setOpenExternalLinks(True)
                lbl.setTextInteractionFlags(Qt.TextBrowserInteraction)
                inner.addWidget(lbl)

            layout.addWidget(cgb)

        layout.addStretch()

    def setTopicToGroubbox(self, topic, groupBox):
        layout = groupBox.layout()

        # Topic als QPushButton mit Stil
        topic_button = QPushButton(topic['publicProcedureName'])
        if topic['topic'] == "solar":
            topic_button.setStyleSheet("""
            QPushButton {
                background-color: #FDAC54;
                border-radius: 5px;
                padding: 6px;
                color: #fff;
                font-weight: bold;
            }
            """)
        elif topic['topic'] == "wind":
            topic_button.setStyleSheet("""
            QPushButton {
                background-color: #137BDC;
                border-radius: 5px;
                padding: 6px;
                color: #fff;
                font-weight: bold;
            }
            """)

        topic_button.setToolTip(topic['publicProcedureDescription'])
        topic_button.setFlat(True)  # Optional: Kein 3D-Effekt
        layout.addWidget(topic_button)

    def adjustTextBrowserHeight(self, textBrowser):
        doc_height = textBrowser.document().size().height()
        textBrowser.setFixedHeight(int(doc_height) + 5)

    def setHorizontalSpacer(self, groupBox):
        layout = groupBox.layout()
        spacerItem = QSpacerItem(
            40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        layout.addItem(spacerItem)

    def generate_agenda_html(self, agenda_items: list[dict]) -> str:
        # Prüfen, ob überhaupt Dokumente vorhanden sind
        documents_present = any(
            item.get("documents")
            and any(doc and doc.get("file") for doc in item["documents"])
            for item in agenda_items
        )

        # Tabellenkopf dynamisch erzeugen
        html = '''<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0//EN" "http://www.w3.org/TR/REC-html40/strict.dtd">
    <html><head><meta name="qrichtext" content="1" /><style type="text/css">
    p, li { white-space: pre-wrap; padding: 0px; margin: 0px; }
    </style></head><body style=" font-family:'Lucida Sans'; font-size:7.8pt; font-weight:400; font-style:normal;"><table border="0" style=" margin:0px; margin-top: -10px; border-collapse:collapse;" width="100%" cellspacing="2" cellpadding="0"><thead>
    <tr><td bgcolor="#f5f7fa" style=" padding:3px;">
    <span style=" font-family:'Lucida Sans','sans-serif'; font-size:10pt; font-weight:600;">TOP</span></td>
    <td bgcolor="#f5f7fa" style=" padding:3px;">
    <span style=" font-family:'Lucida Sans','sans-serif'; font-size:10pt; font-weight:600;">Beschreibung</span></td>'''

        if documents_present:
            html += '''
    <td bgcolor="#f5f7fa" style=" padding:3px;">
    <span style=" font-family:'Lucida Sans','sans-serif'; font-size:10pt; font-weight:600;">Dokumente</span></td>'''

        html += '</tr></thead>'

        for item in agenda_items:
            number = item.get('number', '')
            title = item.get('title', '').replace('\n', '<br />')
            documents = item.get('documents', [])

            valid_docs = []
            for doc in documents:
                if doc is None:
                    continue
                file_info = doc.get('file')
                if not file_info:
                    continue
                url = doc.get('url', '#')
                title_text = file_info.get('title', 'Dokument')
                filesize = Utils.format_bytes(file_info.get('filesize', ''))
                valid_docs.append(
                    f'<a href="{url}"><span style=" font-family:\'Lucida Sans\',\'sans-serif\'; font-size:10pt; text-decoration: underline; color:#4E607A;">{title_text}</span></a>'
                    f'<span style=" font-family:\'Lucida Sans\',\'sans-serif\'; font-size:10pt; text-decoration: underline; color:#A0AEC0;"> ({filesize})</span>'
                )

            html += f'''<tr>
    <td style=" padding:3;">
    <p style=" margin:0px; text-align:center;"><span style=" font-family:'Lucida Sans','sans-serif'; font-size:10pt;">{number}</span></p></td>
    <td style=" padding:3;">
    <p style=" margin:0px;"><span style=" font-family:'Lucida Sans','sans-serif'; font-size:10pt;">{title}</span></p></td>'''

            if documents_present:
                doc_html = "<br />".join(valid_docs) if valid_docs else '&nbsp;'
                html += f'''
    <td style=" vertical-align:middle; padding:3;">
    <p style=" margin:0px;">{doc_html}</p></td>'''

            html += '</tr>'

        html += '</table></body></html>'
        return html
