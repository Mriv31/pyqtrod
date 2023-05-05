from PyQt6 import QtWidgets, QtGui
symbols=["o","t","t1","t2","t3","s","p","h","star","+","d","x"]
colors = [None,"red","orange","black","blue","green","yellow","grey","white"]

class dsStyleMenu(QtWidgets.QMenu):
    def __init__(self,title,parent,PDs):
        super(dsStyleMenu, self).__init__(title,parent)
        self.addMenu(ColorMenu("Change Color",parent=self,dataset=PDs))
        self.addMenu(PointContourColorMenu("Change Point Contour Color",parent=self,dataset=PDs))
        self.addMenu(PointFillingColorMenu("Change Point Filling Color",parent=self,dataset=PDs))
        self.addMenu(PointSizeMenu("Change Point Size",parent=self,dataset=PDs))
        self.addMenu(PointSymbolMenu("Change Symbol",parent=self,dataset=PDs))


class ColorMenu(QtWidgets.QMenu):
    def __init__(self,title,parent,dataset):
        super(ColorMenu, self).__init__(title,parent)
        for c in colors:
            coloraction = QtGui.QAction(c,self)
            self.addAction(coloraction)
            coloraction.triggered.connect(lambda _,y=c: dataset.change_line_color(y))

class PointFillingColorMenu(QtWidgets.QMenu):
    def __init__(self,title,parent,dataset):
        super(PointFillingColorMenu, self).__init__(title,parent)


        for c in colors:
            coloraction = QtGui.QAction(c,self)
            self.addAction(coloraction)
            coloraction.triggered.connect(lambda _,y=c: dataset.change_point_fill_color(y))


class PointContourColorMenu(QtWidgets.QMenu):
    def __init__(self,title,parent,dataset):
        super(PointContourColorMenu, self).__init__(title,parent)



        for c in colors:
            coloraction = QtGui.QAction(c,self)
            self.addAction(coloraction)
            coloraction.triggered.connect(lambda _,y=c: dataset.change_point_color(y))


class PointSizeMenu(QtWidgets.QMenu):
    def __init__(self,title,parent,dataset):
        super(PointSizeMenu, self).__init__(title,parent)


        sizes=range(10)

        for c in sizes:
            coloraction = QtGui.QAction(str(c),self)
            coloraction.triggered.connect(lambda _,y=c: dataset.change_point_size(y))
            self.addAction(coloraction)


class PointSymbolMenu(QtWidgets.QMenu):
    def __init__(self,title,parent,dataset):
        super(PointSymbolMenu, self).__init__(title,parent)



        for c in symbols:
            coloraction = QtGui.QAction(c,self)
            self.addAction(coloraction)
            coloraction.triggered.connect(lambda _,y=c :dataset.change_point_symbol(y))
