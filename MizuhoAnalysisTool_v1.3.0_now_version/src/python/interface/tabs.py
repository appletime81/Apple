from abc import ABCMeta, abstractmethod

def ITabImgRes(metaclass=ABCMeta):

    @abstractmethod
    def GetTabImgRes(self):
        return NotImplemented

    @abstractmethod
    def SetTabImgRes(self, img):
        return NotImplemented