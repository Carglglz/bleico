# @Author: carlosgilgonzalez
# @Date:   2020-08-06T04:12:46+01:00
# @Last modified by:   carlosgilgonzalez
# @Last modified time: 2020-08-06T20:55:29+01:00

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
from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5.QtCore import Qt


class CharacteristicMetadataItem(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(CharacteristicMetadataItem, self).__init__(parent)
        self.textQVBoxLayout = QtWidgets.QVBoxLayout()
        self.deviceQLabel = QtWidgets.QLabel()
        self.uuidQLabel = QtWidgets.QLabel()
        self.textQVBoxLayout.addWidget(self.deviceQLabel)
        self.textQVBoxLayout.addWidget(self.uuidQLabel)
        self.allQHBoxLayout = QtWidgets.QHBoxLayout()
        self.iconQLabel = QtWidgets.QLabel()
        self.allQHBoxLayout.addWidget(self.iconQLabel, 0)
        self.allQHBoxLayout.addLayout(self.textQVBoxLayout, 1)
        self.setLayout(self.allQHBoxLayout)
        # setStyleSheet
        self.deviceQLabel.setStyleSheet('''
            color: rgb(0, 0, 0);
        ''')
        self.uuidQLabel.setStyleSheet('''
            color: rgb(0, 0, 0);
        ''')

    def setTextUp(self, text):
        self.deviceQLabel.setText(text)

    def setTextDown(self, text):
        self.uuidQLabel.setText(text)

    def setIcon(self, imagePath):
        pixmap = QtGui.QPixmap(imagePath)
        pixmap_scaled = pixmap.scaled(128, 128, Qt.KeepAspectRatio,
                                      transformMode=Qt.SmoothTransformation)
        pixmap_scaled.setDevicePixelRatio(2.0)
        self.iconQLabel.setPixmap(pixmap_scaled)


class CharacteristicViewer(QtWidgets.QWidget):
    def __init__(self, log=None, char=None):
        super(CharacteristicViewer, self).__init__()
        self.setWindowTitle("{} [{}]".format(char.name, char.uuid))
        self.setMinimumSize(512, 512)
        # Create QListWidget
        self.log = log
        self.layout = QtWidgets.QGridLayout()
        self.myQListWidget = QtWidgets.QListWidget(self)
        # self.myQListWidget.clicked.connect(self.listview_clicked)
        self.char = char
        # self.setCentralWidget(self.myQListWidget)
        self.layout.addWidget(self.myQListWidget)
        # ADD BUTTON WIDGETS
        self.okButton = QtWidgets.QPushButton('Ok')
        self.okButton.clicked.connect(self.cancel_and_exit)
        hbox = QtWidgets.QHBoxLayout()
        hbox.addStretch(1)
        hbox.addWidget(self.okButton)
        self.layout.addLayout(hbox, 1, 0)
        self.setLayout(self.layout)
        self.populate_items(self.char)
        self.updateGeometry()

    def populate_items(self, char):

        myQCustomQWidget = CharacteristicMetadataItem()
        myQCustomQWidget.setTextUp(char._get_metadata_string())
        # Create QListWidgetItem
        myQListWidgetItem = QtWidgets.QListWidgetItem(self.myQListWidget)
        # Set size hint
        myQListWidgetItem.setSizeHint(myQCustomQWidget.sizeHint())
        # Add QListWidgetItem into QListWidget
        self.myQListWidget.addItem(myQListWidgetItem)
        self.myQListWidget.setItemWidget(
            myQListWidgetItem, myQCustomQWidget)

    def cancel_and_exit(self):
        item = self.myQListWidget.currentItem()
        if item:
            item.setSelected(False)
        self.hide()

    def closeEvent(self, event):
        event.accept()
        item = self.myQListWidget.currentItem()
        if item:
            item.setSelected(False)
