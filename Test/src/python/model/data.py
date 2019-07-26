from wx import Rect

from ..util import ImgProcessUtil

class AnalysisData():

    def __init__(self):
        self._originalImage = None   # wx.Image
        self._enhancedImage = None   # wx.Image
        self.IsUsingEnhancedImage = False
        self.SpecifiedAreaStart = (0, 0)
        self.SpecifiedAreaEnd = (0, 0)
        self.Center = (0, 0)
        self.LogWidth = (0, 0)

    def IsEmpty(self):
        return self._originalImage is None

    '''
        Assign an image, and set all initial coordinates.

        :param img: an wx.Image instance
    '''
    def InitWithImage(self, img):
        w, h = img.GetSize()
        self._originalImage = img
        self._enhancedImage = ImgProcessUtil.GetGammaEnhancedImage(img, w, h)
        self.IsUsingEnhancedImage = False
        self.SpecifiedAreaStart = (w/4, h/4)
        self.SpecifiedAreaEnd = (w*3/4, h*3/4)
        self.Center = (w/2, h/2)
        self.LogWidth = (int(w / 2), int(h / 2))

    def GetTargetImage(self):
        if self.IsUsingEnhancedImage:
            return self._enhancedImage
        else:
            return self._originalImage

    def GetImageOfSpecifiedArea(self):
        if self._originalImage is None:
            return None

        x1, y1 = self.SpecifiedAreaStart
        x2, y2 = self.SpecifiedAreaEnd
        pos = self.SpecifiedAreaStart
        size = (x2 - x1, y2 - y1)
        rect =  Rect(pos, size)
        
        return self._originalImage.GetSubImage(rect)
