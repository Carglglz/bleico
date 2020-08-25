import sys
from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5.QtCore import Qt


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
        pixmap_scaled = pixmap.scaled(48, 48, Qt.KeepAspectRatio,
                                      transformMode=Qt.SmoothTransformation)
        self.iconQLabel.setPixmap(pixmap_scaled)

    def get_device_data(self):
        pass


class BleScanner(QtWidgets.QWidget):
    def __init__(self):
        super(BleScanner, self).__init__()
        # Create QListWidget
        self._ble_scanner = None
        self.layout = QtWidgets.QGridLayout()
        self.myQListWidget = QtWidgets.QListWidget(self)
        self.myQListWidget.clicked.connect(self.listview_clicked)
        self.selected_device = None
        for index, name, icon in [
            ('bledev1\nUUID: 9998175F-9A91-4CA2-B5EA-482AFC3453B9', 'RSSI: -30 dBm',  'signal_GOOD.png'),
            ('bledev2', '9998175F-9A91-4CA2-B5EA-482AFC3453B9', 'signal_LOW.png'),
            ('bledev3', '9998175F-9A91-4CA2-B5EA-482AFC3453B9', 'signal_EXCELLENT.png')]:
            # Create QCustomQWidget
            myQCustomQWidget = ScanDeviceItem()
            myQCustomQWidget.setTextUp(index)
            myQCustomQWidget.setTextDown(name)
            myQCustomQWidget.setIcon(icon)
            # Create QListWidgetItem
            myQListWidgetItem = QtWidgets.QListWidgetItem(self.myQListWidget)
            # Set size hint
            myQListWidgetItem.setSizeHint(myQCustomQWidget.sizeHint())
            # Add QListWidgetItem into QListWidget
            self.myQListWidget.addItem(myQListWidgetItem)
            self.myQListWidget.setItemWidget(
                myQListWidgetItem, myQCustomQWidget)
        # self.setCentralWidget(self.myQListWidget)
        self.layout.addWidget(self.myQListWidget)
        # ADD BUTTON WIDGETS
        self.setLayout(self.layout)

    def listview_clicked(self):
        item = self.myQListWidget.currentItem()
        lw = self.myQListWidget.itemWidget(item)
        self.selected_device = lw
        print(lw.deviceQLabel.text())

    def populate_items(self, scan_list):
        pass
        # scan list --> items
        # for item in scan list:
        # myQCustomQWidget = ScanDeviceItem()
        # myQCustomQWidget.setTextUp(index)
        # myQCustomQWidget.setTextDown(name)
        # myQCustomQWidget.setIcon(icon)
        # # Create QListWidgetItem
        # myQListWidgetItem = QtWidgets.QListWidgetItem(self.myQListWidget)
        # # Set size hint
        # myQListWidgetItem.setSizeHint(myQCustomQWidget.sizeHint())
        # # Add QListWidgetItem into QListWidget
        # self.myQListWidget.addItem(myQListWidgetItem)
        # self.myQListWidget.setItemWidget(
        #     myQListWidgetItem, myQCustomQWidget)

    def clear_items(self):
        self.myQListWidget.clear()

    def do_scan(self):
        pass

    def do_save(self, device_item):
        pass

    def do_connect(self, device_item):
        pass


def main():
    app = QtWidgets.QApplication([])
    window = BleScanner()
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
