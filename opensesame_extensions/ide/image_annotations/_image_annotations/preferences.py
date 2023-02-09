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
            ui=u'extensions.ImageAnnotations.preferences'
        )
        
    def _after_init_widgets(self):
        
        self.ui.radiobutton_no_capture.clicked.connect(self._no_capture)
        self.ui.radiobutton_image_capture.clicked.connect(self._image_capture)
        self.ui.radiobutton_full_capture.clicked.connect(self._full_capture)
        self.event_setting_changed(None, None)
        
    def event_setting_changed(self, setting, value):
        
        if not cfg.image_annotations_enabled:
            self.ui.radiobutton_no_capture.setChecked(True)
        elif not cfg.image_annotations_capture_output:
            self.ui.radiobutton_image_capture.setChecked(True)
        else:
            self.ui.radiobutton_full_capture.setChecked(True)
            
    def _update_setting(self, enabled, capture):
    
        self.extension_manager.fire(
            'setting_changed',
            setting='image_annotations_enabled',
            value=enabled
        )
        self.extension_manager.fire(
            'setting_changed',
            setting='image_annotations_capture_output',
            value=capture
        )
        
    def _no_capture(self):
    
        self._update_setting(False, False)
    
    def _image_capture(self):
    
        self._update_setting(True, False)
    
    def _full_capture(self):
    
        self._update_setting(True, True)
