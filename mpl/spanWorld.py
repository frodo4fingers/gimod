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
        self.cid_p = self.figure.canvas.mpl_connect("button_press_event", self.onPress)
        self.cid_m = self.figure.canvas.mpl_connect("motion_notify_event", self.onMotion)
        self.cid_r = self.figure.canvas.mpl_connect("button_release_event", self.onRelease)

    def disconnect(self):
        self.figure.canvas.mpl_disconnect(self.cid_p)
        self.figure.canvas.mpl_disconnect(self.cid_m)
        self.figure.canvas.mpl_disconnect(self.cid_r)

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
            self.figure.canvas.draw()
            self.parent.printCoordinates(self.x_p, self.y_p, self.x_r, self.y_r, form='World')

        except AttributeError:
            pass


if __name__ == '__main__':
    pass
