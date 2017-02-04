import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle


class SpanRectangle():
    def __init__(self, plot):
        # self.ax = plt.gca()
        self.plot = plot
        # empty rectangle
        self.rect = Rectangle((0, 0), 0, 0, fc="g", alpha=0.5, ec="none")
        self.background = None
        self.ax.add_patch(self.rect)

    def connect(self):
        self.cid_p = self.plot.canvas.mpl_connect("button_press_event", self.onPress)
        self.cid_m = self.plot.canvas.mpl_connect("motion_notify_event", self.onMotion)
        self.cid_r = self.plot.canvas.mpl_connect("button_release_event", self.onRelease)

    def disconnect(self):
        self.plot.canvas.mpl_disconnect(self.cid_p)
        self.plot.canvas.mpl_disconnect(self.cid_m)
        self.plot.canvas.mpl_disconnect(self.cid_r)

    def onPress(self, event):
        if event.button is 1:
            self.x_p = event.xdata
            self.y_p = event.ydata
            self.rect.set_animated(True)
            self.plot.canvas.draw()
            self.background = self.plot.canvas.copy_from_bbox(self.rect.axes.bbox)
            self.rect.axes.draw_artist(self.rect)
            self.plot.canvas.blit(self.rect.axes.bbox)

    def onMotion(self, event):
        if event.inaxes != self.rect.axes: return
        try:
            self.x_m = event.xdata
            self.y_m = event.ydata
            self.rect.set_width(self.x_m - self.x_p)
            self.rect.set_height(self.y_m - self.y_p)
            self.rect.set_xy((self.x_p, self.y_p))

            self.plot.canvas.restore_region(self.background)
            self.rect.axes.draw_artist(self.rect)
            self.plot.canvas.blit(self.rect.axes.bbox)

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
            self.plot.canvas.draw()

        except AttributeError:
            pass

# a = SpanRectangle()
# a.connect()
# plt.show()
