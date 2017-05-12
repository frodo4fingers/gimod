#!/usr/bin/env python
# encoding: UTF-8

try:
    from PyQt5.QtWidgets import QWidget, QApplication, QVBoxLayout, QHBoxLayout, QSpinBox, QDoubleSpinBox, QComboBox, QSizePolicy, QCheckBox, QPushButton, QAction, QActionGroup, QTreeWidget, QTreeWidgetItem, QRadioButton, QFileDialog, QToolBar
    from PyQt5.QtCore import QSize, Qt
    from PyQt5.QtGui import QIcon, QFont

except ImportError:
    from PyQt4.QtGui import QWidget, QApplication, QVBoxLayout, QHBoxLayout, QSpinBox, QDoubleSpinBox, QComboBox, QSizePolicy, QCheckBox, QPushButton, QAction, QIcon, QFont, QActionGroup, QTreeWidget, QTreeWidgetItem, QRadioButton, QFileDialog, QToolBar
    from PyQt4.QtCore import QSize, Qt

import pygimli as pg
from pygimli.meshtools import polytools as plc
import numpy as np


class PropertyTable(QWidget):
    """
        Provides the TreeViewWidget on the left side of the GUI
    """

    def __init__(self, parent=None):
        super(PropertyTable, self).__init__(parent)
        # self.drawPoly = parent.builder.drawPoly
        self.statusBar = parent.statusBar
        self.polys = []
        self.undone = []
        self.setupWidget()

        ''' connect signals '''
        self.btn_redraw.clicked.connect(self.redrawTable)
        self.btn_undo.clicked.connect(self.undoPoly)
        self.btn_redo.clicked.connect(self.redoPoly)

    def setParent(self, newParent):
        self.parent = newParent
        self.drawPoly = self.parent.builder.drawPoly

    def setupWidget(self):
        self.bold = QFont()
        self.bold.setBold(True)
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
        #
        # form the layout
        vbox = QVBoxLayout()
        vbox.addWidget(self.tw_polys)
        vbox.addLayout(hbox)
        # self.show()
        self.setLayout(vbox)

    def fill(self, marker, form, polygon=None, xP=None, yP=None, xR=None, yR=None):
        # FIXME: marker is iterated to existent state. needs to be recounted AFTER table creation so all markers can be chosen for all polys
        # HACK: maybe with redrawTable, bc the marker counter wont change within that process
        twItem = QTreeWidgetItem()
        twItem.setText(0, form)
        twItem.setFont(0, self.bold)
        self.marker = marker

        if form == 'World' or form == 'Rectangle' or form == 'Line':
            # twItem.setBackgroundColor(0, QColor(0, 255, 0))
            # start x
            xStart = QTreeWidgetItem()
            xStart.setFlags(xStart.flags() | Qt.ItemIsEditable)
            xStart.setText(0, "Start x:")
            xStart.setText(1, str(xP))
            twItem.addChild(xStart)
            # start y
            yStart = QTreeWidgetItem()
            yStart.setFlags(yStart.flags() | Qt.ItemIsEditable)
            yStart.setText(0, "Start y:")
            yStart.setText(1, str(yP))
            twItem.addChild(yStart)
            # end x
            xEnd = QTreeWidgetItem()
            xEnd.setFlags(xEnd.flags() | Qt.ItemIsEditable)
            xEnd.setText(0, "End x:")
            xEnd.setText(1, str(xR))
            twItem.addChild(xEnd)
            # end y
            yEnd = QTreeWidgetItem()
            yEnd.setFlags(yEnd.flags() | Qt.ItemIsEditable)
            yEnd.setText(0, "End y:")
            yEnd.setText(1, str(yR))
            twItem.addChild(yEnd)

        if form == 'Circle':
            # insert center
            center = QTreeWidgetItem()
            center.setFlags(center.flags() | Qt.ItemIsEditable)
            center.setText(0, "Center:")
            center.setText(1, (str(round(xP, 2)) + ", " + str(round(yP, 2))))
            twItem.addChild(center)
            # radius
            spx_radius = QDoubleSpinBox()
            spx_radius.setSingleStep(0.01)
            spx_radius.setValue(xR)
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

        if form == 'Line':
            # insert segments
            spx_segments = QSpinBox()
            spx_segments.setValue(1)
            spx_segments.setMinimum(1)
            segments = QTreeWidgetItem()
            segments.setText(0, "Segments:")
            twItem.addChild(segments)
            self.tw_polys.setItemWidget(segments, 1, spx_segments)

        if form != 'Line':
            # insert marker
            # for k in range(self.marker):
            a = QComboBox()
            [a.addItem(str(m + 1)) for m in range(marker)]
            a.setCurrentIndex(marker - 1)
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

        if form != 'World':
            # insert boundary marker
            spx_boundaryMarker = QSpinBox()
            spx_boundaryMarker.setValue(1)
            spx_boundaryMarker.setMinimum(1)
            boundaryMarker = QTreeWidgetItem()
            boundaryMarker.setText(0, "BoundaryMarker:")
            twItem.addChild(boundaryMarker)
            self.tw_polys.setItemWidget(boundaryMarker, 1, spx_boundaryMarker)

        if form == 'Rectangle' or form == 'Circle' or form == 'Line' or form == 'Polygon':
            # insert left direction
            cbx_isLeft = QComboBox()
            cbx_isLeft.addItem('False')
            cbx_isLeft.addItem('True')
            isLeft = QTreeWidgetItem()
            isLeft.setText(0, "isLeft:")
            twItem.addChild(isLeft)
            self.tw_polys.setItemWidget(isLeft, 1, cbx_isLeft)

        if form == 'Rectangle' or form == 'Circle' or form == 'Polygon':
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

        if form == 'Polygon':
            verts = QTreeWidgetItem()
            verts.setText(0, "Verts:")
            verts.setText(1, ', '.join(str(i) for i in polygon))
            verts.setFlags(verts.flags() | Qt.ItemIsEditable)
            twItem.addChild(verts)

        if form != 'Line':
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

    def redrawTable(self, newMarkers):
        # BUG: line misses first half after redraw
        # BUG: after redraw marker might be lost: control mechanism and/or possible manual adding of a marker
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
                if len(newMarkers) != 0:
                    markerPos = newMarkers[i][0]
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
        # self.drawPoly(fillTable=False)

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


if __name__ == '__main__':

    import sys

    app = QApplication(sys.argv)
    ex = PropertyTable()
    ex.show()
    sys.exit(app.exec_())
