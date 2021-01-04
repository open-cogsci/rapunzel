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
from libqtopensesame.misc.config import cfg
from datamatrix import DataMatrix
from qdatamatrix import QDataMatrix
from qtpy.QtWidgets import QDockWidget
from qtpy.QtGui import QFont
from qtpy.QtCore import Qt, QTimer
from libopensesame.oslogging import oslogger
from libqtopensesame.extensions import BaseExtension
from libqtopensesame.misc.translate import translation_context
_ = translation_context(u'WorkspaceExplorer', category=u'extension')


class WorkspaceMatrix(QDataMatrix):

    @property
    def cell_double_clicked(self):

        return self._spreadsheet.cellDoubleClicked


class WorkspaceExplorer(BaseExtension):

    @BaseExtension.as_thread(wait=2500)
    def event_startup(self):

        dm = DataMatrix(length=0)
        dm.initializing = -1
        self._workspace_cache = {}
        self._qdm = WorkspaceMatrix(dm, read_only=True)
        self._qdm.setFont(QFont(cfg.pyqode_font_name, cfg.pyqode_font_size))
        self._qdm.cell_double_clicked.connect(self._inspect_variable)
        self._dock_widget = QDockWidget(self.main_window)
        self._dock_widget.setWidget(self._qdm)
        self._dock_widget.closeEvent = self._on_close_event
        self._dock_widget.setWindowTitle(_(u'Workspace'))
        self._dock_widget.setObjectName('WorkspaceExplorer')
        self._dock_widget.visibilityChanged.connect(
            self._on_visibility_changed
        )
        self.main_window.addDockWidget(
            Qt.RightDockWidgetArea,
            self._dock_widget
        )
        self._set_visible(cfg.workspace_visible)

    def _inspect_variable(self, row, column):

        if self.extension_manager.provide('jupyter_kernel_running'):
            self.extension_manager.fire(
                'notify',
                message=_(u'Cannot inspect variables in running kernel')
            )
            return
        if not row:
            return
        self.extension_manager.fire(
            'data_viewer_inspect',
            name=self._qdm.dm.name[row - 1],
            workspace=self.extension_manager.provide('jupyter_workspace_name')
        )

    def activate(self):

        if not hasattr(self, '_qdm'):
            oslogger.info('ignoring activate until after startup')
            return
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

        if (
            not hasattr(self, '_dock_widget') or
            not self._dock_widget.isVisible()
        ):
            return
        self._dock_widget.setWindowTitle(_(u'Workspace ({})').format(name))
        workspace = workspace_func()
        self._workspace_cache[name] = workspace
        # If the workspace didn't reply, we try again in a second
        if workspace is None or workspace.get(u'no reply', False) is None:
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
            dm.name = ''
            dm.value = ''
            dm.shape = ''
            dm.type = ''
            for row, (var, data) in zip(dm, workspace.items()):
                if data is None:
                    oslogger.warning(u'invalid workspace data: {}'.format(var))
                    continue
                value, type_, shape = data
                row.value = value
                row.name = var
                if shape is not None:
                    row.shape = repr(shape)
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

        # When a kernel is running (which includes being a debugging session)
        # it doesn't respond to silent requests for the workspace. Therefore
        # we use cached copy of the last update.
        if self.extension_manager.provide('jupyter_kernel_running'):
            self._update(name, lambda: self._workspace_cache.get(name, {}))
            return
        self._update(name, workspace_func)

    def event_workspace_new(self, name, workspace_func):

        self._update(name, workspace_func)
