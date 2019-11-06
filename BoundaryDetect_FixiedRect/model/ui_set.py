from wx.lib.floatcanvas.FCObjects import Circle, Line, Rectangle

from .data import AnalysisData


class SampleImgInteractionSet():

    def __init__(self):
        self.SpecifiedArea = UiRectControl()
        self.AnalysisArea = UiCrossControl()

    def UpdateWholeCoordinates(self, bitmap):
        self.SpecifiedArea.UpdateControls(bitmap)
        self.SpecifiedArea.UpdateVisuals()

        self.AnalysisArea.UpdateControls()
        self.AnalysisArea.UpdateVisuals(self.SpecifiedArea.StartCircle.XY, self.SpecifiedArea.EndCircle.XY)

    def UpdateSpecifiedRect(self):
        self.SpecifiedArea.UpdateVisuals()

    def UpdateAnalyzeLines(self):
        self.AnalysisArea.UpdateVisuals(self.SpecifiedArea.StartCircle.XY, self.SpecifiedArea.EndCircle.XY)

    def GetVisualOnlyObjects(self):
        return [
            self.SpecifiedArea.Rect,
            self.AnalysisArea.HorizontalLine,
            self.AnalysisArea.VerticalLine
        ]

    def GetInteractionObjects(self):
        return [
            self.SpecifiedArea.StartCircle,
            self.SpecifiedArea.EndCircle,
            self.AnalysisArea.CenterCircle
        ]


class UiRectControl():

    def __init__(self):
        self.StartCircle = Circle((0, 0), 10, LineColor="Red", FillColor="Red")
        #self.EndCircle = Circle((0, 0), 10, LineColor="Red", FillColor="Red")
        self.Rect = Rectangle((0, 0), (0, 0), LineColor="Red")

    def UpdateControls(self, bitmap):
        w, h = bitmap.Width, bitmap.Height
        self.StartCircle.XY = (-w / 2, h / 2)
        #self.EndCircle.XY = (w / 2, -h / 2)

    def UpdateControls2(self, StartXY, EndXY):
        self.StartCircle.XY = StartXY
        #self.EndCircle.XY = EndXY

    def UpdateVisuals(self, W, H):
        x1, y1 = self.StartCircle.XY
        x2, y2 = (x1+W, y1-H)
        newOrigin = (min(x1, x2), min(y1, y2))
        newOrigin = (min(x1, x2), min(y1, y2))
        newSize = (abs(x2 - x1), abs(y2 - y1))
        self.Rect.SetShape(newOrigin, newSize)


class UiCrossControl():
    def __init__(self):
        self.CenterCircle = Circle((0, 0), 10, LineColor="Green", FillColor="Green")
        self.HorizontalLine = Line(((0, 0), (0, 0)), LineColor="Green")
        self.VerticalLine = Line(((0, 0), (0, 0)), LineColor="Green")

    def UpdateControls(self):
        self.CenterCircle.XY = (0, 0)

    def UpdateVisuals(self, pt1, pt2):
        x1, y1 = pt1
        x2, y2 = pt2
        xa, ya = self.CenterCircle.XY
        self.HorizontalLine.Points = ((x1, ya), (x2, ya))
        self.VerticalLine.Points = ((xa, y1), (xa, y2))
