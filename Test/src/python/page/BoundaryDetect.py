import wx
import os
import cv2
import numpy as np
import math
import argparse
import io
from ..model.ui_set import UiRectControl
from .base import BasePanel
from .angle import getAngle
from matplotlib import pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from wx.lib.floatcanvas import FloatCanvas
from wx.lib.floatcanvas.FCObjects import ScaledBitmap, Rectangle, Bitmap, Line
from PIL import Image

class BoundaryDetectPanel(BasePanel):

    def __init__(self, *args, **kw):

        super().__init__(*args, **kw)

        # Drag object on canvas.
        self.dragObject = None
        self.dragStartPt = None

        ##########Set the scroll panel######################
        self.panel = wx.ScrolledWindow(parent=self)        #
        self.panel.SetScrollbars(1, 1, 1, 1200)            #
        #self.panel.SetBackgroundColour((255,255,0))       #
        self.panel.SetScrollRate(0, 10)                    #
        boxSizer = wx.BoxSizer(wx.VERTICAL)                #
        boxSizer.Add(self.panel)                           #
        self.SetSizer(boxSizer)                            #
        ####################################################

        ###############Set Panel############################
        self.ScrollPanel = wx.Panel(self.panel, id=wx.ID_ANY, size=(2000, 1000), pos=(0, 0), style=0)
        #self.ScrollPanel.SetBackgroundColour((0, 255, 0))
        ###############Set Plot Panel#######################
        self.PlotPanel = wx.Panel(self.ScrollPanel, id=wx.ID_ANY, size=(700, 400), pos=(50, 80))
        #self.PlotPanel.SetBackgroundColour((255, 255, 0))

        self.PlotBiPanel = wx.Panel(self.ScrollPanel, id=wx.ID_ANY, size=(600, 400), pos=(700, 80))
        #self.PlotBiPanel.SetBackgroundColour((255, 255, 0))
        ###############Set ComboBox#########################
        self.ChoiceForDisease = wx.ComboBox(self.ScrollPanel, value='', pos=(150, 50), choices=['Flu A', 'Flu B', 'Myco', 'RSV', 'hMPV', 'StrepA'], size=(100, 20))
        self.ChoiceForDisease.SetValue('Flu A')

        ###############Set StaticTxt########################
        self.Coordinate = wx.StaticText(self.ScrollPanel, label='Coordinate'+'\n'+'Top-left : '+'\n'+'Right-bottom : '+'\n'+'Width : '+'\n'+'Height : '+'\n'+'Rotation : ', pos=(50, 530))

        ###############Set Button###########################
        self.BrowseBut = wx.Button(self.ScrollPanel, label='Browse', pos=(50, 50))
        self.Bind(wx.EVT_BUTTON, self.ShowTheDialog, self.BrowseBut)

    def ShowTheDialog(self, event):
        wildcard = "Image Files (*.bmp, *.jpg, *.png)|*.bmp;*.jpg;*.png"
        dialog = wx.FileDialog(None, "Choose ar file", wildcard=wildcard, style=wx.FD_OPEN)

        self.photoPath = ''

        if dialog.ShowModal() == wx.ID_OK:
            self.photoPath = (dialog.GetPath())
            self.photoPath = self.photoPath.replace('\\', '\\\\')
        dialog.Destroy()

        self.Processing()

    def Processing(self):
        img = cv2.imread(self.photoPath)
        img2 = img.copy()
        self.Angle = getAngle(img)

        plt.imshow(self.Angle[3], 'gray')
        plt.savefig('Binary.jpg')
        imageFile = 'Binary.jpg'
        data = open(imageFile, "rb").read()
        stream = io.BytesIO(data)
        bmp = wx.Bitmap( wx.Image( stream ))
        wx.StaticBitmap(self.PlotBiPanel, -1, bmp, (0, 0))

        if self.ChoiceForDisease.GetValue()=='Flu A':
            tempPath = './DetectSample/A/image_bitmap_20190717154103.bmp'
        elif self.ChoiceForDisease.GetValue()=='Flu B':
            tempPath = './DetectSample/B/005.bmp'
        elif self.ChoiceForDisease.GetValue()=='Myco':
            tempPath = './DetectSample/Myco/00ID_c0_short_Myco1600.bmp'
        elif self.ChoiceForDisease.GetValue()=='StrepA':
            tempPath = './DetectSample/StrepA/image_bitmap_20190716162831.bmp'
        elif self.ChoiceForDisease.GetValue()=='RSV':
            tempPath = './DetectSample/RSV/image_bitmap_20190716162659.bmp'
        elif self.ChoiceForDisease.GetValue()=='hMPV':
            tempPath = './DetectSample/RSV/image_bitmap_20190716162659.bmp'
        else :
            tempPath = ''

        template = cv2.imread(tempPath)
        w = template.shape[1]
        h = template.shape[0]

        methods = ['cv2.TM_SQDIFF_NORMED']

        for meth in methods:
            img = img2.copy()
            method = eval(meth)

            res = cv2.matchTemplate(img, template, method)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

            if method in [cv2.TM_SQDIFF, cv2.TM_SQDIFF_NORMED]:
                top_left = min_loc
            else:
                top_left = max_loc
            bottom_right = (top_left[0] + w, top_left[1] + h)

        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.height, self.width, self.nrgb = img.shape
        tt = cv2.line(img,
                      (self.width-self.Angle[1][0], self.height-self.Angle[1][1]),
                      (self.width-self.Angle[2][0], self.height-self.Angle[2][1]),
                      (255, 0, 0),
                      10)
        height, width, nrgb = tt.shape
        wxbmp = wx.Bitmap.FromBuffer(width, height, tt)
        wxImage = wxbmp.ConvertToImage()

        self.PhotoMaxSize = 500
        if width > height:
            NewW = self.PhotoMaxSize
            NewH = self.PhotoMaxSize * height / width
        else:
            NewH = self.PhotoMaxSize
            NewW = self.PhotoMaxSize * width / height
        wxImage = wxImage.Scale(NewW, NewH)
        wxbmp = wx.Bitmap(wxImage, -1)
        self.NewW = NewW
        self.NewH = NewH

        self.FCObjectBitmap = Bitmap(wxbmp, (0,0), Position='cc')

        self.PlotCanvas = FloatCanvas.FloatCanvas(self.PlotPanel, -1, size=wxImage.GetSize(), BackgroundColor='black')
        self.PlotCanvas.Bind(FloatCanvas.EVT_LEFT_UP, self.OnMouseLeftUp)
        self.PlotCanvas.Bind(FloatCanvas.EVT_MOTION, self.OnMouseMotion)
        self.PlotCanvas.ClearAll(ResetBB=True)
        self.PlotCanvas.AddObject(self.FCObjectBitmap)

        scaleW = NewW / width
        scaleH = NewH / height
        StartX = (top_left[0] - width / 2) * scaleW
        StartY = -(top_left[1] - height / 2) * scaleH
        EndX = (bottom_right[0] - width / 2) * scaleW
        EndY = -(bottom_right[1] - height / 2) * scaleH
        StartXY = (StartX, StartY)
        EndXY = (EndX, EndY)

        self.UiRectControl = UiRectControl()
        self.UiRectControl.UpdateControls2(StartXY, EndXY)
        self.UiRectControl.UpdateVisuals()
        visualObjs = [self.UiRectControl.Rect]
        self.PlotCanvas.AddObjects(visualObjs)
        controlObjs = [self.UiRectControl.StartCircle, self.UiRectControl.EndCircle]
        self.PlotCanvas.AddObjects(controlObjs)
        for item in controlObjs:
            item.Bind(FloatCanvas.EVT_FC_LEFT_DOWN, self.OnHitMark)
        self.PlotCanvas.Draw(True)

        #########Set Global Variables#######################
        self.TopLeft = top_left
        self.BottomRight = bottom_right
        self.width = w
        self.height = h
        self.NewW = NewW
        self.NewH = NewH
        self.scaleW = NewW / width
        self.scaleH = NewH / height
        #########Call Function##############################
        self.TopLeftCoord = self.TopLeft
        self.RightBotCoord = self.BottomRight
        self.ShowAngle()
        self.Coordinate.SetLabel('Coordinate' + '\n'
                                 + 'Top-left : ' + str(self.TopLeft) + '\n'
                                 + 'Right-bottom : ' + str(self.BottomRight) + '\n'
                                 + 'Width : ' + str(self.width) + '\n'
                                 + 'Height : ' + str(self.height) + '\n'
                                 + 'Rotation : %d°' % self.getAngle[0])

    def ShowAngle(self):
        ap = argparse.ArgumentParser()

        ap.add_argument("-i", "-image", required=False, help="Path to the image")
        args = vars(ap.parse_args())

        test_img = None
        if args["i"]:
            test_img = [args["i"]]
        else:
            test_img = [str(self.photoPath)]
        for f in test_img:
            image = cv2.imread(f)
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            gray = cv2.GaussianBlur(gray, (31, 31), 0)
            ret, thresh = cv2.threshold(gray, 30, 200, 0)
        #########Set Global Variables#######################
        self.getAngle = getAngle(image)

    def OnHitMark(self, object):
        self.dragObject = object

    def OnMouseLeftUp(self, event):
        if self.dragObject is None:
            return

        self.dragObject = None
        self.dragStartPt = None

    def OnMouseMotion(self, event):
        newDragPt = event.GetPosition()

        if self.dragObject is not None:
            if self.dragStartPt is not None:
                print(newDragPt)
                delta = newDragPt - self.dragStartPt
                delta.y *= -1
                self.dragObject.Move(delta)
                self.UiRectControl.UpdateVisuals()
                self.PlotCanvas.Draw(True)

            self.dragStartPt = newDragPt
            self.MoveObjectDetection(self.dragObject)

    def MoveObjectDetection(self, obj):
        if obj==self.UiRectControl.StartCircle:
            self.TopLeftImgX = int(self.dragStartPt[0]/self.scaleW)
            self.TopLeftImgY = int(self.dragStartPt[1]/self.scaleH)
            self.TopLeftCoord = (self.TopLeftImgX, self.TopLeftImgY)
        else:
            self.RightBotImgX = int(self.dragStartPt[0]/self.scaleW)
            self.RightBotImgY = int(self.dragStartPt[1]/self.scaleH)
            self.RightBotCoord = (self.RightBotImgX, self.RightBotImgY)

        self.Coordinate.SetLabel('Coordinate' + '\n'+ 'Top-left : ' + str(self.TopLeftCoord) + '\n'+ 'Right-bottom : ' + str(self.RightBotCoord) + '\n'+ 'Width : ' + str(self.width) + '\n'+ 'Height : ' + str(self.height) + '\n'+ 'Rotation : %d°' % self.getAngle[0])