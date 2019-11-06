import wx
import os
import cv2
import numpy as np
import math
import argparse
import io
import time

from model.ui_set import UiRectControl
from angle import getAngle
from matplotlib import pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from wx.lib.floatcanvas import FloatCanvas, FCObjects
from wx.lib.floatcanvas.FCObjects import ScaledBitmap, Rectangle, Bitmap, Line
from PIL import Image
from decimal import *


import scipy.misc


class BoundaryDetect(wx.Frame):

    def __init__(self):

        #上一版v0.3.1
        #上一版v0.4.0
        #現版v0.4.1  2019/10/28(一)
        super().__init__(parent=None, title="Mizuho_BoundaryDetect v0.4.1", size=(1280, 800))

        # Drag object on canvas.
        self.dragObject = None
        self.dragStartPt = None

        ##########Set the scroll panel######################
        self.panel = wx.ScrolledWindow(parent=self)        #
        self.panel.SetScrollbars(1, 1, 1, 1200)            #
        #self.panel.SetBackgroundColour((255,255,0))       #
        self.panel.SetScrollRate(0, 10)                    #
        #boxSizer = wx.BoxSizer(wx.VERTICAL)               #
        #boxSizer.Add(self.panel)                          #
        #self.SetSizer(boxSizer)                           #
        ####################################################

        ###############Set Panel############################
        self.ScrollPanel = wx.Panel(self.panel, id=wx.ID_ANY, size=(2000, 1000), pos=(0, 0), style=0)
        #self.ScrollPanel.SetBackgroundColour((0, 255, 0))
        ###############Set Plot Panel#######################
        self.PlotPanel = wx.Panel(self.ScrollPanel, id=wx.ID_ANY, size=(648, 486), pos=(50, 80))
        #self.PlotPanel.SetBackgroundColour((255, 255, 0))

        self.PlotBiPanel = wx.Panel(self.ScrollPanel, id=wx.ID_ANY, size=(648, 486), pos=(750, 80))
        #self.PlotBiPanel.SetBackgroundColour((255, 255, 0))
        ###############Set ComboBox#########################
        self.ChoiceForDisease = wx.ComboBox(self.ScrollPanel, value='', pos=(242, 53), choices=['Flu A', 'Flu B', 'Myco', 'RSV', 'hMPV', 'StrepA'], size=(100, 20))
        self.ChoiceForDisease.SetValue('Flu A')

        ###############Set StaticTxt########################
        font = wx.Font(12, wx.ROMAN, wx.NORMAL, wx.BOLD, False)
        self.Coordinate = wx.TextCtrl(self.ScrollPanel, style=wx.TE_MULTILINE | wx.TE_READONLY | wx.NO_BORDER, value='Coordinate'+'\n'+'Top-left : '+'\n'+'Right-bottom : '+'\n'+'Width : '+'\n'+'Height : '+'\n'+'Rotation : ', id=wx.ID_ANY, pos=(50, 615), size=(400,115))
        self.Coordinate.SetFont(font)
        self.CropImgMeanValue = wx.TextCtrl(self.ScrollPanel, value='Gray mean value : ', style=wx.TE_MULTILINE | wx.TE_READONLY | wx.NO_BORDER, pos=(50, 745), size=(400,88))
        self.CropImgMeanValue.SetFont(font)
        ###############Set Button###########################
        self.BrowseBut = wx.Button(self.ScrollPanel, label='Browse', pos=(50, 50))
        self.Bind(wx.EVT_BUTTON, self.ShowTheDialog, self.BrowseBut)

        self.ExportTxtBut = wx.Button(self.ScrollPanel, label='Export', pos=(146, 50))
        self.Bind(wx.EVT_BUTTON, self.ExportTxt, self.ExportTxtBut)

        self.PlotCanvas = FloatCanvas.FloatCanvas(self.PlotPanel, -1, size=(648, 486), BackgroundColor='black')

        self.count = 0
        self.Gauge = wx.Gauge(self.ScrollPanel, range=11, pos=(363, 55), style=wx.GA_HORIZONTAL)

        self.click = False
        self.click_lt = False
        self.click_rt = False
        self.click_lb = False
        self.click_rb = False
        self.click_mm = False

    def ShowTheDialog(self, event):
        wildcard = "Image Files (*.bmp, *.jpg, *.png)|*.bmp;*.jpg;*.png"
        dialog = wx.FileDialog(None, "Choose a file", wildcard=wildcard, style=wx.FD_OPEN)

        self.photoPath = ''

        if dialog.ShowModal() == wx.ID_OK:
            self.photoPath = (dialog.GetPath())
            self.photoPath = self.photoPath.replace('\\', '\\\\')
        dialog.Destroy()

        self.Processing()

    def Processing(self):
        img = cv2.imdecode(np.fromfile(self.photoPath, dtype=np.uint8), -1)

        img2 = img.copy()
        self.Angle = getAngle(img)
        self.ZeroMat = [0, 0, 0, 0]
        if self.Angle == self.ZeroMat:
            pass
        else:
            plt.imshow(self.Angle[3], 'gray')
            plt.savefig('Binary.jpg')
            imageFile = 'Binary.jpg'
            data = open(imageFile, "rb").read()
            stream = io.BytesIO(data)
            bmp = wx.Bitmap((wx.Image(stream)).Scale(648, 486, wx.IMAGE_QUALITY_HIGH))
            #image.Scale(width, height, wx.IMAGE_QUALITY_HIGH)
            while True:
                time.sleep(0.3)
                self.count = self.count + 1
                self.Gauge.SetValue(self.count)

                if self.count >= 11:
                    wx.StaticBitmap(self.PlotBiPanel, -1, bmp, (0, 0))
                    self.count = 0
                    break


        if self.ChoiceForDisease.GetValue()=='Flu A':
            tempPath = './DetectSample/A/FluA N M17.bmp'
        elif self.ChoiceForDisease.GetValue()=='Flu B':
            tempPath = './DetectSample/B/FluB N M17.bmp'
        elif self.ChoiceForDisease.GetValue()=='Myco':
            tempPath = './DetectSample/Myco/00ID_c0_short_Myco1600.bmp'
        elif self.ChoiceForDisease.GetValue()=='StrepA':
            tempPath = './DetectSample/StrepA/M26.bmp'
        elif self.ChoiceForDisease.GetValue()=='RSV':
            tempPath = './DetectSample/RSV/image_bitmap_20190716162659.bmp'
        elif self.ChoiceForDisease.GetValue()=='hMPV':
            tempPath = './DetectSample/RSV/image_bitmap_20190716162659.bmp'


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
        self.img = img

        self.height, self.width, self.nrgb = img.shape
        if self.Angle == self.ZeroMat:
            pass
        else:
            tt = cv2.line(img, (self.width-self.Angle[1][0], self.height-self.Angle[1][1]), (self.width-self.Angle[2][0], self.height-self.Angle[2][1]), (255, 0, 0), 10)




        crop_img_lt = cv2.cvtColor(tt[670:670+220, 400:400+220], cv2.COLOR_RGB2GRAY) #左上
        crop_img_rt = cv2.cvtColor(tt[670:670+220, 1980:1980+220], cv2.COLOR_RGB2GRAY) #右上
        crop_img_lb = cv2.cvtColor(tt[1110:1110+220, 400:400+220], cv2.COLOR_RGB2GRAY) #左下
        crop_img_rb = cv2.cvtColor(tt[1110:1110+220, 1980:1980+220], cv2.COLOR_RGB2GRAY) #右下
        crop_img_mm = cv2.cvtColor(tt[875:875+220, 1190:1190+220], cv2.COLOR_RGB2GRAY)  # 右下


        #np.set_printoptions(threshold=np.inf)
        self.lt_mean_value, g, r, a = np.uint8(cv2.mean(crop_img_lt))
        self.rt_mean_value, g, r, a = np.uint8(cv2.mean(crop_img_rt))
        self.lb_mean_value, g, r, a = np.uint8(cv2.mean(crop_img_lb))
        self.rb_mean_value, g, r, a = np.uint8(cv2.mean(crop_img_rb))
        self.mm_mean_value, g, r, a = np.uint8(cv2.mean(crop_img_mm))

        tt = cv2.rectangle(img, (400, 670), (620, 890), (0, 255, 255), 4) #左上
        tt = cv2.rectangle(img, (1980, 670), (2200, 890), (0, 255, 255), 4) #右上
        tt = cv2.rectangle(img, (400, 1110), (620, 1330), (0, 255, 255), 4) #左下
        tt = cv2.rectangle(img, (1980, 1110), (2200, 1330), (0, 255, 255), 4) #右下
        tt = cv2.rectangle(img, (1190, 875), (1410, 1095), (0, 255, 255), 4)  #中間

        height, width, nrgb = tt.shape

        #wxbmp = wx.Bitmap.FromBuffer(width, height, tt)
        #wxImage = wxbmp.ConvertToImage()

        self.PhotoMaxSize = 648
        if width > height:
            NewW = self.PhotoMaxSize
            NewH = self.PhotoMaxSize * height / width
        else:
            NewH = self.PhotoMaxSize
            NewW = self.PhotoMaxSize * width / height
        #wxImage = wxImage.Scale(NewW, NewH)
        #wxbmp = wx.Bitmap(wxImage, -1)

        NewWInt = int(NewW)
        NewHInt = int(NewH)

        tt = cv2.resize(tt , (NewWInt,NewHInt))

        wxbmp = wx.Bitmap.FromBuffer(tt.shape[1], tt.shape[0], tt)


        self.NewW = NewW
        self.NewH = NewH

        self.PlotCanvas.ClearAll(ResetBB=True)
        self.PlotCanvas.SetClientSize(wx.Size(648, 486))
        self.FCObjectBitmap = Bitmap(wxbmp, (0,0), Position='cc')

        self.PlotCanvas.AddObject(self.FCObjectBitmap)
        self.PlotCanvas.Bind(FloatCanvas.EVT_LEFT_UP, self.OnMouseLeftUp)
        self.PlotCanvas.Bind(FloatCanvas.EVT_MOTION, self.OnMouseMotion)

        scaleW = NewW / width
        scaleH = NewH / height

        if self.ChoiceForDisease.GetValue() == 'Flu A':
            # DeltaX = 48
            # DeltaY = 44.5
            DeltaX = 0
            DeltaY = 0
            MoveW, MoveH = (560*NewW/width, 200*NewH/height)
            self.DeltaW = 560
            self.DeltaH = 200
        elif self.ChoiceForDisease.GetValue() == 'Flu B':
            # DeltaX = 49
            # DeltaY = 43
            DeltaX = 0
            DeltaY = 0
            MoveW, MoveH = (560 * NewW / width, 200 * NewH / height)
            self.DeltaW = 560
            self.DeltaH = 200
        elif self.ChoiceForDisease.GetValue() == 'StrepA':
            # DeltaX = 40.5
            # DeltaY = 43
            DeltaX = 0
            DeltaY = 0
            MoveW, MoveH = (920 * NewW / width, 200 * NewH / height)
            self.DeltaW = 920
            self.DeltaH = 200
        elif self.ChoiceForDisease.GetValue() == 'RSV':
            # DeltaX = -5
            # DeltaY = -3
            DeltaX = 0
            DeltaY = 0
            MoveW, MoveH = (920 * NewW / width, 200 * NewH / height)
            self.DeltaW = 920
            self.DeltaH = 200

        elif self.ChoiceForDisease.GetValue() == 'hMPV':
            # DeltaX = -5
            # DeltaY = -3
            DeltaX = 0
            DeltaY = 0
            MoveW, MoveH = (920 * NewW / width, 200 * NewH / height)
            self.DeltaW = 920
            self.DeltaH = 200

        MoveW_sq, MoveH_sq = (220 * NewW / width, 220 * NewH / height)
        self.DeltaW_sq = 220
        self.DeltaH_sq = 220


        StartX = (top_left[0]+DeltaX - width / 2) * scaleW
        StartY = -(top_left[1]+DeltaY - height / 2) * scaleH
        EndX = (bottom_right[0]-DeltaX - width / 2) * scaleW
        EndY = -(bottom_right[1]-DeltaY - height / 2) * scaleH
        StartXY = (StartX, StartY)
        EndXY = (EndX, EndY)

        StartX_lt = (400+0 - width / 2) * scaleW
        StartY_lt = -(670+0 - height / 2) * scaleH
        EndX_lt = (620-0 - width / 2) * scaleW
        EndY_lt = -(890-0 - height / 2) * scaleH
        StartXY_lt = (StartX_lt, StartY_lt)
        EndXY_lt = (EndX_lt, EndY_lt)

        StartX_rt = (1980+0 - width / 2) * scaleW
        StartY_rt = -(670+0 - height / 2) * scaleH
        EndX_rt = (2200-0 - width / 2) * scaleW
        EndY_rt = -(890-0 - height / 2) * scaleH
        StartXY_rt = (StartX_rt, StartY_rt)
        EndXY_rt = (EndX_rt, EndY_rt)

        StartX_lb = (400+0 - width / 2) * scaleW
        StartY_lb = -(1100+0 - height / 2) * scaleH
        EndX_lb = (620-0 - width / 2) * scaleW
        EndY_lb = -(1330-0 - height / 2) * scaleH
        StartXY_lb = (StartX_lb, StartY_lb)
        EndXY_lb = (EndX_lb, EndY_lb)

        StartX_rb = (1980+0 - width / 2) * scaleW
        StartY_rb = -(1100+0 - height / 2) * scaleH
        EndX_rb = (2200-0 - width / 2) * scaleW
        EndY_rb = -(1330-0 - height / 2) * scaleH
        StartXY_rb = (StartX_rb, StartY_rb)
        EndXY_rb = (EndX_rb, EndY_rb)

        StartX_mm = (1190+0 - width / 2) * scaleW
        StartY_mm = -(875+0 - height / 2) * scaleH
        EndX_mm = (1410-0 - width / 2) * scaleW
        EndY_mm = -(1095-0 - height / 2) * scaleH
        StartXY_mm = (StartX_mm, StartY_mm)
        EndXY_mm = (EndX_mm, EndY_mm)

        # (1190, 875), (1410, 1095), (0, 255, 255), 4)

        ###中間方塊#################################################
        self.UiRectControl = UiRectControl()
        self.UiRectControl.UpdateControls2(StartXY, EndXY)
        self.UiRectControl.UpdateVisuals(MoveW, MoveH)
        visualObjs = [self.UiRectControl.Rect]
        self.PlotCanvas.AddObjects(visualObjs)
        controlObjs = [self.UiRectControl.StartCircle]
        self.PlotCanvas.AddObjects(controlObjs)
        for item in controlObjs:
            item.Bind(FloatCanvas.EVT_FC_LEFT_DOWN, self.OnHitMark)
        self.PlotCanvas.Draw(True)
        ###左上方塊#################################################
        self.UiRectControl_lt = UiRectControl()
        self.UiRectControl_lt.UpdateControls2(StartXY_lt, EndXY_lt)
        self.UiRectControl_lt.UpdateVisuals(MoveW_sq, MoveH_sq)
        visualObjs_lt = [self.UiRectControl_lt.Rect]
        self.PlotCanvas.AddObjects(visualObjs_lt)
        controlObjs_lt = [self.UiRectControl_lt.StartCircle]
        self.PlotCanvas.AddObjects(controlObjs_lt)
        for item in controlObjs_lt:
            item.Bind(FloatCanvas.EVT_FC_LEFT_DOWN, self.OnHitMark_lt)
        self.PlotCanvas.Draw(True)
        ###右上下方塊#################################################
        self.UiRectControl_rt = UiRectControl()
        self.UiRectControl_rt.UpdateControls2(StartXY_rt, EndXY_rt)
        self.UiRectControl_rt.UpdateVisuals(MoveW_sq, MoveH_sq)
        visualObjs_rt = [self.UiRectControl_rt.Rect]
        self.PlotCanvas.AddObjects(visualObjs_rt)
        controlObjs_rt = [self.UiRectControl_rt.StartCircle]
        self.PlotCanvas.AddObjects(controlObjs_rt)
        for item in controlObjs_rt:
            item.Bind(FloatCanvas.EVT_FC_LEFT_DOWN, self.OnHitMark_rt)
        self.PlotCanvas.Draw(True)
        ###左下下方塊#################################################
        self.UiRectControl_lb = UiRectControl()
        self.UiRectControl_lb.UpdateControls2(StartXY_lb, StartXY_lb)
        self.UiRectControl_lb.UpdateVisuals(MoveW_sq, MoveH_sq)
        visualObjs_lb = [self.UiRectControl_lb.Rect]
        self.PlotCanvas.AddObjects(visualObjs_lb)
        controlObjs_lb = [self.UiRectControl_lb.StartCircle]
        self.PlotCanvas.AddObjects(controlObjs_lb)
        for item in controlObjs_lb:
            item.Bind(FloatCanvas.EVT_FC_LEFT_DOWN, self.OnHitMark_lb)
        self.PlotCanvas.Draw(True)
        ###右下下方塊#################################################
        self.UiRectControl_rb = UiRectControl()
        self.UiRectControl_rb.UpdateControls2(StartXY_rb, EndXY_rb)
        self.UiRectControl_rb.UpdateVisuals(MoveW_sq, MoveH_sq)
        visualObjs_rb = [self.UiRectControl_rb.Rect]
        self.PlotCanvas.AddObjects(visualObjs_rb)
        visualObjs_rb = [self.UiRectControl_rb.StartCircle]
        self.PlotCanvas.AddObjects(visualObjs_rb)
        for item in visualObjs_rb:
            item.Bind(FloatCanvas.EVT_FC_LEFT_DOWN, self.OnHitMark_rb)
        self.PlotCanvas.Draw(True)
        ###中間方塊#################################################
        self.UiRectControl_mm = UiRectControl()
        self.UiRectControl_mm.UpdateControls2(StartXY_mm, EndXY_mm)
        self.UiRectControl_mm.UpdateVisuals(MoveW_sq, MoveH_sq)
        visualObjs_mm = [self.UiRectControl_mm.Rect]
        self.PlotCanvas.AddObjects(visualObjs_mm)
        visualObjs_mm = [self.UiRectControl_mm.StartCircle]
        self.PlotCanvas.AddObjects(visualObjs_mm)
        for item in visualObjs_mm:
            item.Bind(FloatCanvas.EVT_FC_LEFT_DOWN, self.OnHitMark_mm)
        self.PlotCanvas.Draw(True)

        #########Set Global Variables#######################
        self.TopLeft = top_left
        self.BottomRight = bottom_right
        self.width = w-DeltaX*2
        self.height = h-DeltaY*2
        self.NewW = NewW
        self.NewH = NewH
        self.scaleW = NewW / width
        self.scaleH = NewH / height
        self.MoveW_sq = MoveW_sq
        self.MoveH_sq = MoveH_sq
        self.MoveW = MoveW
        self.MoveH = MoveH
        #########Call Function##############################
        self.TopLeftCoord = np.asarray(self.TopLeft)+np.array([DeltaX, DeltaY])
        self.RightBotCoord = np.asarray(self.BottomRight)-np.array([DeltaX, DeltaY])

        self.TopLeftCoord = (self.TopLeftCoord[0], self.TopLeftCoord[1])
        self.RightBotCoord = (self.RightBotCoord[0], self.RightBotCoord[1])

        self.ShowAngle()
        self.Text = 'Coordinate' + '\n'\
                    + 'Top-left : ' + str(self.TopLeftCoord) + '\n'\
                    + 'Right-bottom : ' + str(self.RightBotCoord) + '\n'\
                    + 'Width : ' + str(int(self.width)) + '\n'\
                    + 'Height : ' + str(int(self.height)) + '\n'\
                    + 'Rotation : %d°' % self.getAngle[0]
        self.Coordinate.SetValue(self.Text)

        self.GrayValueText = 'Gray mean value : '+'\n'\
                              +'Top left : '+str(self.lt_mean_value)+'          '\
                              +'Top right : '+str(self.rt_mean_value)+'\n'\
                              +'Bottom left : '+str(self.lb_mean_value)+'    '\
                              +'Bottom right : '+str(self.rb_mean_value)+'\n'\
                              +'Mid : '+str(self.mm_mean_value)
        self.CropImgMeanValue.SetValue(self.GrayValueText)

    def ShowCropImgMeanValue(self, x, y):

        if self.click_lt==True:
            crop_img_lt = cv2.cvtColor(self.img[x:x+220, y:y+220], cv2.COLOR_RGB2GRAY) #左上
            self.lt_mean_value, g, r, a = np.uint8(cv2.mean(crop_img_lt))
        if self.click_rt == True:
            crop_img_rt = cv2.cvtColor(self.img[x:x+220, y:y+220], cv2.COLOR_RGB2GRAY) #右上
            self.rt_mean_value, g, r, a = np.uint8(cv2.mean(crop_img_rt))
        if self.click_lb == True:
            crop_img_lb = cv2.cvtColor(self.img[x:x+220, y:y+220], cv2.COLOR_RGB2GRAY) #左下
            self.lb_mean_value, g, r, a = np.uint8(cv2.mean(crop_img_lb))
        if self.click_rb == True:
            crop_img_rb = cv2.cvtColor(self.img[x:x+220, y:y+220], cv2.COLOR_RGB2GRAY) #右下
            self.rb_mean_value, g, r, a = np.uint8(cv2.mean(crop_img_rb))
        if self.click_mm == True:
            crop_img_mm = cv2.cvtColor(self.img[x:x+220, y:y+220], cv2.COLOR_RGB2GRAY)  #中間
            self.mm_mean_value, g, r, a = np.uint8(cv2.mean(crop_img_mm))

        #np.set_printoptions(threshold=np.inf)
        # self.lt_mean_value, g, r, a = np.uint8(cv2.mean(crop_img_lt))
        # self.rt_mean_value, g, r, a = np.uint8(cv2.mean(crop_img_rt))
        # self.lb_mean_value, g, r, a = np.uint8(cv2.mean(crop_img_lb))
        # self.rb_mean_value, g, r, a = np.uint8(cv2.mean(crop_img_rb))
        # self.mm_mean_value, g, r, a = np.uint8(cv2.mean(crop_img_mm))

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

            image = cv2.imdecode(np.fromfile(f, dtype=np.uint8), -1)

        self.getAngle = getAngle(image)

    #############################################################################################

    def OnHitMark(self, object):
        self.dragObject = object
        self.click = True
        self.MoveObjectDetection(self.dragStartPt[0], self.dragStartPt[1], self.dragStartPt, self.DeltaW_sq, self.DeltaH_sq)

    def OnHitMark_lt(self, object):
        self.dragObject = object
        self.click_lt = True
        self.MoveObjectDetection(400/4, 670/4, self.dragStartPt, self.DeltaW_sq, self.DeltaH_sq)

    def OnHitMark_rt(self, object):
        self.dragObject = object
        self.click_rt = True
        self.MoveObjectDetection(1980/4, 670/4, self.dragStartPt, self.DeltaW_sq, self.DeltaH_sq)

    def OnHitMark_lb(self, object):
        self.dragObject = object
        self.click_lb = True
        self.MoveObjectDetection(400/4, 1110/4, self.dragStartPt, self.DeltaW_sq, self.DeltaH_sq)

    def OnHitMark_rb(self, object):
        self.dragObject = object
        self.click_rb = True
        self.MoveObjectDetection(1980/4, 1110/4, self.dragStartPt, self.DeltaW_sq, self.DeltaH_sq)
    def OnHitMark_mm(self, object):
        self.dragObject = object
        self.click_mm = True
        self.MoveObjectDetection(1190/4, 875/4, self.dragStartPt, self.DeltaW_sq, self.DeltaH_sq)


    def OnMouseLeftUp(self, event):
        print(int(self.TopLeftImgX), int(self.TopLeftImgY))
        self.ShowCropImgMeanValue(int(self.TopLeftImgX), int(self.TopLeftImgY))



        self.GrayValueText = 'Gray mean value : '+'\n'\
                              +'Top left : '+str(self.lt_mean_value)+'          '\
                              +'Top right : '+str(self.rt_mean_value)+'\n'\
                              +'Bottom left : '+str(self.lb_mean_value)+'    '\
                              +'Bottom right : '+str(self.rb_mean_value)+'\n'\
                              +'Mid : '+str(self.mm_mean_value)
        self.CropImgMeanValue.SetValue(self.GrayValueText)

        if self.dragObject is None:
            return
        self.dragObject = None
        self.dragStartPt = None
        self.click_lb = False
        self.click_lt = False
        self.click_rb = False
        self.click_rt = False
        self.click = False
        self.click_mm = False


    def OnMouseMotion(self, event):
        newDragPt = event.GetPosition()

        if self.dragObject is not None:
            if self.dragStartPt is not None:
                delta = newDragPt - self.dragStartPt
                delta.y *= -1
                self.dragObject.Move(delta)
                if self.click==True:
                    self.UiRectControl.UpdateVisuals(self.MoveW, self.MoveH)
                elif self.click_lt == True:
                    self.UiRectControl_lt.UpdateVisuals(self.MoveW_sq, self.MoveH_sq)
                elif self.click_rt==True:
                    self.UiRectControl_rt.UpdateVisuals(self.MoveW_sq, self.MoveH_sq)
                elif self.click_lb==True:
                    self.UiRectControl_lb.UpdateVisuals(self.MoveW_sq, self.MoveH_sq)
                elif self.click_rb==True:
                    self.UiRectControl_rb.UpdateVisuals(self.MoveW_sq, self.MoveH_sq)
                else:
                    self.UiRectControl_mm.UpdateVisuals(self.MoveW_sq, self.MoveH_sq)
                self.PlotCanvas.Draw(True)

            self.dragStartPt = newDragPt
            if self.click==True:
                self.MoveObjectDetection(self.dragStartPt[0], self.dragStartPt[1], self.dragStartPt, self.DeltaW, self.DeltaH)
            elif self.click_lt==True:
                self.MoveObjectDetection(self.dragStartPt[0], self.dragStartPt[1], self.dragStartPt, self.DeltaW_sq, self.DeltaH_sq)
            elif self.click_rt==True:
                self.MoveObjectDetection(self.dragStartPt[0], self.dragStartPt[1], self.dragStartPt, self.DeltaW_sq, self.DeltaH_sq)
            elif self.click_lb==True:
                self.MoveObjectDetection(self.dragStartPt[0], self.dragStartPt[1], self.dragStartPt, self.DeltaW_sq, self.DeltaH_sq)
            elif self.click_rb == True:
                self.MoveObjectDetection(self.dragStartPt[0], self.dragStartPt[1], self.dragStartPt, self.DeltaW_sq, self.DeltaH_sq)
            elif self.click_mm == True:
                self.MoveObjectDetection(self.dragStartPt[0], self.dragStartPt[1], self.dragStartPt, self.DeltaW_sq, self.DeltaH_sq)

    def MoveObjectDetection(self, x_coord, y_coord, obj, DeltaW, DeltaH):
        # self.TopLeftImgX = round(x_coord/self.scaleW, 0)
        # self.TopLeftImgX = round(self.TopLeftImgX, 0)
        # self.TopLeftImgY = round(y_coord/self.scaleH, 0)
        # self.TopLeftImgY = round(self.TopLeftImgY, 0)
        self.TopLeftImgX = x_coord/self.scaleW
        self.TopLeftImgX = self.TopLeftImgX
        self.TopLeftImgY = y_coord/self.scaleH
        self.TopLeftImgY = self.TopLeftImgY
        self.TopLeftCoord = (self.TopLeftImgX, self.TopLeftImgY)
        self.RightBotCoord = (self.TopLeftImgX+DeltaW, self.TopLeftImgY+DeltaH)
        self.Text = 'Coordinate' + '\n' \
                    + 'Top-left : ' + str(self.TopLeftCoord) + '\n' \
                    + 'Right-bottom : ' + str(self.RightBotCoord) + '\n'\
                    + 'Width : ' + str(int(self.width)) + '\n' \
                    + 'Height : ' + str(int(self.height)) + '\n' + \
                    'Rotation : %d°' % self.getAngle[0]

        self.Coordinate.SetValue(self.Text)

    def ExportTxt(self,event):
        full_path = './Text/Record.txt'  # 也可以创建一个.doc的word文档
        file = open(full_path, 'w')
        file.write(self.Text)
        file.write('\n'+self.GrayValueText)
#########################################################################################################
class App(wx.App):
    def OnInit(self):
        frame = BoundaryDetect()
        frame.Show()
        return True

if __name__ == '__main__':
    app = App()
    app.MainLoop()


#打包指令
#pyinstaller -w --add-data "Text;Text" --add-data "DetectSample;DetectSample" --add-data "FullImagesSamples;FullImagesSamples" BoundaryDetect.py -n "BoundaryDetect v0.4.1"
