from matplotlib.lines import Line2D
# from numpy import allclose
import numpy as np

try:
    from PyQt5.QtWidgets import QApplication, QWidget
    from PyQt5.QtGui import QCursor
    from PyQt5.QtCore import Qt, QPoint

except ImportError:
    from PyQt4.QtQui import QCursor, QApplication, QWidget
    from PyQt4.QtCore import Qt, QPoint

import time


class MagnetizedGrid():
    """
    Everything the grid resembles is stored here. The drawing, the
    magnetization and 'catching' and the scalability.

    Note
    ----
    4me: scrolling with ctrl+g should increase/decrease the density of lines drawn

    Todo
    ----
    *[x] make grid
    *[x] make grid magnetized
    *[ ] make grid free scalable
    """

    def __init__(self, parent=None):
        """Initialize the important variables."""
        self.figure = parent.figure
        self.parent = parent  # builder
        self.gimod = parent.parent
        dot, = self.figure.axis.plot([], [], 'o', c='#ff0000')
        self.dot = dot
        self.grid()
        self.getCanvasHeight()
        self.onMotion = self.onMotion

    def getCanvasHeight(self):
        """."""
        _, self.height = self.figure.canvas.get_width_height()

    def connect(self):
        """."""
        self.cid_p = self.figure.canvas.mpl_connect('button_press_event', self.onPress)
        self.cid_m = self.figure.canvas.mpl_connect('motion_notify_event', self.onMotion)
        self.cid_ae = self.figure.canvas.mpl_connect('axes_enter_event', self.axesEnter)
        self.cid_al = self.figure.canvas.mpl_connect('axes_leave_event', self.axesLeave)
        self.cid_r = self.figure.canvas.mpl_connect('button_release_event', self.onRelease)

    def axesLeave(self, event):
        QApplication.restoreOverrideCursor()

    def axesEnter(self, event):
        QApplication.setOverrideCursor(QCursor(Qt.ArrowCursor))

    def disconnect(self):
        """."""
        try:
            self.figure.canvas.mpl_disconnect(self.cid_p)
            self.figure.canvas.mpl_disconnect(self.cid_m)
            self.figure.canvas.mpl_disconnect(self.cid_ae)
            self.figure.canvas.mpl_disconnect(self.cid_al)
            # self.figure.canvas.mpl_disconnect(self.cid_r)
        except AttributeError:
            # bc the grid might never be magnetized, thus not having any cid to disconnect
            pass

    def disable(self):
        """."""
        # for line in self.all_xlines + self.all_ylines:
        #     line.set_data([], [])
        # disable the grid
        self.figure.axis.grid(False)
        self.dot = self.figure.axis.plot([], [], 'o', c='#ff0000')
        self.figure.canvas.draw()

    def grid(self):
        """."""
        # set the actual grid
        self.figure.axis.grid()
        self.figure.canvas.draw()
        # get the axis ticks. returns a list of x,y-tuple
        x_ticks = [i.get_position()[0] for i in
            self.figure.axis.get_xticklabels()]
        y_ticks = [i.get_position()[1] for i in
            self.figure.axis.get_yticklabels()]

        # establish all cross sections as pixel position data
        self.crossings = []
        for x in x_ticks:
            for y in y_ticks:
                self.crossings.append(tuple(self.figure.axis.transData.transform((x, y))))

    def onPress(self, event):
        """."""
        if event.inaxes:
            try:
                dot, _ = self.vicinity(event.xdata, event.ydata)
            except TypeError:
                # no vicinity at all
                # pass
                self.x_p = event.xdata
                self.y_p = event.ydata
            else:
                # if dot is not None:
                self.x_p = dot[0]
                self.y_p = dot[1]
                self.dot.set_data(self.x_p, self.y_p)
                # self.dot.set_color(color)
                self.dot.set_animated(True)
                self.figure.canvas.draw()
                self.background = self.figure.canvas.copy_from_bbox(self.dot.axes.bbox)
                self.dot.axes.draw_artist(self.dot)
                self.figure.canvas.blit(self.dot.axes.bbox)
            #     else:
            #         self.x_c = None
            #         self.y_c = None
            # except TypeError:
            #     # TypeError: pressing the button was not in the vicinity of a gridline
            #     pass

    def onMotion(self, event):
        """."""
        if event.inaxes:  # meaning within the plotting area
            # print(self.gimod.mapToGlobal(QPoint(*self.transform(event.xdata, event.ydata))))
            # dot = self.transform(event.xdata, event.ydata)
            # print(dot)
            # print(QPoint(dot[0], dot[1]))
            # print(self.gimod.cursor().pos())
            print(type(self.dot), self.dot)
            if isinstance(self.dot, list):
                self.dot = self.dot[0]
            self.dot.set_animated(True)
            self.figure.canvas.draw()
            self.background = self.figure.canvas.copy_from_bbox(self.dot.axes.bbox)
            self.dot.axes.draw_artist(self.dot)
            self.figure.canvas.blit(self.dot.axes.bbox)
            try:
                dot, color = self.vicinity(event.xdata, event.ydata)
                self.x_m = dot[0]
                self.y_m = dot[1]
                self.dot.set_data(self.x_m, self.y_m)
                self.dot.set_color(color)
                self.figure.canvas.restore_region(self.background)
                self.dot.axes.draw_artist(self.dot)
                self.figure.canvas.blit(self.dot.axes.bbox)
            except (ValueError, TypeError):
                self.x_m = event.xdata
                self.y_m = event.ydata
                self.dot.set_data([], [])
                self.dot.axes.draw_artist(self.dot)
                self.dot.set_animated(False)
                self.background = None

    def onRelease(self, event):
        """."""
        if event.inaxes:
            try:
                dot, _ = self.vicinity(event.xdata, event.ydata)
            except TypeError:
                # no vicinity at all
                # pass
                self.x_r = event.xdata
                self.y_r = event.ydata
                self.dot.set_data([], [])
            else:
                # if dot is not None:
                self.x_r = dot[0]
                self.y_r = dot[1]
                self.dot.set_data([], [])
                self.dot.axes.draw_artist(self.dot)
                self.dot.set_animated(False)
                self.background = None
                self.figure.canvas.draw()


    # def onRelease(self, event):
    #     """."""
    #     if event.inaxes:
    #         try:
    #             dot, _ = self.vicinity(event.xdata, event.ydata)
    #             if dot is not None:
    #                 self.x_r = dot[0]
    #                 self.y_r = dot[1]
    #             else:
    #                 self.x_r = None
    #                 self.y_r = None
    #         except TypeError:
    #             # TypeError: pressing the button was not in the vicinity of a gridline
    #             pass
    # def onPress(self, event):
    #     """."""
    #     fix = self.transform(0, -15)
    #     # aim: move cursor here from every point clicked on canvas
    #     print("HEIGHT", self.height)
    #     print("CENTER at", fix)
    #
    #     # the posisitons of click in coordinate system
    #     x = event.xdata
    #     y = event.ydata
    #     # the position of the "click" event
    #     e_pix = QPoint(*self.transform(x, y))
    #     print("event position", e_pix, x, y)
    #
    #     # the current cursor position on the screen when in the drawing area
    #     s_pix = self.gimod.cursor().pos()
    #     print("screen position BEFORE click", s_pix)
    #
    #     # the delta between those two
    #     delta = [s_pix.x() - e_pix.x(), s_pix.y() - (self.height - e_pix.y())]
    #     print("delta", delta)
    #
    #     cursor = QCursor()
    #     cursor.setPos(QPoint(delta[0] + fix[0], delta[1] + (self.height - fix[1])))
    #     # self.gimod.cursor().setPos(QPoint(delta[0] + fix[0], delta[1] + (self.height - fix[1])))
    #     # self.gimod.cursor().setPos(QPoint(delta[0] + fix[0], delta[1] + (self.height - fix[1])))
    #     # cursor.setPos(QPoint(e_pix[0], e_pix[1]))
    #     self.gimod.setCursor(cursor)
    #         # time.sleep(1)
    #     print("screen position AFTER click", self.gimod.cursor().pos())

    def transform(self, x, y):
        """Transform the given x-y-coordinates to pixel position."""
        # return self.figure.axis.transData.inverted().transform((x, y))
        return self.figure.axis.transData.transform((x, y))

    def vicinity(self, x, y, picker=10):
        """
        Calculate the distance between a set magnet and the clicked position.

        Parameters
        ----------
        x: float
            The x-position of the current mouse event
        y: float
            The y-position of the current mouse event
        picker: int [10]
            Sets the sensitive distance to snap from

        Returns
        -------
        tuple()
            A tuple holding the cartesian x,y-coordinates of the point that will be snapped to
        """
        # pixel holds the current cursor postion
        pixel = tuple(self.transform(x, y))
        # crossings are all possible positions of grid lines
        for pos in self.crossings:
            # distance:
            # dist = np.sqrt((pos[0] - pixel[0])**2 + (pos[1] - pixel[1])**2)
            # if dist <= picker:  # to say if it IS in the vicinity of a node
            #     return self.figure.axis.transData.inverted().transform(pos)
            dist_x = abs(pos[0] - pixel[0])
            dist_y = abs(pos[1] - pixel[1])
            color = '#ff0000'
            # dot_x, dot_y = pixel
            if dist_x <= picker and dist_y <= picker:
                # print("MOVED", pos[0], pos[1])
                self.parent.statusbar.showMessage("Locked X-Y-Axes", 1000)
                dot_x = pos[0]
                dot_y = pos[1]
                color = '#61ff00'

            # NOTE: 5 <= dist <= picker allows a 5 pixel radius around each
            # joint so that the junctions can be reached better
            elif 1 <= dist_x <= picker and dist_y > picker:
            # elif dist_x <= picker and dist_y > picker:
                # print(dist_x, dist_y)
                self.parent.statusbar.showMessage("Locked X-Axis", 1000)
                dot_x = pos[0]
                dot_y = pixel[1]
                # color = '#ff0000'
                # self.gimod.setCursor(QCursor.setPos(self.transform(dot_x, dot_y)))

            elif 1 <= dist_y <= picker and dist_x > picker:
            # elif dist_y <= picker and dist_x > picker:
                # print(dist_x, dist_y)
                self.parent.statusbar.showMessage("Locked Y-Axis", 1000)
                dot_x = pixel[0]
                dot_y = pos[1]
                # color = '#ff0000'
                # self.gimod.setCursor(QCursor.setPos(self.transform(dot_x, dot_y)))
            # elif dist_x > picker and dist_y > picker:
            #     print(dist_x, dist_y)
            #     dot_x = pixel[0]
            #     dot_y = pixel[1]
            #     color = 'none'

            if 'dot_x' and 'dot_y' in locals():
            # if dot_x is not None and dot_y is not None:
                # print("yay")
                # self.gimod.setCursor(QCursor.setPos(self.transform(dot_x, dot_y)))
                return self.figure.axis.transData.inverted().transform((dot_x, dot_y)), color
            # else:
            #     return (x, y), color
            # else:
            #     # this is needed when checking for possible ankers while drawing a polygon
            #     return None, None


if __name__ == '__main__':
    pass
