#!/usr/bin/env python
# encoding: UTF-8

from matplotlib.patches import Circle
import numpy as np


class SpanCircle():

    def __init__(self, plot):
        # super(SpanCircle, self).__init__()
        self.figure = plot
        # introduce empty circle to start with
        self.circle = Circle((0, 0), 0, fc="none", ec="black")
        self.background = None
        self.figure.axis.add_patch(self.circle)
        self.released = False
        self.onPress = self.onPress

    def distance(self):
        return round(np.sqrt((self.x_m - self.x_p)**2 + (self.y_m - self.y_p)**2), 2)

    def connect(self):
        self.cid_p = self.figure.canvas.mpl_connect("button_press_event", self.onPress)
        self.cid_m = self.figure.canvas.mpl_connect("motion_notify_event", self.onMotion)
        self.cid_r = self.figure.canvas.mpl_connect("button_release_event", self.onRelease)

    def disconnect(self):
        self.figure.canvas.mpl_disconnect(self.cid_p)
        self.figure.canvas.mpl_disconnect(self.cid_m)
        self.figure.canvas.mpl_disconnect(self.cid_r)

    def onPress(self, event):
        self.released = False
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
        self.released = True
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
            self.figure.canvas.draw()
            # self.getValues()

        except AttributeError:
            pass

    def getValues(self):
        return self.x_p, self.y_p, self.distance()

    def state(self):
        return self.released


if __name__ == "__main__":
    pass
