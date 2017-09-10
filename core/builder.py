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
from pygimli.mplviewer import drawMesh, drawMeshBoundaries, drawModel, drawPLC
from pygimli.meshtools import polytools as plc
from pygimli.meshtools import createMesh, writePLC

# TODO: skizze laden und verändern können im model builder
# TODO: bild als hintergrund einstellen zum nachmalen


class Builder():
    """Contains the main functionality of GIMod!"""

    def __init__(self, parent=None):
        """
        Initialize all import widgets from parent and lists needed in the process of model creation.

        Parameters
        ----------
        parent: <__main__.GIMod object>
            Every widget that needs to be accessed is called in :class:`~GIMod`
        """
        self.parent = parent
        self.figure = parent.plotWidget
        self.toolbar = parent.toolBar
        self.statusbar = parent.statusbar
        # initialize the marker at -1 to get the starting polygon (WORLD *fingers crossed*) with a 0 marker
        self.marker = -1
        # new_markers holds the marker positions that were manually corrected with self.markersMove
        self.new_markers = []
        # store all created polygon objects
        self.polys = []
        # store all parameters of a drawn raw polygon
        self.hand_drawn_polys = []
        # here the stuff is put after undoing it... the list where everything is hidden
        self.undone = []
        self.undone_hand_drawn = []
        # dummy flags for action in :class:`~gui.PolyToolBar` to trigger the right decision
        self.markersClicked = True
        self.gridClicked = True
        self.magnetizeClicked = True
        self.mPolyClicked = True
        self.poly = None
        # introduce polygon form, the edges and (for hand drawn whtaever
        # shaped) polygon as None. Necessary step to prevent the passing of non
        # existent variables when drawing
        self.form = None
        self.x_p = None
        self.y_p = None
        self.x_r = None
        self.y_r = None
        self.polygon = None

    def formPolyWorld(self):
        """
        Connect the mouse event to the canvas for accessing plc.createWorld.
        """
        try:
            self.span.disconnect()
        except AttributeError:
            pass
        self.span = SpanWorld(self)
        self.span.connect()

    def formPolyRectangle(self):
        """
        Connect the mouse event to the canvas for accessing plc.createRectangle.
        """
        try:
            self.span.disconnect()
        except AttributeError:
            pass
        self.span = SpanRectangle(self)
        self.span.connect()

    def formPolyCircle(self):
        """
        Connect the mouse event to the canvas for accessing plc.createCircle.
        """
        try:
            self.span.disconnect()
        except AttributeError:
            pass
        self.span = SpanCircle(self)
        self.span.connect()

    def formPolyLine(self):
        """
        Connect the mouse event to the canvas for accessing plc.createLine.
        """
        try:
            self.span.disconnect()
        except AttributeError:
            pass
        self.span = SpanLine(self)
        self.span.connect()

    def formPolygon(self):
        """
        Connect the mouse event to the canvas for accessing plc.createPolygon.
        """
        try:
            self.span.disconnect()
        except AttributeError:
            pass
        self.span = SpanPoly(self)
        self.span.connect()

    def formPolygonFromFigure(self):
        """
        Create all polygons chosen from a figure.

        Todo
        ----
        + try a progress bar here!! :D
        """
        # clear the table on the side tobe sure
        self.parent.info_tree.tw_polys.clear()
        self.polys.clear()
        self.parent.setCursor(Qt.WaitCursor)

        # how many contours were found.. for showing progress purpose
        n_contours = len(self.parent.image_tools.contoursCutted)
        for i, contour in enumerate(self.parent.image_tools.contoursCutted):
            self.marker += 1
            # show progress in statusbar
            self.parent.statusbar.showMessage("processing found polygons {}/{}".format(i, n_contours))
            # construct poly
            self.constructPoly('Polygon', None, None, None, None, contour, self.marker)

        # draw created polygon
        self.drawPoly()
        # fill the info tree as bulk
        for i, contour in enumerate(self.parent.image_tools.contoursCutted):
            # show progress in statusbar
            self.parent.statusbar.showMessage("processing table entries {}/{}".format(i, n_contours))
            # fill the info tree as bulk
            self.parent.info_tree.fillTable(form='Polygon', polygon=contour, parent_marker=i)

        # turn on buttons to reset figure or delete last build polygon
        self.parent.info_tree.btn_undo.setEnabled(True)
        self.parent.toolBar.acn_reset_figure.setEnabled(True)
        # change message in statusbar to info about the polygon
        self.statusbar.showMessage(str(self.poly))
        self.parent.setCursor(Qt.ArrowCursor)

    def printCoordinates(self, x1, y1, x2, y2, form):
        """
        Create the Polygon for caller/form. This method gets called from :class:`mpl.SpanWorld`, :class:`mpl.SpanRectangle`, :class:`mpl.SpanCircle`, :class:`mpl.SpanLine`, :class:`mpl.SpanPoly`

        Parameters
        ----------
        x1: float
            The x-value in a cartesian coordinate system where the polygon was started.
        x2: float
            The x-value in a cartesian coordinate system where the polygon was finished.
        y1: float
            The y-value in a cartesian coordinate system where the polygon was started.
        y2: float
            The y-value in a cartesian coordinate system where the polygon was finished.
        form: str
            Word describing the polygon that was just drawn.
        """
        # add to the marker for each created polygon
        self.marker += 1
        try:
            self.constructPoly(form, x1, y1, x2, y2, None, self.marker)
        except TypeError:
            # REVIEW: what needs to happen that i land here again?! ...boiiii
            pass
        else:
            # turn on buttons to reset figure or delete last build polygon
            self.parent.info_tree.btn_undo.setEnabled(True)
            self.parent.toolBar.acn_reset_figure.setEnabled(True)
            # draw the created polygon
            self.drawPoly()
            # bulk fill the info tree
            self.fillInfoTree()

    def printPolygon(self, polygon):
        """
        Create the manually designed polygon.

        Parameters
        ----------
        polygon: list
            The vertices/nodes of the designed polygon.
        """
        # add to the marker for each created polygon
        self.marker += 1
        self.constructPoly('Polygon', None, None, None, None, polygon, self.marker)
        # turn on buttons to reset figure or delete last build polygon
        self.parent.info_tree.btn_undo.setEnabled(True)
        self.parent.toolBar.acn_reset_figure.setEnabled(True)
        # draw the created polygon
        self.drawPoly()
        # bulk fill the info tree
        self.fillInfoTree()

    def constructPoly(self, form, x_p, y_p, x_r, y_r, polygon, marker):
        """
        Actually built all the polygon that will be created during modeling process and store them self.polys.

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
        marker: int
            The integer identifier to mark a region in the polygon figure.
        """
        self.hand_drawn_polys.append((form, x_p, y_p, x_r, y_r, polygon, marker))
        if form == 'World':
            self.polys.append(plc.createWorld(start=[x_p, y_p], end=[x_r, y_r], marker=marker))

        elif form == 'Rectangle':
            self.polys.append(plc.createRectangle(start=[x_p, y_p], end=[x_r, y_r], marker=marker))

        elif form == 'Circle':
            self.polys.append(plc.createCircle(
            pos=(x_p, y_p), segments=12, radius=x_r, marker=marker))

        elif form == 'Line':
            self.polys.append(plc.createLine(start=[x_p, y_p], end=[x_r, y_r], segments=1))

        elif form == 'Polygon':
            self.polys.append(plc.createPolygon(polygon, marker=marker, isClosed=True))

    def drawPoly(self, polys=None):
        """
        Merge all created polygons and check for different flags to show the result.

        Parameters
        ----------
        polys: list [None]
            A polys attribute is only passed from :meth:`~gui.InfoTree.redrawTable` when the (maybe altered) content from the info tree is taken and redrawn

        Todo
        ----
        + get rid of the dummy flag for magnetizing the polygons nodes. use parent instead
        """
        # merge all (given) polygons
        if polys is None:
            self.poly = plc.mergePLC(self.polys)
        else:
            self.poly = plc.mergePLC(polys)
        self.figure.axis.cla()

        # check for the region plot option in treeview functions below the table
        if self.parent.info_tree.rbtn_plotRegions.isChecked() is True:
            drawMesh(self.figure.axis, self.poly, fitView=False)
            self.figure.canvas.draw()
        # if the attribute radiobutton below the tree widget is checked the
        # mesh view is slightly more complicated
        else:
            attrMap = self.zipUpMarkerAndAttributes()
            if attrMap:  # not empty
                # create temporary mesh
                temp_mesh = createMesh(self.poly)
                # parse the attributes to the mesh
                attrMap = pg.solver.parseMapToCellArray(attrMap, temp_mesh)
                drawMeshBoundaries(self.figure.axis, temp_mesh, hideMesh=True)
                drawModel(self.figure.axis, temp_mesh, tri=True, data=attrMap)
                self.figure.canvas.draw()
            else:  # empty
                QMessageBox.question(None, 'Whoops..', "Your regions don't have any attributes to plot!", QMessageBox.Ok)

        # TODO: get rid of the dummy flag
        if not self.mPolyClicked:
            x, y = self.getNodes()
            self.mp.plotMagnets(x, y)

        self.enabelingToolBarFunctions()

    def enabelingToolBarFunctions(self):
        """
        After drawing a polygon check whether the ``world`` needs to be
        disabled after creation or the other tools if no world exists.
        """
        # get the poly form as first position from every tuple
        existence = [poly[0] for poly in self.hand_drawn_polys]

        if 'World' in existence:
            self.toolbar.acn_world.setEnabled(False)
            self.toolbar.acn_rectangle.setEnabled(True)
            self.toolbar.acn_circle.setEnabled(True)
            self.toolbar.acn_line.setEnabled(True)
            self.toolbar.acn_polygon.setEnabled(True)
            self.toolbar.acn_markerCheck.setEnabled(True)
            self.toolbar.acn_magnetizePoly.setEnabled(True)
            self.toolbar.acn_world.setChecked(False)
            self.parent.mb_save_poly.setEnabled(True)
        else:
            self.toolbar.acn_world.setEnabled(True)
            self.toolbar.acn_rectangle.setEnabled(False)
            self.toolbar.acn_circle.setEnabled(False)
            self.toolbar.acn_line.setEnabled(False)
            self.toolbar.acn_polygon.setEnabled(False)
            self.toolbar.acn_markerCheck.setEnabled(False)
            self.toolbar.acn_magnetizePoly.setEnabled(False)
            self.parent.mb_save_poly.setEnabled(False)
            try:
                # disconnect the last used polytool
                self.span.disconnect()
            except AttributeError:
                # landing here if handling creating polygons from picture since
                # there isn't any self.span object from dragging a figure.
                # using the opportunity instead to activate the marker checking
                # function and the option to save as poly
                self.toolbar.acn_markerCheck.setEnabled(True)
                self.parent.mb_save_poly.setEnabled(True)

    def fillInfoTree(self):
        """
        Fill the tree view to the left that holds information about every
        polygon. Always fill from beginning so the marker gets set right with
        every new made polygon.
        """
        self.parent.info_tree.tw_polys.clear()
        for entry in self.hand_drawn_polys:
            # form, x_p, y_p, x_r, y_r, polygon, marker
            self.parent.info_tree.fillTable(entry[0], entry[1], entry[2], entry[3], entry[4], entry[5], entry[6])

    def resetFigure(self):
        """
        When clicked the user is asked if all achievements should really be discarded, since this method will clear the figure, the info tree and everything that has been stored.
        """
        reply = QMessageBox.question(None, 'Careful there!', "You are about to delete your project.. proceed?", QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
        if reply == QMessageBox.Yes:
            # clear everything from plot
            self.parent.plotWidget.resetFigure()
            self.hand_drawn_polys = []
            self.undone = []
            self.polys = []
            self.parent.info_tree.tw_polys.clear()
            # and disable functions that are only accessible if a poly is there
            self.parent.info_tree.btn_undo.setEnabled(False)
            self.parent.toolBar.acn_reset_figure.setEnabled(False)
            # enable/disable polytools
            self.enabelingToolBarFunctions()
            # set marker to begin with 1
            self.marker = -1
            # hide the iamge dialog again
            self.parent.toolBar.widgetAction.setVisible(False)
        else:
            pass

    def markersMove(self):
        """
        Plot dots as marker positions which can be moved to reset the position
        of any marker if there are multiple markers in one region.

        Todo
        ----
        + get rid of the dummy flag for the marker moving thingy... use parent instead
        """
        try:  # to avoid emitting a signal and using it multiple ways
            self.span.disconnect()
        except AttributeError:
            pass

        # TODO: this:
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
                self.new_markers.append(list(val.values()))
                p.disconnect()
            self.markersClicked = True
            self.parent.toolBar.acn_markerCheck.setChecked(False)
            self.parent.info_tree.redrawTable()
            self.parent.setCursor(Qt.ArrowCursor)

    def markerSize(self):
        """
        Calculate the size of the to-be-plotted red dot which represents the marker.

        Todo
        ----
        + make the marker dot pixel size!
        """
        m, n = self.figure.axis.get_xlim()
        return abs(m - n)/50

    def toggleGrid(self):
        """
        Plot a grid to orientate the polygon creation.

        Todo
        ----
        + MAKE THIS WORK!!
        + also it would be nice if the grid was freely scalable.. like ctrl+g+wheel to set the stepping width of the grid
        + get ffin rid of those dummy flags!!!
        """
        if self.gridClicked is True:
            self.figure.axis.grid()
            self.gridClicked = False
        else:
            self.figure.axis.grid(False)
            self.gridClicked = True
            self.acn_gridToggle.setChecked(False)
        self.figure.canvas.draw()

    def magnetizeGrid(self):
        """
        Magnetize the grid to better snap to a hard point.

        Todo
        ----
        + MAKE THIS WORK!!
        + magnetize intersections and edges?!
        """
        if self.magnetize is True:
            self.figure.axis.grid()
            self.magnetize = False
        else:
            self.figure.axis.grid(False)
            self.magnetize = True
            self.parent.toolBarself.acn_magnetizeGrid.setChecked(False)
        self.figure.canvas.draw()

    def magnetizePoly(self):
        """
        Magnetize the nodes of each existing and drawn polygon so it is easier
        to connect two polygons.

        Note
        ----
        Magnetized nodes turn light green when they are 'active' and turn red
        when snapping reached the radius to the point.

        Todo
        ----------
        + magnetize the edges
        """
        if self.mPolyClicked is True:
            x = []
            y = []
            # collect the positions from the polygon
            x, y = self.getNodes()

            self.mp = MagnetizePolygons(self, x, y)
            self.mp.connect()
            # HACK: against flickering and false data while spanning:
            self.span.disconnect()
            self.span.connect()
            self.mPolyClicked = False
        else:
            self.mp.disconnect()
            # self.figure.axis.grid(False)  # why is this here?!
            self.mPolyClicked = True
            self.parent.toolBar.acn_magnetizeGrid.setChecked(False)
        self.figure.canvas.draw()

    def getNodes(self):
        """
        Retrieve the x, y-coordinates for every polygon in the figure.

        Returns
        -------
        x: list
            All the gathered x coordinates.
        y: list
            All the gathered y coordinates.
        """
        arr = self.poly.positions()
        x = list(pg.x(arr))
        y = list(pg.y(arr))

        return x, y

    def undoPoly(self):
        """
        Remove last made polygon from list and store it so it won't be lost completely.
        """
        # set the marker down
        self.marker -= 1
        # remove the last created polygon
        self.undone.append(self.polys.pop())
        # remove the parameters of the last created polygon
        self.undone_hand_drawn.append(self.hand_drawn_polys.pop())
        # remove last added entry from treewidget
        self.parent.info_tree.tw_polys.takeTopLevelItem(self.parent.info_tree.tw_polys.topLevelItemCount() - 1)
        # since the one removed wandered into the redo list, the button can now be enabled
        self.parent.info_tree.btn_redo.setEnabled(True)
        if not len(self.polys) == 0:
            self.drawPoly()
            self.fillInfoTree()
        else:
            self.figure.axis.cla()
            self.figure.canvas.draw()
            self.parent.info_tree.btn_undo.setEnabled(False)
            self.enabelingToolBarFunctions()

    def redoPoly(self):
        """
        Redo the undone. Every undone polygon is stored and can be recalled.
        """
        if len(self.undone) > 0:
            # append the last undone back to the original
            self.polys.append(self.undone.pop())
            self.hand_drawn_polys.append(self.undone_hand_drawn.pop())
            # self.hand_drawn_polys.pop()
            self.marker += 1
            self.drawPoly()
            self.fillInfoTree()

        if len(self.undone) == 0:
            self.parent.info_tree.btn_redo.setEnabled(False)

    def zipUpMarkerAndAttributes(self):
        """
        Join marker and attribute into list so it can be pased to cells and
        check if duplicates were made.
        """
        attrMap = []
        for i, a in enumerate(self.parent.info_tree.polyAttributes):
            if a == '' or a == '\n':
                self.statusbar.showMessage("ERROR: empty attributes can't be assigned!")
            else:
                try:
                    a = float(a)
                    # self.statusbar.showMessage("{} is a float now".format(a))
                    attrMap.append([self.parent.info_tree.polyMarkers[i], a])
                except ValueError:
                    self.statusbar.showMessage("ERROR: some values seem to be string. int or float is needed")

        return attrMap


if __name__ == '__main__':

    import sys

    app = QApplication(sys.argv)
    builderWin = Builder()
    builderWin.show()
    sys.exit(builderWin.exec_())
