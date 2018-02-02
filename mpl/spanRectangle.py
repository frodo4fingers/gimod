#!/usr/bin/env python
# encoding: UTF-8

from matplotlib.patches import Rectangle
from .mplbase import MPLBase


class SpanRectangle(MPLBase):
    """Provide the visualization for creating a PolyRectangle."""

    def __init__(self, parent=None):
        """
        Initialize all important variables for matplotlib drawing.

        Parameters
        ----------
        parent: :class:`core.builder.Builder`
        """
        super(SpanRectangle, self).__init__(parent)
        self.gimod = parent.parent
        self.parent = parent
        self.figure = self.parent.figure
        # empty rectangle to start with
        self.rect = Rectangle((0, 0), 0, 0, fc='none', alpha=0.5, ec='lightblue')
        self.background = None
        self.figure.axis.add_patch(self.rect)
        self.onPress = self.onPress

    def onPress(self, event):
        """Collect the data of the starting corner of the rectangle."""
        print("rectangle press")
        if event.inaxes != self.rect.axes:
            return
        if event.button is 1:  # left mouse button
            self.x_p = event.xdata
            self.y_p = event.ydata
            if self.gimod.toolbar.acn_magnetizeGrid.isChecked():
                self.x_p = self.parent.grid.x_p
                self.y_p = self.parent.grid.y_p
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
            # set the data to the helper while spanning
            self.rect.set_width(self.x_m - self.x_p)
            self.rect.set_height(self.y_m - self.y_p)
            self.rect.set_xy((self.x_p, self.y_p))

            self.figure.canvas.restore_region(self.background)
            self.rect.axes.draw_artist(self.rect)
            self.figure.canvas.blit(self.rect.axes.bbox)
        except (AttributeError, TypeError):
            pass

    # def onRelease(self, event):
    #     """Restore the canvas and empty the rectangles data."""
    #     if event.inaxes != self.rect.axes:
    #         return
    #     try:
    #         self.x_r = event.xdata
    #         self.y_r = event.ydata
    #         if self.gimod.toolbar.acn_magnetizeGrid.isChecked():
    #             self.x_r = self.parent.grid.x_r
    #             self.y_r = self.parent.grid.y_r
    #         self.rect.set_width(0)
    #         self.rect.set_height(0)
    #         self.rect.set_xy((0, 0))
    #         self.rect.axes.draw_artist(self.rect)
    #         self.rect.set_animated(False)
    #         self.background = None
    #         self.figure.canvas.draw()
    #         self.sendToBuilder()
    #     except AttributeError:
    #         pass

    def onRelease(self, event):
        """Restore the canvas and empty the rectangles data."""
        print("rectangle release")
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

            # send rectangle data to builder after check if the cursor postion
            # was grapped by the magnetized grid
            if self.gimod.toolbar.acn_magnetizeGrid.isChecked():
                # if self.parent.grid.x_r is not None:
                self.x_r = self.parent.grid.x_r
                self.y_r = self.parent.grid.y_r

                # if self.parent.grid.x_p is not None:
                #     self.x_p = self.parent.grid.x_p
                #     self.y_p = self.parent.grid.y_p
            # draw the actually spanned rectangle
            rect = Rectangle((0, 0), 0, 0, fc='none', lw=1, ec='lightblue')
            rect.set_width(self.x_r - self.x_p)
            rect.set_height(self.y_r - self.y_p)
            rect.set_xy((self.x_p, self.y_p))
            # self.drawToCanvas(rect)
            self.figure.canvas.draw()
            # self.disconnect()
            # self.parent.printCoordinates(self.x_p, self.y_p, self.x_r, self.y_r, form='Rectangle')
            self.parent.storeMPLPaths(rect, ['Rectangle', [self.x_p, self.y_p, self.x_r, self.y_r]])
            self.x_p = None
            self.y_p = None
            self.x_r = None
            self.y_r = None
        except AttributeError:
            pass

    # def sendToBuilder(self):
    #     """Send the rectangle data to :meth:`core.builder.Builder.printCoordinates`."""
    #     if self.gimod.toolbar.acn_magnetizePoly.isChecked():
    #         if self.parent.mp.x_r is not None:
    #             self.x_r = self.parent.mp.x_r
    #             self.y_r = self.parent.mp.y_r
    #
    #         if self.parent.mp.x_p is not None:
    #             self.x_p = self.parent.mp.x_p
    #             self.y_p = self.parent.mp.y_p
    #
    #     # if self.gimod.toolbar.acn_magnetizeGrid.isChecked():
    #     #     # if self.parent.grid.x_r is not None:
    #     #     self.x_r = self.parent.grid.x_m
    #     #     self.y_r = self.parent.grid.y_m
    #
    #         # if self.parent.grid.x_p is not None:
    #         #     self.x_p = self.parent.grid.x_p
    #         #     self.y_p = self.parent.grid.y_p
    #
    #     # self.parent.printCoordinates(self.x_p, self.y_p, self.x_r, self.y_r, form='Rectangle')
    #     self.parent.storeMPLPaths(['Rectangle', [self.x_p, self.y_p, self.x_r, self.y_r]])


if __name__ == '__main__':
    pass
