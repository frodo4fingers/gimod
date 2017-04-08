#!/usr/bin/env python
# encoding: UTF-8

from matplotlib.patches import Rectangle
# BUG: cant create world twice e.g. after undoing the creation due to false dimension it cant be done a second time... shame


class SpanWorld(object):

    def __init__(self, parent=None):
        # self.ax = plt.gca()
        self.parent = parent
        self.figure = self.parent.figure
        # empty rectangle
        self.rect = Rectangle((0, 0), 0, 0, fc='none', alpha=0.5, ec='blue')
        self.background = None
        self.figure.axis.add_patch(self.rect)
        self.onPress = self.onPress

    def connect(self):
        self.cidP = self.figure.canvas.mpl_connect("button_press_event", self.onPress)
        self.cidM = self.figure.canvas.mpl_connect("motion_notify_event", self.onMotion)
        self.cidR = self.figure.canvas.mpl_connect("button_release_event", self.onRelease)

    def disconnect(self):
        self.figure.canvas.mpl_disconnect(self.cidP)
        self.figure.canvas.mpl_disconnect(self.cidM)
        self.figure.canvas.mpl_disconnect(self.cidR)

    def onPress(self, event):
        if event.button is 1:
            self.xP = event.xdata
            self.yP = event.ydata
            self.rect.set_animated(True)
            self.figure.canvas.draw()
            self.background = self.figure.canvas.copy_from_bbox(self.rect.axes.bbox)
            self.rect.axes.draw_artist(self.rect)
            self.figure.canvas.blit(self.rect.axes.bbox)

    def onMotion(self, event):
        if event.inaxes != self.rect.axes: return
        try:
            self.xM = event.xdata
            self.yM = event.ydata
            self.rect.set_width(self.xM - self.xP)
            self.rect.set_height(self.yM - self.yP)
            self.rect.set_xy((self.xP, self.yP))

            self.figure.canvas.restore_region(self.background)
            self.rect.axes.draw_artist(self.rect)
            self.figure.canvas.blit(self.rect.axes.bbox)

        except (AttributeError, TypeError):
            pass

    def onRelease(self, event):
        try:
            self.xR = event.xdata
            self.yR = event.ydata
            self.rect.set_width(0)
            self.rect.set_height(0)
            self.rect.set_xy((0, 0))
            self.rect.axes.draw_artist(self.rect)
            self.rect.set_animated(False)
            self.background = None
            self.figure.canvas.draw()
            self.parent.printCoordinates(self.xP, self.yP, self.xR, self.yR, form='World')

        except AttributeError:
            pass


if __name__ == '__main__':
    pass
