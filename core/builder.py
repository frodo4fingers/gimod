#!/usr/bin/env python
# encoding: UTF-8

try:
    from PyQt5.QtWidgets import QMessageBox
    from PyQt5.QtCore import Qt

except ImportError:
    from PyQt4.QtGui import QMessageBox
    from PyQt4.QtCore import Qt

from matplotlib import patches
from matplotlib.patches import Polygon, Rectangle

from mpl import (SpanWorld, SpanRectangle, SpanCircle, SpanLine, SpanPoly,
        DraggablePoint, MagnetizePolygons, MagnetizedGrid, MPLBase)

import pygimli as pg
from pygimli.mplviewer import drawMesh, drawMeshBoundaries, drawModel
from pygimli.meshtools import polytools as plc
from pygimli.meshtools import createMesh

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
        self.figure = parent.plotwidget.plot_sketch
        self.toolbar = parent.toolbar
        self.statusbar = parent.statusbar
        # initialize the marker at -1 to get the starting polygon (WORLD *fingers crossed*) with a 0 marker
        self.marker = -1
        # new_markers holds the marker positions that were manually corrected with self.markersMove
        self.new_markers = []
        # store all created polygon objects
        self.polys = []
        # store all parameters of a drawn raw polygon
        self.mpl_paths = []
        self.patches = []
        self.undone_patches = []
        # the positions of every drawn poly-edge to mark those in a scatter plot
        self.magnets = []
        # here the stuff is put after undoing it... the list where everything is hidden
        self.undone = []
        self.undone_mpl_paths = []
        # storage for the drawn/spanned matplotlib-polygons
        self.mpl_polys = []
        # TODO: get rid of these!!!
        # dummy flags for action in :class:`~gui.PolyToolBar` to trigger the right decision
        self.markersClicked = True
        self.gridClicked = True
        self.magnetizeClicked = True
        self.mPolyClicked = True
        self.poly = None
        self.world_clicked = False
        self.rect_clicked = False
        self.circle_clicked = False
        self.line_clicked = False
        self.polygon_clicked = False
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
        # if self.toolbar.acn_world.isChecked():
        if self.world_clicked is False:
            self.world_clicked = True
            try:
                self.span.disconnect()
            except AttributeError:
                pass
            self.span = SpanWorld(self)
            self.span.connect()
        else:
            self.span.disconnect()
            self.toolbar.acn_world.setChecked(False)
            self.world_clicked = False

    def formPolyRectangle(self):
        """
        Connect the mouse event to the canvas for accessing plc.createRectangle.
        """
        if self.rect_clicked is False:
            self.rect_clicked = True
            try:
                # if something is already checked
                self.span.disconnect()
            except AttributeError:
                # nothing else is chcecked
                pass
            self.span = SpanRectangle(self)
            self.span.connect()
        else:
            self.span.disconnect()
            self.toolbar.acn_rectangle.setChecked(False)
            self.rect_clicked = False

    def formPolyCircle(self):
        """
        Connect the mouse event to the canvas for accessing plc.createCircle.
        """
        if self.circle_clicked is False:
            self.circle_clicked = True
            try:
                # if something is already checked
                self.span.disconnect()
            except AttributeError:
                # nothing else is chcecked
                pass
            self.span = SpanCircle(self)
            self.span.connect()
        else:
            self.span.disconnect()
            self.toolbar.acn_circle.setChecked(False)
            self.circle_clicked = False

    def formPolyLine(self):
        """
        Connect the mouse event to the canvas for accessing plc.createLine.
        """
        if self.line_clicked is False:
            self.line_clicked = True
            try:
                # if something is already checked
                self.span.disconnect()
            except AttributeError:
                # nothing else is chcecked
                pass
            self.span = SpanLine(self)
            self.span.connect()
        else:
            self.span.disconnect()
            self.toolbar.acn_line.setChecked(False)
            self.line_clicked = False

    def formPolygon(self):
        """
        Connect the mouse event to the canvas for accessing plc.createPolygon.
        """
        if self.polygon_clicked is False:
            self.polygon_clicked = True
            try:
                # if something is already checked
                self.span.disconnect()
            except AttributeError:
                # nothing else is chcecked
                pass
            self.span = SpanPoly(self)
            self.span.connect()
        else:
            self.span.disconnect()
            self.toolbar.acn_polygon.setChecked(False)
            self.polygon_clicked = False

    def formPolygonFromFigure(self):
        """
        Create all polygons chosen from a figure.

        Todo
        ----
        + try a progress bar here!! :D
        """
        # clear the table on the side tobe sure
        self.parent.setCursor(Qt.WaitCursor)

        if len(self.mpl_paths) > 0:
            # this when something is drawn by hand
            self.constructPoly()
            self.drawPoly()
        else:
            # this is called when an image is being taken into polygon form
            self.parent.info_tree.tw_polys.clear()
            self.polys.clear()
            self.span = MPLBase(self)
            
            # get the current axes limitations to establish the world polygon first
            xlim = self.figure.axis.get_xlim()
            ylim = self.figure.axis.get_ylim()
            world = Rectangle((int(xlim[0]), int(ylim[0])), int(xlim[1] - xlim[0]), int(ylim[1] - ylim[0]), fc='none', lw=1, ec='blue')
            verts = world.get_verts()
            self.span.drawMagnets(verts)
            self.magnets.append(verts)
            self.storeMPLPaths(world, ['World', [int(xlim[0]), int(ylim[0]), int(xlim[1]), int(ylim[1])]])

            for p in self.parent.image_tools.contoursCutted:
                poly = Polygon(p)
                verts = poly.get_verts()
                self.span.drawMagnets(verts)
                self.magnets.append(verts)
                self.storeMPLPaths(poly, ['Polygon', p])
            
            self.constructPoly()
            # draw created polygon
            self.drawPoly()

            # turn on buttons to reset figure or delete last build polygon
            self.parent.info_tree.btn_undo.setEnabled(True)
            self.parent.toolbar.acn_reset_figure.setEnabled(True)
            # activate all the polytools
            # NOTE: not calling enableToolBarFunctions() because when loading a
            # figure the world tag doesn't exist which would be necessary to work
            # this method
            self.parent.toolbar.acn_polygon.setEnabled(True)
            self.parent.toolbar.acn_rectangle.setEnabled(True)
            self.parent.toolbar.acn_circle.setEnabled(True)
            self.parent.toolbar.acn_line.setEnabled(True)
            self.parent.toolbar.acn_markerCheck.setEnabled(True)
            self.parent.toolbar.acn_magnetizePoly.setEnabled(True)

        # change message in statusbar to info about the polygon
        self.statusbar.showMessage(str(self.poly))
        self.parent.setCursor(Qt.ArrowCursor)

    def storeMPLPaths(self, patch, d):
        """
        Append the given values from each span and start filling the overview
        table with the given values.

        Parameters
        ----------
        d: dict
            Dictionary structure containing what was drawn and what are the parameters.
        """
        self.patches.append(patch)
        if d[0] == 'World':
            self.mpl_paths.append(('World', *d[1], None))
        elif d[0] == 'Rectangle':
            self.mpl_paths.append(('Rectangle', *d[1], None))
        elif d[0] == 'Circle':
            self.mpl_paths.append(('Circle', *d[1], None, None))
        elif d[0] == 'Line':
            self.mpl_paths.append(('Line', *d[1], None))
        elif d[0] == 'Polygon':
            self.mpl_paths.append(('Polygon', None, None, None, None, d[1]))

        # add a marker according to the number of created polygons
        for i, poly in enumerate(self.mpl_paths):
            # HACK .. more or less
            if len(self.mpl_paths[i]) < 7:
                self.mpl_paths[i] = (*poly, i)
        # determine the range of markers
        self.marker = len(self.mpl_paths)
        # draw them all as mpl objects
        self.span.drawToCanvas(self.patches)
        self.enableToolBarFunctions()

        self.fillInfoTree()

        # turn on buttons to reset figure or delete last build polygon
        self.parent.info_tree.btn_undo.setEnabled(True)
        self.parent.toolbar.acn_reset_figure.setEnabled(True)
        self.parent.toolbar.acn_polygonize.setEnabled(True)

    def constructPoly(self):
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
        # self.mpl_paths.append((form, x_p, y_p, x_r, y_r, polygon, marker))
        self.polys.clear()
        for poly in self.mpl_paths:
            form = poly[0]
            x_p = poly[1]
            y_p = poly[2]
            x_r = poly[3]
            y_r = poly[4]
            polygon = poly[5]
            marker = poly[6]
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

    def drawPoly(self, polys=None, to_merge=True):
        """
        Merge all created polygons and check for different flags to show the result.

        Parameters
        ----------
        polys: list [None]
            A polys attribute is only passed from
            :meth:`~gui.InfoTree.redrawTable` when the (maybe altered) content
            from the info tree is taken and redrawn

        to_merge: bool [True]
            ???CALLED FROM WHERE???

        Todo
        ----
        + get rid of the dummy flag for magnetizing the polygons nodes. use parent instead
        + check if two polygons with same region marker have the same attribute
        """
        # merge all (given) polygons
        if to_merge:
            if polys is not None:
                # necessaray step because redrawing checks for the list of
                # polys to grep the marker positions. if the renewed marker
                # positions after marker setting are not yet there, the old
                # positions are taken and all steps need to be repeated until
                # eternity
                self.polys = polys
            self.poly = plc.mergePLC(self.polys)
            self.parent.plotwidget.plot_poly.axis.cla()

        # check for the region plot option in treeview functions below the table
        if self.parent.info_tree.rbtn_plotRegions.isChecked() is True:
            drawMesh(self.parent.plotwidget.plot_poly.axis, self.poly, fitView=False)
            self.parent.plotwidget.plot_poly.canvas.draw()
        # if the attribute radiobutton below the tree widget is checked the
        # mesh view is slightly more complicated
        else:
            attr_map = self.zipUpMarkerAndAttributes()
            if attr_map:  # not empty
                # create temporary mesh
                temp_mesh = createMesh(self.poly)
                # parse the attributes to the mesh
                attr_map = pg.solver.parseMapToCellArray(attr_map, temp_mesh)
                drawMeshBoundaries(self.parent.plotwidget.plot_poly.axis, temp_mesh, hideMesh=True)
                drawModel(self.parent.plotwidget.plot_poly.axis, temp_mesh, tri=True, data=attr_map)
                self.parent.plotwidget.plot_poly.canvas.draw()
            else:  # empty
                QMessageBox.question(None, 'Whoops..', "Your regions don't have any attributes to plot!", QMessageBox.Ok)

        # set the tab active where the polygon structure was plotted
        self.parent.plotwidget.setCurrentIndex(1)

        # redraw the grid if it is checked:
        if self.parent.toolbar.acn_gridToggle.isChecked():
            # if it is checked there is a self.grid
            self.grid.disable()
            self.grid.grid()

        if self.parent.toolbar.acn_magnetizeGrid.isChecked():
            self.grid.disconnect()
            self.grid.connect()

        # TODO: get rid of the dummy flag
        if not self.mPolyClicked:
            x, y = self.getNodes()
            self.mp.plotMagnets(x, y)

        self.parent.statusbar.showMessage(str(self.poly))
        # self.enableToolBarFunctions()

    def enableToolBarFunctions(self):
        """
        After drawing a polygon check whether the ``world`` needs to be
        disabled after creation or the other tools if no world exists.
        """
        # get the poly form as first position from every tuple
        existence = [poly[0] for poly in self.mpl_paths]

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
            # REVIEW: this down here
            # try:
            #     # disconnect the last used polytool
            #     self.span.disconnect()
            # except AttributeError:
            #     # if a figure is loaded and polygonized a world might be drawn
            #     # around and thats nearly all... so disconnect the drawing
            #     # signal to prevent unvoluntary drawing
            #     pass
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
        for entry in self.mpl_paths:
            # form, x_p, y_p, x_r, y_r, polygon, marker
            self.parent.info_tree.fillTable(entry[0], entry[1], entry[2], entry[3], entry[4], entry[5], entry[6])

    def resetFigure(self):
        """
        When clicked the user is asked if all achievements should really be discarded, since this method will clear the figure, the info tree and everything that has been stored.
        """
        reply = QMessageBox.question(None, 'Careful there!', "You are about to delete your project.. proceed?", QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
        if reply == QMessageBox.Yes:
            # clear everything from plot
            self.parent.plotwidget.plot_sketch.resetFigure()
            self.mpl_paths = []
            self.undone = []
            self.polys = []
            self.parent.info_tree.tw_polys.clear()
            # and disable functions that are only accessible if a poly is there
            self.parent.info_tree.btn_undo.setEnabled(False)
            self.parent.toolbar.acn_reset_figure.setEnabled(False)
            # enable/disable polytools
            self.enableToolBarFunctions()
            # set marker to begin with 1
            self.marker = -1
            # hide the iamge dialog again
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
        # disconnect all drawing signals
        try:
            self.span.disconnect()
        except AttributeError:
            pass

        # TODO: this:
        if self.markersClicked is True:
            self.markersClicked = False
            self.dps = []
            # create a draggable point for every polygon, so the marker position can be reset
            for i, p in enumerate(self.polys):
                # m = pg.center(p.positions())
                # cast the RegionMarkerPLC object to list and take the first
                # two entries: x, y
                try:
                    pos = list(p.regionMarker()[0])[:2]
                except IndexError:
                    # meaning it is a line from createLine
                    self.dps.append(None)
                    pass
                else:
                    mark = patches.Circle(pos, radius=self.markerSize(), fc='r')
                    self.figure.axis.add_patch(mark)
                    dp = DraggablePoint(mark, i, pos)
                    dp.connect()
                    self.dps.append(dp)
            self.figure.canvas.draw()

        else:
            self.parent.setCursor(Qt.WaitCursor)
            for p in self.dps:
                try:
                    val = p.returnValue()
                except AttributeError:
                    # meaning that i hit a None - a line
                    continue
                else:
                    self.new_markers.append(list(val.values()))
                    p.disconnect()
            self.markersClicked = True
            # uncheck the button
            self.parent.toolbar.acn_markerCheck.setChecked(False)
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
        """."""
        if self.parent.toolbar.acn_gridToggle.isChecked():
            # NOTE: will only call init and nothing more
            self.grid = MagnetizedGrid(self)
            self.parent.toolbar.acn_magnetizeGrid.setEnabled(True)
        else:
            self.parent.toolbar.acn_magnetizeGrid.setEnabled(False)
            self.parent.toolbar.acn_magnetizeGrid.setChecked(False)
            self.grid.disconnect()
            self.grid.disable()
        # grid.grid()

    def toggleMagnetizedGrid(self):
        """."""
        if self.parent.toolbar.acn_magnetizeGrid.isChecked():
            # since the polytools getting 'self' it may occur that they are
            # triggered before the grid is magnetized and therefor will miss
            # some mouse event variables. so whatever polytool is enabled it
            # will be disconnected and re-instanciated again.
            # if hasattr(self, 'span'):
            #     self.span.disconnect()
            if self.world_clicked is True:
                self.world_clicked = False
                self.formPolyWorld()
            elif self.rect_clicked is True:
                self.rect_clicked = False
                self.formPolyRectangle()
            elif self.circle_clicked is True:
                self.circle_clicked = False
                self.formPolyCircle()
            elif self.line_clicked is True:
                self.line_clicked = False
                self.formPolyLine()
            elif self.polygon_clicked is True:
                self.polygon_clicked = False
                self.formPolygon()
            self.grid.connect()

        else:
            self.grid.disconnect()
            # self.grid.disable()
            # self.grid.dot.set_data([], [])
            # self.figure.canvas.draw()

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
            # x = []
            # y = []
            # # collect the positions from the polygon
            # x, y = self.getNodes()

            # self.mp = MagnetizePolygons(self, x, y)
            self.mp = MagnetizePolygons(self)
            self.mp.connect()
            # HACK: against flickering and false data while spanning:
            self.span.disconnect()
            self.span.connect()
            self.mPolyClicked = False
        else:
            self.mp.disconnect()
            # self.figure.axis.grid(False)  # why is this here?!
            self.mPolyClicked = True
            # self.parent.toolbar.acn_magnetizeGrid.setChecked(False)
        self.figure.canvas.draw()

    # def getNodes(self):
    #     """
    #     Retrieve the x, y-coordinates for every polygon in the figure.
    #
    #     Returns
    #     -------
    #     x: list
    #         All the gathered x coordinates.
    #     y: list
    #         All the gathered y coordinates.
    #     """
    #     arr = self.poly.positions()
    #     x = list(pg.x(arr))
    #     y = list(pg.y(arr))
    #
    #     return x, y

    def undoPoly(self):
        """
        Remove last made polygon from list and store it so it won't be lost completely.
        """
        print("triggered")
        # get the index of the rightclicked item if not None
        if hasattr(self.parent.info_tree.contextmenu, 'to_del'):
            idx = self.parent.info_tree.contextmenu.to_del
        else:
            idx = None
        if idx is None:
            idx = -1
            take_at = self.parent.info_tree.tw_polys.topLevelItemCount() - 1
        else:
            take_at = idx

        print(idx, take_at)
        # set the marker down
        self.marker -= 1
        # remove the last created polygon
        # self.undone.append(self.polys.pop(idx))
        self.undone_patches.append(self.patches.pop(idx))
        # remove the parameters of the last created polygon
        self.undone_mpl_paths.append(self.mpl_paths.pop(idx))
        # print(len(self.undone), len(self.undone_mpl_paths))
        print(len(self.undone_patches), len(self.undone_mpl_paths))
        # remove entry from treewidget at index
        self.parent.info_tree.tw_polys.takeTopLevelItem(take_at)
        # since the one removed wandered into the redo list, the button can now be enabled
        self.parent.info_tree.btn_redo.setEnabled(True)
        # if not len(self.polys) == 0:
        if not len(self.patches) == 0:
            # self.drawPoly()
            self.span.drawToCanvas(self.patches)
            self.fillInfoTree()
        else:
            self.figure.axis.cla()
            self.figure.canvas.draw()
            self.parent.info_tree.btn_undo.setEnabled(False)
            self.enableToolBarFunctions()

    def redoPoly(self):
        """
        Redo the undone. Every undone polygon is stored and can be recalled.
        """
        # if len(self.undone) > 0:
        if len(self.undone_patches) > 0:
            # append the last undone back to the original
            # self.polys.append(self.undone.pop())
            self.patches.append(self.undone_patches.pop())
            self.mpl_paths.append(self.undone_mpl_paths.pop())
            # self.mpl_paths.pop()
            self.marker += 1
            # self.drawPoly()
            self.span.drawToCanvas(self.patches)
            self.fillInfoTree()

        # if len(self.undone) == 0:
        if len(self.undone_mpl_paths) == 0:
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
    pass
