# This Python file uses the following encoding: utf-8
from PyQt6 import QtWidgets
from functools import partial


class MatrixDialog(QtWidgets.QDialog):
    def __init__(self, name, mat=None, checked=False, icon=None, parent=None):
        super(MatrixDialog, self).__init__(parent)
        self.name = name
        self.icon = icon
        self.mat = mat
        self.okButton = QtWidgets.QPushButton("OK")

        hbox = QtWidgets.QHBoxLayout()
        hbox.addStretch(1)
        hbox.addWidget(self.okButton)
        matrix = QtWidgets.QGridLayout()
        for i in range(4):
            for j in range(4):
                matrix.addWidget(QtWidgets.QLabel("a" + str(i) + str(j)), i, 2 * j)
                dbbox = QtWidgets.QDoubleSpinBox()
                dbbox.setRange(-8, 8)
                dbbox.setDecimals(3)
                dbbox.setSingleStep(0.01)
                dbbox.setValue(mat[i][j])
                dbbox.valueChanged.connect(partial(self.changemat, i=i, j=j))
                matrix.addWidget(dbbox, i, 2 * j + 1)

        vbox = QtWidgets.QVBoxLayout()
        vbox.addLayout(matrix)
        vbox.addStretch(1)
        vbox.addLayout(hbox)

        self.setLayout(vbox)
        # self.setLayout(layout)
        self.setWindowTitle(self.name)
        if self.icon is not None:
            self.setWindowIcon(self.icon)

        self.okButton.clicked.connect(self.accept)

    def changemat(self, x, i, j):
        self.mat[i, j] = x

    def accept(self):
        QtWidgets.QDialog.accept(self)


class MatrixChoose(QtWidgets.QDialog):
    def __init__(self, name, file=None, checked=False, icon=None, parent=None):
        super(MatrixChoose, self).__init__(parent)
        self.name = name
        self.icon = icon
        self.NIf = file
        self.okButton = QtWidgets.QPushButton("OK")
        self.cancelButton = QtWidgets.QPushButton("Cancel")

        hbox = QtWidgets.QHBoxLayout()
        hbox.addStretch(1)
        hbox.addWidget(self.okButton)
        hbox.addWidget(self.cancelButton)

        vbox = QtWidgets.QVBoxLayout()
        bdb1 = QtWidgets.QRadioButton(
            "Unitary correction matrix (before data of october 2022)"
        )
        bdb1.toggled.connect(partial(self.set_option_mat, i=0))
        bdb2 = QtWidgets.QRadioButton(
            "True optics based correction matrix (after data of october 2022)"
        )
        bdb2.toggled.connect(partial(self.set_option_mat, i=1))
        vbox.addWidget(bdb1)
        vbox.addWidget(bdb2)
        bdb1.setChecked(True)
        self.option = 0

        vbox.addStretch(1)
        vbox.addLayout(hbox)

        self.setLayout(vbox)
        # self.setLayout(layout)
        self.setWindowTitle(self.name)
        if self.icon is not None:
            self.setWindowIcon(self.icon)

        self.okButton.clicked.connect(self.accept)
        self.cancelButton.clicked.connect(self.reject)

    def set_option_mat(self, i):
        self.option = i

    def accept(self):
        if self.option == 1:
            self.NIf.init_optics_matrix()

        else:
            self.NIf.init_unitary_matrix()

        QtWidgets.QDialog.accept(self)
