from PyQt5 import uic
from qgis.PyQt.QtCore import Qt
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QLabel, QGroupBox,
                              QSizePolicy, QApplication)
from qgis.PyQt.QtGui import QFont
from qgis.gui import QgsCollapsibleGroupBox
import os

from ..utils.utils import Utils


class DetailDialog(QDialog):
    def __init__(self, result_group=None, api=None, parent=None):
        super().__init__(parent)
        self.plugin_dir = os.path.dirname(os.path.abspath(__file__))
        ui_path = os.path.join(self.plugin_dir, "detail_dialog.ui")
        uic.loadUi(ui_path, self)

        if result_group is not None and api is not None:
            self.populate(result_group, api)

    def populate(self, result_group, api):
        context = result_group.context

        self.lRISBreadcrumbs.setText(Utils.buildRISBreadcrumbs(context))
        self.lLocation.setText(Utils.getLocationString(context.entity_name))

        if context.date:
            self.lDate.setText(Utils.format_date(context.date))
        else:
            self.lDate.hide()

        QApplication.setOverrideCursor(Qt.WaitCursor)
        try:
            if result_group.group_type == "meeting":
                meeting_id = result_group.group_key.split(":", 1)[1]
                meeting = api.get_meeting(meeting_id, detail="full")
                if meeting:
                    self._populate_meeting(meeting)
            elif result_group.group_type == "proposal":
                proposal_id = result_group.group_key.split(":", 1)[1]
                proposal = api.get_proposal(proposal_id, detail="full")
                if proposal:
                    self._populate_proposal(proposal)
        finally:
            QApplication.restoreOverrideCursor()

    def _populate_meeting(self, meeting):
        self.lTitle.setText(meeting.title or "")
        self.lTitle.setWordWrap(True)

        if meeting.description:
            self.lDescription.setText(meeting.description)
            self.lDescription.setWordWrap(True)
            self.lDescription.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Minimum)
            self.lDescription.adjustSize()
        else:
            self.lDescription.hide()

        self._set_document_boxes(meeting.documents)

        self.tbAgendaItems.setOpenExternalLinks(True)
        self.tbAgendaItems.setTextInteractionFlags(Qt.TextBrowserInteraction)
        html = self._generate_agenda_html(meeting.agenda_items)
        self.tbAgendaItems.setHtml(html)
        self.tbAgendaItems.document().adjustSize()
        QTimer.singleShot(0, lambda: self._adjust_text_browser_height(self.tbAgendaItems))

    def _populate_proposal(self, proposal):
        self.lTitle.setText(proposal.title or "")
        self.lTitle.setWordWrap(True)

        if proposal.description:
            self.lDescription.setText(proposal.description)
            self.lDescription.setWordWrap(True)
            self.lDescription.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Minimum)
            self.lDescription.adjustSize()
        else:
            self.lDescription.hide()

        self._set_document_boxes(proposal.documents)

        self.tbAgendaItems.setOpenExternalLinks(True)
        self.tbAgendaItems.setTextInteractionFlags(Qt.TextBrowserInteraction)
        html = self._generate_agenda_html(proposal.agenda_items)
        self.tbAgendaItems.setHtml(html)
        self.tbAgendaItems.document().adjustSize()
        QTimer.singleShot(0, lambda: self._adjust_text_browser_height(self.tbAgendaItems))

    def _set_document_boxes(self, documents):
        parent_gb = self.gbDocuments
        categories = {
            "invitation": ("Einladungen", []),
            "beschluss":  ("Beschlüsse",  []),
            "agenda":     ("Tagesordnungen", []),
            "other":      ("Sonstiges",   []),
        }

        for doc in (documents or []):
            if not doc.file or doc.file.mime_type != "application/pdf":
                continue
            key = (doc.type or "").lower()
            if key not in categories:
                key = "other"
            categories[key][1].append(doc)

        any_docs = any(items for _, items in categories.values())
        if not any_docs:
            parent_gb.hide()
            parent_gb.setParent(None)
            return

        layout = parent_gb.layout()
        if layout is None:
            layout = QVBoxLayout()
            parent_gb.setLayout(layout)
        else:
            while layout.count():
                child = layout.takeAt(0)
                if child.widget():
                    child.widget().deleteLater()

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
                file_name = doc.file.file_name or doc.original_url or "Dokument"
                lbl = QLabel(
                    f'<a href="{doc.file.download_url}"><span style=" font-family:\'Lucida Sans\',\'sans-serif\'; font-size:10pt; text-decoration: underline; color:#4E607A;">{file_name}</span></a>',
                    cgb
                )
                lbl.setOpenExternalLinks(True)
                lbl.setTextInteractionFlags(Qt.TextBrowserInteraction)
                inner.addWidget(lbl)

            layout.addWidget(cgb)

        layout.addStretch()

    def _generate_agenda_html(self, agenda_items):
        documents_present = any(
            item.documents and any(d.file for d in item.documents)
            for item in agenda_items
        )

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
            number = item.number or ''
            title = (item.title or '').replace('\n', '<br />')

            valid_docs = []
            for doc in item.documents:
                if not doc.file:
                    continue
                url = doc.file.download_url
                file_name = doc.file.file_name or 'Dokument'
                valid_docs.append(
                    f'<a href="{url}"><span style=" font-family:\'Lucida Sans\',\'sans-serif\'; font-size:10pt; text-decoration: underline; color:#4E607A;">{file_name}</span></a>'
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

    def _adjust_text_browser_height(self, textBrowser):
        doc_height = textBrowser.document().size().height()
        textBrowser.setFixedHeight(int(doc_height) + 5)
