import wx
import numpy as np
import cv2
from wx.lib.scrolledpanel import ScrolledPanel
from pandas import DataFrame
from PIL import Image
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from matplotlib.figure import Figure
from wx.lib.floatcanvas import FloatCanvas
from wx.lib.floatcanvas.FCObjects import ScaledBitmap, Rectangle, Bitmap, Line
from ..model.ui_set import UiRectControl
FilePath = ''
class MyFrame(wx.Frame):
############################################################################################################################
    def __init__(self):
        super().__init__(parent=None, title="Mizuho", size=(1280, 800))
        self.panel = wx.ScrolledWindow(parent=self)
        self.panel.SetScrollbars(1, 1, 1, 1000)
        self.panel.SetScrollRate(0,10)

        self.PlotPanel = wx.Panel(self.panel, id=wx.ID_ANY, size=(600, 400), pos=(50, 100))
        self.PlotCanvas = FloatCanvas.FloatCanvas(self.PlotPanel, -1, size=(600, 400), BackgroundColor='black')



############################################################################################################################
class App(wx.App):
    def OnInit(self):
        frame = MyFrame()
        frame.Show()
        return True

if __name__ == '__main__':
    app = App()
    app.MainLoop()