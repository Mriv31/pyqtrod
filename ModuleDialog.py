# This Python file uses the following encoding: utf-8
from PyQt6 import QtCore
from PyQt6 import QtWidgets, uic, QtGui

class ModuleDialog(QtWidgets.QDialog):
     def __init__(self, name, stringlist=None, checked=False, icon=None, parent=None):
         super(ModuleDialog, self).__init__(parent)

         self.name = name
         self.icon = icon
         self.model = QtGui.QStandardItemModel()
         self.listView = QtWidgets.QListView()

         if stringlist is not None:
             for i in range(len(stringlist)):
                 item = QtGui.QStandardItem(stringlist[i])
                 item.setCheckable(True)
                 check = QtCore.Qt.Unchecked
                 item.setCheckState(check)
                 self.model.appendRow(item)

         self.listView.setModel(self.model)

         self.okButton = QtWidgets.QPushButton("OK")
         self.cancelButton = QtWidgets.QPushButton("Cancel")
         self.selectButton = QtWidgets.QPushButton("Select All")
         self.unselectButton = QtWidgets.QPushButton("Unselect All")

         hbox = QtWidgets.QHBoxLayout()
         hbox.addStretch(1)
         hbox.addWidget(self.okButton)
         hbox.addWidget(self.cancelButton)
         hbox.addWidget(self.selectButton)
         hbox.addWidget(self.unselectButton)

         vbox = QtWidgets.QVBoxLayout()
         vbox.addWidget(self.listView)
         vbox.addStretch(1)
         vbox.addLayout(hbox)

         self.setLayout(vbox)
         #self.setLayout(layout)
         self.setWindowTitle(self.name)
         if self.icon is not None: self.setWindowIcon(self.icon)

         self.okButton.clicked.connect(self.accept)
         self.cancelButton.clicked.connect(self.reject)
         self.selectButton.clicked.connect(self.select)
         self.unselectButton.clicked.connect(self.unselect)

     def reject(self):
         QtWidgets.QDialog.reject(self)

     def accept(self):
         self.choices = []
         i = 0
         while self.model.item(i):
             if self.model.item(i).checkState():
                 self.choices.append(self.model.item(i).text())
             i += 1
         QtWidgets.QDialog.accept(self)

     def select(self):
         i = 0
         while self.model.item(i):
             item = self.model.item(i)
             item.setCheckState(QtCore.Qt.Checked)
             i += 1
     def get_selected_modules(self):
         l = []
         i = 0
         while self.model.item(i):
             item = self.model.item(i)
             if item.checkState() == QtCore.Qt.Checked:
                 l.append(self.model.item(i).text())
             i += 1
         return l

     def unselect(self):
         i = 0
         while self.model.item(i):
             item = self.model.item(i)
             item.setCheckState(QtCore.Qt.Unchecked)
             i += 1


