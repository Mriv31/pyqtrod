# This Python file uses the following encoding: utf-8
from PyQt6 import QtCore
from PyQt6 import QtWidgets, uic, QtGui


class ActionStyle(QtWidgets.QProxyStyle):
    def __init__(self, style = None):
        super().__init__(style)
        self._colors = dict()

    def setColor(self, text, color):
        self._colors[text] = color

    def drawControl(self, element, option, painter, widget):
        if element == QtWidgets.QStyle.ControlElement.CE_MenuItem:
            text = option.text
            option_ = QtWidgets.QStyleOptionMenuItem(option)
            if text in self._colors:
                color = self._colors[text]
            else:
                color = QtGui.QColor("#A9BBAE")
            option_.palette.setColor(QtGui.QPalette.ColorRole.Text, QtGui.QColor(color))
            return self.baseStyle().drawControl(element, option_, painter, widget)
        return self.baseStyle().drawControl(element, option, painter, widget)

class MenuStyler():
    def __init__(self, menu):
        style = ActionStyle()
        style.setBaseStyle(menu.style())
        menu.setStyle(style)
        self._style = style
        self._menu = menu

    def setColor(self, key, color):
        if isinstance(key, str):
            self._style.setColor(key, color)
        elif isinstance(key, int):
            text = self._menu.actions()[key].text()
            self._style.setColor(text, color)
        else:
            raise ValueError("Key must be either int or string")

