#!/usr/bin/env python
# encoding: UTF-8


class DraggablePoint():
    """
    thank you very much:
    http://stackoverflow.com/questions/21654008/matplotlib-drag-overlapping-points-interactively
    """
    lock = None  # only one can be animated at a time

    def __init__(self, point=None, marker=None, center=None):
        # print("dp init")
        self.point = point
        self.press = None
        self.background = None
        self.center = center
        self.marker = marker
        self.params = (self.marker, self.center)
        self.dict = {}
        self.on_press = self.on_press

    def connect(self):
        """
            connect to all the events we need
        """
        self.cidpress = self.point.figure.canvas.mpl_connect('button_press_event', self.on_press)
        self.cidrelease = self.point.figure.canvas.mpl_connect('button_release_event', self.on_release)
        self.cidmotion = self.point.figure.canvas.mpl_connect('motion_notify_event', self.on_motion)

    def on_press(self, event):
        # if press out ouf point boundary
        if event.inaxes != self.point.axes:
            return
        # if more than one object oculd be moved
        if DraggablePoint.lock is not None:
            return
        contains, attrd = self.point.contains(event)
        if not contains:
            return
        self.press = (self.point.center), event.xdata, event.ydata
        DraggablePoint.lock = self
        # draw everything but the selected rectangle and store the pixel buffer
        canvas = self.point.figure.canvas
        axes = self.point.axes
        self.point.set_animated(True)
        canvas.draw()
        self.background = canvas.copy_from_bbox(self.point.axes.bbox)
        # now redraw just the rectangle
        axes.draw_artist(self.point)
        # and blit just the redrawn area
        canvas.blit(axes.bbox)

    def on_motion(self, event):
        if DraggablePoint.lock is not self:
            return
        if event.inaxes != self.point.axes:
            return
        self.point.center, xpress, ypress = self.press
        dx = event.xdata - xpress
        dy = event.ydata - ypress
        self.point.center = (self.point.center[0]+dx, self.point.center[1]+dy)

        canvas = self.point.figure.canvas
        axes = self.point.axes
        # restore the background region
        canvas.restore_region(self.background)
        # redraw just the current rectangle
        axes.draw_artist(self.point)
        # blit just the redrawn area
        canvas.blit(axes.bbox)

    def on_release(self, event):
        """
            on release we reset the press data
        """
        if DraggablePoint.lock is not self:
            return
        self.press = None
        DraggablePoint.lock = None
        # turn off the rect animation property and reset the background
        self.point.set_animated(False)
        self.background = None
        # redraw the full figure
        self.point.figure.canvas.draw()
        self.center = event.xdata, event.ydata
        # return self.marker, self.center
        self.returnValue()

    def returnValue(self):
        """
        added by myself to get the final marker position after movement out of the class objects
        """
        self.dict[self.marker] = self.point.center
        return self.dict

    def disconnect(self):
        """
            disconnect all the stored connection ids
        """
        self.point.figure.canvas.mpl_disconnect(self.cidpress)
        self.point.figure.canvas.mpl_disconnect(self.cidrelease)
        self.point.figure.canvas.mpl_disconnect(self.cidmotion)
