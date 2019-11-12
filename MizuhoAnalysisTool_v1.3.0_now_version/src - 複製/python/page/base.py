from abc import abstractmethod

from wx import Panel

class BasePanel(Panel):

    @abstractmethod
    def GetTabImgRes(self):
        pass

    @abstractmethod
    def SetTabImgRes(self, img):
        pass

    @abstractmethod
    def GetDiseaseParams(self):
        pass

    @abstractmethod
    def SetDiseaseParams(self, params):
        pass

    @abstractmethod
    def GetLoadingImgPath(self):
        pass

    @abstractmethod
    def SetLoadingImgPath(self, ImgPath):
        pass

class DiseaseParams():
    CtrlRGB_Index = 0
    disease = ''
    Ctrlst = ''
    Ctrlpn = ''
    CtrlRS = ''
    CtrlRE = ''
    Ctrlcolor = ''
    TestRGB_Index = 0
    Testst = ''
    Testpn = ''
    TestRS = ''
    TestRE = ''
    Testcolor = ''
    useFilter = None
    usePeakDetection = None
    useEnhance = None


