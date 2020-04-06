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
from libqtopensesame.widgets.base_preferences_widget import (
    BasePreferencesWidget
)
from libqtopensesame.misc.config import cfg


class Preferences(BasePreferencesWidget):
    
    def __init__(self, main_window):

        super(Preferences, self).__init__(
            main_window,
            ui=u'extensions.OpenSesameIDE.preferences'
        )
        
    def _before_init_widgets(self):
        
        self.ui.cfg_opensesame_ide_default_encoding.setDisabled(
            cfg.opensesame_ide_use_system_default_encoding
        )
