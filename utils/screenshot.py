import os
import wx
from desktopmagic.screengrab_win32 import getRectAsImage

class SelectableFrame(wx.Frame):

    c1 = None
    c2 = None

    def __init__(self, parent=None, id=-1, title=""):

        displays = (wx.Display(i) for i in range(wx.Display.GetCount()))
        sizes = [display.GetGeometry().GetSize() for display in displays]
        totalsize = sizes[0].__add__(sizes[1])

        wx.Frame.__init__(self, parent, id, title, size=totalsize)
        self.panel = wx.Panel(self, size=totalsize)

        self.panel.Bind(wx.EVT_MOTION, self.OnMouseMove)
        self.panel.Bind(wx.EVT_LEFT_DOWN, self.OnMouseDown)
        self.panel.Bind(wx.EVT_LEFT_UP, self.OnMouseUp)
        self.panel.Bind(wx.EVT_PAINT, self.OnPaint)

        self.SetCursor(wx.StockCursor(wx.CURSOR_CROSS))

        self.SetTransparent(50)

    def OnMouseMove(self, event):
        if event.Dragging() and event.LeftIsDown():
            self.c2 = event.GetPosition()
            self.Refresh()

    def OnMouseDown(self, event):
        self.c1 = event.GetPosition()

    def OnMouseUp(self, event):
        self.SetCursor(wx.StockCursor(wx.CURSOR_ARROW))
        x1, y1, x2, y2 = (self.c1.x, self.c1.y, self.c2.x, self.c2.y)
        fileName = os.path.join(os.environ['TEMP'], 'screenshot.png')
        rect256 = getRectAsImage((x1, y1, x2, y2))
        rect256.save(fileName, format='png')
        self.Close()

    def OnPaint(self, event):
        if self.c1 is None or self.c2 is None: return

        dc = wx.PaintDC(self.panel)
        dc.SetPen(wx.Pen('red', 1))

        dc.DrawRectangle(self.c1.x, self.c1.y, self.c2.x - self.c1.x, self.c2.y - self.c1.y)


class ScreenShot(wx.App):

    def OnInit(self):
        self.frame = SelectableFrame()
        self.frame.Show(True)
        self.SetTopWindow(self.frame)
        return True

    def getCoordinates(self):
        return (self.frame.c1.x, self.frame.c1.y, self.frame.c2.x, self.frame.c2.y)
