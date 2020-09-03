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
from bleico.ble_device import ble_scan
from bleico.devtools import store_dev
import time
import os
from bleak.uuids import uuidstr_to_str


class ScanDeviceItem(QtWidgets.QWidget):
    def __init__(self, device=None, parent=None):
        super(ScanDeviceItem, self).__init__(parent)
        self.device = device
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


class BleScanner(QtWidgets.QWidget):
    def __init__(self, log=None, SRC_PATH=None):
        super(BleScanner, self).__init__()
        self.setWindowTitle("Bleico Scanner")
        self.setMinimumSize(512, 512)
        # Create QListWidget
        self._ble_scanner = None
        self.log = log
        self.layout = QtWidgets.QGridLayout()
        self.myQListWidget = QtWidgets.QListWidget(self)
        self.myQListWidget.clicked.connect(self.listview_clicked)
        self.selected_device = None
        self.device_to_connect = None
        self.devices = []
        self._RSSI_icon = 'signal_{}.png'
        self.SRC_PATH = SRC_PATH
        # self.setCentralWidget(self.myQListWidget)
        self.layout.addWidget(self.myQListWidget)
        # ADD BUTTON WIDGETS
        self.scanButton = QtWidgets.QPushButton('Scan')
        self.connectButton = QtWidgets.QPushButton('Connect')
        self.cancelButton = QtWidgets.QPushButton('Cancel')
        self.saveButton = QtWidgets.QPushButton('Save')
        self.scanButton.clicked.connect(self.scan_again)
        self.connectButton.clicked.connect(self.do_connect)
        self.saveButton.clicked.connect(self.do_save)
        self.cancelButton.clicked.connect(self.cancel_and_exit)
        self.connectButton.setEnabled(False)
        self.saveButton.setEnabled(False)
        hbox = QtWidgets.QHBoxLayout()
        hbox.addStretch(1)
        hbox.addWidget(self.scanButton)
        hbox.addWidget(self.connectButton)
        hbox.addWidget(self.saveButton)
        hbox.addWidget(self.cancelButton)
        self.layout.addLayout(hbox, 1, 0)
        self.setLayout(self.layout)
        # SPLASH SCREEN
        self.splash_pix = QtGui.QPixmap(os.path.join(self.SRC_PATH, "bleico.png"), 'PNG')
        self.scaled_splash = self.splash_pix.scaled(
            512, 512, Qt.KeepAspectRatio, transformMode=Qt.SmoothTransformation)
        self.splash = QtWidgets.QSplashScreen(
            self.scaled_splash, Qt.WindowStaysOnTopHint)
        self.splash.setWindowFlags(
            Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        self.splash.setEnabled(False)
        self.splash.show()
        self.splash.showMessage("Scanning for device...",
                                Qt.AlignHCenter | Qt.AlignBottom, Qt.white)
        self.do_scan()
        self.splash.clearMessage()
        self.splash.close()
        if self.devices:
            self.populate_items(self.devices)
        self.updateGeometry()

    def do_scan(self):
        self.devices = []
        n = 0
        self.log.info('Scanning...')
        while n < 3:
            try:
                self.devices = ble_scan()
                n += 1
                if len(self.devices) > 0:
                    break
                else:
                    self.log.info('Scanning...')
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(e)
                time.sleep(1)
        if len(self.devices) == 0:
            self.log.info('No BLE device found')
        else:
            self.devices = sorted(self.devices, key=lambda dev: dev.rssi)
            self.devices.reverse()
            self.log.info('BLE device/s found: {}'.format(len(self.devices)))
            for dev in self.devices:
                services = []
                if hasattr(dev, 'metadata'):
                    if isinstance(dev.metadata, dict):
                        if 'uuids' in dev.metadata.keys():
                            try:
                                services = [uuidstr_to_str(serv.lower()) for serv in dev.metadata['uuids']]
                            except Exception as e:
                                services = []

                self.log.info("NAME: {}, UUID: {}, RSSI: {} dBm".format(dev.name, dev.address,
                                                          dev.rssi))

    def listview_clicked(self):
        item = self.myQListWidget.currentItem()
        lw = self.myQListWidget.itemWidget(item)
        self.selected_device = lw.deviceQLabel.text().split('\n')[-1].replace('UUID: ', '')
        self.log.info("Device selected: {}".format(self.selected_device))
        self.connectButton.setEnabled(True)
        self.saveButton.setEnabled(True)

    def populate_items(self, scan_list):
        # scan list --> items
        # for item in scan list:
        for dev in scan_list:
            try:
                services = [uuidstr_to_str(serv.lower()) for serv in dev.metadata['uuids']]
            except Exception as e:
                services = []
            icon = os.path.join(self.SRC_PATH, self._RSSI_icon.format(self.map_rssi_level_icon(dev.rssi)))
            myQCustomQWidget = ScanDeviceItem()
            myQCustomQWidget.setTextUp("{}\nUUID: {}".format(dev.name, dev.address))
            myQCustomQWidget.setTextDown("RSSI: {} dBm  Services: {}".format(dev.rssi, ','.join(services)))
            myQCustomQWidget.setIcon(icon)
            # Create QListWidgetItem
            myQListWidgetItem = QtWidgets.QListWidgetItem(self.myQListWidget)
            # Set size hint
            myQListWidgetItem.setSizeHint(myQCustomQWidget.sizeHint())
            # Add QListWidgetItem into QListWidget
            self.myQListWidget.addItem(myQListWidgetItem)
            self.myQListWidget.setItemWidget(
                myQListWidgetItem, myQCustomQWidget)

    def map_rssi_level_icon(self, rssi):
        if rssi <= (-90):  # LEVEL 0 --> VERY_LOW
            return "VERY_LOW"
        elif rssi > (-90) and rssi <= (-80):  # LEVEL 1 --> LOW
            return "LOW"
        elif rssi > (-80) and rssi <= (-70):  # LEVEL 2 --> GOOD
            return "GOOD"
        elif rssi > (-70) and rssi <= (-60):  # LEVEL 3 --> VERY_GOOD
            return "VERY_GOOD"
        elif rssi > (-60):  # LEVEL 4 --> EXCELLENT
            return "EXCELLENT"

    def clear_items(self):
        self.myQListWidget.clear()

    def do_save(self):
        if self.selected_device:
            store_dev('bleico_', uuid=self.selected_device, read_timeout=1,
                      dir=os.path.join(os.environ['HOME'], ".bleico"))

            self.log.info('bleico device settings saved in ~/.bleico directory!')

    def do_connect(self):
        if self.selected_device:
            self.hide()
            self.device_to_connect = self.selected_device
            self.log.info("Connecting to: {}".format(self.selected_device))

    def scan_again(self):
        self.connectButton.setEnabled(False)
        self.saveButton.setEnabled(False)
        self.devices = []
        self.clear_items()
        self.do_scan()
        if self.devices:
            self.populate_items(self.devices)

    def cancel_and_exit(self):
        self.hide()
        self.device_to_connect = 'CANCEL'

    def closeEvent(self, event):
        self.device_to_connect = 'CANCEL'
        print(self.device_to_connect)
        event.accept()
