#!/usr/bin/env python
# encoding: UTF-8

""" class for tab with main model builder components """
from PyQt4 import QtGui
from pygimli.mplviewer import drawMesh
from pygimli.meshtools import polytools as plc
import numpy as np
from matplotlib.patches import Rectangle, Circle


class Builder(object):
    """
        sprinkle some visual sugar for polytool contruction :-)
    """

    clicker = 0

    # def __init__(self, plotWidget, parent=None):
    def __init__(self, plotWidget, table):
        # stuff
        super(Builder, self).__init__()
        self.figure = plotWidget
        self.table = table
        print("FUCKING INIT")
        # try:
        #     self.marker = self.marker
        #     print("try")
        # except AttributeError:
        #     print("except")
        self.marker = 1
        self.polys = []

    """
    @classmethod
    def marker(cls, n=0):
        clicked = cls(cls.clicker)
        clicked += n
        print(clicked)
        return clicked
    """

    def buildCircle(self):
        print("now a circle")
        # try:
        #     self.object.disconnect()
        # except AttributeError:
        #     pass
        self.object = SpanCircle(self.figure, self.table)
        self.object.connect()

    def buildRectangle(self):
        print("now a rectangle")
        # try:
        #     self.object.disconnect()
        # except AttributeError:
        #     pass
        self.object = SpanRectangle(self.figure, self.table)
        self.object.connect()

    def buildLine(self):
        print("now a line")
        # try:
        #     self.object.disconnect()
        # except AttributeError:
        #     pass
        self.object = SpanLine(self.figure, self.table)
        self.object.connect()

    # def disconnect(self):
    #     # print("disconnect", self.marker)
    #     self.marker = self.object.disconnect()
    #     print("def disconnect", self.marker)
    #     # return clicker

    def getPoly(self):
        return self.poly, self.table

    def distance(self):
        return round(np.sqrt((self.x_m - self.x_p)**2 + (self.y_m - self.y_p)**2), 2)

    def draw(self, form):
        """
            zeug
        """
        print("draw", self.marker)
        if len(self.polys) > 1:
            self.poly = plc.mergePLC(self.polys)
        else:
            self.poly = self.polys[0]
        self.figure.axis.cla()
        drawMesh(self.figure.axis, self.poly, fitView=False)
        self.figure.canvas.draw()
        self.fillTable(form)

    def drawCircle(self):
        """
            draw simple circle with polytools
        """
        self.polys.append(plc.createCircle(pos=(self.x_p, self.y_p), segments=12, radius=self.distance(), marker=self.marker))
        print("circle", self.marker, len(self.polys))

        self.draw(form="circle")

    def drawRectangle(self):
        """
            draw simple rectangle with polytools
            >>> kannweg5/8
        """
        self.polys.append(plc.createRectangle(start=[self.x_p, self.y_p], end=[self.x_r, self.y_r], marker=self.marker))
        print("rectangle", self.marker, len(self.polys))

        self.draw(form="rectangle")

    def drawWorld(self):
        """
            draw world where every other polygon will be stored in
        """
        self.polys.append(plc.createWorld(start=[self.x_p, self.y_p], end=[self.x_r, self.y_r], marker=self.marker))
        print("world", self.marker, len(self.polys))

        self.draw(form="world")

    def drawLine(self):
        """
            draw line.. *duh*
        """
        self.polys.append(plc.createLine(start=[self.x_p, self.y_p], end=[self.x_r, self.y_r], segments=3, boundaryMarker=1))
        print("line", self.marker, len(self.polys))

        self.draw(form="line")

    def drawPolygon(self):
        """
            function where the clicked polygon is assembled
            >>> kannweg2
        """

    # TODO: def redrawTable(self):

    def fillTable(self, form):
        """
            for construction: header labels >>>
            "Type", "x0", "y0", "x1", "y1", "Radius", "Segments", "Start", "End", "Marker", "Area", "Boundary", "Left?", "Hole?", "Closed?"
        """
        print("table", self.marker)
        # update table on release
        self.table.setColumnCount(self.marker)
        col = self.marker - 1
        # insert poly type... circle/world/rectangle/hand
        self.table.setItem(0, col, QtGui.QTableWidgetItem(form))

        # if form == "circle":
        # insert position
        self.table.setItem(1, col, QtGui.QTableWidgetItem(str(round(self.x_p, 2))))
        self.table.setItem(2, col, QtGui.QTableWidgetItem(str(round(self.y_p, 2))))

        if form == "rectangle" or form == "world" or form == "line":
            self.table.setItem(3, col, QtGui.QTableWidgetItem(str(round(self.x_r, 2))))
            self.table.setItem(4, col, QtGui.QTableWidgetItem(str(round(self.y_r, 2))))

        if form == "circle":
            # insert segments
            spx_segments = QtGui.QSpinBox()
            spx_segments.setValue(12)
            spx_segments.setMinimum(3)
            self.table.setCellWidget(6, col, spx_segments)

        if form == "line":
            # insert segments
            spx_segments = QtGui.QSpinBox()
            spx_segments.setValue(3)
            spx_segments.setMinimum(3)
            self.table.setCellWidget(6, col, spx_segments)

        if form == "circle":
            # insert radius
            spx_radius = QtGui.QDoubleSpinBox()
            spx_radius.setSingleStep(0.01)
            spx_radius.setValue(self.distance())
            self.table.setCellWidget(5, col, spx_radius)
            # insert start
            spx_start = QtGui.QDoubleSpinBox()
            spx_start.setValue(0.00)
            spx_start.setMinimum(0.00)
            spx_start.setSingleStep(0.01)
            spx_start.setMaximum(2*np.pi)
            self.table.setCellWidget(7, col, spx_start)
            # insert end
            spx_end = QtGui.QDoubleSpinBox()
            spx_end.setValue(2*np.pi)
            spx_end.setMinimum(0.00)
            spx_end.setSingleStep(0.01)
            spx_end.setMaximum(2*np.pi)
            self.table.setCellWidget(8, col, spx_end)

        if not form == "line":
            # insert marker
            for k in range(self.marker):
                a = QtGui.QComboBox(self.table)
                [a.addItem(str(m+1)) for m in range(self.marker)]
                a.setCurrentIndex(k)
                self.table.setCellWidget(9, k, a)
            # insert area
            spx_area = QtGui.QDoubleSpinBox()
            spx_area.setSingleStep(0.01)
            spx_area.setValue(0.00)
            spx_area.setMinimum(0.00)
            self.table.setCellWidget(10, col, spx_area)

        if not form == "world":
            # insert boundary marker
            self.table.setItem(11, col, QtGui.QTableWidgetItem(str(1)))
            # insert left direction
            cbx_isLeft = QtGui.QComboBox()
            cbx_isLeft.addItem("False")
            cbx_isLeft.addItem("True")
            self.table.setCellWidget(12, col, cbx_isLeft)

        if form != "world" and form != "line":
            # insert is hole
            cbx_isHole = QtGui.QComboBox()
            cbx_isHole.addItem("False")
            cbx_isHole.addItem("True")
            self.table.setCellWidget(13, col, cbx_isHole)
            # insert is closed
            cbx_isClosed = QtGui.QComboBox()
            cbx_isClosed.addItem("False")
            cbx_isClosed.addItem("True")
            self.table.setCellWidget(14, col, cbx_isClosed)

        self.table.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        self.table.resizeColumnsToContents()

        # iterate marker counter
        self.marker += 1
        print("table", self.marker)


class SpanLine(Builder):

    def __init__(self, *args):
        super(SpanLine, self).__init__(*args)
        # introduce empty line to start with
        line, = self.figure.axis.plot([0], [0], c="black")
        self.line = line
        self.background = None
        # self.onPress = self.onPress

    def connect(self):
        self.cid_p = self.figure.canvas.mpl_connect("button_press_event", self.onPress)
        self.cid_m = self.figure.canvas.mpl_connect("motion_notify_event", self.onMotion)
        self.cid_r = self.figure.canvas.mpl_connect("button_release_event", self.onRelease)

    def disconnect(self):
        self.figure.canvas.mpl_disconnect(self.cid_p)
        self.figure.canvas.mpl_disconnect(self.cid_m)
        self.figure.canvas.mpl_disconnect(self.cid_r)

    # def getXY(self):
    #     """
    #         return spanning coordinates
    #     """
    #     return self.x_p, self.y_p, self.x_r, self.y_r

    def onPress(self, event):
        if event.button is 1:
            self.x_p = event.xdata
            self.y_p = event.ydata
            self.line.set_animated(True)
            self.figure.canvas.draw()
            self.background = self.figure.canvas.copy_from_bbox(self.line.axes.bbox)
            self.line.axes.draw_artist(self.line)
            self.figure.canvas.blit(self.line.axes.bbox)

    def onMotion(self, event):
        if event.inaxes != self.line.axes: return
        try:
            self.x_m = event.xdata
            self.y_m = event.ydata
            self.line.set_data([self.x_p, self.x_m], [self.y_p, self.y_m])
            # TODO: den radius am ansatzpunkt anzeigen
            # self.figure.axis.annotate(self.distance(), xy=(self.x_p, self.y_p))

            self.figure.canvas.restore_region(self.background)
            self.line.axes.draw_artist(self.line)
            self.figure.canvas.blit(self.line.axes.bbox)

        except (AttributeError, TypeError):
            pass

    def onRelease(self, event):
        try:
            self.x_r = event.xdata
            self.y_r = event.ydata
            # set line empty to remove from view
            self.line.set_data([0], [0])
            self.line.axes.draw_artist(self.line)
            # set back variables
            self.line.set_animated(False)
            self.background = None
            self.drawLine()

        except AttributeError:
            pass


class SpanRectangle(Builder):
    def __init__(self, *args):
        super(SpanRectangle, self).__init__(*args)
        # empty rectangle
        self.rect = Rectangle((0, 0), 0, 0, fc="none", alpha=0.5, ec="black")
        self.background = None
        self.figure.axis.add_patch(self.rect)

    def connect(self):
        self.cid_p = self.figure.canvas.mpl_connect("button_press_event", self.onPress)
        self.cid_m = self.figure.canvas.mpl_connect("motion_notify_event", self.onMotion)
        self.cid_r = self.figure.canvas.mpl_connect("button_release_event", self.onRelease)

    def disconnect(self):
        self.figure.canvas.mpl_disconnect(self.cid_p)
        self.figure.canvas.mpl_disconnect(self.cid_m)
        self.figure.canvas.mpl_disconnect(self.cid_r)
        print("rectangle disconnect", self.marker)
        return self.marker

    def onPress(self, event):
        if event.button is 1:
            self.x_p = event.xdata
            self.y_p = event.ydata
            self.rect.set_animated(True)
            self.figure.canvas.draw()
            self.background = self.figure.canvas.copy_from_bbox(self.rect.axes.bbox)
            self.rect.axes.draw_artist(self.rect)
            self.figure.canvas.blit(self.rect.axes.bbox)

    def onMotion(self, event):
        if event.inaxes != self.rect.axes: return
        try:
            self.x_m = event.xdata
            self.y_m = event.ydata
            self.rect.set_width(self.x_m - self.x_p)
            self.rect.set_height(self.y_m - self.y_p)
            self.rect.set_xy((self.x_p, self.y_p))

            self.figure.canvas.restore_region(self.background)
            self.rect.axes.draw_artist(self.rect)
            self.figure.canvas.blit(self.rect.axes.bbox)

        except (AttributeError, TypeError):
            pass

    def onRelease(self, event):
        try:
            self.x_r = event.xdata
            self.y_r = event.ydata
            self.rect.set_width(0)
            self.rect.set_height(0)
            self.rect.set_xy((0, 0))
            self.rect.axes.draw_artist(self.rect)
            self.rect.set_animated(False)
            self.background = None
            self.drawRectangle()

        except AttributeError:
            pass


class SpanCircle(Builder):

    def __init__(self, *args):
        super(SpanCircle, self).__init__(*args)
        # introduce empty circle to start with
        self.circle = Circle((0, 0), 0, fc="none", ec="black")
        self.background = None
        self.figure.axis.add_patch(self.circle)
        # WTF!!!!
        self.onPress = self.onPress

    def connect(self):
        # self.marker = 1
        self.cid_p = self.figure.canvas.mpl_connect("button_press_event", self.onPress)
        self.cid_m = self.figure.canvas.mpl_connect("motion_notify_event", self.onMotion)
        self.cid_r = self.figure.canvas.mpl_connect("button_release_event", self.onRelease)

    def disconnect(self):
        self.figure.canvas.mpl_disconnect(self.cid_p)
        self.figure.canvas.mpl_disconnect(self.cid_m)
        self.figure.canvas.mpl_disconnect(self.cid_r)
        print("circle disconnect", self.marker)
        # return self.marker

    def onPress(self, event):
        if event.button is 1:
            self.x_p = event.xdata
            self.y_p = event.ydata
            self.circle.set_animated(True)
            self.figure.canvas.draw()
            self.background = self.figure.canvas.copy_from_bbox(self.circle.axes.bbox)
            self.circle.axes.draw_artist(self.circle)
            self.figure.canvas.blit(self.circle.axes.bbox)

    def onMotion(self, event):
        if event.inaxes != self.circle.axes: return
        try:
            self.x_m = event.xdata
            self.y_m = event.ydata
            # inconsistent mpl crap
            self.circle.center = (self.x_p, self.y_p)
            self.circle.set_radius(self.distance())
            # TODO: den radius am ansatzpunkt anzeigen
            # self.figure.axis.annotate(self.distance(), xy=(self.x_p, self.y_p))

            self.figure.canvas.restore_region(self.background)
            self.circle.axes.draw_artist(self.circle)
            self.figure.canvas.blit(self.circle.axes.bbox)

        except (AttributeError, TypeError):
            pass

    def onRelease(self, event):
        try:
            self.x_r = event.xdata
            self.y_r = event.ydata
            # inconsistent mpl crap
            self.circle.center = (0, 0)
            self.circle.set_radius(0)
            self.circle.axes.draw_artist(self.circle)
            # set back variables
            self.circle.set_animated(False)
            self.background = None
            self.drawCircle()

        except AttributeError:
            pass
