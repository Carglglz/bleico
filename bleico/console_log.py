#!/usr/bin/env python3
# @Author: carlosgilgonzalez
# @Date:   2020-07-12T15:41:44+01:00
# @Last modified by:   carlosgilgonzalez
# @Last modified time: 2020-08-06T20:55:36+01:00

"""
Copyright (c) 2020 Carlos G. Gonzalez and others (see the AUTHORS file).
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.
You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import logging
from PyQt5.QtWidgets import QPlainTextEdit
from PyQt5.QtGui import QColor


class QPlainTextEditLogger(logging.Handler):
    def __init__(self):
        super().__init__()

        self.widget = QPlainTextEdit()
        self.widget.setReadOnly(True)
        self.widget.setMaximumBlockCount(1000)
        p = self.widget.viewport().palette()
        p.setColor(self.widget.viewport().backgroundRole(), QColor(0, 0, 0))
        self.widget.viewport().setPalette(p)
        self.widget.setStyleSheet("background-color: rgb(0, 0, 0); color: rgb(255, 255, 255)")

    def emit(self, record):  # emit callback, call adds msg to widget in main thread
        msg = self.format(record)
        self.widget.appendPlainText(msg)
