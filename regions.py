#!/usr/bin/env python
# encoding: UTF-8

""" model builder components """
from PyQt4 import QtGui
from pygimli.mplviewer import drawMeshBoundaries, drawMesh, drawPLC, drawModel
from pygimli.meshtools import polytools as plc
from pygimli.meshtools import createMesh, writePLC
import pygimli as pg
from shapely.geometry import Polygon, Point
from matplotlib import patches
from mpl import DraggablePoint
from collections import defaultdict, Counter


class RegionQuickCheck(QtGui.QWidget):

    def __init__(self, parent=None):
        super(RegionQuickCheck, self).__init__(parent)
        self.parent = parent
        self.builder = parent.builder
        self.figure = parent.plotWidget
        self.newMarkerPositions = None

        self.setupUI()

        """ connect signals """
        self.btn_init.clicked.connect(self.retrievePolygon)
        self.btn_refresh.clicked.connect(self.regionShow)
        self.btn_check.toggled.connect(self.regionCheckMarkerPosition)
        self.btn_export.clicked.connect(self.regionExportPoly)
        # self.btn_init.clicked.connect(self.fillTableFromFigure)

    def setupUI(self):
        self.btn_init = QtGui.QPushButton("init")

        self.btn_refresh = QtGui.QPushButton()
        self.btn_refresh.setIcon(QtGui.QIcon("material/ic_refresh_black_24px.svg"))
        self.btn_refresh.setEnabled(False)
        self.btn_refresh.setSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Minimum)

        self.btn_check = QtGui.QPushButton("check")
        self.btn_check.setCheckable(True)
        self.btn_check.setEnabled(False)

        self.btn_export = QtGui.QPushButton()
        self.btn_export.setIcon(QtGui.QIcon("material/ic_save_black_24px.svg"))
        self.btn_export.setToolTip("save as *.poly")
        self.btn_export.setEnabled(False)
        self.btn_export.setSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Minimum)

        self.rbtn_plotRegions = QtGui.QRadioButton("plot regions")
        self.rbtn_plotRegions.setChecked(True)
        self.rbtn_plotRegions.setEnabled(False)
        self.rbtn_plotAttributes = QtGui.QRadioButton("plot attributes")
        self.rbtn_plotAttributes.setEnabled(False)

        self.table_regions = QtGui.QTableWidget(self)
        self.table_regions.setColumnCount(3)
        self.table_regions.setHorizontalHeaderLabels(("Marker", "Hole", "Attribute"))

        hbox_rbtns = QtGui.QHBoxLayout()
        hbox_rbtns.addWidget(self.rbtn_plotRegions)
        hbox_rbtns.addWidget(self.rbtn_plotAttributes)
        hbox_rbtns.addWidget(self.btn_refresh)
        hbox_btns = QtGui.QHBoxLayout()
        hbox_btns.addWidget(self.btn_check)
        hbox_btns.addStretch(1)
        hbox_btns.addWidget(self.btn_export)

        vbox = QtGui.QVBoxLayout()
        vbox.addWidget(self.btn_init)
        vbox.addLayout(hbox_rbtns)
        vbox.addWidget(self.table_regions)
        vbox.addLayout(hbox_btns)

        self.setLayout(vbox)

    def retrievePolygon(self):

        self.polys = self.builder.getPoly()
        # if empty there must be a 'figure'
        if len(self.polys) == 0:
            self.polyTuples = self.parent.polygons_dens
            self.polys = []
            # marker positions for possible repositioning
            self.markers = []
            self.fillTableFromFigure()
            # print(self.polys)
            # self.polys = [plc.createPolygon(p, isClosed=True) for p in self.polys]
            for i, p in enumerate(self.polyTuples):
                self.polys.append(plc.createPolygon(p, isClosed=True))

                # if marker psotions have been moved manually, take these
                if self.newMarkerPositions:
                    markerPosition = tuple(self.newMarkerPositions[i])
                else:
                    markerPosition = self.regionCenter(p)

                if self.table_regions.cellWidget(i+1, 1).currentText() == 'False':  # not hole
                    pg.Mesh.addRegionMarker(self.polys[i], markerPosition, marker=int(self.table_regions.cellWidget(i+1, 0).currentText()))
                else:  # hole
                    pg.Mesh.addHoleMarker(self.polys[i], markerPosition)

                self.markers.append(markerPosition)

            self.poly = plc.mergePLC(self.polys)

        self.parent.statusBar.showMessage("got {} polygons".format(len(self.polys)))

        # print(len(self.polys))
        self.btn_refresh.setEnabled(True)
        self.btn_check.setEnabled(True)
        self.btn_export.setEnabled(True)
        self.rbtn_plotRegions.setEnabled(True)
        self.rbtn_plotAttributes.setEnabled(True)

        self.regionShow()

    def regionShow(self):
        """
            plot regions (or attribute table)
        """
        self.figure.axis.cla()
        if self.rbtn_plotRegions.isChecked() is True:
            # drawPLC(self.plotWidget.axis, self.poly)
            drawMesh(self.figure.axis, self.poly, fitView=False)

        elif self.rbtn_plotAttributes.isChecked() is True:
            self.regionGetAttributes()
            mesh_tmp = createMesh(self.poly)
            try:
                attr_map = pg.solver.parseMapToCellArray(self.attr_map, mesh_tmp)
                drawMeshBoundaries(self.figure.axis, mesh_tmp, hideMesh=True)
                drawModel(self.figure.axis, mesh_tmp, tri=True, alpha=0.65, data=attr_map)

            except (AttributeError, IndexError):
                # self.statusBar.showMessage("unsufficient data in attribute table")
                self.parent.statusBar.showMessage("ERROR: wrong or missing values in attribute column", 3000)
                pass

        self.figure.axis.set_ylim(self.figure.axis.get_ylim()[::-1])
        self.figure.canvas.draw()

    def regionCenter(self, poly):
        """
            find centroid as marker position
            # FIXME ...potentially dangerous method... since the center could be overlayed by another polygon
        """
        ref_polygon = Polygon(poly)
        # get the x and y coordinate of the centroid
        pnts = ref_polygon.centroid.wkt.split(" ")[1:]

        return (float(pnts[0][1:]), float(pnts[1][:-1]))

    def regionCheckMarkerPosition(self):
        """
            check if every marker position is in its respective polygon. the distance between
            marker position and polygon border should be shortest if its the own polygon!
        """
        warning = False
        if self.btn_check.isChecked() is True:
            for i, mark in enumerate(self.markers):
                point = Point(mark)
                for k, poly in enumerate(self.polyTuples):
                    dist = point.distance(Polygon(poly))
                    # print(i+2, k+2, dist)
                    if i != k and dist == 0.:
                        warning = True

            if warning:
                self.parent.statusBar.showMessage("WARNING: there seems to be some overlay")
                self.regionMoveMarkers()
            else:
                self.parent.statusBar.showMessage("regions and markers seem to be fine", 3000)
        else:
            self.newMarkerPositions = []
            for p in self.dps:
                val = p.returnValue()
                # print(val.values())
                self.newMarkerPositions.append(list(val.values())[0])
                # TODO: marker positions wont vanish. why!
                p.disconnect()
            self.parent.statusBar.showMessage("updating...")

            self.retrievePolygon()
            # self.regionRefresh(new_markers=new_markers)

    def regionMoveMarkers(self):
        """
            plots dots as marker positions which can be moved
        """
        self.dps = []

        for i, m in enumerate(self.markers):
            mark = patches.Circle(m, radius=8, fc="r")
            self.figure.axis.add_patch(mark)
            dp = DraggablePoint(mark, i+2, m)
            dp.connect()
            self.dps.append(dp)
        self.figure.canvas.draw()

    def regionGetAttributes(self):
        """
            before going on with plotting the attributes etc. check for nonsense and multiple value specifications for the one marker
        """
        key_attr = False
        self.attr_map = []
        tmp_mark = []
        tmp_attr = []
        tmp_idx = []
        for i in range(self.rows):
            try:
                # get values from attribute column
                mark = int(self.table_regions.cellWidget(i, 0).currentText())
                attr = float(self.table_regions.item(i, 2).text())
                if mark not in tmp_mark:
                    tmp_mark.append(mark)
                else:
                    tmp_idx.append(i)
                    tmp_attr.append(attr)
                self.attr_map.append([mark, attr])
                if self.table_regions.cellWidget(i, 1).currentText() == 'False':
                    # fill green if successfull
                    self.table_regions.item(i, 2).setBackground(QtGui.QColor(2, 164, 6, 0.5 * 255))
                else:
                    # or white if its hole and it doesnt matter
                    self.table_regions.item(i, 2).setBackground(QtGui.QColor(255, 255, 255, 0.5 * 255))
            except ValueError:
                if self.table_regions.cellWidget(i, 1).currentText() == 'False':
                    # fill red if error
                    self.table_regions.item(i, 2).setBackground(QtGui.QColor(172, 7, 0, 0.5 * 255))
                    key_attr = True
                else:
                    # or white if its hole and it doesnt matter
                    self.table_regions.item(i, 2).setBackground(QtGui.QColor(255, 255, 255, 0.5 * 255))
        # check if duplicates in attribute column exists. len 0 means different values for same
        # marker
        if len([k for k, v in Counter(tmp_attr).items() if v>1]) == 0:
            for idx in tmp_idx:
                self.table_regions.item(idx, 2).setBackground(QtGui.QColor(255, 179, 0, 0.5 * 255))
                key_attr = True

        if key_attr:
            self.parent.statusBar.showMessage("WARNING: duplicate or wrong data in attribute table")

    def fillTableFromFigure(self):
        self.rows = len(self.polyTuples) + 1
        self.table_regions.setRowCount(self.rows)  # +1 for world around model

        for i in range(self.rows):  # row
            # column 1 - region marker no.
            cbx_marker = QtGui.QComboBox(self.table_regions)
            [cbx_marker.addItem(str(m+1)) for m in range(self.rows)]
            cbx_marker.setCurrentIndex(i)
            self.table_regions.setCellWidget(i, 0, cbx_marker)

            # column 2 - isHoleMarker
            cbx_isHole = QtGui.QComboBox(self.table_regions)
            cbx_isHole.addItem("False")
            cbx_isHole.addItem("True")
            self.table_regions.setCellWidget(i, 1, cbx_isHole)

            # column 3 - attributes
            self.table_regions.setItem(i, 2, QtGui.QTableWidgetItem("None"))

        self.table_regions.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        self.table_regions.resizeColumnsToContents()

    def regionExportPoly(self):
        """
            export the poly figure
        """
        export_poly = QtGui.QFileDialog.getSaveFileName(
            self, caption="Save Poly Figure")

        # if export_poly:
        if export_poly.endswith(".poly"):
            writePLC(self.poly, export_poly)
        else:
            writePLC(self.poly, export_poly + ".poly")


if __name__ == '__main__':

    import sys

    app = QtGui.QApplication(sys.argv)
    regionWin = RegionQuickCheck()
    regionWin.show()
    sys.exit(regionWin.exec_())
