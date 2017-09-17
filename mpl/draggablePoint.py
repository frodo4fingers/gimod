#!/usr/bin/env python
# encoding: UTF-8


class DraggablePoint():
    """
    Provide the functionality to plot a circle for each polygon at the position
    of the region marker. Thank you very much:
    http://stackoverflow.com/questions/21654008/matplotlib-drag-overlapping-points-interactively

    Todo
    ----
    Make points depend on pixel width not a "random size"
    """
    lock = None  # only one can be animated at a time

    def __init__(self, point=None, marker=None, center=None):
        """
        Initialize all necessary variables.

        Parameters
        ----------
        point: <matplotlib.patches.Circle>
            A dot marking the position of the region marker
        marker: int
            Integer representing the marker region
        center: RVector3
            Position of the region marker
        """
        self.point = point
        self.press = None
        self.background = None
        self.center = center
        self.marker = marker
        self.params = (self.marker, self.center)
        self.dict = {}
        self.onPress = self.onPress

    def connect(self):
        """Connect to all the events needed."""
        self.cid_p = self.point.figure.canvas.mpl_connect(
            'button_press_event', self.onPress)
        self.cid_r = self.point.figure.canvas.mpl_connect(
            'button_release_event', self.onRelease)
        self.cid_m = self.point.figure.canvas.mpl_connect(
            'motion_notify_event', self.onMotion)

    def disconnect(self):
        """Disconnect all the stored connection ids."""
        self.point.figure.canvas.mpl_disconnect(self.cid_p)
        self.point.figure.canvas.mpl_disconnect(self.cid_r)
        self.point.figure.canvas.mpl_disconnect(self.cid_m)

    def onPress(self, event):
        """Start the process to drag it along if a dot is hit."""
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

    def onMotion(self, event):
        """Move the dot under the cursor and let it be dragged until release."""
        if DraggablePoint.lock is not self:
            return
        if event.inaxes != self.point.axes:
            return
        self.point.center, xpress, ypress = self.press
        dx = event.xdata - xpress
        dy = event.ydata - ypress
        self.point.center = (
            self.point.center[0] + dx, self.point.center[1] + dy)

        canvas = self.point.figure.canvas
        axes = self.point.axes
        # restore the background region
        canvas.restore_region(self.background)
        # redraw just the current rectangle
        axes.draw_artist(self.point)
        # blit just the redrawn area
        canvas.blit(axes.bbox)

    def onRelease(self, event):
        """Reset the press data on release."""
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
        Get the final position of the marker dot out of the object.

        Returns
        -------
        dict()
            Containing the dot's center (x, y) with region marker as key
        """
        self.dict[self.marker] = self.point.center
        return self.dict


if __name__ == '__main__':
    pass
