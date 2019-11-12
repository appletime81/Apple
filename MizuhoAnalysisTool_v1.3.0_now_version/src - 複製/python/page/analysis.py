from operator import xor

import numpy
from wx import (ALL, EVT_BUTTON, EVT_CHECKBOX, EVT_CHECKLISTBOX, EVT_RADIOBOX,
                EVT_SIZE, ID_OK, App, Bitmap, Image, Point, Rect, Size)
from wx.lib.floatcanvas import FCObjects, FloatCanvas
from wx.xrc import XRCCTRL, XmlResource, XmlResourceHandler
from wxmplot import PlotPanel

from ..helper import ColorListCtrlHelper, PtGridHelper
from ..model.data import AnalysisData
from ..model.ui_set import SampleImgInteractionSet
from ..util import CoordConvertUtil, CsvUtil, DialogUtil, ImgStatisticUtil
from .base import BasePanel


class AnalysisPanelHandler(XmlResourceHandler):

    def __init__(self, panel, *args, **kw):
        super().__init__(*args, **kw)

        self.panel = panel

    def CanHandle(self, node):
        return self.IsOfClass(node, "wxPanel") and node.GetAttribute('name') == 'root'

    def DoCreateResource(self):
        self.CreateChildren(self.panel)

        return self.panel

class AnalysisPanel(BasePanel):

    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)

        res = XmlResource('src/layout/panel_direct_analysis.xrc')
        res.InsertHandler(AnalysisPanelHandler(self))
        res.LoadPanel(None, "root")

        self.InitData()
        self.InitPanel()

    def InitData(self):
        self.dragObject = None
        self.dragStartPt = None

        self.analysisData = AnalysisData()
        self.sampleImgInteractionSet = SampleImgInteractionSet()
        
        self.logX = None
        self.logY = None

        self.graphDrewAxis = 0
        

    """
        UI Initialization
    """

    def InitPanel(self):
        self.InitMenuComponents()
        self.InitMsgComponents()
        self.InitBodyComponents()

    def InitMenuComponents(self):
        self.mainWindow = XRCCTRL(self, 'main_window')

        self.browseButton = XRCCTRL(self, 'button_browse')
        self.browseButton.Bind(EVT_BUTTON, self.OnBrowse)

        self.exportCsvButton = XRCCTRL(self, 'button_export_csv')
        self.exportCsvButton.Bind(EVT_BUTTON, self.OnExportCsv)

    def InitMsgComponents(self):
        self.msgPanel = XRCCTRL(self, 'msg_panel')

    def InitBodyComponents(self):
        self.InitImgInteractionComponents()
        self.InitAnalysisDataComponents()
        self.InitAnalysisGraphComponents()

    def InitImgInteractionComponents(self):
        self.samplePanel = XRCCTRL(self, 'panel_sample')
        self.samplePanel.Bind(EVT_SIZE, self.OnSampleCanvasSizeChanged)
        self.sampleCanvas = FloatCanvas.FloatCanvas(self.samplePanel, -1, size=self.samplePanel.GetSize())
        self.sampleCanvas.Bind(FloatCanvas.EVT_LEFT_UP, self.OnMouseLeftUp)
        self.sampleCanvas.Bind(FloatCanvas.EVT_MOTION, self.OnMouseMotion)
        self.sampleCanvas.Bind(FloatCanvas.EVT_MOUSEWHEEL, self.OnMouseWheel)

        self.enhancedImgCheckBox = XRCCTRL(self, 'enhanced_img_checkbox')
        self.enhancedImgCheckBox.Bind(EVT_CHECKBOX, self.OnEnhancedImgChecked)

        self.specifiedAreaGrid = XRCCTRL(self, 'grid_specified_area')
        PtGridHelper.SetupStartEnd(self.specifiedAreaGrid, self.OnSpecifiedAreaGridChanged)

        self.analysisCenterGrid = XRCCTRL(self, 'grid_analysis_center')
        PtGridHelper.SetupOne(self.analysisCenterGrid, self.OnAnalysisCenterGridChanged)

        self.logWidthGrid = XRCCTRL(self, 'grid_log_width')
        PtGridHelper.SetupOne(self.logWidthGrid, self.OnLogWidthGridChanged)

    def InitAnalysisDataComponents(self):
        self.xLogList = XRCCTRL(self, 'listctrl_x')

        self.yLogList = XRCCTRL(self, 'listctrl_y')

    def InitAnalysisGraphComponents(self):
        self.chartPanel = XRCCTRL(self, 'panel_chart')
        self.chartPanel.Bind(EVT_SIZE, self.OnChartSizeChanged)
        self.chart = PlotPanel(self.chartPanel, 
                                size=self.chartPanel.Size, 
                                dpi=100,
                                show_config_popup=False)
        self.chart.BuildPanel()

        self.graphAxisRadioBox = XRCCTRL(self, 'radiobox_graph_axis')
        self.graphAxisRadioBox.Bind(EVT_RADIOBOX, self.OnGraphDisplayConfigChanged)

        self.graphColorCheckListBox = XRCCTRL(self, 'checklistbox_graph_color')
        self.graphColorCheckListBox.Bind(EVT_CHECKLISTBOX, self.OnGraphDisplayConfigChanged)

    """
        UI Events
    """

    def OnBrowse(self, event):
        with DialogUtil.CreateLoadImgDialog(self) as fileDialog:
            if fileDialog.ShowModal() == ID_OK:
                path = fileDialog.GetPath()
                self.ImgPath = path
                self.ProcessSample(path)
                self.exportCsvButton.Enable()

    def OnExportCsv(self, event):
        with DialogUtil.CreateSaveCsvDialog(self) as fileDialog:
            if fileDialog.ShowModal() == ID_OK:
                path = fileDialog.GetPath()
                CsvUtil.ExportCSV(path, self.logX, self.logY)

    def OnSampleCanvasSizeChanged(self, event):
        self.sampleCanvas.Position = Point(0, 0)
        self.sampleCanvas.Size = self.samplePanel.Size

    def OnHitMark(self, object):
        self.dragObject = object

    def OnMouseLeftUp(self, event):
        # May encounter when double-clicking in file dialog
        if self.dragObject is None:
            return

        if not self.analysisData.IsEmpty():
            if self.dragObject is not self.sampleCanvas:
                self.GenerateAndDisplayNewLogs()

        self.dragObject = None
        self.dragStartPt = None

    def OnMouseMotion(self, event):
        newDragPt = event.GetPosition()

        if self.dragObject is not None:
            if self.dragStartPt is not None:
                delta = newDragPt - self.dragStartPt
                delta.y *= -1   # Y on canvas is opposite to window (this event)
                self.dragObject.Move(delta)
                self.FcObjCollisionDetection(self.dragObject)
                self.UpdateSampleDrawing()
                self.UpdateGridData(self.dragObject)
            self.dragStartPt = newDragPt

    def OnMouseWheel(self, event):
        wheelRotation = event.GetWheelRotation()
        zoom = 1.0 + wheelRotation / abs(wheelRotation) * 0.1
        self.sampleCanvas.Zoom(zoom, centerCoords="pixel")

    def OnEnhancedImgChecked(self, event):
        self.analysisData.IsUsingEnhancedImage = event.IsChecked()
        
        if not self.analysisData.IsEmpty():
            self.GenerateAndDisplayNewLogs()
            self.DisplayImageOnCanvas()

    def OnSpecifiedAreaGridChanged(self, event):
        col = event.GetCol()
        self.GridCollisionDetection(self.specifiedAreaGrid, col)
        self.UpdateSpecifiedAreaFromGrid(col)
        self.UpdateSampleDrawing()
        self.GenerateAndDisplayNewLogs()

    def OnAnalysisCenterGridChanged(self, event):
        self.GridCollisionDetection(self.analysisCenterGrid)
        self.UpdateAnalysisCenterFromGrid()
        self.UpdateSampleDrawing()
        self.GenerateAndDisplayNewLogs()

    def OnLogWidthGridChanged(self, event):
        self.analysisData.LogWidth = PtGridHelper.GetGridPoint(self.logWidthGrid)
        self.GenerateAndDisplayNewLogs()

    def OnGraphDisplayConfigChanged(self, event):
        self.DrawLogsOnChart()

    def OnChartSizeChanged(self, event):
        self.chart.Position = Point(0, 0)
        self.chart.Size = self.chartPanel.Size

    """
        UI-related methods
    """

    def ProcessSample(self, path):
        self.LoadSample(path)
        # Add markers with default position
        self.DisplayImageOnCanvas(isResetMarkers=True)
        self.enhancedImgCheckBox.SetValue(False)    # Reset enhanced checkbox
        self.UpdateSpecifiedAreaFromCanvas(0) # Start point
        self.UpdateSpecifiedAreaFromCanvas(1) # End point
        self.UpdateAnalysisCenterFromCanvas()
        self.SetInitialLogWidth()
        self.GenerateAndDisplayNewLogs()


    def LoadSample(self, path):
        image = Image(path)
        self.analysisData.InitWithImage(image)

    def DisplayImageOnCanvas(self, isResetMarkers=False):
        self.sampleCanvas.ClearAll()
        self.AddImageToCanvas()
        self.CalculateDataScreenScale()
        if isResetMarkers:
            self.sampleImgInteractionSet.UpdateWholeCoordinates(self.bitmap)
        self.AddMarkersToCanvas()
        self.sampleCanvas.Draw()

    def AddImageToCanvas(self):
        image = self.analysisData.GetTargetImage()
        bmpScreenHeight = self.sampleCanvas.Size.Height * 0.8  # Make circles easy to click on the corner
        self.bitmap = FCObjects.ScaledBitmap(Bitmap(image), (0, 0), bmpScreenHeight, Position="cc")  
        self.sampleCanvas.AddObject(self.bitmap)

    def CalculateDataScreenScale(self):
        image = self.analysisData.GetTargetImage()
        self.scaledBmpSize = Size(self.bitmap.Width, self.bitmap.Height)
        self.SetSampleDisplayScale(self.scaledBmpSize, image.GetSize())

    def SetSampleDisplayScale(self, scaledSize, imgSize):
        try:
            self.sampleDisplayScaleX = scaledSize.Width / imgSize.Width
            self.sampleDisplayScaleY = scaledSize.Height / imgSize.Height
        except BaseException:
            self.sampleDisplayScaleX = 1.0
            self.sampleDisplayScaleY = 1.0


    def AddMarkersToCanvas(self):
        visualHelpers = self.sampleImgInteractionSet.GetVisualOnlyObjects()
        self.sampleCanvas.AddObjects(visualHelpers)
        markers = self.sampleImgInteractionSet.GetInteractionObjects()
        self.sampleCanvas.AddObjects(markers)
        for item in markers:
            item.Bind(FloatCanvas.EVT_FC_LEFT_DOWN, self.OnHitMark)

    def FcObjCollisionDetection(self, obj):
        bitmapWidth = self.scaledBmpSize.Width
        bitmapHeight = self.scaledBmpSize.Height
        start = self.sampleImgInteractionSet.SpecifiedArea.StartCircle.XY
        end = self.sampleImgInteractionSet.SpecifiedArea.EndCircle.XY
        center = self.sampleImgInteractionSet.AnalysisArea.CenterCircle.XY
        
        if obj is self.sampleImgInteractionSet.SpecifiedArea.StartCircle:
            self.sampleImgInteractionSet.SpecifiedArea.StartCircle.XY = (
                sorted([-bitmapWidth / 2, start[0], center[0]])[1],
                sorted([bitmapHeight / 2, start[1], center[1]])[1]
            )
        elif obj is self.sampleImgInteractionSet.SpecifiedArea.EndCircle:
            self.sampleImgInteractionSet.SpecifiedArea.EndCircle.XY = (
                sorted([center[0], end[0], bitmapWidth / 2])[1],
                sorted([center[1], end[1], -bitmapHeight / 2])[1]
            )
        elif obj is self.sampleImgInteractionSet.AnalysisArea.CenterCircle:
            self.sampleImgInteractionSet.AnalysisArea.CenterCircle.XY = (
                sorted([start[0], center[0], end[0]])[1],
                sorted([start[1], center[1], end[1]])[1]
            )

    def GridCollisionDetection(self, grid, col=0):
        origin = (0, 0)
        image = self.analysisData.GetTargetImage()
        bmpSize = (image.Width, image.Height)
        start = PtGridHelper.GetGridPoint(self.specifiedAreaGrid)
        end = PtGridHelper.GetGridPoint(self.specifiedAreaGrid, col=1)
        center = PtGridHelper.GetGridPoint(self.analysisCenterGrid)

        if grid is self.specifiedAreaGrid:
            if col == 0:    # Start
                start = self.GetCollidedCoord(start, origin, center)
                PtGridHelper.SetGridPoint(self.specifiedAreaGrid, start[0], start[1], col)
                self.UpdateSpecifiedAreaData(col, start[0], start[1])
            else:   # End
                end = self.GetCollidedCoord(end, center, bmpSize)
                PtGridHelper.SetGridPoint(self.specifiedAreaGrid, end[0], end[1], col)
                self.UpdateSpecifiedAreaData(col, end[0], end[1])
        elif grid is self.analysisCenterGrid:
            center = self.GetCollidedCoord(center, start, end)
            PtGridHelper.SetGridPoint(self.analysisCenterGrid, center[0], center[1], col)
            self.analysisData.Center = center

    def GetCollidedCoord(self, center, minPt, maxPt):
        return (
            self.GetCollidedVal(center[0], minPt[0], maxPt[0]),
            self.GetCollidedVal(center[1], minPt[1], maxPt[1])
        )

    def GetCollidedVal(self, center, minVal, maxVal):
        if center < minVal:
            return minVal
        elif center > maxVal:
            return maxVal
        else:
            return center

    def SetInitialLogWidth(self):
        x, y = self.analysisData.LogWidth
        PtGridHelper.SetGridPoint(self.logWidthGrid, x, y)

    def GenerateAndDisplayNewLogs(self):
        self.ChangeDisplay(isCalculating=True)
        self.GenerateLogData()
        self.DisplayLogData()
        self.DrawLogsOnChart()
        self.ChangeDisplay(isCalculating=False)

    def ChangeDisplay(self, isCalculating):
        self.msgPanel.Show(isCalculating)
        self.mainWindow.Show(not isCalculating)

        if isCalculating:
            self.GenerateCalculatingMsg()

    def GenerateCalculatingMsg(self):
        self.Layout()   # Make layout correct for hidden UI components
        msgCanvas = FloatCanvas.FloatCanvas(self.msgPanel, -1, size=self.msgPanel.GetSize())
        text = FCObjects.Text("Calculating...", (0, 0), Size=24, Position="cc")
        msgCanvas.AddObject(text)
        msgCanvas.Draw(True)

    def GenerateLogData(self):
        self.GenerateDirectionalLogs(0)
        self.GenerateDirectionalLogs(1)

    def DisplayLogData(self):
        ColorListCtrlHelper.UpdateData(self.xLogList, self.logX)
        ColorListCtrlHelper.UpdateData(self.yLogList, self.logY)

    def DrawLogsOnChart(self):
        self.chart.clear()

        dataList = self.logX if self.graphAxisRadioBox.GetSelection() == 0 else self.logY
        if dataList is not None:
            x = [data[0] for data in dataList]
            print(x)
            colorIndex = [0, 1, 2]
            colors = ['red', 'green', 'blue']
            for index in colorIndex:
                if self.graphColorCheckListBox.IsChecked(index):
                    color = colors[index]
                    data = [data[index + 1] for data in dataList]
                    print(data)
                    self.chart.oplot(x, data, ymin=0, ymax=255, color=color, delay_draw=True)
                    # TODO: sth. wrong with legend after using delay_draw=True
            self.chart.draw()
            self.chart.unzoom_all()

    def UpdateSampleDrawing(self):
        self.sampleImgInteractionSet.UpdateSpecifiedRect()
        self.sampleImgInteractionSet.UpdateAnalyzeLines()
        self.sampleCanvas.Draw(True)

    def UpdateGridData(self, object):
        if object == self.sampleImgInteractionSet.SpecifiedArea.StartCircle:
            self.UpdateSpecifiedAreaFromCanvas(0)
        elif object == self.sampleImgInteractionSet.SpecifiedArea.EndCircle:
            self.UpdateSpecifiedAreaFromCanvas(1)
        elif object == self.sampleImgInteractionSet.AnalysisArea.CenterCircle:
            self.UpdateAnalysisCenterFromCanvas()

    def UpdateSpecifiedAreaFromCanvas(self, col):
        try:
            xc, yc = self.GetSpecifiedCircle(col).XY
            xi, yi = CoordConvertUtil.GetImageCoordinate(self.scaledBmpSize, xc, yc, self.sampleDisplayScaleX, self.sampleDisplayScaleY)

            PtGridHelper.SetGridPoint(self.specifiedAreaGrid, xi, yi, col=col)

            self.UpdateSpecifiedAreaData(col, xi, yi)
        except BaseException:
            print('Exception')

    '''
        Get the circle to get updated.

        :param col: int, updated column of self.specifiedAreaGrid
        :return instance of FCObjects.Circle
    '''
    def GetSpecifiedCircle(self, col):
        if col == 0:
            return self.sampleImgInteractionSet.SpecifiedArea.StartCircle
        else:
            return self.sampleImgInteractionSet.SpecifiedArea.EndCircle

    '''
        Update one point of specified area.

        :param col: int, updated column of self.specifiedAreaGrid
        :param x: int, x of coordinate
        :param y: int, y of coordinate
    '''
    def UpdateSpecifiedAreaData(self, col, x, y):
        if col == 0:
            self.analysisData.SpecifiedAreaStart = (x, y)
        else:
            self.analysisData.SpecifiedAreaEnd = (x, y)

    def UpdateSpecifiedAreaFromGrid(self, col):
        try:
            xi, yi = PtGridHelper.GetGridPoint(self.specifiedAreaGrid, col)
            xw, yw = (xi * self.sampleDisplayScaleX, yi * self.sampleDisplayScaleY)
            xc, yc = CoordConvertUtil.GetCanvasCoordinate(self.scaledBmpSize, xw, yw)

            self.GetSpecifiedCircle(col).SetPoint((xc, yc))

            self.UpdateSpecifiedAreaData(col, xi, yi)

            self.sampleCanvas.Draw(True)
        except BaseException:
            print('Exception')

    def UpdateAnalysisCenterFromCanvas(self):
        xc, yc = self.sampleImgInteractionSet.AnalysisArea.CenterCircle.XY
        xi, yi = CoordConvertUtil.GetImageCoordinate(self.scaledBmpSize, xc, yc, self.sampleDisplayScaleX, self.sampleDisplayScaleY)
        
        PtGridHelper.SetGridPoint(self.analysisCenterGrid, xi, yi)

        self.analysisData.Center = (xi, yi)

    def UpdateAnalysisCenterFromGrid(self):
        try:
            xi, yi = PtGridHelper.GetGridPoint(self.analysisCenterGrid)
            xw, yw = (xi * self.sampleDisplayScaleX, yi * self.sampleDisplayScaleY)
            xc, yc = CoordConvertUtil.GetCanvasCoordinate(self.scaledBmpSize, xw, yw)

            self.sampleImgInteractionSet.AnalysisArea.CenterCircle.SetPoint((xc, yc))

            self.analysisData.Center = (xi, yi)

            self.sampleCanvas.Draw(True)
        except ValueError:
            print('\nValueError - UpdateAnalysisCenterFromGrid\n')

    '''
        Get logs by direction of axis.

        :param direction: int, 0 for X axis, and 1 for Y axis
    '''
    def GenerateDirectionalLogs(self, direction):
        try:
            if direction == 0:
                self.logX = ImgStatisticUtil.GetHorizontalLogs(self.analysisData)
            elif direction == 1:
                self.logY = ImgStatisticUtil.GetVerticalLogs(self.analysisData)
        except ValueError:
            print('\nValueError - GenerateDirectionalLogs\n')

    # Methods for tabs passing image resource
    # TODO: use sth. like interface to do this?

    def GetTabImgRes(self):
        return self.analysisData.GetImageOfSpecifiedArea()

    def SetTabImgRes(self, img):
        pass

    def GetDiseaseParams(self):
        pass

    def SetDiseaseParams(self, params):
        pass

    def GetLoadingImgPath(self):
        return self.ImgPath

    def SetLoadingImgPath(self, ImgPath):
        pass