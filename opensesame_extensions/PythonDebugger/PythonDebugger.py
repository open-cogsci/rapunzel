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
import os
import zmq
import time
import pickle
from libqtopensesame.extensions import BaseExtension
from libopensesame.oslogging import oslogger
from qtpy.QtCore import QTimer


class PythonDebugger(BaseExtension):

    def event_startup(self):
        
        self._zmq_context = zmq.Context()
        self._zmq_socket = self._zmq_context.socket(zmq.REP)
        self._zmq_socket.bind("tcp://*:5555")
        self._listen_for_pdb()
        
    def _listen_for_pdb(self):
         
        #  Wait for next request from client
        try:
            message = self._zmq_socket.recv_pyobj(flags=zmq.NOBLOCK)
        except zmq.error.ZMQError:
            QTimer.singleShot(1000, self._listen_for_pdb)
            return
        try:
            self._zmq_socket.send(b'ok')
        except zmq.error.ZMQError:
            oslogger.error('failed to send reply')
        if os.path.exists(message['path']):
            self.extension_manager.fire(
                'ide_open_file',
                path=message['path'],
                line_number=message['line']
            )
            try:
                # Refocus the console, not the editor
                self.extension_manager['JupyterConsole']._focus()
            except:
                pass
        self.extension_manager.fire(
            'workspace_update',
            name=self.extension_manager.provide('jupyter_workspace_name'),
            workspace_func=(lambda: message['workspace'])
        )
        QTimer.singleShot(500, self._listen_for_pdb)

    def provide_rapunzel_pdb(self):
        
        with open(
            os.path.join(os.path.dirname(__file__), u'rapunzel_pdb.py')
        ) as f:
            return f.read()
