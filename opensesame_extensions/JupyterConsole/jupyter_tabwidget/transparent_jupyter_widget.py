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
import uuid
import ast
import time
import json
import inspect
from libqtopensesame.misc.base_subcomponent import BaseSubcomponent
from qtpy.QtWidgets import QApplication
from qtconsole.rich_jupyter_widget import RichJupyterWidget


GLOBAL_EXPR = u'''{
key: (
    json.dumps(val, default=lambda x: '<no preview>'),
    val.__class__.__name__,
    len(val) if hasattr(val, '__len__') else '<na>'
)
for key, val in globals().items()
if not key.startswith(u'_') and
key not in ('In', 'Out') and
not callable(val) and
not inspect.isclass(val) and
not inspect.ismodule(val)
}'''


class TransparentJupyterWidget(RichJupyterWidget, BaseSubcomponent):

    def __init__(self, jupyter_console):

        self._name = jupyter_console.name
        self._jupyter_console = jupyter_console
        super(TransparentJupyterWidget, self).__init__(jupyter_console)
        self.setup(jupyter_console)
        self.executed.connect(self._on_executed)
        self.executing.connect(self._on_executing)

    def _on_executing(self):

        self._jupyter_console.set_busy(True)

    def _on_executed(self):

        self._jupyter_console.set_busy(False)
        self.extension_manager.fire(
            u'workspace_update',
            name=self._name,
            workspace_func=self.get_workspace_globals
        )


class OutprocessJupyterWidget(TransparentJupyterWidget):

    """Makes the Python workspace of a Jupyter console with a kernel running in
    a different process accessible.
    """

    def __init__(self, jupyter_console):

        self._user_expressions = {}
        super(OutprocessJupyterWidget, self).__init__(jupyter_console)

    def _handle_execute_reply(self, msg):

        self._user_expressions = msg.get(
            u'content',
            {}
        ).get(u'user_expressions', {})
        return super(OutprocessJupyterWidget, self)._handle_execute_reply(msg)

    def get_workspace_globals(self):

        key = str(uuid.uuid4())
        self._kernel_client.execute(
            u'import json; import inspect',
            silent=True,
            user_expressions={
                key: GLOBAL_EXPR
            }
        )
        for _ in range(100):
            if key in self._user_expressions:
                break
            time.sleep(0.01)
            QApplication.processEvents()
        else:
            return {u'no reply': None}
        reply = self._user_expressions[key].get(
            u'data',
            {}
        ).get(u'text/plain', u'{"invalid reply": None}')
        try:
            return ast.literal_eval(reply)
        except (ValueError, SyntaxError):
            return {u'cannot eval reply': None}

    def set_workspace_globals(self, global_dict):

        pass


class InprocessJupyterWidget(TransparentJupyterWidget):

    """Makes the Python workspace of a Jupyter console with a kernel running in
    the same process accessible.
    """

    def __init__(self, parent):

        self._jupyter_console = parent
        super(InprocessJupyterWidget, self).__init__(parent)

    def get_workspace_globals(self):

        return {
            key: (
                json.dumps(val, default=lambda x: u'<no preview>'),
                val.__class__.__name__,
                len(val) if hasattr(val, '__len__') else '<na>'
            )
            for key, val
            in self._kernel_manager.kernel.shell.user_global_ns.copy().items()
            if not key.startswith(u'_') and
            key not in ('In', 'Out') and
            not callable(val) and
            not inspect.isclass(val) and
            not inspect.ismodule(val)
        }

    def set_workspace_globals(self, global_dict):

        self._kernel_manager.kernel.shell.push(global_dict)
