#!/usr/bin/env python
# encoding: UTF-8

''' model builder components '''
try:
    from PyQt5.QtWidgets import QWidget, QApplication, QVBoxLayout, QHBoxLayout, QSpinBox, QDoubleSpinBox, QComboBox, QSizePolicy, QCheckBox, QPushButton, QAction, QActionGroup, QTreeWidget, QTreeWidgetItem, QRadioButton, QFileDialog, QMessageBox
    from PyQt5.QtCore import Qt, QSize
    from PyQt5.QtGui import QIcon, QFont

except ImportError:
    from PyQt4.QtGui import QWidget, QApplication, QVBoxLayout, QHBoxLayout, QSpinBox, QDoubleSpinBox, QComboBox, QSizePolicy, QCheckBox, QPushButton, QAction, QIcon, QFont, QActionGroup, QTreeWidget, QTreeWidgetItem, QRadioButton, QFileDialog, QMessageBox
    from PyQt4.QtCore import Qt, QSize

from matplotlib import patches

from mpl import SpanWorld, SpanRectangle, SpanCircle, SpanLine, SpanPoly, DraggablePoint, MagnetizePolygons
# from core import ImageTools
import numpy as np

import pygimli as pg
from pygimli.mplviewer import drawMesh, drawMeshBoundaries, drawModel
from pygimli.meshtools import polytools as plc
from pygimli.meshtools import createMesh, writePLC

# TODO: skizze laden und verändern können im model builder
# TODO: bild als hintergrund einstellen zum nachmalen
# TODO: disable world after creation  # pun intended


class Builder():

    def __init__(self, parent=None):
        # super(Builder, self).__init__(parent)
        self.parent = parent
        self.figure = parent.plotWidget
        # self.toolBar = parent.toolBar
        self.statusBar = parent.statusBar
        self.marker = 1  # 0
        self.newMarkers = []
        self.polys = []
        self.undone = []
        # self.imageClicked = True
        self.markersClicked = True
        self.gridClicked = True
        self.magnetizeClicked = True
        self.mPolyClicked = True
        self.poly = None

        self.form = None
        self.x_p = None
        self.y_p = None
        self.x_r = None
        self.y_r = None
        self.polygon = None

    def formPolyWorld(self):
        try:
            self.span.disconnect()
        except AttributeError:
            pass
        self.span = SpanWorld(self)
        self.span.connect()

    def formPolyRectangle(self):
        try:
            self.span.disconnect()
        except AttributeError:
            pass
        self.span = SpanRectangle(self)
        self.span.connect()

    def formPolyCircle(self):
        try:
            self.span.disconnect()
        except AttributeError:
            pass
        self.span = SpanCircle(self)
        self.span.connect()

    def formPolyLine(self):
        try:
            self.span.disconnect()
        except AttributeError:
            pass
        self.span = SpanLine(self)
        self.span.connect()

    def formPolygon(self):
        try:
            self.span.disconnect()
        except AttributeError:
            pass
        self.span = SpanPoly(self)
        self.span.connect()

    def formPolygonFromFigure(self):
        self.parent.info_tree.tw_polys.clear()
        self.polys.clear()
        self.marker = 1
        self.parent.setCursor(Qt.WaitCursor)
        cont_ = len(self.parent.image_tools.contoursCutted)
        for i, contour in enumerate(self.parent.image_tools.contoursCutted):
            self.parent.statusBar.showMessage("processing found polygons {}/{}".format(i, cont_))
            self.printPolygon(contour)
        self.figure.axis.set_ylim(self.figure.axis.get_ylim()[::-1])
        # self.figure.canvas.draw()
        self.statusBar.showMessage(str(self.poly))
        self.parent.setCursor(Qt.ArrowCursor)
        self.parent.statusBar.clearMessage()

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
            self.polys.append(plc.createLine(start=[self.x_p, self.y_p], end=[self.x_r, self.y_r], segments=1))

        elif self.form == 'Polygon':
            self.polys.append(plc.createPolygon(self.polygon, marker=self.marker, isClosed=True))

        self.parent.info_tree.btn_undo.setEnabled(True)
        self.parent.toolBar.acn_reset_figure.setEnabled(True)
        self.drawPoly()

    def drawPoly(self, fillTable=True, polys=None):
        if polys is None:
            self.poly = plc.mergePLC(self.polys)
        else:
            self.poly = plc.mergePLC(polys)
        self.figure.axis.cla()

        # check for the region plot option in treeview functions below the table
        if self.parent.info_tree.rbtn_plotRegions.isChecked() is True:
            drawMesh(self.figure.axis, self.poly, fitView=False)
            self.figure.canvas.draw()
        else:
            attrMap = self.zipUpMarkerAndAttributes()
            if attrMap:  # not empty
                meshTmp = createMesh(self.poly)
                # try:
                attrMap = pg.solver.parseMapToCellArray(attrMap, meshTmp)
                drawMeshBoundaries(self.figure.axis, meshTmp, hideMesh=True)
                drawModel(self.figure.axis, meshTmp, tri=True, data=attrMap)
                self.figure.canvas.draw()
            else:  # empty
                QMessageBox.question(None, 'Whoops..' , "Your regions don't have any attributes to plot!", QMessageBox.Ok)

        if fillTable:
            self.parent.info_tree.fillTable(self.form, self.x_p, self.y_p, self.x_r, self.y_r, self.polygon, self.marker)
            # iterate marker counter
            self.marker += 1

        if not self.mPolyClicked:
            x,y =self.getNodes()
            self.mp.plotMagnets(x, y)

    def resetFigure(self):
        """
        When clicked the user is asked if all achievements should really be discarded, since this method will clear the figure, the info tree and everything that has been stored.
        """
        reply = QMessageBox.question(None, 'Careful there!' , "You are about to delete your project.. proceed?", QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
        if reply == QMessageBox.Yes:
            # clear everything
            self.figure.axis.cla()
            self.figure.canvas.draw()
            self.undone = []
            self.polys = []
            self.parent.info_tree.tw_polys.clear()
            # and disable functions that are only accessible if a poly is there
            self.parent.info_tree.btn_undo.setEnabled(False)
            self.parent.toolBar.acn_reset_figure.setEnabled(False)
        else:
            pass


    def markersMove(self):
        """
            plots dots as marker positions which can be moved
        """
        try:  # to avoid emitting a signal and using it multiple ways
            self.span.disconnect()
        except AttributeError:
            pass

        if self.markersClicked is True:
            self.markersClicked = False
            self.dps = []
            for i, p in enumerate(self.polys):
                m = pg.center(p.positions())
                mark = patches.Circle(m, radius=self.markerSize(), fc='r')
                self.figure.axis.add_patch(mark)
                dp = DraggablePoint(mark, i, m)
                dp.connect()
                self.dps.append(dp)
            self.figure.canvas.draw()

        else:
            # BUG: figure upside down
            self.parent.setCursor(Qt.WaitCursor)
            for p in self.dps:
                val = p.returnValue()
                self.newMarkers.append(list(val.values()))
                p.disconnect()
            self.markersClicked = True
            self.parent.toolBar.acn_markerCheck.setChecked(False)
            self.parent.info_tree.redrawTable()
            self.parent.setCursor(Qt.ArrowCursor)

    def markerSize(self):
        m, n = self.figure.axis.get_xlim()
        return abs(m - n)/50

    def toggleGrid(self):
        if self.gridClicked is True:
            self.figure.axis.grid()
            self.gridClicked = False
        else:
            self.figure.axis.grid(False)
            self.gridClicked = True
            self.acn_gridToggle.setChecked(False)
        self.figure.canvas.draw()

    def magnetizeGrid(self):
        if self.magnetize is True:
            self.figure.axis.grid()
            self.magnetize = False
        else:
            self.figure.axis.grid(False)
            self.magnetize = True
            self.parent.toolBarself.acn_magnetizeGrid.setChecked(False)
        self.figure.canvas.draw()

    def magnetizePoly(self):
        if self.mPolyClicked is True:
            x = []
            y = []
            x, y = self.getNodes()

            self.mp = MagnetizePolygons(self, x, y)
            self.mp.connect()
            # HACK: against flickering and false data while spanning:
            self.span.disconnect()
            self.span.connect()
            self.mPolyClicked = False
        else:
            self.mp.disconnect()
            self.figure.axis.grid(False)
            self.mPolyClicked = True
            self.parent.toolBar.acn_magnetizeGrid.setChecked(False)
        self.figure.canvas.draw()

    def getNodes(self):
        arr = self.poly.positions()
        x = list(pg.x(arr))
        y = list(pg.y(arr))

        return x, y

    def undoPoly(self):
        """
            remove last made polygon from list and store it so it won't be lost
        """
        self.undone.append(self.polys.pop())
        self.parent.info_tree.tw_polys.takeTopLevelItem(self.parent.info_tree.tw_polys.topLevelItemCount() - 1)
        self.marker -= 1
        self.parent.info_tree.btn_redo.setEnabled(True)
        if not len(self.polys) == 0:
            self.drawPoly(fillTable=False)
        else:
            self.figure.axis.cla()
            self.figure.canvas.draw()
            self.parent.info_tree.btn_undo.setEnabled(False)

    def redoPoly(self):
        if len(self.undone) > 0:
            self.polys.append(self.undone.pop())
            self.marker += 1
            self.drawPoly(fillTable=True)
        if len(self.undone) == 0:
            self.parent.info_tree.btn_redo.setEnabled(False)

    def getPoly(self):
        return self.polys

    # TODO: move to gimod.py
    def exportPoly(self):
        """
            export the poly figure
        """
        export_poly = QFileDialog.getSaveFileName(
            self, caption='Save Poly Figure')

        # if export_poly:
        if export_poly.endswith('.poly'):
            writePLC(self.poly, export_poly)
        else:
            writePLC(self.poly, export_poly + '.poly')

    def zipUpMarkerAndAttributes(self):
        """
            join marker and attribute into list so it can be pased to cells and check if duplicates were made
        """
        attrMap = []
        for i, a in enumerate(self.parent.info_tree.polyAttributes):
            if a == '' or a == '\n':
                self.statusBar.showMessage("ERROR: empty attributes can't be assigned!")
            else:
                try:
                    a = float(a)
                    # self.statusBar.showMessage("{} is a float now".format(a))
                    attrMap.append([self.parent.info_tree.polyMarkers[i], a])
                except ValueError:
                    self.statusBar.showMessage("ERROR: some values seem to be string. int or float is needed")

        return attrMap

    def getPoly(self):
        return self.poly


if __name__ == '__main__':

    import sys

    app = QApplication(sys.argv)
    builderWin = Builder()
    builderWin.show()
    sys.exit(builderWin.exec_())
