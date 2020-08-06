# @Author: carlosgilgonzalez
# @Date:   2020-08-06T04:12:46+01:00
# @Last modified by:   carlosgilgonzalez
# @Last modified time: 2020-08-06T18:34:21+01:00

# from https://stackoverflow.com/questions/50666680/python-checkbox-selection-in-qlistview

from PyQt5 import QtWidgets, QtGui, QtCore


class ChecklistDialog(QtWidgets.QDialog):
    def __init__(self,
                 name,
                 stringlist=None,
                 checked=False,
                 icon=None,
                 parent=None,
                 log=None,
                 check_list=None):
        super(ChecklistDialog, self).__init__(parent)

        self.name = name
        self.icon = icon
        self.log = log
        self.choices = []
        self.check_list = check_list
        self.model = QtGui.QStandardItemModel()
        self.listView = QtWidgets.QListView()

        for string in stringlist:
            item = QtGui.QStandardItem(string)
            item.setCheckable(True)
            check = \
                (QtCore.Qt.Checked if checked else QtCore.Qt.Unchecked)
            item.setCheckState(check)
            self.model.appendRow(item)

        self.listView.setModel(self.model)

        self.okButton = QtWidgets.QPushButton('OK')
        self.cancelButton = QtWidgets.QPushButton('Cancel')
        self.selectButton = QtWidgets.QPushButton('Select All')
        self.unselectButton = QtWidgets.QPushButton('Unselect All')

        hbox = QtWidgets.QHBoxLayout()
        hbox.addStretch(1)
        hbox.addWidget(self.okButton)
        hbox.addWidget(self.cancelButton)
        hbox.addWidget(self.selectButton)
        hbox.addWidget(self.unselectButton)

        vbox = QtWidgets.QVBoxLayout(self)
        vbox.addWidget(self.listView)
        vbox.addStretch(1)
        vbox.addLayout(hbox)

        self.setWindowTitle(self.name)
        if self.icon:
            self.setWindowIcon(self.icon)

        self.okButton.clicked.connect(self.onAccepted)
        self.cancelButton.clicked.connect(self.reject)
        self.selectButton.clicked.connect(self.select)
        self.unselectButton.clicked.connect(self.unselect)

    def onAccepted(self):
        self.choices = [self.model.item(i).text() for i in
                        range(self.model.rowCount())
                        if self.model.item(i).checkState()
                        == QtCore.Qt.Checked]
        self.accept()
        self.log.info('Checklist Choices {}'.format(self.choices))
        for ch in self.choices:
            if ch not in self.check_list:
                self.check_list.append(ch)
        for ch in self.check_list.copy():
            if ch not in self.choices:
                self.check_list.remove(ch)

    def select(self):
        for i in range(self.model.rowCount()):
            item = self.model.item(i)
            item.setCheckState(QtCore.Qt.Checked)

    def unselect(self):
        for i in range(self.model.rowCount()):
            item = self.model.item(i)
            item.setCheckState(QtCore.Qt.Unchecked)
