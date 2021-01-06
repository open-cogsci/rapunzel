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
import uuid
import yaml
from qtpy import QtWidgets, QtCore
from pyqode.core import modes
from libopensesame.oslogging import oslogger
from libopensesame import misc
from libqtopensesame.misc.config import cfg
from libqtopensesame.extensions import BaseExtension
from libqtopensesame.misc.translate import translation_context
_ = translation_context(u'ImageAnnotations', category=u'extension')


class ImageAnnotations(BaseExtension):
    """Receives images that result from code execution (sent by JupyterConsole)
    and shows these as annotations next to the executed code. Relies on
    ImageAnnotationsMode and ImageAnnotationsPanel from pyqode.core.
    """
    
    def event_startup(self):
        """Creates a folder for the image files if it doesn't exist, and
        restores the image annotation info.
        """
        self._image_folder = os.path.join(
            self.main_window.home_folder,
            '.opensesame',
            'image_annotations'
        )
        if not os.path.exists(self._image_folder):
            oslogger.debug('creating {}'.format(self._image_folder))
            os.mkdir(self._image_folder)
        try:
            self._image_annotations = safe_yaml_load(cfg.image_annotations)
            assert(isinstance(self._image_annotations, dict))
        except BaseException:
            oslogger.warning('failed to parse image annotations from config')
            self._image_annotations = {}
            
    def event_register_editor(self, editor):
        """When an editor is registered, an ImageAnnotationsMode is added, but
        only if the editor already has an ImageAnnotationsPanel, which is
        managed by pyqode_manager.
        """
        try:
            editor.panels.get('ImageAnnotationsPanel')
        except KeyError:
            return
        mode = modes.ImageAnnotationsMode()
        mode.annotation_clicked.connect(self._on_annotation_clicked)
        editor.modes.append(mode)
        mode.set_annotations(self._image_annotations)
        
    def event_image_annotations_new(self, img, fmt, code):
        """Receives a new image annotation, where `img` is the image data,
        `fmt` is the format, and code is the code snippet that resulted in
        creating of the image.
        """
        editor = self.extension_manager.provide('ide_current_editor')
        if (
            editor is None or
            'ImageAnnotationsMode' not in list(editor.modes.keys())
        ):
            return
        if editor.file.path not in self._image_annotations:
            self._image_annotations[editor.file.path] = {}
        self._image_annotations[editor.file.path][code] \
            = self._figure_file(img, fmt)
        cfg.image_annotations = yaml.dump(self._image_annotations)
        editor.modes.get('ImageAnnotationsMode').set_annotations(
            self._image_annotations
        )
        
    def _figure_file(self, img, fmt):
        """Save an image to file and return the filename. Inspired by Spyder's
        `figurebrowser.py`.
        """
        if fmt == 'image/svg+xml':
            ext = '.svg'
        elif fmt == 'image/png':
            ext = '.png'
        elif fmt == 'image/jpeg':
            ext = '.jpg'
        else:
            raise ValueError('invalid image format: {}'.format(fmt))
        path = os.path.join(self._image_folder, uuid.uuid4().hex + ext)
        oslogger.debug('writing image to {}'.format(path))
        if fmt == 'image/svg+xml' and isinstance(img, str):
            img = img.encode('utf-8')
        with open(path, 'wb') as fd:
            fd.write(img)
        return path
    
    def _open_annotation(self, path):
        """Opens a single annotation image."""
        misc.open_url(path)
        
    def _open_folder(self):
        """Opens the folder that contains the image annotations."""
        misc.open_url(self._image_folder)
        
    def _clear_annotation(self, path=None):
        """Clear a single image annotation, or all image annotations in `path`
        is `None`.
        """
        editor = self.extension_manager.provide('ide_current_editor')
        if (
            editor is None or
            'ImageAnnotationsMode' not in list(editor.modes.keys())
        ):
            return
        if path is None:
            self._image_annotations[editor.file.path] = {}
        else:
            for code, img_path in list(
                self._image_annotations[editor.file.path].items()
            ):
                if img_path == path:
                    del self._image_annotations[editor.file.path][code]
        editor.modes.get('ImageAnnotationsMode').set_annotations(
            self._image_annotations
        )
        cfg.image_annotations = yaml.dump(self._image_annotations)

    def _on_annotation_clicked(self, msg, event):
        """Shows a context menu on the annotation."""
        if event.button() != QtCore.Qt.RightButton:
            return
        menu = QtWidgets.QMenu(self.main_window)
        menu.addAction(_('Open'), lambda: self._open_annotation(msg.path))
        menu.addSeparator()
        menu.addAction(_('Clear'), lambda: self._clear_annotation(msg.path))
        menu.addAction(_('Clear all'), self._clear_annotation)
        menu.addSeparator()
        menu.addAction(_('Open folder'), self._open_folder)
        menu.exec(event.globalPos())
