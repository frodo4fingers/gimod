#!/usr/bin/env python
# encoding: UTF-8


class SpanLine(object):

    def __init__(self, parent=None):
        # super(SpanLine, self).__init__(parent)
        self.parent = parent
        self.figure = self.parent.figure
        # introduce empty line to start with
        line, = self.figure.axis.plot([0], [0], c='blue')
        self.x_p = []
        self.y_p = []
        self.line = line
        self.clicker = -1
        self.onPress = self.onPress

    def connect(self):
        self.cid_p = self.figure.canvas.mpl_connect('button_press_event', self.onPress)
        self.cid_r = self.figure.canvas.mpl_connect('button_release_event', self.onRelease)

    def disconnect(self):
        self.figure.canvas.mpl_disconnect(self.cid_p)
        self.figure.canvas.mpl_disconnect(self.cid_r)

    def onPress(self, event):
        if event.button is 1:
            self.x_p.append(event.xdata)
            self.y_p.append(event.ydata)
            self.line.set_data(self.x_p, self.y_p)
            self.figure.canvas.draw()
            self.clicker += 1

    def onRelease(self, event):
        if self.clicker > 0:
            self.line.set_data([0], [0])
            self.parent.printCoordinates(self.x_p[self.clicker - 1], self.y_p[self.clicker - 1], self.x_p[self.clicker], self.y_p[self.clicker], form="Line")


if __name__ == '__main__':
    pass
