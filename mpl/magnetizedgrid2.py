from matplotlib.lines import Line2D
# from numpy import allclose
import numpy as np


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

    def __init__(self, parent):
        """Initialize the important variables."""
        self.figure = parent.figure
        self.parent = parent
        dot, = self.figure.axis.plot([], [], 'o', c='#ff0000')
        self.dot = dot
        self.grid()
        self.onMotion = self.onMotion

    def connect(self):
        """."""
        self.cid_p = self.figure.canvas.mpl_connect('button_press_event', self.onPress)
        self.cid_m = self.figure.canvas.mpl_connect('motion_notify_event', self.onMotion)
        self.cid_r = self.figure.canvas.mpl_connect('button_release_event', self.onRelease)

    def disconnect(self):
        """."""
        try:
            self.figure.canvas.mpl_disconnect(self.cid_p)
            self.figure.canvas.mpl_disconnect(self.cid_m)
            self.figure.canvas.mpl_disconnect(self.cid_r)
        except AttributeError:
            # bc the grid might never be magnetized, thus not having any cid to disconnect
            pass

    def disable(self):
        """."""
        # for line in self.all_xlines + self.all_ylines:
        #     line.set_data([], [])
        # disable the grid
        self.figure.axis.grid(False)
        self.figure.canvas.draw()

    def grid(self):
        """."""
        # set the actual grid
        self.figure.axis.grid(True)
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
                if dot is not None:
                    self.x_p = dot[0]
                    self.y_p = dot[1]
                else:
                    self.x_p = None
                    self.y_p = None
            except TypeError:
                # TypeError: pressing the button was not in the vicinity of a gridline
                pass

            # # print(event.xdata, event.ydata, dot)
            # except TypeError:
            #     # TypeError: pressing the button was not in the vicinity of a gridline
            #     pass
            # else:

    def onMotion(self, event):
        """."""
        if event.inaxes:  # meaning within the plotting area
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
                self.dot.set_data([], [])
                self.dot.axes.draw_artist(self.dot)
                self.dot.set_animated(False)
                self.background = None

    def onRelease(self, event):
        """."""
        if event.inaxes:
            try:
                dot, _ = self.vicinity(event.xdata, event.ydata)
                if dot is not None:
                    self.x_r = dot[0]
                    self.y_r = dot[1]
                else:
                    self.x_r = None
                    self.y_r = None
            except TypeError:
                # TypeError: pressing the button was not in the vicinity of a gridline
                pass

            # # print(event.xdata, event.ydata, dot)
            # except TypeError:
            #     pass
            # else:

    def vicinity(self, x, y, picker=15):
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
        pixel = tuple(self.figure.axis.transData.transform((x, y)))
        # crossings are all possible positions of grid lines
        for pos in self.crossings:
            # distance:
            # dist = np.sqrt((pos[0] - pixel[0])**2 + (pos[1] - pixel[1])**2)
            # if dist <= picker:  # to say if it IS in the vicinity of a node
            #     return self.figure.axis.transData.inverted().transform(pos)
            dist_x = abs(pos[0] - pixel[0])
            dist_y = abs(pos[1] - pixel[1])

            # dot_x, dot_y = pixel
            if dist_x <= picker and dist_y <= picker:
                self.parent.statusbar.showMessage("Locked X-Y-Axes", 1000)
                dot_x = pos[0]
                dot_y = pos[1]
                color = '#61ff00'

            # NOTE: 5 <= dist <= picker allows a 5 pixel radius around each
            # joint so that the junctions can be reached better
            elif 5 <= dist_x <= picker and dist_y > picker:
                self.parent.statusbar.showMessage("Locked X-Axis", 1000)
                dot_x = pos[0]
                dot_y = pixel[1]
                color = '#ff0000'

            elif 5 <= dist_y <= picker and dist_x > picker:
                self.parent.statusbar.showMessage("Locked Y-Axis", 1000)
                dot_x = pixel[0]
                dot_y = pos[1]
                color = '#ff0000'

            if 'dot_x' and 'dot_y' in locals():
                # print("yay")
                return self.figure.axis.transData.inverted().transform((dot_x, dot_y)), color
            # else:
            #     # this is needed when checking for possible ankers while drawing a polygon
            #     return None, None


if __name__ == '__main__':
    pass
