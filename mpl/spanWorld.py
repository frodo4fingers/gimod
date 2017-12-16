#!/usr/bin/env python
# encoding: UTF-8

from matplotlib.patches import Rectangle


class SpanWorld():
    """Provide the visualization for creating a PolyWorld."""

    def __init__(self, parent=None):
        """
        Initialize all important variables for matplotlib drawing.

        Parameters
        ----------
        parent: :class:`core.builder.Builder`
        """
        self.parent = parent
        self.figure = self.parent.figure
        # empty rectangle
        self.rect = Rectangle((0, 0), 0, 0, fc='none', alpha=0.5, ec='blue')
        self.background = None
        self.figure.axis.add_patch(self.rect)
        self.onPress = self.onPress

    def connect(self):
        """Connect all events needed for line drawing and 'preview'."""
        self.cid_p = self.figure.canvas.mpl_connect("button_press_event", self.onPress)
        self.cid_m = self.figure.canvas.mpl_connect("motion_notify_event", self.onMotion)
        self.cid_r = self.figure.canvas.mpl_connect("button_release_event", self.onRelease)

    def disconnect(self):
        """Disconnect all the stored connection ids."""
        self.figure.canvas.mpl_disconnect(self.cid_p)
        self.figure.canvas.mpl_disconnect(self.cid_m)
        self.figure.canvas.mpl_disconnect(self.cid_r)

    def onPress(self, event):
        """Collect the data of the starting corner of the rectangle."""
        if event.inaxes != self.rect.axes:
            return
        if event.button is 1:  # left mouse button
            self.x_p = event.xdata
            self.y_p = event.ydata
            if self.parent.parent.toolBar.acn_magnetizeGrid.isChecked():
                self.x_p = self.parent.grid.x_m
                self.y_p = self.parent.grid.y_m
            self.rect.set_animated(True)
            self.figure.canvas.draw()
            self.background = self.figure.canvas.copy_from_bbox(self.rect.axes.bbox)
            self.rect.axes.draw_artist(self.rect)
            self.figure.canvas.blit(self.rect.axes.bbox)

    def onMotion(self, event):
        """Resize the helper rectangle while spanning."""
        if event.inaxes != self.rect.axes:
            return
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
        """Restore the canvas and empty the rectangles data."""
        if event.inaxes != self.rect.axes:
            return
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
            # send rectangle data to builder after check if the cursor postion
            # was grapped by the magnetized grid
            if self.parent.parent.toolBar.acn_magnetizeGrid.isChecked():
                # if self.parent.grid.x_r is not None:
                self.x_r = self.parent.grid.x_m
                self.y_r = self.parent.grid.y_m

                # if self.parent.grid.x_p is not None:
                #     self.x_p = self.parent.grid.x_p
                #     self.y_p = self.parent.grid.y_p

            self.parent.printCoordinates(self.x_p, self.y_p, self.x_r, self.y_r, form='World')
        except AttributeError:
            pass


if __name__ == '__main__':
    pass
