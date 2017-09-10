#!/usr/bin/env python
# encoding: UTF-8

from matplotlib.patches import Circle
import numpy as np


class SpanCircle(object):

    def __init__(self, parent=None):
        # super(SpanCircle, self).__init__()
        self.parent = parent
        self.figure = self.parent.figure
        # introduce empty circle to start with
        self.circle = Circle((0, 0), 0, fc='none', ec='blue')
        self.background = None
        self.figure.axis.add_patch(self.circle)
        self.onPress = self.onPress

    def distance(self):
        return round(np.sqrt((self.x_m - self.x_p)**2 + (self.y_m - self.y_p)**2), 2)

    def connect(self):
        self.cid_p = self.figure.canvas.mpl_connect('button_press_event', self.onPress)
        self.cid_m = self.figure.canvas.mpl_connect('motion_notify_event', self.onMotion)
        self.cid_r = self.figure.canvas.mpl_connect('button_release_event', self.onRelease)

    def disconnect(self):
        self.figure.canvas.mpl_disconnect(self.cid_p)
        self.figure.canvas.mpl_disconnect(self.cid_m)
        self.figure.canvas.mpl_disconnect(self.cid_r)

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
            # inconsistent mpl stuff
            self.circle.center = (0, 0)
            self.circle.set_radius(0)
            self.circle.axes.draw_artist(self.circle)
            # set back variables
            self.circle.set_animated(False)
            self.background = None
            self.figure.canvas.draw()
            self.sendToBuilder()

        except AttributeError:
            pass

    def sendToBuilder(self):
        # TODO: IF necessary the circle needs to be rotated, so that the point where the click is released lies on the edge!
        # if self.parent.acn_magnetizePoly.isChecked() is True:
        #     if self.parent.mp.x_m is not None:
        #         self.x_m = self.parent.mp.x_m
        #         self.y_m = self.parent.mp.y_m
        #
        #     if self.parent.mp.x_p is not None:
        #         self.x_p = self.parent.mp.x_p
        #         self.y_p = self.parent.mp.y_p

        self.parent.printCoordinates(self.x_p, self.y_p, self.distance(), None, form='Circle')


if __name__ == '__main__':
    pass
