from wx import EVT_NOTEBOOK_PAGE_CHANGED, ID_ANY, Frame
from wx.xrc import XRCCTRL, XmlResource

from ..page.analysis import AnalysisPanel
from ..page.detection import DetectionPanel
from ..page.multi_result import MultiResultPanel
from ..page.BoundaryDetect import BoundaryDetectPanel
from ..util.constants import AppVersion

class TabbedFrame(Frame):

    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)

        res = XmlResource('src/layout/frame_tabbed.xrc')
        frame = res.LoadFrame(None, 'root')
        frame.SetTitle(frame.GetTitle() + " " + AppVersion)
        self.InitFrame(frame)
        frame.Show()
        frame.Maximize(True)

    def InitFrame(self, frame):
        frame.SetMinSize(frame.GetSize()) # XRC cannot set this

        self.notebook = XRCCTRL(frame, 'notebook')
        self.notebook.Bind(EVT_NOTEBOOK_PAGE_CHANGED, self.OnPageChanged)
        
        # TODO: create interface or sth for sharing resources

        tabAnalysis = AnalysisPanel(self.notebook)
        self.notebook.AddPage(tabAnalysis, "Analysis")

        tabDetection = DetectionPanel(self.notebook)
        self.notebook.AddPage(tabDetection, "Detection")

        tabMultiResult = MultiResultPanel(self.notebook)
        self.notebook.AddPage(tabMultiResult, "MultiResult")

        tabBoundaryDetect = BoundaryDetectPanel(self.notebook)
        self.notebook.AddPage(tabBoundaryDetect, "BoundaryDetect")

    def OnPageChanged(self, event):
        oldPage = self.notebook.GetPage(event.OldSelection)
        image = oldPage.GetTabImgRes()
        params = oldPage.GetDiseaseParams()

        newPage = self.notebook.GetPage(event.Selection)
        newPage.SetTabImgRes(image)
        newPage.SetDiseaseParams(params)
