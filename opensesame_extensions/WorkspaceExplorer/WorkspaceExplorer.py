# coding=utf-8

"""
This file is part of OpenSesame.

OpenSesame is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

OpenSesame is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with OpenSesame.  If not, see <http://www.gnu.org/licenses/>.
"""

from libopensesame.py3compat import *
from qdatamatrix import QDataMatrix
from datamatrix import DataMatrix
from qtpy.QtWidgets import QDockWidget
from qtpy.QtCore import Qt, QTimer
from libqtopensesame.misc.config import cfg
from libqtopensesame.extensions import BaseExtension
from libqtopensesame.misc.translate import translation_context
_ = translation_context(u'WorkspaceExplorer', category=u'extension')


class WorkspaceMatrix(QDataMatrix):

    def __init__(self, dm):

        super(WorkspaceMatrix, self).__init__(dm)
        self._spreadsheet.contextMenuEvent = self._on_context_menu

    def refresh(self):

        super(WorkspaceMatrix, self).refresh()
        self._spreadsheet.setRowCount(len(self._dm)+1)
        self._spreadsheet.setColumnCount(len(self.dm.columns))
        # Make cells readonly
        for row in range(0, self._spreadsheet.rowCount()):
            for col in range(self._spreadsheet.columnCount()):
                item = self._spreadsheet.item(row, col)
                if item is None:
                    continue
                item.setFlags(item.flags() ^ Qt.ItemIsEditable)

    def _on_context_menu(self, e):

        pass


class WorkspaceExplorer(BaseExtension):

    def event_startup(self):

        dm = DataMatrix(length=0)
        dm.initializing = -1
        self._qdm = WorkspaceMatrix(dm)
        self._dock_widget = QDockWidget(self.main_window)
        self._dock_widget.setWidget(self._qdm)
        self._dock_widget.closeEvent = self._on_close_event
        self._dock_widget.setWindowTitle(_(u'Workspace'))
        self._dock_widget.visibilityChanged.connect(
            self._on_visibility_changed
        )
        self.main_window.addDockWidget(
            Qt.RightDockWidgetArea,
            self._dock_widget
        )
        self._set_visible(cfg.workspace_visible)

    def activate(self):

        self._set_visible(not cfg.workspace_visible)

    def _on_visibility_changed(self, visible):

        if not visible:
            return
        self._update(
            self.extension_manager.provide('jupyter_workspace_name'),
            lambda: self.extension_manager.provide(
                'jupyter_workspace_globals'
            )
        )

    def _on_close_event(self, e):

        self._set_visible(False)

    def _update(self, name, workspace_func):

        if not self._dock_widget.isVisible():
            return
        self._dock_widget.setWindowTitle(_(u'Workspace ({})').format(name))
        workspace = workspace_func()
        # If the workspace didn't reply, we try again in a second
        if workspace.get(u'no reply', False) is None:
            QTimer.singleShot(
                1000,
                lambda: self._update(name, workspace_func)
            )
            return
        # If the current kernel doesn't expose its workspace, indicate this
        if workspace.get(u'not supported', False) is None:
            dm = DataMatrix(length=0)
            dm.kernel_not_supported = -1
        # Create a DataMatrix that exposes the workspace
        else:
            dm = DataMatrix(length=len(workspace))
            dm.sorted = False
            dm.name = -1
            dm.value = -1
            dm['length'] = -1
            dm.type = -1
            for row, (var, (value, type_, length)) in zip(
                dm,
                workspace.items()
            ):
                row.name = var
                # Unstrip the quotes that JSON automatically adds to strings
                row.value = (
                    u'<no preview>'
                    if value == u'"<no preview>"'
                    else value
                )
                row['length'] = length
                row.type = type_
        self._qdm.dm = dm
        self._qdm.refresh()

    def _set_visible(self, visible):

        cfg.workspace_visible = visible
        self.set_checked(visible)
        if visible:
            self._dock_widget.show()
        else:
            self._dock_widget.hide()

    def event_workspace_update(self, name, workspace_func):

        self._update(name, workspace_func)

    def event_workspace_restart(self, name, workspace_func):

        self._update(name, workspace_func)

    def event_workspace_switch(self, name, workspace_func):

        self._update(name, workspace_func)

    def event_workspace_new(self, name, workspace_func):

        self._update(name, workspace_func)
