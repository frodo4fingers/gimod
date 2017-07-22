#!/usr/bin/env python
# encoding: UTF-8

''' model builder components '''
try:
    from PyQt5.QtWidgets import QWidget, QApplication, QVBoxLayout, QHBoxLayout, QSpinBox, QDoubleSpinBox, QComboBox, QSizePolicy, QCheckBox, QPushButton, QAction, QActionGroup, QTreeWidget, QTreeWidgetItem, QRadioButton, QFileDialog
    from PyQt5.QtCore import Qt
    from PyQt5.QtGui import QIcon, QFont

except ImportError:
    from PyQt4.QtGui import QWidget, QApplication, QVBoxLayout, QHBoxLayout, QSpinBox, QDoubleSpinBox, QComboBox, QSizePolicy, QCheckBox, QPushButton, QAction, QIcon, QFont, QActionGroup, QTreeWidget, QTreeWidgetItem, QRadioButton, QFileDialog
    from PyQt4.QtCore import Qt

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


class Builder(QWidget):

    def __init__(self, parent=None):
        super(Builder, self).__init__(parent)
        self.parent = parent
        self.figure = parent.plotWidget
        # self.toolBar = parent.toolBar
        self.statusBar = parent.statusBar
        self.marker = 1  # 0
        self.newMarkers = []
        self.polys = []
        self.undone = []
        self.imageClicked = True
        self.markersClicked = True
        self.gridClicked = True
        self.magnetizeClicked = True
        self.mPolyClicked = True
        self.poly = None

        self.setupUI()

        ''' connect signals '''
        # self.acn_image.triggered.connect(self.imagery)
        # self.acn_imageAsBackground.stateChanged.connect(self.imageryBackground)
        # self.acn_imageThreshold1.valueChanged.connect(self.updateImagery)
        # self.acn_imageThreshold2.valueChanged.connect(self.updateImagery)
        # self.acn_imageDensity.valueChanged.connect(self.updateImagery)
        # self.acn_imagePolys.valueChanged.connect(self.updateImagery)
        # self.acn_polygonize.triggered.connect(self.formPolygonFromFigure)
        #
        # self.acn_world.triggered.connect(self.formPolyWorld)
        # self.acn_rectangle.triggered.connect(self.formPolyRectangle)
        # self.acn_circle.triggered.connect(self.formPolyCircle)
        # self.acn_line.triggered.connect(self.formPolyLine)
        # self.acn_polygon.triggered.connect(self.formPolygon)
        # self.acn_markerCheck.triggered.connect(self.markersMove)
        #
        # self.acn_gridToggle.triggered.connect(self.toggleGrid)
        # self.acn_magnetizeGrid.triggered.connect(self.magnetizeGrid)
        # self.acn_magnetizePoly.triggered.connect(self.magnetizePoly)

        self.btn_redraw.clicked.connect(self.redrawTable)

        self.btn_undo.clicked.connect(self.undoPoly)
        self.btn_redo.clicked.connect(self.redoPoly)

    def setupUI(self):
        """
            composing the layout for the tab
        """
        self.bold = QFont()
        self.bold.setBold(True)
        # polytool buttons

        # self.grp_imageTools = QActionGroup(self)
        # self.acn_image = QAction(QIcon('icons/ic_image.svg'), 'image', self.grp_imageTools)
        # self.acn_image.setToolTip("Load image to set as model background or try to extract polygons from")
        # self.acn_image.setCheckable(True)
        #
        # self.acn_polygonize = QAction(QIcon('icons/ic_polygonize.svg'), 'image', self.grp_imageTools)
        # self.acn_polygonize.setToolTip("polygonize the contours")
        # self.acn_polygonize.setVisible(False)
        #
        # self.acn_imageAsBackground = QCheckBox('as background')
        # # self.acn_imageAsBackground.setEnabled(False)
        # self.acn_imageAsBackground.setToolTip("set the chosen image as background to paint your model")
        # self.acn_imageThreshold1 = QSpinBox()
        # self.acn_imageThreshold1.setRange(0, 254)
        # self.acn_imageThreshold1.setValue(200)
        # self.acn_imageThreshold1.setToolTip("bottom value for threshold")
        # self.acn_imageThreshold2 = QSpinBox()
        # self.acn_imageThreshold2.setRange(1, 255)
        # self.acn_imageThreshold2.setValue(255)
        # self.acn_imageThreshold2.setToolTip("top value for threshold")
        # self.acn_imageDensity = QSpinBox()
        # self.acn_imageDensity.setToolTip("set density of dots in polygon")
        # self.acn_imagePolys = QSpinBox()
        # self.acn_imagePolys.setToolTip("set the number of polygons used for model creation")
        # acnBox = QHBoxLayout()
        # acnBox.addWidget(self.acn_imageAsBackground)
        # acnBox.addWidget(self.acn_imageThreshold1)
        # acnBox.addWidget(self.acn_imageThreshold2)
        # acnBox.addWidget(self.acn_imageDensity)
        # acnBox.addWidget(self.acn_imagePolys)
        # acnBox.setContentsMargins(0, 0, 0, 1)
        # acnWidget = QWidget()
        # acnWidget.setLayout(acnBox)
        #
        # self.grp_polyTools = QActionGroup(self)
        # self.acn_world = QAction(QIcon('icons/ic_spanWorld.svg'), 'world', self.grp_polyTools, checkable=True)
        # self.acn_world.setToolTip("Create your model world where everything happens")
        #
        # self.acn_rectangle = QAction(QIcon('icons/ic_spanRectangle.svg'), 'rectangle', self.grp_polyTools, checkable=True)
        # self.acn_rectangle.setToolTip("Create a rectangle body")
        #
        # self.acn_circle = QAction(QIcon('icons/ic_spanCircle.svg'), 'circle', self.grp_polyTools, checkable=True)
        # self.acn_circle.setToolTip("Create a circle body")
        #
        # self.acn_line = QAction(QIcon('icons/ic_spanLine.png'), 'line', self.grp_polyTools, checkable=True)
        # self.acn_line.setToolTip("Create a line by clicking")
        #
        # self.acn_polygon = QAction(QIcon('icons/ic_spanPoly.svg'), 'polygon', self.grp_polyTools, checkable=True)
        # self.acn_polygon.setToolTip("Create a polygon by clicking, finish with double click")
        #
        # self.acn_markerCheck = QAction(QIcon('icons/marker_check.svg'), 'marker', self.grp_polyTools, checkable=True)
        # self.acn_markerCheck.setToolTip("check and reset marker positions")
        #
        # # self.grp_gridTools = QActionGroup(self)
        # self.acn_gridToggle = QAction(QIcon('icons/grid.svg'), 'grid', None, checkable=True)
        # self.acn_gridToggle.setToolTip("turn on and off a grid")
        # self.acn_gridToggle.setEnabled(False)
        #
        # self.acn_magnetizeGrid = QAction(QIcon('icons/grid_magnetize.svg'), 'magnetizeGrid', None, checkable=True)
        # self.acn_magnetizeGrid.setToolTip("magnetize the grid junctions")
        # self.acn_magnetizeGrid.setEnabled(False)
        #
        # self.acn_magnetizePoly = QAction(QIcon('icons/magnetize.svg'), 'magnetizePoly', None, checkable=True)
        # self.acn_magnetizePoly.setToolTip("magnetize the polygons")
        #
        # self.toolBar.addAction(self.acn_image)
        # self.widgetAction = self.toolBar.addWidget(acnWidget)
        # self.widgetAction.setVisible(False)
        # self.toolBar.addAction(self.acn_polygonize)
        # self.toolBar.addSeparator()
        # self.toolBar.addAction(self.acn_world)
        # self.toolBar.addAction(self.acn_polygon)
        # self.toolBar.addAction(self.acn_rectangle)
        # self.toolBar.addAction(self.acn_circle)
        # self.toolBar.addAction(self.acn_line)
        # self.toolBar.addSeparator()
        # self.toolBar.addAction(self.acn_markerCheck)
        # self.toolBar.addSeparator()
        # self.toolBar.addAction(self.acn_gridToggle)
        # self.toolBar.addAction(self.acn_magnetizeGrid)
        # self.toolBar.addAction(self.acn_magnetizePoly)

        self.tw_polys = QTreeWidget()
        self.tw_polys.setAlternatingRowColors(True)
        self.tw_polys.setHeaderLabels(("Type", "Value"))
        # TODO: stretch that darn first column to content!
        # self.tw_polys.header().hide()
        # self.tw_polys.showDropIndicator()
        # self.tw_polys.setRootIsDecorated(False)

        # redraw table button
        self.btn_undo = QPushButton()
        self.btn_undo.setToolTip("undo last poly")
        self.btn_undo.setIcon(QIcon('icons/ic_undo_black_18px.svg'))
        self.btn_undo.setEnabled(False)
        self.btn_redo = QPushButton()
        self.btn_redo.setToolTip("redo last poly")
        self.btn_redo.setIcon(QIcon('icons/ic_redo_black_18px.svg'))
        self.btn_redo.setEnabled(False)
        self.rbtn_plotRegions = QRadioButton('regions')
        self.rbtn_plotRegions.setChecked(True)
        self.rbtn_plotAttributes = QRadioButton('attributes')
        self.btn_export = QPushButton()
        self.btn_export.setIcon(QIcon("icons/ic_save_black_24px.svg"))
        self.btn_export.setToolTip("save as *.poly")
        self.btn_export.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        self.btn_redraw = QPushButton()
        self.btn_redraw.setToolTip("redraw whole table after changes were made")
        self.btn_redraw.setIcon(QIcon('icons/ic_refresh_black_24px.svg'))

        # TODO: move that to gimod.py:
        hbox = QHBoxLayout()
        hbox.addWidget(self.btn_undo)
        hbox.addWidget(self.btn_redo)
        hbox.addWidget(self.rbtn_plotRegions)
        hbox.addWidget(self.rbtn_plotAttributes)
        hbox.addStretch(1)
        hbox.addWidget(self.btn_redraw)
        hbox.addStretch(1)
        hbox.addWidget(self.btn_export)
        # hbox.setMargin(0)

        # form the layout
        vbox = QVBoxLayout()
        vbox.addWidget(self.tw_polys)
        vbox.addLayout(hbox)
        self.setLayout(vbox)

    # def imagery(self):
    #     if self.imageClicked is True:
    #         # FIXME: cheeky piece of shit... wont accept given formats
    #         self.fname = QFileDialog.getOpenFileName(self, caption='choose sketch')[0]
    #         if self.fname:
    #             self.widgetAction.setVisible(True)
    #             self.acn_polygonize.setVisible(True)
    #             self.imageClicked = False
    #             # instanciate the imageTools class
    #             self.imageTools = ImageTools(self)
    #             self.imageTools.getContours()
    #
    #     else:
    #         self.widgetAction.setVisible(False)
    #         self.acn_polygonize.setVisible(False)
    #         self.acn_image.setChecked(False)
    #         self.imageClicked = True
    #
    # def updateImagery(self):
    #     self.imageTools.getContours()
    #
    # def imageryBackground(self):
    #     if self.acn_imageAsBackground.isChecked() is True:
    #         self.acn_imageThreshold1.setEnabled(False)
    #         self.acn_imageThreshold2.setEnabled(False)
    #         self.acn_imagePolys.setEnabled(False)
    #         self.acn_imageDensity.setEnabled(False)
    #         self.imageTools.setBackground()
    #     else:
    #         self.updateImagery()
    #         self.acn_imageThreshold1.setEnabled(True)
    #         self.acn_imageThreshold2.setEnabled(True)
    #         self.acn_imagePolys.setEnabled(True)
    #         self.acn_imageDensity.setEnabled(True)

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
        self.tw_polys.clear()
        self.polys.clear()
        self.marker = 1
        self.parent.setCursor(Qt.WaitCursor)
        for c in self.imageTools.contoursCutted:
            self.printPolygon(c)
        self.figure.axis.set_ylim(self.figure.axis.get_ylim()[::-1])
        self.figure.canvas.draw()
        self.statusBar.showMessage(str(self.poly))
        self.parent.setCursor(Qt.ArrowCursor)

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

        self.btn_undo.setEnabled(True)
        self.drawPoly()

    def drawPoly(self, fillTable=True):
        self.poly = plc.mergePLC(self.polys)
        self.figure.axis.cla()

        if self.rbtn_plotRegions.isChecked() is True:
            drawMesh(self.figure.axis, self.poly, fitView=False)
            self.figure.canvas.draw()
        else:
            attrMap = self.zipUpMarkerAndAttributes()
            meshTmp = createMesh(self.poly)
            # try:
            attrMap = pg.solver.parseMapToCellArray(attrMap, meshTmp)
            drawMeshBoundaries(self.figure.axis, meshTmp, hideMesh=True)
            drawModel(self.figure.axis, meshTmp, tri=True, data=attrMap)
            self.figure.canvas.draw()

        if fillTable:
            self.fillTable()
            # iterate marker counter
            self.marker += 1

        if not self.mPolyClicked:
            x,y =self.getNodes()
            self.mp.plotMagnets(x, y)

    def fillTable(self):
        # FIXME: marker is iterated to existent state. needs to be recounted AFTER table creation so all markers can be chosen for all polys
        # HACK: maybe with redrawTable, bc the marker counter wont change within that process
        twItem = QTreeWidgetItem()
        twItem.setText(0, self.form)
        twItem.setFont(0, self.bold)

        if self.form == 'World' or self.form == 'Rectangle' or self.form == 'Line':
            # twItem.setBackgroundColor(0, QColor(0, 255, 0))
            # start x
            xStart = QTreeWidgetItem()
            xStart.setFlags(xStart.flags() | Qt.ItemIsEditable)
            xStart.setText(0, "Start x:")
            xStart.setText(1, str(self.x_p))
            twItem.addChild(xStart)
            # start y
            yStart = QTreeWidgetItem()
            yStart.setFlags(yStart.flags() | Qt.ItemIsEditable)
            yStart.setText(0, "Start y:")
            yStart.setText(1, str(self.y_p))
            twItem.addChild(yStart)
            # end x
            xEnd = QTreeWidgetItem()
            xEnd.setFlags(xEnd.flags() | Qt.ItemIsEditable)
            xEnd.setText(0, "End x:")
            xEnd.setText(1, str(self.x_r))
            twItem.addChild(xEnd)
            # end y
            yEnd = QTreeWidgetItem()
            yEnd.setFlags(yEnd.flags() | Qt.ItemIsEditable)
            yEnd.setText(0, "End y:")
            yEnd.setText(1, str(self.y_r))
            twItem.addChild(yEnd)

        if self.form == 'Circle':
            # insert center
            center = QTreeWidgetItem()
            center.setFlags(center.flags() | Qt.ItemIsEditable)
            center.setText(0, "Center:")
            center.setText(1, (str(round(self.x_p, 2)) + ", " + str(round(self.y_p, 2))))
            twItem.addChild(center)
            # radius
            spx_radius = QDoubleSpinBox()
            spx_radius.setSingleStep(0.01)
            spx_radius.setValue(self.x_r)
            radius = QTreeWidgetItem()
            radius.setText(0, "Radius:")
            twItem.addChild(radius)
            self.tw_polys.setItemWidget(radius, 1, spx_radius)
            # insert segments
            spx_segments = QSpinBox()
            spx_segments.setValue(12)
            spx_segments.setMinimum(3)
            spx_segments.setMaximum(int(1e10))
            segments = QTreeWidgetItem()
            segments.setText(0, "Segments:")
            twItem.addChild(segments)
            self.tw_polys.setItemWidget(segments, 1, spx_segments)
            # insert start
            spx_start = QDoubleSpinBox()
            spx_start.setValue(0.00)
            spx_start.setMinimum(0.00)
            spx_start.setSingleStep(0.01)
            spx_start.setMaximum(2 * np.pi)
            start = QTreeWidgetItem()
            start.setText(0, "Start angle:")
            twItem.addChild(start)
            self.tw_polys.setItemWidget(start, 1, spx_start)
            # insert end
            spx_end = QDoubleSpinBox()
            spx_end.setValue(2 * np.pi)
            spx_end.setMinimum(0.00)
            spx_end.setSingleStep(0.01)
            spx_end.setMaximum(2 * np.pi)
            end = QTreeWidgetItem()
            end.setText(0, "End angle:")
            twItem.addChild(end)
            self.tw_polys.setItemWidget(end, 1, spx_end)

        if self.form == 'Line':
            # insert segments
            spx_segments = QSpinBox()
            spx_segments.setValue(1)
            spx_segments.setMinimum(1)
            segments = QTreeWidgetItem()
            segments.setText(0, "Segments:")
            twItem.addChild(segments)
            self.tw_polys.setItemWidget(segments, 1, spx_segments)

        if self.form != 'Line':
            # insert marker
            # for k in range(self.marker):
            a = QComboBox()
            [a.addItem(str(m + 1)) for m in range(self.marker)]
            a.setCurrentIndex(self.marker - 1)
            marker = QTreeWidgetItem()
            marker.setText(0, "Marker:")
            twItem.addChild(marker)
            self.tw_polys.setItemWidget(marker, 1, a)
            # insert area
            spx_area = QDoubleSpinBox()
            spx_area.setSingleStep(0.01)
            spx_area.setValue(0.00)
            spx_area.setMinimum(0.00)
            area = QTreeWidgetItem()
            area.setText(0, "Area:")
            twItem.addChild(area)
            self.tw_polys.setItemWidget(area, 1, spx_area)

        if self.form != 'World':
            # insert boundary marker
            spx_boundaryMarker = QSpinBox()
            spx_boundaryMarker.setValue(1)
            spx_boundaryMarker.setMinimum(1)
            boundaryMarker = QTreeWidgetItem()
            boundaryMarker.setText(0, "BoundaryMarker:")
            twItem.addChild(boundaryMarker)
            self.tw_polys.setItemWidget(boundaryMarker, 1, spx_boundaryMarker)

        if self.form == 'Rectangle' or self.form == 'Circle' or self.form == 'Line' or self.form == 'Polygon':
            # insert left direction
            cbx_isLeft = QComboBox()
            cbx_isLeft.addItem('False')
            cbx_isLeft.addItem('True')
            isLeft = QTreeWidgetItem()
            isLeft.setText(0, "isLeft:")
            twItem.addChild(isLeft)
            self.tw_polys.setItemWidget(isLeft, 1, cbx_isLeft)

        if self.form == 'Rectangle' or self.form == 'Circle' or self.form == 'Polygon':
            # insert is hole
            cbx_isHole = QComboBox()
            cbx_isHole.addItem('False')
            cbx_isHole.addItem('True')
            isHole = QTreeWidgetItem()
            isHole.setText(0, "isHole:")
            twItem.addChild(isHole)
            self.tw_polys.setItemWidget(isHole, 1, cbx_isHole)
            # insert is closed
            cbx_isClosed = QComboBox()
            cbx_isClosed.addItem('False')
            cbx_isClosed.addItem('True')
            cbx_isClosed.setCurrentIndex(1)
            isClosed = QTreeWidgetItem()
            isClosed.setText(0, "isClosed:")
            twItem.addChild(isClosed)
            self.tw_polys.setItemWidget(isClosed, 1, cbx_isClosed)

        if self.form == 'Polygon':
            verts = QTreeWidgetItem()
            verts.setText(0, "Verts:")
            verts.setText(1, ', '.join(str(i) for i in self.polygon))
            verts.setFlags(verts.flags() | Qt.ItemIsEditable)
            twItem.addChild(verts)

        if self.form != 'Line':
            attributes = QTreeWidgetItem()
            attributes.setText(0, "Attributes:")
            attributes.setFlags(attributes.flags() | Qt.ItemIsEditable)
            twItem.addChild(attributes)

        self.tw_polys.addTopLevelItem(twItem)
        twItem.setExpanded(True)  # needs to happen after adding to tree
        if not self.tw_polys.currentItem():
            self.tw_polys.setCurrentItem(self.tw_polys.topLevelItem(0))
            self.tw_polys.setEnabled(True)
        self.tw_polys.resizeColumnToContents(0)

    def redrawTable(self):
        # BUG: line misses first half after redraw
        # BUG: after redraw marker might be lost: control mechanism and/or possible manual adding of a marker
        self.parent.setCursor(Qt.WaitCursor)
        self.statusBar.showMessage("updating...")
        self.polys.clear()
        polyMeta = []
        for i in range(self.tw_polys.topLevelItemCount()):
            meta = []
            # get polygon type
            meta.append(self.tw_polys.topLevelItem(i).text(0))
            for k in range(self.tw_polys.topLevelItem(i).childCount()):
                try:
                    # text from ComboBox
                    meta.append(self.tw_polys.itemWidget(self.tw_polys.topLevelItem(i).child(k), 1).currentIndex())
                except AttributeError:
                    try:
                        # value from DoubleSpinBox
                        meta.append(self.tw_polys.itemWidget(self.tw_polys.topLevelItem(i).child(k), 1).value())
                    except AttributeError:
                        # normal text cell
                        meta.append(self.tw_polys.topLevelItem(i).child(k).text(1))
            polyMeta.append(meta)

        self.polyAttributes = []
        self.polyMarkers = []
        for i, p in enumerate(polyMeta):
            if p[0] == 'World':
                self.polys.append(plc.createWorld(
                start=[float(p[1]), float(p[2])], end=[float(p[3]), float(p[4])], marker=int(p[5]), area=float(p[6])
                ))
                self.polyAttributes.append(p[7])
                self.polyMarkers.append(int(p[5]))

            elif p[0] == 'Rectangle':
                self.polys.append(plc.createRectangle(
                start=[float(p[1]), float(p[2])], end=[float(p[3]), float(p[4])], marker=int(p[5]), area=float(p[6]), boundaryMarker=int(p[7]), isHole=int(p[9]), isClosed=int(p[10])
                ))  # leftDirection=int(p[8])
                self.polyAttributes.append(p[11])
                self.polyMarkers.append(int(p[5]))

            elif p[0] == 'Circle':
                self.polys.append(plc.createCircle(
                pos=tuple(np.asarray(p[1].split(', '), dtype=float)), radius=float(p[2]), segments=int(p[3]), start=float(p[4]), end=float(p[5]), marker=int(p[6]), area=float(p[7]), boundaryMarker=int(p[8]), leftDirection=int(p[9]), isHole=int(p[10]), isClosed=int(p[11])
                ))
                self.polyAttributes.append(p[12])
                self.polyMarkers.append(int(p[6]))

            elif p[0] == 'Line':
                self.polys.append(plc.createLine(
                start=[float(p[1]), float(p[2])], end=[float(p[3]), float(p[4])], segments=int(p[5]), boundaryMarker=int(p[6]), leftDirection=int(p[7])
                ))
            elif p[0] == 'Polygon':
                # meh..
                vertStr = p[7].replace('[', '').replace(']', '').replace(',', '').split(' ')
                verts = [[float(vertStr[i]), float(vertStr[i+1])] for i in range(0, len(vertStr), 2)]
                poly = plc.createPolygon(
                verts=verts, area=float(p[2]), boundaryMarker=int(p[3]), isClosed=int(p[6]))  # leftDirection=int(p[4])

                if len(self.newMarkers) != 0:
                    markerPos = self.newMarkers[i][0]
                else:
                    markerPos = pg.center(verts)

                if int(p[5]) == 1:
                    pg.Mesh.addHoleMarker(poly, markerPos)
                else:
                    pg.Mesh.addRegionMarker(poly, markerPos, marker=int(p[1]))
                self.polys.append(poly)
                self.polyAttributes.append(p[8])
                self.polyMarkers.append(int(p[1]))

        self.statusBar.clearMessage()
        self.drawPoly(fillTable=False)
        self.parent.setCursor(Qt.ArrowCursor)

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
            self.acn_markerCheck.setChecked(False)
            self.redrawTable()
            self.parent.setCursor(Qt.ArrowCursor)

    def markerSize(self):
        m, n = self.figure.axis.get_xlim()
        return abs(m - n)/50

    # def toggleGrid(self):
    #     if self.gridClicked is True:
    #         self.figure.axis.grid()
    #         self.gridClicked = False
    #     else:
    #         self.figure.axis.grid(False)
    #         self.gridClicked = True
    #         self.acn_gridToggle.setChecked(False)
    #     self.figure.canvas.draw()
    #
    # def magnetizeGrid(self):
    #     if self.magnetize is True:
    #         self.figure.axis.grid()
    #         self.magnetize = False
    #     else:
    #         self.figure.axis.grid(False)
    #         self.magnetize = True
    #         self.acn_magnetizeGrid.setChecked(False)
    #     self.figure.canvas.draw()
    #
    # def magnetizePoly(self):
    #     if self.mPolyClicked is True:
    #         x = []
    #         y = []
    #         x, y = self.getNodes()
    #
    #         self.mp = MagnetizePolygons(self, x, y)
    #         self.mp.connect()
    #         # HACK: against flickering and false data while spanning:
    #         self.span.disconnect()
    #         self.span.connect()
    #         self.mPolyClicked = False
    #     else:
    #         self.mp.disconnect()
    #         self.figure.axis.grid(False)
    #         self.mPolyClicked = True
    #         self.acn_magnetizeGrid.setChecked(False)
    #     self.figure.canvas.draw()
    #
    # def getNodes(self):
    #     arr = self.poly.positions()
    #     x = list(pg.x(arr))
    #     y = list(pg.y(arr))
    #
    #     return x, y

    def undoPoly(self):
        """
            remove last made polygon from list and store it so it won't be lost
        """

        self.undone.append(self.polys.pop())
        self.tw_polys.takeTopLevelItem(self.tw_polys.topLevelItemCount() - 1)
        self.marker -= 1
        self.btn_redo.setEnabled(True)
        if not len(self.polys) == 0:
            self.drawPoly(fillTable=False)
        else:
            self.figure.axis.cla()
            self.figure.canvas.draw()
            self.btn_undo.setEnabled(False)

    def redoPoly(self):
        if len(self.undone) > 0:
            self.polys.append(self.undone.pop())
            self.marker += 1
            self.drawPoly(fillTable=True)
        if len(self.undone) == 0:
            self.btn_redo.setEnabled(False)

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
            join marker and attribute into list so it can be pased to cells and check if duplicates
            were made
        """
        attrMap = []
        for i, a in enumerate(self.polyAttributes):
            if a == '' or a == '\n':
                self.statusBar.showMessage("ERROR: empty attributes can't be assigned!")
            else:
                try:
                    a = float(a)
                    # self.statusBar.showMessage("{} is a float now".format(a))
                    attrMap.append([self.polyMarkers[i], a])
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
