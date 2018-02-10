#!/usr/bin/env python
# encoding: UTF-8


try:
    from PyQt5.QtWidgets import (QWidget, QTreeWidget, QTreeWidgetItem,
        QPushButton, QRadioButton, QSizePolicy, QHBoxLayout, QVBoxLayout,
        QComboBox, QSpinBox, QDoubleSpinBox, QAction, QMenu)
    from PyQt5.QtCore import Qt, QSize
    from PyQt5.QtGui import QIcon, QFont, QColor

except ImportError:
    from PyQt4.QtGui import (QWidget, QTreeWidget, QTreeWidgetItem,
        QPushButton, QRadioButton, QSizePolicy, QHBoxLayout, QVBoxLayout,
        QComboBox, QSpinBox, QDoubleSpinBox, QIcon, QFont, QColor, QAction, QMenu)
    from PyQt4.QtCore import Qt, QSize

import numpy as np
import pygimli as pg
from pygimli.meshtools import polytools as plc
import matplotlib.pyplot as plt


class InfoTree(QWidget):
    """
    This class resembles the information tree on the left side. It contains the
    parameters of every drawn polygon and holds some more widgets to edit and
    redraw these.
    """

    def __init__(self, parent=None):
        """
        Initialize the widget itself and call super class to get the functionality of QWidget.

        Parameters
        ----------
        parent: <__main__.GIMod object>
            Every widget that needs to be accessed is called in :class:`~GIMod`
        """
        super(InfoTree, self).__init__(parent)
        self.parent = parent
        self.setupWidget()

        # connect the rightclick to contextmenu
        self.tw_polys.customContextMenuRequested.connect(self.contextmenu.rightClicked)

    def setupWidget(self):
        """
        Set up the QTreeWidget. Every Polygon holds some specs that are
        editable through QSpinBox and other widgets
        """
        # set up bold font for the list entry 'headers'
        self.bold = QFont()
        self.bold.setBold(True)

        # instanciate the widget that holds all information about each polygon
        self.tw_polys = QTreeWidget()
        self.tw_polys.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tw_polys.setAlternatingRowColors(True)
        self.tw_polys.setUniformRowHeights(True)
        self.tw_polys.setContentsMargins(0, 0, 0, 0)
        self.tw_polys.setHeaderLabels(("PolyTool", "Parameters"))
        # TODO: stretch that darn first column to content!
        # self.tw_polys.header().hide()
        # self.tw_polys.showDropIndicator()
        # self.tw_polys.setRootIsDecorated(False)

        # button to undo the last created polygon
        self.btn_undo = QPushButton()
        self.btn_undo.setIconSize(QSize(18, 18))
        self.btn_undo.setFixedSize(28, 28)
        self.btn_undo.setToolTip("undo last poly")
        self.btn_undo.setIcon(QIcon('icons/ic_undo_black_18px.svg'))
        self.btn_undo.setEnabled(False)

        # button to redo the last undone polygon
        self.btn_redo = QPushButton()
        self.btn_redo.setIconSize(QSize(18, 18))
        self.btn_redo.setFixedSize(28, 28)
        self.btn_redo.setToolTip("redo last poly")
        self.btn_redo.setIcon(QIcon('icons/ic_redo_black_18px.svg'))
        self.btn_redo.setEnabled(False)

        # buttons to decide if just the region is plotted or the attributes
        # passed from tree
        self.rbtn_plotRegions = QRadioButton('regions')
        self.rbtn_plotRegions.setChecked(True)
        self.rbtn_plotAttributes = QRadioButton('attributes')

        # button to draw all polygons defined/altered in the tree widget
        self.btn_redraw = QPushButton()
        self.btn_redraw.setIconSize(QSize(18, 18))
        self.btn_redraw.setFixedSize(28, 28)
        self.btn_redraw.setToolTip(
            "redraw whole table after changes were made")
        self.btn_redraw.setIcon(QIcon('icons/ic_refresh_black_24px.svg'))

        # set up the layout for the tree tools
        hbox = QHBoxLayout()
        hbox.addWidget(self.btn_undo)
        hbox.addWidget(self.btn_redo)
        hbox.addWidget(self.rbtn_plotRegions)
        hbox.addWidget(self.rbtn_plotAttributes)
        hbox.addStretch(1)
        hbox.addWidget(self.btn_redraw)
        hbox.setContentsMargins(0, 0, 0, 0)

        # establish the layout
        vbox = QVBoxLayout()
        vbox.addWidget(self.tw_polys)
        vbox.addLayout(hbox)
        vbox.setContentsMargins(0, 0, 0, 0)
        self.setLayout(vbox)

        self.contextmenu = ContextMenu(self)

    def fillTable(self, form, x_p=None, y_p=None, x_r=None, y_r=None, polygon=None, parent_marker=None):
        """
        Fill the tree widget on the left with information accessible in several
        cell widgets.

        Parameters
        ----------
        form: str
            Word describing the polygon that was just drawn.
        x_p: float
            The x-value in a cartesian coordinate system where the polygon was started.
        y_p: float
            The y-value in a cartesian coordinate system where the polygon was started.
        x_r: float
            The x-value in a cartesian coordinate system where the polygon was finished.
        y_r: float
            The y-value in a cartesian coordinate system where the polygon was finished.
        polygon: list
            The vertices/nodes of the designed polygon.
        parent_marker: int
            The integer identifier to mark a region in the polygon figure.

        Todo
        ----
        + add toolTips for each widget!
        """
        # create an entry item
        tw_item = QTreeWidgetItem()
        # tw_item.setContextMenuPolicy(Qt.CustomContextMenu)
        tw_item.setText(0, form)
        tw_item.setFont(0, self.bold)

        if form == 'World' or form == 'Rectangle' or form == 'Line':
            # tw_item.setBackgroundColor(0, QColor(0, 255, 0))
            # start x
            x_start = QTreeWidgetItem()
            x_start.setToolTip(
                1, "The x-position where the figure was started")
            x_start.setFlags(x_start.flags() | Qt.ItemIsEditable)
            x_start.setText(0, "Start x:")
            x_start.setText(1, str(x_p))
            tw_item.addChild(x_start)
            # start y
            y_start = QTreeWidgetItem()
            y_start.setToolTip(
                1, "The y-position where the figure was started")
            y_start.setFlags(y_start.flags() | Qt.ItemIsEditable)
            y_start.setText(0, "Start y:")
            y_start.setText(1, str(y_p))
            tw_item.addChild(y_start)
            # end x
            x_end = QTreeWidgetItem()
            x_end.setToolTip(1, "The x-position where the figure was finished")
            x_end.setFlags(x_end.flags() | Qt.ItemIsEditable)
            x_end.setText(0, "End x:")
            x_end.setText(1, str(x_r))
            tw_item.addChild(x_end)
            # end y
            y_end = QTreeWidgetItem()
            y_end.setToolTip(1, "The y-position where the figure was finished")
            y_end.setFlags(y_end.flags() | Qt.ItemIsEditable)
            y_end.setText(0, "End y:")
            y_end.setText(1, str(y_r))
            tw_item.addChild(y_end)

        if form == 'Circle':
            # insert center
            center = QTreeWidgetItem()
            center.setToolTip(1, "Marks the center of the created cirlce")
            center.setFlags(center.flags() | Qt.ItemIsEditable)
            center.setText(0, "Center:")
            center.setText(1, (str(round(x_p, 2)) + ", " + str(round(y_p, 2))))
            tw_item.addChild(center)
            # radius
            spx_radius = QDoubleSpinBox()
            spx_radius.setToolTip("The Radius of the circle")
            spx_radius.setSingleStep(0.01)
            spx_radius.setValue(x_r)
            radius = QTreeWidgetItem()
            radius.setText(0, "Radius:")
            tw_item.addChild(radius)
            self.tw_polys.setItemWidget(radius, 1, spx_radius)
            # insert segments
            spx_segments = QSpinBox()
            spx_segments.setToolTip(
                "The number of edges to resemble the circle")
            spx_segments.setValue(12)
            spx_segments.setMinimum(3)
            spx_segments.setMaximum(int(1e10))
            segments = QTreeWidgetItem()
            segments.setText(0, "Segments:")
            tw_item.addChild(segments)
            self.tw_polys.setItemWidget(segments, 1, spx_segments)
            # insert start
            spx_start = QDoubleSpinBox()
            spx_start.setToolTip("The angle where the circle should be start")
            spx_start.setValue(0.00)
            spx_start.setMinimum(0.00)
            spx_start.setSingleStep(0.01)
            spx_start.setMaximum(2 * np.pi)
            start = QTreeWidgetItem()
            start.setText(0, "Start angle:")
            tw_item.addChild(start)
            self.tw_polys.setItemWidget(start, 1, spx_start)
            # insert end
            spx_end = QDoubleSpinBox()
            spx_end.setToolTip("The angle where the circle should stop")
            spx_end.setValue(2 * np.pi)
            spx_end.setMinimum(0.00)
            spx_end.setSingleStep(0.01)
            spx_end.setMaximum(2 * np.pi)
            end = QTreeWidgetItem()
            end.setText(0, "End angle:")
            tw_item.addChild(end)
            self.tw_polys.setItemWidget(end, 1, spx_end)

        if form == 'Line':
            # insert segments
            spx_segments = QSpinBox()
            spx_segments.setToolTip(
                "The number of segments the line should consist of")
            spx_segments.setValue(1)
            spx_segments.setMinimum(1)
            segments = QTreeWidgetItem()
            segments.setText(0, "Segments:")
            tw_item.addChild(segments)
            self.tw_polys.setItemWidget(segments, 1, spx_segments)

        if form != 'Line':
            # insert marker
            a = QComboBox()
            [a.addItem(str(m))
             for m in range(self.parent.builder.marker)]
            # [a.addItem(str(m + 1))
            #  for m in range(-1, self.parent.builder.marker)]
            a.setToolTip("Choose a marker the polygon should belong to")
            a.setCurrentIndex(parent_marker)
            marker = QTreeWidgetItem()
            marker.setText(0, "Marker:")
            tw_item.addChild(marker)
            self.tw_polys.setItemWidget(marker, 1, a)
            # insert area
            spx_area = QDoubleSpinBox()
            spx_area.setToolTip(
                "The maximum area the later meshed region should have")
            spx_area.setSingleStep(0.01)
            spx_area.setValue(0.00)
            spx_area.setMinimum(0.00)
            area = QTreeWidgetItem()
            area.setText(0, "Area:")
            tw_item.addChild(area)
            self.tw_polys.setItemWidget(area, 1, spx_area)

        if form != 'World':
            # insert boundary marker
            spx_boundaryMarker = QSpinBox()
            spx_boundaryMarker.setToolTip(
                "set an identifier to a border to pass parameters later on")
            spx_boundaryMarker.setValue(1)
            spx_boundaryMarker.setMinimum(1)
            boundaryMarker = QTreeWidgetItem()
            boundaryMarker.setText(0, "BoundaryMarker:")
            tw_item.addChild(boundaryMarker)
            self.tw_polys.setItemWidget(boundaryMarker, 1, spx_boundaryMarker)

        if form == 'Rectangle' or form == 'Circle' or form == 'Line' or form == 'Polygon':
            # insert left direction
            cbx_is_left = QComboBox()
            cbx_is_left.setToolTip("...")
            cbx_is_left.addItem('False')
            cbx_is_left.addItem('True')
            if form == 'Line':
                cbx_is_left.setCurrentIndex(1)
            is_left = QTreeWidgetItem()
            is_left.setText(0, "is left:")
            tw_item.addChild(is_left)
            self.tw_polys.setItemWidget(is_left, 1, cbx_is_left)

        if form == 'Rectangle' or form == 'Circle' or form == 'Polygon':
            # insert is hole
            cbx_is_hole = QComboBox()
            cbx_is_hole.setToolTip(
                "Set True if the region should mark a hole region")
            cbx_is_hole.addItem('False')
            cbx_is_hole.addItem('True')
            is_hole = QTreeWidgetItem()
            is_hole.setText(0, "is hole:")
            tw_item.addChild(is_hole)
            self.tw_polys.setItemWidget(is_hole, 1, cbx_is_hole)
            # insert is closed
            cbx_is_closed = QComboBox()
            cbx_is_closed.setToolTip("Choose of polygon is closed or open")
            cbx_is_closed.addItem('False')
            cbx_is_closed.addItem('True')
            cbx_is_closed.setCurrentIndex(1)
            is_closed = QTreeWidgetItem()
            is_closed.setText(0, "is closed:")
            tw_item.addChild(is_closed)
            self.tw_polys.setItemWidget(is_closed, 1, cbx_is_closed)

        if form == 'Polygon':
            verts = QTreeWidgetItem()
            verts.setToolTip(1, "All the vertices that resemble the polygon")
            verts.setText(0, "Verts:")
            verts.setText(1, ', '.join(str(i) for i in polygon))
            verts.setFlags(verts.flags() | Qt.ItemIsEditable)
            tw_item.addChild(verts)

        if form != 'Line':
            attributes = QTreeWidgetItem()
            attributes.setToolTip(1, "Set a physical parameter to the Polygon")
            attributes.setText(0, "Attributes:")
            attributes.setFlags(attributes.flags() | Qt.ItemIsEditable)
            tw_item.addChild(attributes)

        self.tw_polys.addTopLevelItem(tw_item)
        tw_item.setExpanded(True)  # needs to happen after adding to tree
        if not self.tw_polys.currentItem():
            self.tw_polys.setCurrentItem(self.tw_polys.topLevelItem(0))
            self.tw_polys.setEnabled(True)
        self.tw_polys.resizeColumnToContents(0)
        self.colorizeTreeItemHeaders()

    def colorizeTreeItemHeaders(self):
        """
        Colorize the line that describes which polygon is described with the
        children listed below. Needs to happen afterwards by iterating through
        the content since the color range changes with the amount of ppolygons
        drawn.
        """
        items = self.tw_polys.topLevelItemCount()
        # 'None' to get the default colormap
        cmap = plt.cm.get_cmap(None, items)
        colors = []
        for i in range(cmap.N):
            # will return rgba
            rgba = cmap(i)[:3]
            # convert to int (0..255) values for qt
            colors.append([int(k * 255) for k in rgba])

        for i in range(items):
            # use the splatter (*) operator to extract from list directly
            self.tw_polys.topLevelItem(i).setData(
                0, Qt.BackgroundRole, QColor(*colors[i], 255 / 2))
            self.tw_polys.topLevelItem(i).setData(
                1, Qt.BackgroundRole, QColor(*colors[i], 255 / 2))
            # 255/2 to receive alpha=0.5 as it is hard coded is gimli's meshview
            # TODO: the dropdown indicator is not colored!!

    def redrawTable(self):
        """
        Collect all the info from the tree widget and redraw all content.

        Important
        ---------
        + there is a bug regarding the drawn line... its missing after the redraw
        """
        # BUG: line missing (first half) after redraw
        self.parent.setCursor(Qt.WaitCursor)
        self.parent.statusbar.showMessage("updating...")
        polyMeta = []
        for i in range(self.tw_polys.topLevelItemCount()):
            meta = []
            # get polygon type
            meta.append(self.tw_polys.topLevelItem(i).text(0))
            for k in range(self.tw_polys.topLevelItem(i).childCount()):
                try:
                    # text from ComboBox
                    meta.append(self.tw_polys.itemWidget(
                        self.tw_polys.topLevelItem(i).child(k), 1).currentIndex())
                except AttributeError:
                    try:
                        # value from DoubleSpinBox
                        meta.append(self.tw_polys.itemWidget(
                            self.tw_polys.topLevelItem(i).child(k), 1).value())
                    except AttributeError:
                        # normal text cell
                        meta.append(self.tw_polys.topLevelItem(
                            i).child(k).text(1))
            polyMeta.append(meta)

        # the lists are being called in builders zipUpMarkerAndAttributes to
        # establish a map to color the mesh
        self.polyAttributes = []
        self.polyMarkers = []
        polys = []
        for i, p in enumerate(polyMeta):
            if p[0] == 'World':
                polys.append(plc.createWorld(
                    start=[float(p[1]), float(p[2])],
                    end=[float(p[3]), float(p[4])],
                    marker=int(p[5]),
                    area=float(p[6])
                ))
                self.polyAttributes.append(p[7])
                self.polyMarkers.append(int(p[5]))

            elif p[0] == 'Rectangle':
                polys.append(plc.createRectangle(
                    start=[float(p[1]), float(p[2])],
                    end=[float(p[3]), float(p[4])],
                    marker=int(p[5]),
                    area=float(p[6]),
                    boundaryMarker=int(p[7]),
                    isHole=int(p[9]),
                    isClosed=int(p[10])
                ))  # leftDirection=int(p[8])
                self.polyAttributes.append(p[11])
                self.polyMarkers.append(int(p[5]))

            elif p[0] == 'Circle':
                polys.append(plc.createCircle(
                    pos=tuple(np.asarray(p[1].split(', '),
                    dtype=float)), radius=float(p[2]),
                    segments=int(p[3]),
                    start=float(p[4]),
                    end=float(p[5]),
                    marker=int(p[6]),
                    area=float(p[7]),
                    boundaryMarker=int(p[8]),
                    leftDirection=int(p[9]),
                    isHole=int(p[10]),
                    isClosed=int(p[11])
                ))
                self.polyAttributes.append(p[12])
                self.polyMarkers.append(int(p[6]))

            elif p[0] == 'Line':
                polys.append(plc.createLine(
                    start=[float(p[1]), float(p[2])],
                    end=[float(p[3]), float(p[4])],
                    segments=int(p[5]),
                    boundaryMarker=int(p[6]),
                    leftDirection=int(p[7])
                ))
            elif p[0] == 'Polygon':
                # meh..
                vertStr = p[7].replace('[', '').replace(
                    ']', '').replace(',', '').split(' ')
                verts = [[float(vertStr[i]), float(vertStr[i + 1])]
                         for i in range(0, len(vertStr), 2)]
                poly = plc.createPolygon(
                    verts=verts,
                    area=float(p[2]),
                    boundaryMarker=int(p[3]),
                    isClosed=int(p[6]
                ))  # leftDirection=int(p[4])

                if len(self.parent.builder.new_markers) != 0:
                    marker_pos = self.parent.builder.new_markers[i][0]
                else:
                    # take the position from the existing polys
                    marker_pos = list(self.parent.builder.polys[i].regionMarker()[0])[:2]

                if int(p[5]) == 1:
                    pg.Mesh.addHoleMarker(poly, marker_pos)
                else:
                    pg.Mesh.addRegionMarker(poly, marker_pos, marker=int(p[1]))
                polys.append(poly)
                self.polyAttributes.append(p[8])
                self.polyMarkers.append(int(p[1]))

        self.parent.statusbar.clearMessage()
        self.parent.builder.drawPoly(polys=polys)
        self.parent.setCursor(Qt.ArrowCursor)


class ContextMenu(QMenu):
    """
    Hold the functionality for right clicking an item in the treewidget.
    (or later rightclicking a polygon)
    """

    def __init__(self, parent=None):
        """."""
        super(ContextMenu, self).__init__(parent)
        self.parent = parent  # the infotree
        self.setupMenu()

        # connec the signals of the right click menu
        self.acn_remove.triggered.connect(self.parent.parent.builder.undoPoly)

    def setupMenu(self):
        """Organize the methods in the menu."""
        # Popup Menu is not visible, but we add actions from above
        self.acn_remove = QAction("Remove this Polygon from Mesh creation",
            None, checkable=False)

        self.popMenu = QMenu(self)
        self.popMenu.addAction(self.acn_remove)

    def rightClicked(self, point):
        clicked_item = self.parent.tw_polys.itemAt(point)
        # only show the item if its the parent!
        if clicked_item.childCount() != 0:
            self.to_del = self.parent.tw_polys.indexOfTopLevelItem(clicked_item)
            self.popMenu.exec_(self.parent.tw_polys.mapToGlobal(point))
            self.to_del = None


if __name__ == '__main__':
    pass
