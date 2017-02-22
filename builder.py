#!/usr/bin/env python
# encoding: UTF-8

''' model builder components '''
from PyQt4 import QtGui
from pygimli.mplviewer import drawMesh
from pygimli.meshtools import polytools as plc
import numpy as np
from PyQt4 import QtCore, QtGui

from mpl import SpanWorld, SpanRectangle, SpanCircle, SpanLine, SpanPoly

# TODO: DIE BUTTONS NUR ENABLEN WENN DER TAB AKTIV IST!!!!!!!!!
# TODO: skizze laden und verändern können im model builder
# TODO: beliebiges polygon erstellen durch rumklicken
# TODO: tabelle mit qlistwidget ersetzen
# TODO: bild als hintergrund einstellen zum nachmalen
# TODO: disable world after creation


class Builder(QtGui.QWidget):

    def __init__(self, plotWidget, parent=None):
        super(Builder, self).__init__(parent)
        self.figure = plotWidget
        self.marker = 1
        self.polys = []
        self.undone = []

        self.setupUI()

        ''' connect signals '''
        self.acn_world.triggered.connect(self.createPolyWorld)
        self.acn_rectangle.triggered.connect(self.createPolyRectangle)
        self.acn_circle.triggered.connect(self.createPolyCircle)
        self.acn_line.triggered.connect(self.createPolyLine)
        self.acn_polygon.triggered.connect(self.FormPolygon)

        self.btn_redraw.clicked.connect(self.redrawTable)

        self.btn_undo.clicked.connect(self.undoPoly)
        # self.btn_redo.clicked.connect(self.redoPoly)

    def setupUI(self):
        """
            composing the layout for the tab
        """
        # polytool buttons
        self.grp_polyTools = QtGui.QActionGroup(self)

        self.acn_world = QtGui.QAction(QtGui.QIcon('material/ic_spanWorld.svg'), 'world', self.grp_polyTools)
        self.acn_world.setToolTip("Create your model world where everything happens")
        self.acn_world.setCheckable(True)

        self.acn_rectangle = QtGui.QAction(QtGui.QIcon('material/ic_spanRectangle.svg'), 'rectangle', self.grp_polyTools)
        self.acn_rectangle.setToolTip("Create a rectangle body")
        self.acn_rectangle.setCheckable(True)

        self.acn_circle = QtGui.QAction(QtGui.QIcon('material/ic_spanCircle.svg'), 'circle', self.grp_polyTools)
        self.acn_circle.setToolTip("Create a circle body")
        self.acn_circle.setCheckable(True)

        self.acn_line = QtGui.QAction(QtGui.QIcon('material/ic_spanLine.png'), 'line', self.grp_polyTools)
        self.acn_line.setToolTip("Create a line by clicking")
        self.acn_line.setCheckable(True)

        self.acn_polygon = QtGui.QAction(QtGui.QIcon('material/ic_spanPoly.svg'), 'polygon', self.grp_polyTools)
        self.acn_polygon.setToolTip("Create a polygon by clicking, finish with double click")
        self.acn_polygon.setCheckable(True)

        tb = QtGui.QToolBar()
        tb.setMovable(False)
        tb.addAction(self.acn_world)
        tb.addAction(self.acn_polygon)
        tb.addAction(self.acn_rectangle)
        tb.addAction(self.acn_circle)
        tb.addAction(self.acn_line)

        # parameter table for different polygons
        # TODO: gegen gescheites qlistwidget ersetzen! tabelle ist scheiße
        self.polys_table = QtGui.QTableWidget(self)
        self.polys_table.setRowCount(15)
        self.polys_table.setVerticalHeaderLabels(
            ('Type', 'x0', 'y0', 'x1', 'y1', 'Radius', 'Segments', 'Start', 'End', 'Marker', 'Area', 'Boundary', 'Left?', 'Hole?', 'Closed?'))

        # redraw table button
        self.btn_undo = QtGui.QPushButton()
        self.btn_undo.setToolTip("undo last poly")
        self.btn_undo.setIcon(QtGui.QIcon('material/ic_undo_black_18px.svg'))
        self.btn_redo = QtGui.QPushButton()
        self.btn_redo.setToolTip("redo last poly")
        self.btn_redo.setIcon(QtGui.QIcon('material/ic_redo_black_18px.svg'))
        self.btn_redo.setEnabled(False)
        self.btn_redraw = QtGui.QPushButton()
        self.btn_redraw.setToolTip("redraw whole table after changes were made")
        self.btn_redraw.setIcon(QtGui.QIcon('material/ic_refresh_black_24px.svg'))

        hbox = QtGui.QHBoxLayout()
        hbox.addWidget(self.btn_undo)
        hbox.addWidget(self.btn_redo)
        hbox.addStretch(1)
        hbox.addWidget(self.btn_redraw)
        hbox.setMargin(0)

        # form the layout
        vbox = QtGui.QVBoxLayout()
        vbox.addWidget(tb)
        vbox.addWidget(self.polys_table)
        vbox.addLayout(hbox)
        self.setLayout(vbox)

    def createPolyWorld(self):
        try:
            self.span.disconnect()
        except AttributeError:
            pass
            self.span = SpanWorld(self)
            self.span.connect()

    def createPolyRectangle(self):
        try:
            self.span.disconnect()
        except AttributeError:
            pass
        self.span = SpanRectangle(self)
        self.span.connect()

    def createPolyCircle(self):
        try:
            self.span.disconnect()
        except AttributeError:
            pass
        self.span = SpanCircle(self)
        self.span.connect()

    def createPolyLine(self):
        try:
            self.span.disconnect()
        except AttributeError:
            pass
        self.span = SpanLine(self)
        self.span.connect()

    def FormPolygon(self):
        try:
            self.span.disconnect()
        except AttributeError:
            pass
        self.span = SpanPoly(self)
        self.span.connect()

    def printCoordinates(self, x1, y1, x2, y2, form):

        self.x_p = x1
        self.y_p = y1
        self.x_r = x2
        self.y_r = y2
        self.form = form

        self.constructPoly()

    def printPolygon(self, polygon):
        self.polygon = polygon
        self.form = 'Polygon'

        self.constructPoly()

    def constructPoly(self):

        if self.form == 'World':
            self.polys.append(plc.createWorld(start=[self.x_p, self.y_p], end=[self.x_r, self.y_r], marker=self.marker))

        elif self.form == 'Rectangle':
            self.polys.append(plc.createRectangle(start=[self.x_p, self.y_p], end=[self.x_r, self.y_r], marker=self.marker))

        elif self.form == 'Circle':
            self.polys.append(plc.createCircle(
            pos=(self.x_p, self.y_p), segments=12, radius=self.x_r, marker=self.marker))

        elif self.form == 'Line':
            self.polys.append(plc.createLine(start=[self.x_p, self.y_p], end=[self.x_r, self.y_r], segments=2))

        elif self.form == 'Polygon':
            self.polys.append(plc.createPolygon(self.polygon, marker=self.marker, isClosed=True))

        self.drawPoly()

    def drawPoly(self, fillTable=True):
        self.poly = plc.mergePLC(self.polys)
        self.figure.axis.cla()

        drawMesh(self.figure.axis, self.poly, fitView=False)
        self.figure.canvas.draw()

        if fillTable:
            self.fillTable()
            # iterate marker counter
            self.marker += 1

    def fillTable(self):
        """
            for construction: header labels >>>
            'Type', 'x0', 'y0', 'x1', 'y1', 'Radius', 'Segments', 'Start', 'End', 'Marker', 'Area', 'Boundary', 'Left?', 'Hole?', 'Closed?'
        """
        # update table on release
        self.polys_table.setColumnCount(len(self.polys))
        col = len(self.polys) - 1
        # insert poly type... circle/world/rectangle/hand
        self.polys_table.setItem(0, col, QtGui.QTableWidgetItem(self.form))

        # insert position
        if not self.form == 'Polygon':
            self.polys_table.setItem(
                1, col, QtGui.QTableWidgetItem(str(round(self.x_p, 2))))
            self.polys_table.setItem(
                2, col, QtGui.QTableWidgetItem(str(round(self.y_p, 2))))
        else:
            self.restrictCellFromEditing(1, col)
            self.restrictCellFromEditing(2, col)

        if self.form == 'Rectangle' or self.form == 'World' or self.form == 'Line':
            self.polys_table.setItem(
                3, col, QtGui.QTableWidgetItem(str(round(self.x_r, 2))))
            self.polys_table.setItem(
                4, col, QtGui.QTableWidgetItem(str(round(self.y_r, 2))))
        else:
            self.restrictCellFromEditing(3, col)
            self.restrictCellFromEditing(4, col)

        if self.form == 'Circle':
            # insert segments
            spx_segments = QtGui.QSpinBox()
            spx_segments.setValue(12)
            spx_segments.setMinimum(3)
            self.polys_table.setCellWidget(6, col, spx_segments)
            # insert radius
            spx_radius = QtGui.QDoubleSpinBox()
            spx_radius.setSingleStep(0.01)
            spx_radius.setValue(self.x_r)
            self.polys_table.setCellWidget(5, col, spx_radius)
            # insert start
            spx_start = QtGui.QDoubleSpinBox()
            spx_start.setValue(0.00)
            spx_start.setMinimum(0.00)
            spx_start.setSingleStep(0.01)
            spx_start.setMaximum(2 * np.pi)
            self.polys_table.setCellWidget(7, col, spx_start)
            # insert end
            spx_end = QtGui.QDoubleSpinBox()
            spx_end.setValue(2 * np.pi)
            spx_end.setMinimum(0.00)
            spx_end.setSingleStep(0.01)
            spx_end.setMaximum(2 * np.pi)
            self.polys_table.setCellWidget(8, col, spx_end)
        else:
            self.restrictCellFromEditing(5, col)
            self.restrictCellFromEditing(6, col)
            self.restrictCellFromEditing(7, col)
            self.restrictCellFromEditing(8, col)

        if self.form == 'Line':
            # insert segments
            spx_segments = QtGui.QSpinBox()
            spx_segments.setValue(2)
            spx_segments.setMinimum(2)
            self.polys_table.setCellWidget(6, col, spx_segments)

        if not self.form == 'Line':
            # insert marker
            for k in range(self.marker):
                a = QtGui.QComboBox(self.polys_table)
                [a.addItem(str(m + 1)) for m in range(self.marker)]
                a.setCurrentIndex(k)
                self.polys_table.setCellWidget(9, k, a)
            # insert area
            spx_area = QtGui.QDoubleSpinBox()
            spx_area.setSingleStep(0.01)
            spx_area.setValue(0.00)
            spx_area.setMinimum(0.00)
            self.polys_table.setCellWidget(10, col, spx_area)
        else:
            self.restrictCellFromEditing(9, col)
            self.restrictCellFromEditing(10, col)

        if not self.form == 'World':
            # insert boundary marker
            self.polys_table.setItem(11, col, QtGui.QTableWidgetItem(str(1)))
        else:
            self.restrictCellFromEditing(11, col)

        if self.form == 'Rectangle' or self.form == 'Circle' or self.form == 'Line' or self.form == 'Polygon':
            # insert left direction
            cbx_isLeft = QtGui.QComboBox()
            cbx_isLeft.addItem('False')
            cbx_isLeft.addItem('True')
            self.polys_table.setCellWidget(12, col, cbx_isLeft)
        else:
            self.restrictCellFromEditing(12, col)

        if self.form == 'Rectangle' or self.form == 'Circle' or self.form == 'Polygon':
            # insert is hole
            cbx_isHole = QtGui.QComboBox()
            cbx_isHole.addItem('False')
            cbx_isHole.addItem('True')
            self.polys_table.setCellWidget(13, col, cbx_isHole)
            # insert is closed
            cbx_isClosed = QtGui.QComboBox()
            cbx_isClosed.addItem('False')
            cbx_isClosed.addItem('True')
            cbx_isClosed.setCurrentIndex(1)
            self.polys_table.setCellWidget(14, col, cbx_isClosed)
        else:
            self.restrictCellFromEditing(13, col)
            self.restrictCellFromEditing(14, col)

        self.polys_table.setSizePolicy(
            QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        self.polys_table.resizeColumnsToContents()

    def redrawTable(self):
        """
            read the table after editing figures and redraw all polys
        """
        # empty the list of polygon figures
        del self.polys[:]

        for col in range(self.polys_table.columnCount()):

            item = self.polys_table.item(0, col).text()
            try:
                position1 = [float(self.polys_table.item(1, col).text()), float(self.polys_table.item(2, col).text())]
            except (AttributeError, ValueError):
                pass
            try:  # Rectangle & World
                position2 = [float(self.polys_table.item(3, col).text()), float(self.polys_table.item(4, col).text())]
            except (AttributeError, ValueError):
                pass
            try:  # Circle
                radius = self.polys_table.cellWidget(5, col).value()
            except (AttributeError, ValueError):
                pass
            try:  # Circle & Line
                segments = self.polys_table.cellWidget(6, col).value()
            except (AttributeError, ValueError):
                pass
            try:
                start = self.polys_table.cellWidget(7, col).value()
            except (AttributeError, ValueError):
                pass
            try:
                end = self.polys_table.cellWidget(8, col).value()
            except (AttributeError, ValueError):
                pass
            try:
                marker = int(self.polys_table.cellWidget(9, col).currentText())
            except (AttributeError, ValueError):
                pass
            try:
                area = self.polys_table.cellWidget(10, col).value()
            except (AttributeError, ValueError):
                pass
            try:
                boundaryMarker = int(self.polys_table.item(11, col).text())
            except (AttributeError, ValueError):
                pass
            try:
                leftDirection = int(self.polys_table.cellWidget(12, col).currentIndex())
            except (AttributeError, ValueError):
                pass
            try:
                isHole = int(self.polys_table.cellWidget(13, col).currentIndex())
            except (AttributeError, ValueError):
                pass
            try:
                isClosed = int(self.polys_table.cellWidget(14, col).currentIndex())
            except (AttributeError, ValueError):
                pass

            if item == 'World':
                self.polys.append(plc.createWorld(
                start=position1, end=position2, marker=marker, area=area
                ))
            elif item == 'Rectangle':
                self.polys.append(plc.createRectangle(
                    start=position1, end=position2, marker=marker, area=area, boundaryMarker=boundaryMarker, isHole=isHole, isClosed=isClosed
                ))  # leftDirection=leftDirection
            elif item == 'Circle':
                self.polys.append(plc.createCircle(
                pos=position1, radius=radius, segments=segments, start=start, end=end, marker=marker, area=area, boundaryMarker=boundaryMarker, leftDirection=leftDirection, isHole=isHole, isClosed=isClosed
                ))
            elif item == 'Line':
                self.polys.append(plc.createLine(
                start=start, end=end, segments=segments, boundaryMarker=boundaryMarker, leftDirection=leftDirection
                ))
            elif item == 'Rectangle':
                self.polys.append(plc.createPolygon(
                verts=self.polygon, boundaryMarker=boundaryMarker, leftDirection=leftDirection, marker=marker, area=area
                ))

        self.drawPoly(fillTable=False)

    def undoPoly(self):
        """
            remove last made polygon from list and store it so it won't be lost
        """
        self.undone.append(self.polys.pop())
        self.polys_table.removeColumn(self.polys_table.columnCount() - 1)
        self.marker -= 1
        self.drawPoly(fillTable=False)

    def redoPoly(self):
        self.polys.append(self.undone.pop())
        self.marker += 1
        self.drawPoly()

    def getPoly(self):
        return self.polys

    def restrictCellFromEditing(self, i, j):
        item = QtGui.QTableWidgetItem()
        item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
        # item.setBackground(QtCore.Qt.gray)
        self.polys_table.setItem(i, j, item)


if __name__ == '__main__':

    import sys

    app = QtGui.QApplication(sys.argv)
    builderWin = Builder()
    builderWin.show()
    sys.exit(builderWin.exec_())
