#!/usr/bin/env python
# encoding: UTF-8

from matplotlib.lines import Line2D


class SpanPoly(object):

    def __init__(self, parent=None):
        self.parent = parent
        self.figure = parent.figure
        motionLine, = self.figure.axis.plot([0], [0], lw=0.5)
        line, = self.figure.axis.plot([0], [0], c='black')
        self.x = []
        self.y = []
        self.line = line
        self.motionLine = motionLine
        self.background = None
        self.onPress = self.onPress

    def connect(self):
        self.cid_p = self.figure.canvas.mpl_connect('button_press_event', self.onPress)
        self.cid_dp = self.figure.canvas.mpl_connect('button_press_event', self.onPress)
        self.cid_m = self.figure.canvas.mpl_connect('motion_notify_event', self.onMotion)
        self.cid_r = self.figure.canvas.mpl_connect('button_release_event', self.onRelease)

    def disconnect(self):
        self.figure.canvas.mpl_disconnect(self.cid_p)
        self.figure.canvas.mpl_disconnect(self.cid_dp)
        self.figure.canvas.mpl_disconnect(self.cid_m)
        self.figure.canvas.mpl_disconnect(self.cid_r)

    def onPress(self, event):
        # reset line for next click
        self.motionLine.set_data([0], [0])
        self.background = None
        self.motionLine.set_animated(False)
        self.figure.canvas.draw()

        if event.button is 1:
            # BUG: after creating ONE polygon by hand the second one wont draw the already clicked parts of itself
            if event.dblclick:  # close polygon
                self.parent.printPolygon([[self.x[i], self.y[i]] for i in range(len(self.x))])
                self.x = []
                self.y = []
            else:  # append point to polygon
                self.x.append(event.xdata)
                self.y.append(event.ydata)
                self.line.set_data(self.x, self.y)
                # self.line.axes.draw_artist(self.line)
                self.figure.canvas.draw()

    def onRelease(self, event):
        try:  # to drag the line with the cursor
            self.motionLine.set_animated(True)
            self.background = self.figure.canvas.copy_from_bbox(self.motionLine.axes.bbox)
            self.motionLine.axes.draw_artist(self.motionLine)
            self.figure.canvas.blit(self.motionLine.axes.bbox)
        except (IndexError, TypeError):
            pass

    def onMotion(self, event):
        try:  # to draw this stuff
            self.motionLine.set_data((self.x[-1], event.xdata), (self.y[-1], event.ydata))
            self.figure.canvas.restore_region(self.background)
            self.motionLine.axes.draw_artist(self.motionLine)
            self.figure.canvas.blit(self.motionLine.axes.bbox)
        except (AttributeError, IndexError, TypeError):
            pass
