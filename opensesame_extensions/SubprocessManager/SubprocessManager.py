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
import psutil
from qtpy.QtWidgets import QDockWidget
from datamatrix import DataMatrix
from qdatamatrix import QDataMatrix
from qtpy.QtCore import Qt, QTimer
from libqtopensesame.misc.config import cfg
from libopensesame.oslogging import oslogger
from libqtopensesame.extensions import BaseExtension
from libqtopensesame.misc.translate import translation_context
_ = translation_context(u'SubprocessManager', category=u'extension')


class SubprocessDockWidget(QDockWidget):
    
    def __init__(self, subprocess_manager):
        
        QDockWidget.__init__(self, subprocess_manager.main_window)
        self._subprocess_manager = subprocess_manager
        self._qdm = QDataMatrix(self._subprocess_manager.dm(), read_only=True)        
        self.setWidget(self._qdm)
        self.setWindowTitle(_('Subprocesses'))
        self.setObjectName('SubprocessManager')
        self.visibilityChanged.connect(self._refresh)
    
    def _refresh(self):

        if not self.isVisible():
            return
        self._qdm.dm = self._subprocess_manager.dm()
        self._qdm.refresh()
        QTimer.singleShot(2000, self._refresh)
    

class SubprocessManager(BaseExtension):

    def activate(self):

        if not hasattr(self, '_dock_widget'):
            self._dock_widget = SubprocessDockWidget(self)
            self.main_window.addDockWidget(
                Qt.RightDockWidgetArea,
                self._dock_widget
            )
        self._dock_widget.setVisible(True)

    def dm(self):
        
        died = []
        pids = []
        states = []
        descs = []
        for pid, description in self._processes.items():
            if not psutil.pid_exists(pid):
                self._ended.append((pid, description))
                died.append(pid)
            else:
                pids.append(pid)
                states.append('running')
                descs.append(description)
        for pid in died:
            del self._processes[pid]
        if cfg.subprocess_manager_show_ended:
            for pid, description in self._ended:
                pids.append(pid)
                states.append('ended')
                descs.append(description)
        dm = DataMatrix(length=len(pids))
        dm.pid = pids
        dm.state = states
        dm.description = descs
        return dm
        
    def event_register_subprocess(self, pid, description):
        
        oslogger.debug('{}: {}'.format(pid, description))
        if not hasattr(self, '_processes'):
            self._processes = {}
            self._ended = []
        self._processes[pid] = description

    def event_close(self):
        
        running = psutil.pids()
        for pid in self._processes:
            if not psutil.pid_exists(pid):
                continue
            oslogger.debug('killing process {}'.format(pid))
            p = psutil.Process(pid)
            p.kill()
