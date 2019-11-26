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
from calibrationAlgorithm import *


import scipy.misc


class BoundaryDetect(wx.Frame):

    def __init__(self):

        #上一版v0.3.1
        #上一版v0.4.0
        #上一版v0.4.1  2019/10/28(一)
        #現版v0.4.2   2019/11/07(四)
        super().__init__(parent=None, title="Mizuho_BoundaryDetect v0.4.2", size=(1280, 800))

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
        self.ChoiceForDisease = wx.ComboBox(self.ScrollPanel, value='', pos=(390, 53), choices=['Flu A', 'Flu B', 'Myco', 'RSV', 'hMPV', 'StrepA'], size=(100, 20))
        self.ChoiceForDisease.SetValue('Flu A')


        font_title = wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.BOLD, False)

        self.StaticTextTitleCoordinate = wx.StaticText(self.ScrollPanel, label='Coordinate', pos=(50, 615))
        self.StaticTextPoint1 = wx.StaticText(self.ScrollPanel, label='Point 1 :', pos=(50, 645))
        self.StaticTextPoint2 = wx.StaticText(self.ScrollPanel, label='Point 2 :', pos=(50, 675))
        self.StaticTextPoint3 = wx.StaticText(self.ScrollPanel, label='Point 3 :', pos=(50, 705))

        self.StaticTextGrayMeanValue = wx.StaticText(self.ScrollPanel, label='Gray Mean Value', pos=(50, 745))
        self.StaticTextTopLeft = wx.StaticText(self.ScrollPanel, label='Top-Left :', pos=(50,775))
        self.StaticTextTopRight = wx.StaticText(self.ScrollPanel, label='Top-Right :', pos=(50, 805))
        self.StaticTextBottomLeft = wx.StaticText(self.ScrollPanel, label='Bottom-Left :', pos=(50, 835))
        self.StaticTextBottomRight = wx.StaticText(self.ScrollPanel, label='Bottom-Right :', pos=(50, 865))
        self.StaticTextMid = wx.StaticText(self.ScrollPanel, label='Mid :', pos=(50, 895))

        ###############Set TextCtrl########################
        self.TextCtrlPoint1 = wx.TextCtrl(self.ScrollPanel, value='', pos=(100, 644), size=(80, 17))
        self.TextCtrlPoint2 = wx.TextCtrl(self.ScrollPanel, value='', pos=(100, 674), size=(80, 17))
        self.TextCtrlPoint3 = wx.TextCtrl(self.ScrollPanel, value='', pos=(100, 704), size=(80, 17))

        self.TextCtrlTopLeft = wx.TextCtrl(self.ScrollPanel, value='', pos=(136, 774), size=(50, 17))
        self.TextCtrlTopRight = wx.TextCtrl(self.ScrollPanel, value='', pos=(136, 804), size=(50, 17))
        self.TextCtrlBottomLeft = wx.TextCtrl(self.ScrollPanel, value='', pos=(136, 834), size=(50, 17))
        self.TextCtrlBottomRight = wx.TextCtrl(self.ScrollPanel, value='', pos=(136, 864), size=(50, 17))
        self.TextCtrlMid = wx.TextCtrl(self.ScrollPanel, value='', pos=(136, 894), size=(50, 17))

        #設定字體大小
        self.StaticTextGrayMeanValue.SetFont(font_title)
        self.StaticTextTitleCoordinate.SetFont(font_title)

        #self.CropImgMeanValue.SetFont(font)
        self.BrowseBut = wx.Button(self.ScrollPanel, label='Browse', pos=(50, 50))
        self.Bind(wx.EVT_BUTTON, self.ShowTheDialog, self.BrowseBut)

        self.ExportTxtBut = wx.Button(self.ScrollPanel, label='Export', pos=(146, 50))
        self.Bind(wx.EVT_BUTTON, self.ExportTxt, self.ExportTxtBut)

        self.RefreshBut = wx.Button(self.ScrollPanel, label='Refresh', pos=(242, 50))
        self.Bind(wx.EVT_BUTTON, self.Processing, self.RefreshBut)

        self.PlotCanvas = FloatCanvas.FloatCanvas(self.PlotPanel, -1, size=(648, 486), BackgroundColor='black')

        self.RaidoButton_lt = wx.RadioButton(self.ScrollPanel, label='Left-Top Square', pos=(50, 572))
        self.RaidoButton_rt = wx.RadioButton(self.ScrollPanel, label='Right-Top Square', pos=(170, 572))
        self.RaidoButton_lb = wx.RadioButton(self.ScrollPanel, label='Left-Bottom Square', pos=(297, 572))
        self.RaidoButton_rb = wx.RadioButton(self.ScrollPanel, label='Right-Bottom Square', pos=(434, 572))
        self.RaidoButton_mm = wx.RadioButton(self.ScrollPanel, label='Mid Square', pos=(580, 572))

        self.count = 0
        #self.Gauge = wx.Gauge(self.ScrollPanel, range=11, pos=(500, 55), style=wx.GA_SMOOTH)

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

        self.Processing(event=None)

    def Processing(self, event):
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
            self.Gauge = wx.ProgressDialog('Processing', 'Please wait....', maximum=100000, parent=None)
            while True:
                self.count = self.count + 0.1
                self.Gauge.Update(self.count, str(int(self.count*100/100000))+'%')
                if self.count >= 100000:
                    wx.StaticBitmap(self.PlotBiPanel, -1, bmp, (0, 0))
                    self.count = 0
                    break
        self.Gauge.Destroy()

        TEST_FOLDER = 'calibration_samples'
        template = cv2.imread(os.path.join(TEST_FOLDER, 'template.bmp'), cv2.IMREAD_COLOR)

        if self.ChoiceForDisease.GetValue()=='Flu A':
            match_locations, res = detectAndRemoveSame(img, template, 2)
            print(match_locations)
        if self.ChoiceForDisease.GetValue()=='Flu B':
            match_locations, res = detectAndRemoveSame(img, template, 3)


        #
        # template = cv2.imread(tempPath)
        # w = template.shape[1]
        # h = template.shape[0]
        #
        # methods = ['cv2.TM_SQDIFF_NORMED']
        #
        # for meth in methods:
        #     img = img2.copy()
        #     method = eval(meth)
        #
        #     res = cv2.matchTemplate(img, template, method)
        #     min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
        #
        #     if method in [cv2.TM_SQDIFF, cv2.TM_SQDIFF_NORMED]:
        #         top_left = min_loc
        #     else:
        #         top_left = max_loc
        #     bottom_right = (top_left[0] + w, top_left[1] + h)



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

        height, width, nrgb = tt.shape

        self.PhotoMaxSize = 648
        if width > height:
            NewW = self.PhotoMaxSize
            NewH = self.PhotoMaxSize * height / width
        else:
            NewH = self.PhotoMaxSize
            NewW = self.PhotoMaxSize * width / height

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
            DeltaX = 48
            DeltaY = 44
            MoveW, MoveH = (0*NewW/width, 0*NewH/height) #(560*NewW/width, 200*NewH/height)
            self.DeltaW = 0 #560
            self.DeltaH = 0 #200
        elif self.ChoiceForDisease.GetValue() == 'Flu B':
            DeltaX = 49
            DeltaY = 43
            MoveW, MoveH = (560 * NewW / width, 200 * NewH / height)
            self.DeltaW = 560
            self.DeltaH = 200
        elif self.ChoiceForDisease.GetValue() == 'StrepA':
            DeltaX = 40
            DeltaY = 43
            MoveW, MoveH = (920 * NewW / width, 200 * NewH / height)
            self.DeltaW = 920
            self.DeltaH = 200
        elif self.ChoiceForDisease.GetValue() == 'RSV':
            DeltaX = -5
            DeltaY = -3
            MoveW, MoveH = (920 * NewW / width, 200 * NewH / height)
            self.DeltaW = 920
            self.DeltaH = 200
        elif self.ChoiceForDisease.GetValue() == 'hMPV':
            DeltaX = -5
            DeltaY = -3
            MoveW, MoveH = (920 * NewW / width, 200 * NewH / height)
            self.DeltaW = 920
            self.DeltaH = 200

        MoveW_sq, MoveH_sq = (220 * NewW / width, 220 * NewH / height)
        self.DeltaW_sq = 220
        self.DeltaH_sq = 220

        StartX = (match_locations[0][0]-DeltaX - width / 2) * scaleW
        StartY = -(match_locations[0][1]-DeltaY - height / 2) * scaleH
        # EndX = (bottom_right[0]-DeltaX - width / 2) * scaleW
        # EndY = -(bottom_right[1]-DeltaY - height / 2) * scaleH
        # EndX = (top_left[0]+DeltaX - width / 2) * scaleW
        # EndY = -(top_left[1]+DeltaY - height / 2) * scaleH
        StartXY = (StartX, StartY)
        EndXY = StartXY
        Original_coord = StartXY
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

        ###中間偵測結果方塊#################################################
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
        # self.TopLeft = top_left
        # self.BottomRight = bottom_right
        # self.width = w-DeltaX*2
        # self.height = h-DeltaY*2
        self.NewW = NewW
        self.NewH = NewH
        self.scaleW = NewW / width
        self.scaleH = NewH / height
        self.MoveW_sq = MoveW_sq
        self.MoveH_sq = MoveH_sq
        self.MoveW = MoveW
        self.MoveH = MoveH
        #########Call Function##############################


        self.ShowAngle()
        #self.Text = 'Coordinate :' + '\n' + 'Point1 : ' + str(self.TopLeftCoord) + '\n' + 'Point2 : ' + str(self.RightBotCoord) + '\n' + 'Rotation : %d°' % self.getAngle[0]+'\n\n'
        #self.Text = self.Text + 'Gray mean value :' + '\n' + 'Top-Left :' + str(self.lt_mean_value) + '\n' + 'Top-Right :' + str(self.rt_mean_value) + '\n' + 'Bottom-Left :' + str(self.lb_mean_value) + '\n' + 'Bottom-Right :' + str(self.rb_mean_value)+'\n'+'Mid :'+str(self.mm_mean_value)

        self.TextCtrlPoint1.SetValue(str(StartXY))

        self.TextCtrlTopRight.SetValue(str(self.rt_mean_value))
        self.TextCtrlBottomLeft.SetValue(str(self.lb_mean_value))
        self.TextCtrlBottomRight.SetValue(str(self.rb_mean_value))
        self.TextCtrlTopLeft.SetValue(str(self.lt_mean_value))
        self.TextCtrlMid.SetValue(str(self.mm_mean_value))


    def ShowCropImgMeanValue(self, x, y):
        if self.click_lt==True:
            crop_img_lt = cv2.cvtColor(self.img[y:y+220, x:x+220], cv2.COLOR_RGB2GRAY) #左上
            self.lt_mean_value, g, r, a = np.uint8(cv2.mean(crop_img_lt))
        if self.click_rt == True:
            crop_img_rt = cv2.cvtColor(self.img[y:y+220, x:x+220], cv2.COLOR_RGB2GRAY) #右上
            self.rt_mean_value, g, r, a = np.uint8(cv2.mean(crop_img_rt))
        if self.click_lb == True:
            crop_img_lb = cv2.cvtColor(self.img[y:y+220, x:x+220], cv2.COLOR_RGB2GRAY) #左下
            self.lb_mean_value, g, r, a = np.uint8(cv2.mean(crop_img_lb))
        if self.click_rb == True:
            crop_img_rb = cv2.cvtColor(self.img[y:y+220, x:x+220], cv2.COLOR_RGB2GRAY) #右下
            self.rb_mean_value, g, r, a = np.uint8(cv2.mean(crop_img_rb))
        if self.click_mm == True:
            crop_img_mm = cv2.cvtColor(self.img[y:y+220, x:x+220], cv2.COLOR_RGB2GRAY)  #中間
            self.mm_mean_value, g, r, a = np.uint8(cv2.mean(crop_img_mm))

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

    def OnHitMark(self, object):
        self.dragObject = object
        self.click = True
        self.RaidoButton_lt.SetValue(False)
        self.RaidoButton_rt.SetValue(False)
        self.RaidoButton_lb.SetValue(False)
        self.RaidoButton_rb.SetValue(False)
        self.RaidoButton_mm.SetValue(False)

    def OnHitMark_lt(self, object):
        self.dragObject = object
        self.click_lt = True
        self.MoveObjectDetection(400/4, 670/4, self.dragStartPt, self.DeltaW_sq, self.DeltaH_sq)
        self.RaidoButton_lt.SetValue(True)
        self.RaidoButton_rt.SetValue(False)
        self.RaidoButton_lb.SetValue(False)
        self.RaidoButton_rb.SetValue(False)
        self.RaidoButton_mm.SetValue(False)

    def OnHitMark_rt(self, object):
        self.dragObject = object
        self.click_rt = True
        self.MoveObjectDetection(1980/4, 670/4, self.dragStartPt, self.DeltaW_sq, self.DeltaH_sq)
        self.RaidoButton_rt.SetValue(True)
        self.RaidoButton_lt.SetValue(False)
        self.RaidoButton_lb.SetValue(False)
        self.RaidoButton_rb.SetValue(False)
        self.RaidoButton_mm.SetValue(False)

    def OnHitMark_lb(self, object):
        self.dragObject = object
        self.click_lb = True
        self.MoveObjectDetection(400/4, 1110/4, self.dragStartPt, self.DeltaW_sq, self.DeltaH_sq)
        self.RaidoButton_lb.SetValue(True)
        self.RaidoButton_lt.SetValue(False)
        self.RaidoButton_rt.SetValue(False)
        self.RaidoButton_rb.SetValue(False)
        self.RaidoButton_mm.SetValue(False)

    def OnHitMark_rb(self, object):
        self.dragObject = object
        self.click_rb = True
        self.MoveObjectDetection(1980/4, 1110/4, self.dragStartPt, self.DeltaW_sq, self.DeltaH_sq)
        self.RaidoButton_rb.SetValue(True)
        self.RaidoButton_lt.SetValue(False)
        self.RaidoButton_rt.SetValue(False)
        self.RaidoButton_lb.SetValue(False)
        self.RaidoButton_mm.SetValue(False)

    def OnHitMark_mm(self, object):
        self.dragObject = object
        self.click_mm = True
        self.MoveObjectDetection(1190/4, 875/4, self.dragStartPt, self.DeltaW_sq, self.DeltaH_sq)
        self.RaidoButton_mm.SetValue(True)
        self.RaidoButton_lt.SetValue(False)
        self.RaidoButton_rt.SetValue(False)
        self.RaidoButton_lb.SetValue(False)
        self.RaidoButton_rb.SetValue(False)

    def OnMouseLeftUp(self, event):
        try:
            self.ShowCropImgMeanValue(int(self.TopLeftImgX), int(self.TopLeftImgY))
        except AttributeError:
            pass

        self.TextCtrlTopRight.SetValue(str(self.rt_mean_value))
        self.TextCtrlBottomLeft.SetValue(str(self.lb_mean_value))
        self.TextCtrlBottomRight.SetValue(str(self.rb_mean_value))
        self.TextCtrlTopLeft.SetValue(str(self.lt_mean_value))
        self.TextCtrlMid.SetValue(str(self.mm_mean_value))

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
        self.TopLeftImgX = int(x_coord/self.scaleW)
        self.TopLeftImgY = int(y_coord/self.scaleH)
        self.TopLeftCoord = (int((self.TopLeftImgX+DeltaW/2)), int((self.TopLeftImgY+DeltaH/2)))

        #self.Text = 'Coordinate :'+'\n'+'Point1 : '+str(self.TopLeftCoord)+'\n'+'Point2 : '+str(self.RightBotCoord)+'\n'+'Rotation : %d°' % self.getAngle[0]+'\n\n'
        #self.Text = self.Text+'Gray mean value :'+'\n'+'Top-Left :'+str(self.lt_mean_value)+'\n'+'Top-Right :'+str(self.rt_mean_value)+'\n'+'Bottom-Left :'+str(self.lb_mean_value)+'\n'+'Bottom-Right :'+str(self.rb_mean_value)+'\n'+'Mid :'+str(self.mm_mean_value)

        self.TextCtrlPoint1.SetValue(str(self.TopLeftCoord))

    def ExportTxt(self,event):
        full_path = "./Text/"
        try:
            os.makedirs(full_path)
        except FileExistsError:
            pass
            #print("檔案已存在。")
        file = open(full_path+'Record.txt', 'w')
        file.write(self.Text)


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
#pyinstaller -w --add-data "Text;Text" --add-data "DetectSample;DetectSample" --add-data "FullImagesSamples;FullImagesSamples" BoundaryDetect_version2.py -n "BoundaryDetect v0.4.2"
