﻿import numpy as np
import wx
import os
import cv2
from ..algorithm.VirusDetectAlgo import *
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from matplotlib.figure import Figure
from pandas import DataFrame
from PIL import Image
from wx.lib.scrolledpanel import ScrolledPanel
from .base import BasePanel, DiseaseParams
from wx.lib.floatcanvas import FloatCanvas, FCObjects
from wx.lib.floatcanvas.FCObjects import ScaledBitmap, Rectangle, Bitmap
from decimal import *


class DetectionPanel(BasePanel):

    def __init__(self, *args, **kw):
        #####Set Scrooled Panel########################
        super().__init__(*args, **kw)                 #
        self.panel = wx.ScrolledWindow(parent=self)   #
        #self.panel.SetBackgroundColour((255,255,0))  #
        self.panel.SetScrollbars(1, 1, 1, 1200)       #
        self.panel.SetScrollRate(0, 10)               #
        boxSizer = wx.BoxSizer(wx.VERTICAL)           #
        boxSizer.Add(self.panel)                      #
        self.SetSizer(boxSizer)                       #
        ###############################################

        #####Set the photo size###########################
        self.PhotoMaxSize = 350

        #####Set the left panels##########################
        self.LoadOriginalImgPanel = wx.Panel(parent=self.panel, id=wx.ID_ANY, size=(500, 500), pos=(50, 30), style=0)
        #self.LoadOriginalImgPanel.SetBackgroundColour((0, 255, 0))

        self.OriginalStatisticsPanel = wx.Panel(self.LoadOriginalImgPanel, id=wx.ID_ANY, size=(450, 200), pos=(0, 235), style=0)
        #self.OriginalStatisticsPanel.SetBackgroundColour((0, 0, 255))

        self.LoadEnhanceImgPanel = wx.Panel(self.panel, id=wx.ID_ANY, size=(500, 500), pos=(50, 560), style=0)
        #self.LoadEnhanceImgPanel.SetBackgroundColour((0, 255, 0))

        self.EnhancedStatisticsPanel = wx.Panel(self.LoadEnhanceImgPanel, id=wx.ID_ANY, size=(450, 200), pos=(0, 235), style=0)
        #self.EnhancedStatisticsPanel.SetBackgroundColour((255, 0, 0))

        #####Set the right panels#########################
        self.SlopeFigurePanel = wx.Panel(self.panel, id=wx.ID_ANY, size=(2000, 1017), pos=(550, 380), style=wx.TAB_TRAVERSAL)
        #self.SlopeFigurePanel.SetBackgroundColour((0, 255, 0))

        self.SlopeStatisticsPanel = wx.Panel(self.panel, id=wx.ID_ANY, size=(500, 220), pos=(555, 5), style=0)
        #self.SlopeStatisticsPanel.SetBackgroundColour((0, 0, 255))

        #####Set Float Cavans#############################
        self.OriginalImg = FloatCanvas.FloatCanvas(self.LoadOriginalImgPanel, -1, size=(500, 190), BackgroundColor='black')
        self.EnhanceImg = FloatCanvas.FloatCanvas(self.LoadEnhanceImgPanel, -1, size=(500, 190), BackgroundColor='black')

        #####Set the buttons##############################
        OkTestLineBut = wx.Button(self.SlopeFigurePanel, label='OK', pos=(320, 286), size=(50, 50))
        OkTestLineBut.Bind(wx.EVT_BUTTON, self.TestLine)

        # CalBut = wx.Button(self.SlopeFigurePanel, label='Calculate', pos=(470, 10000))
        # CalBut.Bind(wx.EVT_BUTTON, self.Calculate)
        #####Show the StaticText##########################
        self.ShowStaticText()

        #####Show the TextCtrl############################
        self.ShowTextCtrl()
        self.ShowResultTextCtrl()

        #####Show the Virus option########################
        self.VirusColorOption()

        #####Show the CheckBox for enhance################
        self.CheckBoxForEnhance()
        #self.CheckBoxEnhance.Bind(wx.EVT_CHECKBOX, self.TestLineWithEnhanceComboBox)

        #####Show the CheckBox for 4 blocks###############
        self.CheckBoxFor4Blocks()

        #####Show the CheckBox for White Balance##########
        self.CheckBoxForWhiteBalance()
        #self.CheckBoxUseWhiteBalance.Bind(wx.EVT_CHECKBOX, self.TestLineWithWhiteBlanceComboBox)


        #####Show the ScrollMenu##########################
        self.ScrollMenu()

        #####Show the CheckBox for UseFilter##############
        #self.CheckBoxForUseFilter()

        ##Show the CheckBox & ComboBox for SmoothFilter###
        self.CheckBoxAndComboBoxForSmoothFilter()

        #####Set default parameters#######################
        self.DefaultParameters()

        #####Set disease##################################
        self.ChoiceForDisease.Bind(wx.EVT_COMBOBOX, self.SetDefaultParameters)



        #####Build Rect##################################
        self.BuildRect()

        #####Set Figure Cavans############################
        self.OriginalImgFig = Figure()
        self.OriginalImgChart = FigureCanvas(self.OriginalStatisticsPanel, -1, self.OriginalImgFig)

        self.EnhancedImgFig = Figure()
        self.EnhancedImgChart = FigureCanvas(self.EnhancedStatisticsPanel, -1, self.EnhancedImgFig)

        # self.SlopeFigure = Figure()
        # self.SlopeFigureChart = FigureCanvas(self.SlopeStatisticsPanel, -1, self.SlopeFigure)

        self.StaticBoxLeftTop = wx.StaticBox(self.panel, id=wx.ID_ANY, label='Original Image', pos=(45, 13), size=(510, 490))
        self.StaticBoxLeftBot = wx.StaticBox(self.panel, id=wx.ID_ANY, label='Enhanced Image', pos=(45, 525), size=(510, 490))

        self.ClickBtnPN()

        self.PnThresholdBut.Bind(wx.EVT_BUTTON, self.GeneratePN)
        self.CheckBoxBlocks.Bind(wx.EVT_CHECKBOX, self.CheckBox4BlocksEvent)

    def GetLoadingImgPath(self):
        pass

    def SetLoadingImgPath(self, ImgPath):
        self.ImgPath = ImgPath


    def GetTabImgRes(self):
        return None

    def SetTabImgRes(self, img):

        if img is not None:

            self.img = img
            self.OriginalImgMat = np.asarray(img.GetDataBuffer())
            W, H = img.GetSize()
            self.OriginalImgMat = np.reshape(self.OriginalImgMat, (H, W, 3))
            if W > H:
                self.NewW = self.PhotoMaxSize
                self.NewH = self.PhotoMaxSize * H / W
            else:
                self.NewH = self.PhotoMaxSize
                self.NewW = self.PhotoMaxSize * W / H
            self.W = W
            self.H = H
            self.ScaledImg = img.Scale(self.NewW, self.NewH)


            #####Add the original pic########################
            self.BitmapImg = Bitmap(wx.Bitmap(self.ScaledImg), (0, 0), Position='cc', InForeground=False)
            # self.OriginalImg.ClearAll(ResetBB=True)
            # self.OriginalImg.AddObject(self.BitmapImg)
            # self.OriginalImg.Draw(True)

            #####Call function###############################
            self.EnhanceImage()
            self.WhiteBalanceImage()
            self.EnhanceAndWhiteBalanceImage()
            self.numpy2wximage()

            self.boundary_original_rect = None
            self.boundary_enhanced_rect = None
            self.boundary_original_ctrl_rect = None
            self.boundary_enhanced_ctrl_rect = None

    def BuildRect(self):
        self.Rect1 = None
        self.Rect2 = None
        self.Rect3 = None
        self.Rect4 = None
        self.Rect5 = None
        self.Rect6 = None
        self.Rect7 = None
        self.Rect8 = None

    def EnhanceImage(self):
        r=[];g=[];b=[]
        W, H = self.img.GetSize()
        for y in range(H):
            for x in range(W):
                r.append((self.img.GetRed(x, y)))
                g.append((self.img.GetGreen(x, y)))
                b.append((self.img.GetBlue(x, y)))
        r = np.array(r).reshape(len(r), 1)
        g = np.array(g).reshape(len(g), 1)
        b = np.array(b).reshape(len(b), 1)
        image_matrix = np.hstack((r, g, b))
        image_matrix = np.reshape(image_matrix, (H, W, 3))
        im = gamma_enhance(image_matrix, enhance_value=2)
        self.EnhancedImgMat = im

    def WhiteBalanceImage(self):
        r=[];g=[];b=[]
        W, H = self.img.GetSize()
        for y in range(H):
            for x in range(W):
                r.append((self.img.GetRed(x, y)))
                g.append((self.img.GetGreen(x, y)))
                b.append((self.img.GetBlue(x, y)))
        r = np.array(r).reshape(len(r), 1)
        g = np.array(g).reshape(len(g), 1)
        b = np.array(b).reshape(len(b), 1)
        image_matrix = np.hstack((r, g, b))
        image_matrix = np.reshape(image_matrix, (H, W, 3))
        im = white_balance(image_matrix)
        self.WhiteBalanceImgMat = im
        print(self.WhiteBalanceImgMat)

    def EnhanceAndWhiteBalanceImage(self):
        r=[];g=[];b=[]
        W, H = self.img.GetSize()
        for y in range(H):
            for x in range(W):
                r.append((self.img.GetRed(x, y)))
                g.append((self.img.GetGreen(x, y)))
                b.append((self.img.GetBlue(x, y)))
        r = np.array(r).reshape(len(r), 1)
        g = np.array(g).reshape(len(g), 1)
        b = np.array(b).reshape(len(b), 1)
        image_matrix = np.hstack((r, g, b))
        image_matrix = np.reshape(image_matrix, (H, W, 3))
        self.original_image_matrix = image_matrix
        im = gamma_enhance(image_matrix, enhance_value=2)
        im = white_balance(im)
        self.EnhanceWhiteBalanceImgMat = im


    def numpy2wximage(self):
        width = self.W
        height = self.H
        #load EnhanceImage and WhiteBalanceImage and EnhanceWhiteBalance Image
        image_matrix_enhance = self.EnhancedImgMat
        image_matrix_whitebalance = self.WhiteBalanceImgMat
        image_matrix_enhance_whitebalance = self.EnhanceWhiteBalanceImgMat

        wxbmp_enhance = wx.Bitmap.FromBuffer(width, height, image_matrix_enhance)
        wxbmp_whitebalance = wx.Bitmap.FromBuffer(width, height, image_matrix_whitebalance)
        wxbmp_enhance_whitebalance = wx.Bitmap.FromBuffer(width, height, image_matrix_enhance_whitebalance)

        wxImage_enhance = wxbmp_enhance.ConvertToImage()
        wxImage_whitebalance = wxbmp_whitebalance.ConvertToImage()
        wxImage_enhance_whitebalance = wxbmp_enhance_whitebalance.ConvertToImage()

        if width > height:
            NewW = self.PhotoMaxSize
            NewH = self.PhotoMaxSize * height / width
        else:
            NewH = self.PhotoMaxSize
            NewW = self.PhotoMaxSize * width / height

        wxImage_enhance = wxImage_enhance.Scale(NewW, NewH)
        wxImage_whitebalance = wxImage_whitebalance.Scale(NewW, NewH)
        wxImage_enhance_whitebalance = wxImage_enhance_whitebalance.Scale(NewW, NewH)

        #####Add the original pic########################
        self.EnhancedBitmapImg = Bitmap(wx.Bitmap(wxImage_enhance), (0, 0), Position='cc', InForeground=False)
        self.WhiteBalanceBitmapImg = Bitmap(wx.Bitmap(wxImage_whitebalance), (0, 0), Position='cc', InForeground=False)
        self.EnhancedWhiteBalanceBitmapImg = Bitmap(wx.Bitmap(wxImage_enhance_whitebalance), (0, 0), Position='cc', InForeground=False)

        # self.EnhanceImg.ClearAll(ResetBB=True)
        # self.EnhanceImg.AddObject(self.EnhancedBitmapImg)
        # self.EnhanceImg.Draw(True)

    def ShowPlot(self, im):
        image = np.array(im)
        r, g, b = image[:, :, 0], image[:, :, 1], image[:, :, 2]
        r = np.average(np.transpose(r), axis=1)
        g = np.average(np.transpose(g), axis=1)
        b = np.average(np.transpose(b), axis=1)
        gray = np.average(np.average(np.transpose(image), axis=0), axis=1)
        pic_width_pixel = np.size(r, 0)
        df = pd.DataFrame({'x': range(0, pic_width_pixel), 'j1': r, 'j2': g, 'j3': b, 'j4': gray})
        return df

    def ShowPlot_Enhance(self, im):
        image = np.array(im)
        if self.CheckBoxEnhance.GetValue()==True and self.CheckBoxUseWhiteBalance.GetValue()==False:
            image = gamma_enhance(image)
        elif self.CheckBoxEnhance.GetValue()==True and self.CheckBoxUseWhiteBalance.GetValue()==True:
            image = gamma_enhance(image)
            image = white_balance(image)
        elif self.CheckBoxEnhance.GetValue() == False and self.CheckBoxUseWhiteBalance.GetValue() == True:
            image = white_balance(image)
        else:
            image = image
        r, g, b = image[:, :, 0], image[:, :, 1], image[:, :, 2]
        r = np.average(np.transpose(r), axis=1)
        g = np.average(np.transpose(g), axis=1)
        b = np.average(np.transpose(b), axis=1)
        gray = np.average(np.average(np.transpose(image), axis=0), axis=1)
        pic_width_pixel = np.size(r, 0)
        df = pd.DataFrame({'x': range(0, pic_width_pixel), 'j1': r, 'j2': g, 'j3': b, 'j4': gray})
        return df

    def ReturnSlopeDF(self, df_array):
        pic_width_pixel = len(df_array)
        df = pd.DataFrame({'x': range(0, pic_width_pixel), 'j1': df_array})
        return df

    def ShowStaticText(self):

        #########Result Title#####
        self.StatictxtResltTitleLeft = wx.StaticText(self.panel, label='Control Line', pos=(600, 240))
        self.StatictxtResltTitleRight = wx.StaticText(self.panel, label='Test Line', pos=(800, 240))

        self.StatictextCtrlLineResult = wx.StaticText(self.panel, label='Result : ', pos=(600, 257))
        self.StatictextCtrlLineMax = wx.StaticText(self.panel, label='Max Value : ', pos=(600, 282))
        self.StatictextCtrlLineMin = wx.StaticText(self.panel, label='Min Value : ', pos=(600, 307))
        self.StatictextCtrlLinePeak = wx.StaticText(self.panel, label='MaxPeak : ', pos=(600, 332))

        self.StatictextTestLineResult = wx.StaticText(self.panel, label='Result : ', pos=(800, 257))
        self.StatictextTestLineMax = wx.StaticText(self.panel, label='Max Value : ', pos=(800, 282))
        self.StatictextTestLineMin = wx.StaticText(self.panel, label='Min Value : ', pos=(800, 307))
        self.StatictextTestLinePeak = wx.StaticText(self.panel, label='MaxPeak : ', pos=(800, 332))

        self.ResultText = wx.StaticText(self.SlopeFigurePanel, label='Result : ', pos=(50, 10))
        self.statictext_virus_title = wx.StaticText(self.SlopeFigurePanel, label='Disease : ', pos=(50, 40))

        #########Control Line Input Para Area#####
        self.StatictextCtrlLineTitle = wx.StaticText(self.SlopeFigurePanel, label='Control Line', pos=(50, 100))
        self.StatictextCtrlLineColor = wx.StaticText(self.SlopeFigurePanel, label='RGB Color ', pos=(50, 130))
        self.StatictextCtrlLineSt = wx.StaticText(self.SlopeFigurePanel, label='Strides Threshold : ', pos=(50, 160))
        self.StatictextCtrlLinePN = wx.StaticText(self.SlopeFigurePanel, label='PN Threshold : ', pos=(50, 190))
        self.StatictextCtrlLineRS = wx.StaticText(self.SlopeFigurePanel, label='Range of Start : ', pos=(50, 220))
        self.StatictextCtrlLineRE = wx.StaticText(self.SlopeFigurePanel, label='Range of End : ', pos=(50, 250))

        #########Test Line Input Para Area########
        self.StatictextTestLineTitle = wx.StaticText(self.SlopeFigurePanel, label='Test Line', pos=(320, 100))
        self.StatictextTestLineSt = wx.StaticText(self.SlopeFigurePanel, label='Strides Threshold : ', pos=(320, 160))
        self.StatictextTestLinePN = wx.StaticText(self.SlopeFigurePanel, label='PN Threshold : ', pos=(320, 190))
        self.StatictextTestLineRS = wx.StaticText(self.SlopeFigurePanel, label='Range of Start : ', pos=(320, 220))
        self.StatictextTestLineRE = wx.StaticText(self.SlopeFigurePanel, label='Range of End : ', pos=(320, 250))

        self.StdTxt = wx.StaticText(self.SlopeFigurePanel, label='Std. Value', pos=(507, 170))

    def ShowTextCtrl(self):
        self.InputValueTxtGamma = wx.TextCtrl(parent=self.SlopeFigurePanel, pos=(71, 10000), size=(33, 23))
        #########Control Line#####
        self.InputValueTxtCtrlLineSt = wx.TextCtrl(self.SlopeFigurePanel, pos=(157, 160), size=(33, 23))
        self.InputValueTxtCtrlLinePN = wx.TextCtrl(self.SlopeFigurePanel, pos=(157, 190), size=(33, 25))
        self.InputValueTxtCtrlLineRS = wx.TextCtrl(self.SlopeFigurePanel, pos=(157, 220), size=(33, 23))
        self.InputValueTxtCtrlLineRE = wx.TextCtrl(self.SlopeFigurePanel, pos=(157, 250), size=(33, 23))

        #########Test Line########
        self.InputValueTxtTestLineSt = wx.TextCtrl(self.SlopeFigurePanel, pos=(427, 160), size=(33, 23))
        self.InputValueTxtTestLinePN = wx.TextCtrl(self.SlopeFigurePanel, pos=(427, 190), size=(33, 25))
        self.InputValueTxtTestLineRS = wx.TextCtrl(self.SlopeFigurePanel, pos=(427, 220), size=(33, 23))
        self.InputValueTxtTestLineRE = wx.TextCtrl(self.SlopeFigurePanel, pos=(427, 250), size=(33, 23))

        ###Control line Result###
        #self.CtrlLineResult = wx.TextCtrl(self.SlopeStatisticsPanel, pos=(224, 243), size=(33, 23))#203 357


    def ShowResultTextCtrl(self):
        #str = 'Result : \nMax Value : \nMini Value : \nMaxPeak : '
        # self.TextCtrlLineResult = wx.TextCtrl(self.SlopeStatisticsPanel, style=wx.TE_MULTILINE|wx.TE_READONLY|wx.NO_BORDER, value=str,id=wx.ID_ANY, pos=(50, 259), size=(150, 70))
        # self.TextTestLineResult = wx.TextCtrl(self.SlopeStatisticsPanel, style=wx.TE_MULTILINE|wx.TE_READONLY|wx.NO_BORDER, value=str,id=wx.ID_ANY, pos=(320, 259), size=(150, 70))
        self.CtrlLineResult = wx.TextCtrl(self.panel, pos=(680, 255), size=(70, 20))  # 203 357
        self.CtrlLineMaxValue = wx.TextCtrl(self.panel, pos=(680, 280), size=(70, 20))  # 203 357
        self.CtrlLineMinValue = wx.TextCtrl(self.panel, pos=(680, 305), size=(70, 20))  # 203 357
        self.CtrlLineMaxPeak = wx.TextCtrl(self.panel, pos=(680, 330), size=(70, 20))  # 203 357

        self.TestLineResult = wx.TextCtrl(self.panel, pos=(880, 255), size=(70, 20))  # 203 357
        self.TestLineMaxValueText = wx.TextCtrl(self.panel, pos=(880, 280), size=(70, 20))  # 203 357
        self.TestLineMinValueText = wx.TextCtrl(self.panel, pos=(880, 305), size=(70, 20))  # 203 357
        self.TestLineMaxPeakText = wx.TextCtrl(self.panel, pos=(880, 330), size=(70, 20))  # 203 357


    def VirusColorOption(self):
        self.ChoiceForDisease = wx.ComboBox(self.SlopeFigurePanel, value='', pos=(114, 40), choices=['Flu A', 'Flu B', 'Myco', 'RSV', 'hMPV', 'StrepA'], size=(100, 20))
        self.ChoiceForCtrlLineRGB = wx.ComboBox(self.SlopeFigurePanel, value='', pos=(114, 130), choices=['R', 'G', 'B'], size=(100, 20))
        self.ChoiceForTestLineRGB = wx.ComboBox(self.SlopeFigurePanel, value='', pos=(320, 130), choices=['R', 'G', 'B'], size=(100, 20))

    def CheckBoxForEnhance(self):
        self.CheckBoxEnhance = wx.CheckBox(self.panel, id=wx.ID_ANY, label='Enhance', pos=(56, 544))
        self.CheckBoxEnhance.SetValue(True)

    # def CheckBoxForUseFilter(self):
    #     self.CheckBoxUseFilter = wx.CheckBox(self.SlopeFigurePanel, id=wx.ID_ANY, label='Use Filter', pos=(150, 420))
    #     self.CheckBoxUseFilter.Bind(wx.EVT_CHECKBOX, self.SetDefaultParameters)
    #     self.CheckBoxUseFilter.SetValue(True)
    #     if self.CheckBoxUseFilter.GetValue()==True:
    #         self.useFilter = True
    #     else:
    #         self.useFilter = False

    def CheckBoxAndComboBoxForSmoothFilter(self):
        self.CheckBoxUseSmoothFilter = wx.CheckBox(self.SlopeFigurePanel, id=wx.ID_ANY, label='Use SmoothFilter', pos=(50, 70))
        self.CheckBoxUseSmoothFilter.SetValue(True)
        self.ComboBoxSmoothFilter = wx.ComboBox(self.SlopeFigurePanel, id=wx.ID_ANY, value='3', choices=['3', '5', '7', '9', '11', '13', '15'], pos=(170, 67))


    def CheckBoxFor4Blocks(self):
        self.CheckBoxBlocks = wx.CheckBox(self.SlopeFigurePanel, id=wx.ID_ANY, label='4 Blocks Detection', pos=(230, 70))
        self.CheckBoxBlocks.SetValue(False)

    def CheckBox4BlocksEvent(self, event):
        if self.CheckBoxBlocks.GetValue()==True:
            self.StdValue.SetValue('2')
        else:
            self.StdValue.SetValue('4')
        self.GeneratePN4Blocks()

    def CheckBoxForWhiteBalance(self):
        self.CheckBoxUseWhiteBalance = wx.CheckBox(self.panel, id=wx.ID_ANY, label='White Balance', pos=(136, 544))
        self.CheckBoxUseWhiteBalance.SetValue(True)


    def ScrollMenu(self):
        #4Blocks選單
        self.BlockNum = wx.ComboBox(self.SlopeFigurePanel, value='4', choices=['4', '3', '2', '1'], pos=(356, 67))
        #標準差選單
        self.StdValue = wx.ComboBox(self.SlopeFigurePanel, value='4', choices=['5', '4', '3', '2', '1'], pos=(510, 188), size=(51, 22))

    def ClickBtnPN(self):
        self.PnThresholdBut = wx.Button(self.SlopeFigurePanel, label='Cal.', pos=(475, 187), size=(30,25))

    def DefaultParameters(self):
        self.ChoiceForDisease.SetSelection(0)
        line_para_map = get_line_para_map('FluA')

        #####Test line default parameters############
        self.ChoiceForTestLineRGB.SetSelection(line_para_map[1][0])
        self.InputValueTxtGamma.SetValue('2')
        self.InputValueTxtTestLineSt.SetValue(str(line_para_map[1][3]))
        self.InputValueTxtTestLinePN.SetValue(str(line_para_map[1][4]))
        self.InputValueTxtTestLineRS.SetValue(str(line_para_map[1][1]))
        self.InputValueTxtTestLineRE.SetValue(str(line_para_map[1][2]))

        #####Control line default parameters#########
        self.ChoiceForCtrlLineRGB.SetSelection(line_para_map[0][0])
        self.InputValueTxtGamma.SetValue('2')
        self.InputValueTxtCtrlLineSt.SetValue(str(line_para_map[0][3]))
        self.InputValueTxtCtrlLinePN.SetValue(str(line_para_map[0][4]))
        self.InputValueTxtCtrlLineRS.SetValue(str(line_para_map[0][1]))
        self.InputValueTxtCtrlLineRE.SetValue(str(line_para_map[0][2]))

    def SetDefaultParameters(self, event):
        if self.CheckBoxUseSmoothFilter.GetValue()==True:
            #self.useFilter = True
            para=[get_line_para_map('FluA'), get_line_para_map('FluB'), get_line_para_map('Myco'), get_line_para_map('RSV-hMPV'), get_line_para_map('StrepA')]
        else:
            #self.useFilter = False
            para=[get_line_para_map('FluA'), get_line_para_map('FluB'), get_line_para_map('Myco'), get_line_para_map('RSV-hMPV'), get_line_para_map('StrepA')]
        if self.ChoiceForDisease.GetValue() == 'Flu A':
            self.ChoiceForTestLineRGB.SetSelection(para[0][1][0])
            self.InputValueTxtGamma.SetValue('2')
            self.InputValueTxtTestLineSt.SetValue(str(para[0][1][3]))
            self.InputValueTxtTestLinePN.SetValue(str(para[0][1][4]))
            self.InputValueTxtTestLineRS.SetValue(str(para[0][1][1]))
            self.InputValueTxtTestLineRE.SetValue(str(para[0][1][2]))
            # self.ChoiceForCtrlLineRGB
            self.ChoiceForCtrlLineRGB.SetSelection(para[0][0][0])
            self.InputValueTxtCtrlLineSt.SetValue(str(para[0][0][3]))
            self.InputValueTxtCtrlLinePN.SetValue(str(para[0][0][4]))
            self.InputValueTxtCtrlLineRS.SetValue(str(para[0][0][1]))
            self.InputValueTxtCtrlLineRE.SetValue(str(para[0][0][2]))

        if self.ChoiceForDisease.GetValue() == 'Flu B':
            self.ChoiceForCtrlLineRGB.SetSelection(para[1][0][0])
            self.InputValueTxtGamma.SetValue('2')
            self.InputValueTxtCtrlLineSt.SetValue(str(para[1][0][3]))
            self.InputValueTxtCtrlLinePN.SetValue(str(para[1][0][4]))
            self.InputValueTxtCtrlLineRS.SetValue(str(para[1][0][1]))
            self.InputValueTxtCtrlLineRE.SetValue(str(para[1][0][2]))

            self.ChoiceForTestLineRGB.SetSelection(para[1][1][0])
            self.InputValueTxtTestLineSt.SetValue(str(para[1][1][3]))
            self.InputValueTxtTestLinePN.SetValue(str(para[1][1][4]))
            self.InputValueTxtTestLineRS.SetValue(str(para[1][1][1]))
            self.InputValueTxtTestLineRE.SetValue(str(para[1][1][2]))

        if self.ChoiceForDisease.GetValue() == 'Myco':
            self.ChoiceForCtrlLineRGB.SetSelection(para[2][0][0])
            self.InputValueTxtGamma.SetValue('2')
            self.InputValueTxtCtrlLineSt.SetValue(str(para[2][0][3]))
            self.InputValueTxtCtrlLinePN.SetValue(str(para[2][0][4]))
            self.InputValueTxtCtrlLineRS.SetValue(str(para[2][0][1]))
            self.InputValueTxtCtrlLineRE.SetValue(str(para[2][0][2]))

            self.ChoiceForTestLineRGB.SetSelection(para[2][1][0])
            self.InputValueTxtTestLineSt.SetValue(str(para[2][1][3]))
            self.InputValueTxtTestLinePN.SetValue(str(para[2][1][4]))
            self.InputValueTxtTestLineRS.SetValue(str(para[2][1][1]))
            self.InputValueTxtTestLineRE.SetValue(str(para[2][1][2]))

        if self.ChoiceForDisease.GetValue() == 'RSV':
            self.ChoiceForCtrlLineRGB.SetSelection(para[3][0][0])
            self.InputValueTxtGamma.SetValue('2')
            self.InputValueTxtCtrlLineSt.SetValue(str(para[3][0][3]))
            self.InputValueTxtCtrlLinePN.SetValue(str(para[3][0][4]))
            self.InputValueTxtCtrlLineRS.SetValue(str(para[3][0][1]))
            self.InputValueTxtCtrlLineRE.SetValue(str(para[3][0][2]))

            self.ChoiceForTestLineRGB.SetSelection(para[3][1][0])
            self.InputValueTxtTestLineSt.SetValue(str(para[3][1][3]))
            self.InputValueTxtTestLinePN.SetValue(str(para[3][1][4]))
            self.InputValueTxtTestLineRS.SetValue(str(para[3][1][1]))
            self.InputValueTxtTestLineRE.SetValue(str(para[3][1][2]))

        if self.ChoiceForDisease.GetValue() == 'hMPV':
            self.ChoiceForCtrlLineRGB.SetSelection(para[3][0][0])
            self.InputValueTxtGamma.SetValue('2')
            self.InputValueTxtCtrlLineSt.SetValue(str(para[3][0][3]))
            self.InputValueTxtCtrlLinePN.SetValue(str(para[3][0][4]))
            self.InputValueTxtCtrlLineRS.SetValue(str(para[3][0][1]))
            self.InputValueTxtCtrlLineRE.SetValue(str(para[3][0][2]))

            self.ChoiceForTestLineRGB.SetSelection(para[3][2][0])
            self.InputValueTxtTestLineSt.SetValue(str(para[3][2][3]))
            self.InputValueTxtTestLinePN.SetValue(str(para[3][2][4]))
            self.InputValueTxtTestLineRS.SetValue(str(para[3][2][1]))
            self.InputValueTxtTestLineRE.SetValue(str(para[3][2][2]))

        if self.ChoiceForDisease.GetValue() == 'StrepA':
            self.ChoiceForCtrlLineRGB.SetSelection(para[4][0][0])
            self.InputValueTxtGamma.SetValue('2')
            self.InputValueTxtCtrlLineSt.SetValue(str(para[4][0][3]))
            self.InputValueTxtCtrlLinePN.SetValue(str(para[4][0][4]))
            self.InputValueTxtCtrlLineRS.SetValue(str(para[4][0][1]))
            self.InputValueTxtCtrlLineRE.SetValue(str(para[4][0][2]))

            self.ChoiceForTestLineRGB.SetSelection(para[4][1][0])
            self.InputValueTxtTestLineSt.SetValue(str(para[4][1][3]))
            self.InputValueTxtTestLinePN.SetValue(str(para[4][1][4]))
            self.InputValueTxtTestLineRS.SetValue(str(para[4][1][1]))
            self.InputValueTxtTestLineRE.SetValue(str(para[4][1][2]))

    def GeneratePN(self, event):

        Disease = self.ChoiceForDisease.GetValue()

        ImgPathList = []

        if Disease=='Flu A':
            NegPath='./samples/FluA/0'
        elif Disease=='Flu B':
            NegPath='./samples/FluB/0'
        elif Disease=='Myco':
            NegPath='./samples/Myco/0'
        elif Disease == 'RSV':
            NegPath='./samples/RSV-hMPV/0'
        elif Disease=='hMPV':
            NegPath='./samples/RSV-hMPV/0'
        else:
            NegPath='./samples/StrepA/0'

        paths = os.listdir(NegPath)

        for i in range(len(paths)):
            if paths[i].find('ini') >= 0:
                pass
            else:
                ImgPathList.append(NegPath+'/'+paths[i])

        Ctrl_stride_threshold = int(self.InputValueTxtCtrlLineSt.GetValue())
        Ctrl_PN_Threshold = float(self.InputValueTxtCtrlLinePN.GetValue())
        Ctrl_start_interval = int(self.InputValueTxtCtrlLineRS.GetValue())
        Ctrl_end_interval = int(self.InputValueTxtCtrlLineRE.GetValue())
        Ctrl_RGB_Index = self.ChoiceForCtrlLineRGB.GetCurrentSelection()

        Test_stride_threshold = int(self.InputValueTxtTestLineSt.GetValue())
        Test_PN_Threshold = float(self.InputValueTxtTestLinePN.GetValue())
        Test_start_interval = int(self.InputValueTxtTestLineRS.GetValue())
        Test_end_interval = int(self.InputValueTxtTestLineRE.GetValue())
        Test_RGB_Index = self.ChoiceForTestLineRGB.GetCurrentSelection()

        Ctrl_para = [Ctrl_RGB_Index, Ctrl_start_interval, Ctrl_end_interval, Ctrl_stride_threshold, Ctrl_PN_Threshold]
        Test_para = [Test_RGB_Index, Test_start_interval, Test_end_interval, Test_stride_threshold, Test_PN_Threshold]

        line_parameters = [Ctrl_para, Test_para]

        if self.CheckBoxBlocks.GetValue()==True:
            self.pn1, self.pn2 = calculateCutOffValue4Block(ImgPathList, line_parameters, self.CheckBoxEnhance.GetValue(), self.CheckBoxUseWhiteBalance.GetValue(), self.CheckBoxUseSmoothFilter.GetValue(), smoothing_value=int(self.ComboBoxSmoothFilter.GetValue()), std_rate=int(self.StdValue.GetValue())) #Check2
            self.InputValueTxtTestLinePN.SetValue(str(np.round(self.pn1, decimals=3)))
        else:
            self.pn1, self.pn2 = calculateCutOffValue(ImgPathList, line_parameters, self.CheckBoxEnhance.GetValue(), self.CheckBoxUseWhiteBalance.GetValue(), self.CheckBoxUseSmoothFilter.GetValue(), smoothing_value=int(self.ComboBoxSmoothFilter.GetValue()), std_rate=int(self.StdValue.GetValue())) #Check2
            self.InputValueTxtTestLinePN.SetValue(str(np.round(self.pn1, decimals=3)))


    def GeneratePN4Blocks(self):

        if self.CheckBoxBlocks.GetValue() == True:
            Disease = self.ChoiceForDisease.GetValue()

            ImgPathList = []

            if Disease=='Flu A':
                NegPath='./samples/FluA/0'
            elif Disease=='Flu B':
                NegPath='./samples/FluB/0'
            elif Disease=='Myco':
                NegPath='./samples/Myco/0'
            elif Disease == 'RSV':
                NegPath='./samples/RSV-hMPV/0'
            elif Disease=='hMPV':
                NegPath='./samples/RSV-hMPV/0'
            else:
                NegPath='./samples/StrepA/0'

            paths = os.listdir(NegPath)

            for i in range(len(paths)):
                if paths[i].find('ini') >= 0:
                    pass
                else:
                    ImgPathList.append(NegPath+'/'+paths[i])

            Ctrl_stride_threshold = int(self.InputValueTxtCtrlLineSt.GetValue())
            Ctrl_PN_Threshold = float(self.InputValueTxtCtrlLinePN.GetValue())
            Ctrl_start_interval = int(self.InputValueTxtCtrlLineRS.GetValue())
            Ctrl_end_interval = int(self.InputValueTxtCtrlLineRE.GetValue())
            Ctrl_RGB_Index = self.ChoiceForCtrlLineRGB.GetCurrentSelection()

            Test_stride_threshold = int(self.InputValueTxtTestLineSt.GetValue())
            Test_PN_Threshold = float(self.InputValueTxtTestLinePN.GetValue())
            Test_start_interval = int(self.InputValueTxtTestLineRS.GetValue())
            Test_end_interval = int(self.InputValueTxtTestLineRE.GetValue())
            Test_RGB_Index = self.ChoiceForTestLineRGB.GetCurrentSelection()

            Ctrl_para = [Ctrl_RGB_Index, Ctrl_start_interval, Ctrl_end_interval, Ctrl_stride_threshold, Ctrl_PN_Threshold]
            Test_para = [Test_RGB_Index, Test_start_interval, Test_end_interval, Test_stride_threshold, Test_PN_Threshold]

            line_parameters = [Ctrl_para, Test_para]

            if self.CheckBoxBlocks.GetValue()==True:
                self.pn1, self.pn2 = calculateCutOffValue4Block(ImgPathList, line_parameters, self.CheckBoxEnhance.GetValue(),self.CheckBoxUseWhiteBalance.GetValue(), self.CheckBoxUseSmoothFilter.GetValue(), smoothing_value=int(self.ComboBoxSmoothFilter.GetValue()), std_rate=int(self.StdValue.GetValue())) #Check2
                self.InputValueTxtTestLinePN.SetValue(str(np.round(self.pn1, decimals=3)))
            else:
                self.pn1, self.pn2 = calculateCutOffValue(ImgPathList, line_parameters, self.CheckBoxEnhance.GetValue(),self.CheckBoxUseWhiteBalance.GetValue(), self.CheckBoxUseSmoothFilter.GetValue(), smoothing_value=int(self.ComboBoxSmoothFilter.GetValue()), std_rate=int(self.StdValue.GetValue()))#Check2
                self.InputValueTxtTestLinePN.SetValue(str(np.round(self.pn1, decimals=3)))
            #self.ShowCalculatedPN.SetValue(str(np.round(self.pn1, decimals=3)))
        else:
            Disease = self.ChoiceForDisease.GetValue()
            if Disease=='Flu A':
                Disease='FluA'
                self.InputValueTxtTestLinePN.SetValue(str(line_para_map[Disease][1][4]))
            elif Disease=='Flu B':
                Disease = 'FluB'
                self.InputValueTxtTestLinePN.SetValue(str(line_para_map[Disease][1][4]))
            elif Disease=='hMPV':
                Disease = 'RSV-hMPV'
                self.InputValueTxtTestLinePN.SetValue(str(line_para_map[Disease][2][4]))
            elif Disease=='RSV':
                Disease = 'RSV-hMPV'
                self.InputValueTxtTestLinePN.SetValue(str(line_para_map[Disease][1][4]))

            #self.InputValueTxtTestLinePN.SetValue(OriginalPN[0])

    def CtrlLine(self):
        self.OriginalImgFig.clf()
        self.EnhancedImgFig.clf()
        #self.SlopeFigure.clf()
        self.SlopeFigure = Figure()
        self.SlopeFigureChart = FigureCanvas(self.SlopeStatisticsPanel, -1, self.SlopeFigure)

        self.OriginalImg.ClearAll()
        self.EnhanceImg.ClearAll()

        self.OriginalImg.AddObject(self.BitmapImg)
        if self.CheckBoxEnhance.GetValue()==True:
            self.EnhanceImg.AddObject(self.EnhancedBitmapImg)
            print('Enhance')
            if self.CheckBoxUseWhiteBalance.GetValue()==True:
                self.EnhanceImg.ClearAll()
                self.EnhanceImg.AddObject(self.EnhancedWhiteBalanceBitmapImg)
                print('EnhanceWhite')
            else:
                pass
        elif self.CheckBoxUseWhiteBalance.GetValue()==True:
            self.EnhanceImg.ClearAll()
            self.EnhanceImg.AddObject(self.WhiteBalanceBitmapImg)
            print('EnhanceWhite')
        else:
            self.EnhanceImg.AddObject(self.BitmapImg)

        self.EnhanceImg.Draw(Force=True)
        self.OriginalImg.Draw(Force=True)

        #讀取圖片
        im = cv2.imdecode(np.fromfile(self.ImgPath, dtype=np.uint8), -1)
        im = cv2.cvtColor(im, cv2.COLOR_BGR2RGB)
        self.img = im

        self.Ctrl_stride_threshold = int(self.InputValueTxtCtrlLineSt.GetValue())
        self.Ctrl_PN_Threshold = float(self.InputValueTxtCtrlLinePN.GetValue())
        self.Ctrl_start_interval = int(self.InputValueTxtCtrlLineRS.GetValue())
        self.Ctrl_end_interval = int(self.InputValueTxtCtrlLineRE.GetValue())
        self.Ctrl_RGB_Index = self.ChoiceForCtrlLineRGB.GetCurrentSelection()

        self.Test_stride_threshold = int(self.InputValueTxtTestLineSt.GetValue())
        self.Test_PN_Threshold = float(self.InputValueTxtTestLinePN.GetValue())
        self.Test_start_interval = int(self.InputValueTxtTestLineRS.GetValue())
        self.Test_end_interval = int(self.InputValueTxtTestLineRE.GetValue())
        self.Test_RGB_Index = self.ChoiceForTestLineRGB.GetCurrentSelection()

        if self.Ctrl_RGB_Index == 0:
            self.Ctrl_color = 'red'
        elif self.Ctrl_RGB_Index == 1:
            self.Ctrl_color = 'green'
        else:
            self.Ctrl_color = 'blue'

        if self.Test_RGB_Index == 0:
            self.Test_color = 'red'
        elif self.Test_RGB_Index == 1:
            self.Test_color = 'green'
        else:
            self.Test_color = 'blue'

        #宣告parameters參數
        self.Ctrl_para = [self.Ctrl_RGB_Index, self.Ctrl_start_interval, self.Ctrl_end_interval, self.Ctrl_stride_threshold, self.Ctrl_PN_Threshold]
        self.Test_para = [self.Test_RGB_Index, self.Test_start_interval, self.Test_end_interval, self.Test_stride_threshold, self.Test_PN_Threshold]
        self.line_para = [self.Ctrl_para, self.Test_para]

        #宣告TestDFArr
        if self.CheckBoxEnhance.GetValue()==True:
            self.TestLineMultiDFArr = gamma_enhance(self.img)
        else:
            self.TestLineMultiDFArr = self.img

        if self.CheckBoxEnhance.GetValue()==True and self.CheckBoxBlocks.GetValue() == False:
            self.CtrlResult, self.result1, self.result2 = algorithm3_with_slope(self.img, self.line_para, True, self.CheckBoxUseWhiteBalance.GetValue(), self.CheckBoxUseSmoothFilter.GetValue(), int(self.ComboBoxSmoothFilter.GetValue()), True, False) #Check

            if self.CtrlResult[0] == 1:
                self.TestDFArr = self.result1[6]
                self.TestMaxIndex = self.result1[2]
                self.TestMaxValue = self.result1[3]
                self.TestMinIndex = self.result1[4]
                self.TestMinValue = self.result1[5]
                self.FinalTestResult = self.ResultTextConvert(self.result1[0])
            else:
                self.TestDFArr = self.CtrlResult[6]
                self.TestMaxIndex = self.CtrlResult[2]
                self.TestMaxValue = self.CtrlResult[3]
                self.TestMinIndex = self.CtrlResult[4]
                self.TestMinValue = self.CtrlResult[5]

        elif self.CheckBoxEnhance.GetValue()==True and self.CheckBoxBlocks.GetValue() == True:
            self.CtrlResult, self.result1, self.result2, self.test_result1_pred, self.test_result2_pred = algorithm3_with_slope_4block(self.img, self.line_para, True, self.CheckBoxUseWhiteBalance.GetValue() ,self.CheckBoxUseSmoothFilter.GetValue(), int(self.ComboBoxSmoothFilter.GetValue()), True, False, num_positive=int(self.BlockNum.GetValue())) #Check
            if self.CtrlResult[0] == 1:
                pass
            else:
                self.TestDFArr = self.CtrlResult[6]
                self.TestMaxIndex = self.CtrlResult[2]
                self.TestMaxValue = self.CtrlResult[3]
                self.TestMinIndex = self.CtrlResult[4]
                self.TestMinValue = self.CtrlResult[5]
            self.SetBoundaryLineForBlocks(self.OriginalImg, self.EnhanceImg, int(self.InputValueTxtTestLineRS.GetValue()), int(self.InputValueTxtTestLineRE.GetValue()))

        elif self.CheckBoxEnhance.GetValue() == False and self.CheckBoxBlocks.GetValue() == False:
            self.CtrlResult, self.result1, self.result2 = algorithm3_with_slope(self.img, self.line_para, False, self.CheckBoxUseWhiteBalance.GetValue(), self.CheckBoxUseSmoothFilter.GetValue(), int(self.ComboBoxSmoothFilter.GetValue()), True, False) #Check
            if self.CtrlResult[0] == 1:
                self.TestDFArr = self.result1[6]
                self.TestMaxIndex = self.result1[2]
                self.TestMaxValue = self.result1[3]
                self.TestMinIndex = self.result1[4]
                self.TestMinValue = self.result1[5]
                self.FinalTestResult = self.ResultTextConvert(self.result1[0])
            else:
                self.TestDFArr = self.CtrlResult[6]
                self.TestMaxIndex = self.CtrlResult[2]
                self.TestMaxValue = self.CtrlResult[3]
                self.TestMinIndex = self.CtrlResult[4]
                self.TestMinValue = self.CtrlResult[5]

        else:# self.CheckBoxEnhance.GetValue() == False and self.CheckBoxBlocks.GetValue() == True:
            self.CtrlResult, self.result1, self.result2, self.test_result1_pred, self.test_result2_pred = algorithm3_with_slope_4block(self.img, self.line_para, False, self.CheckBoxUseWhiteBalance.GetValue(), self.CheckBoxUseSmoothFilter.GetValue(), int(self.ComboBoxSmoothFilter.GetValue()), True, False, num_positive=int(self.BlockNum.GetValue())) #Check
            if self.CtrlResult[0] == 1:
                pass
            else:
                self.TestDFArr = self.CtrlResult[6]
                self.TestMaxIndex = self.CtrlResult[2]
                self.TestMaxValue = self.CtrlResult[3]
                self.TestMinIndex = self.CtrlResult[4]
                self.TestMinValue = self.CtrlResult[5]
            self.SetBoundaryLineForBlocks(self.OriginalImg, self.EnhanceImg, int(self.InputValueTxtTestLineRS.GetValue()), int(self.InputValueTxtTestLineRE.GetValue()))


        if self.CtrlResult[0]==1:
            self.ctrl_result = 'Positive'
        else:
            self.ctrl_result = 'Negative'

        CtrlMaxValue = np.around(self.CtrlResult[3], decimals=3)
        CtrlMinValue = np.around(self.CtrlResult[5], decimals=3)
        CtrlMaxPeak = np.around(self.CtrlResult[1], decimals=3)

        if self.ctrl_result == 'Positive':
            #CtrlString = 'Result :'+self.ctrl_result+'\n'+'Max Value :'+str(CtrlMaxValue)+'\n'+'Mini Value :'+str(CtrlMinValue)+'\n'+'MaxPeak :'+str(CtrlMaxPeak)
            self.CtrlLineResult.SetValue(self.ctrl_result)
            self.CtrlLineMaxValue.SetValue(str(CtrlMaxValue))
            self.CtrlLineMinValue.SetValue(str(CtrlMinValue))
            self.CtrlLineMaxPeak.SetValue(str(CtrlMaxPeak))
        else:
            CtrlString = 'Result :'+'Control Line ERROR'+'\n'+'Max Value :'+str(CtrlMaxValue)+'\n'+'Mini Value :'+str(CtrlMinValue)+'\n'+'MaxPeak :'+str(CtrlMaxPeak)
            self.CtrlLineResult.SetValue('Control Line ERROR')
            self.CtrlLineMaxValue.SetValue(str(CtrlMaxValue))
            self.CtrlLineMinValue.SetValue(str(CtrlMinValue))
            self.CtrlLineMaxPeak.SetValue(str(CtrlMaxPeak))
            self.ResultText.SetLabel('Result : Control Line ERROR')
        #4色統計圖
        self.ShowOriginalImgChartForCtrlLine(self.Ctrl_start_interval, self.Ctrl_end_interval, 0, 250)
        self.ShowOriginalImgChartForTestLine(self.Test_start_interval, self.Test_end_interval, 0, 250)
        self.ShowEnhancedImgChartForCtrlLine(self.Ctrl_start_interval, self.Ctrl_end_interval, 0, 250)
        self.ShowEnhancedImgChartForTestLine(self.Test_start_interval, self.Test_end_interval, 0, 250)


    def TestLine(self, event):
        self.CtrlLine()

        if self.ctrl_result == 'Positive':
            if self.CheckBoxBlocks.GetValue() == True and self.CheckBoxEnhance.GetValue() == True:
                self.Rect5.Bind(FloatCanvas.EVT_FC_LEFT_DOWN, self.Block5Event)
                self.Rect6.Bind(FloatCanvas.EVT_FC_LEFT_DOWN, self.Block6Event)
                self.Rect7.Bind(FloatCanvas.EVT_FC_LEFT_DOWN, self.Block7Event)
                self.Rect8.Bind(FloatCanvas.EVT_FC_LEFT_DOWN, self.Block8Event)
                self.PlotCtrlLineBoundary()
                if self.test_result1_pred == 1:
                    self.FinalTestResult = 'Positive'
                else:
                    self.FinalTestResult = 'Negative'
                self.ResultText.SetLabel('Result : ' + self.FinalTestResult)
                self.SlopeStatisticsChartForCtrlLine(self.Ctrl_color, self.Ctrl_start_interval, self.Ctrl_end_interval, -20, 20)
            elif self.CheckBoxBlocks.GetValue() == True and self.CheckBoxEnhance.GetValue() == False:
                self.Rect1.Bind(FloatCanvas.EVT_FC_LEFT_DOWN, self.Block1Event)
                self.Rect2.Bind(FloatCanvas.EVT_FC_LEFT_DOWN, self.Block2Event)
                self.Rect3.Bind(FloatCanvas.EVT_FC_LEFT_DOWN, self.Block3Event)
                self.Rect4.Bind(FloatCanvas.EVT_FC_LEFT_DOWN, self.Block4Event)
                self.PlotCtrlLineBoundary()
                if self.test_result1_pred == 1:
                    self.FinalTestResult = 'Positive'
                else:
                    self.FinalTestResult = 'Negative'
                self.ResultText.SetLabel('Result : ' + self.FinalTestResult)
                self.SlopeStatisticsChartForCtrlLine(self.Ctrl_color, self.Ctrl_start_interval, self.Ctrl_end_interval, -20, 20)
            else:
                print(np.mean(self.TestDFArr))
                self.SlopeStatisticsChartForCtrlLine(self.Ctrl_color, self.Ctrl_start_interval, self.Ctrl_end_interval, -20, 20)
                self.SlopeStatisticsChartForTestLine(self.Test_color, self.Test_start_interval, self.Test_end_interval, -20, 20)
                TestString = 'Result :' + self.FinalTestResult + '\n' + 'Max Value :' + str(np.round(self.result1[3], decimals=3)) + '\n' + 'Mini Value :' + str(np.round(self.result1[5], decimals=3)) + '\n' + 'MaxPeak :' + str(np.round(self.result1[1], decimals=3))
                self.ResultText.SetLabel('Result : ' + self.FinalTestResult)
                self.TestLineResult.SetValue(self.FinalTestResult)
                self.TestLineMaxValueText.SetValue(str(np.round(self.result1[3], decimals=3)))
                self.TestLineMinValueText.SetValue(str(np.round(self.result1[5], decimals=3)))
                self.TestLineMaxPeakText.SetValue(str(np.round(self.result1[1], decimals=3)))
                self.PlotCtrlLineBoundary()
                self.PlotTestLineBoundary()
        else:
            # print(np.mean(self.TestDFArr))
            self.PlotCtrlLineBoundary()
            #self.PlotTestLineBoundary()
            self.SlopeStatisticsChartForCtrlLine(self.Ctrl_color, self.Ctrl_start_interval, self.Ctrl_end_interval, -20,20)
            self.SlopeStatisticsChartForTestLine(self.Test_color, self.Ctrl_start_interval, self.Ctrl_end_interval, -20,20)
            self.TextTestLineResult.SetValue('')


    def CtrlLineWithComboBox(self):
        self.OriginalImgFig.clf()
        self.EnhancedImgFig.clf()
        #self.SlopeFigure.clf()
        self.SlopeFigure = Figure()
        self.SlopeFigureChart = FigureCanvas(self.SlopeStatisticsPanel, -1, self.SlopeFigure)

        self.OriginalImg.ClearAll()
        self.EnhanceImg.ClearAll()

        self.OriginalImg.AddObject(self.BitmapImg)
        if self.CheckBoxEnhance.GetValue()==True:
            self.EnhanceImg.AddObject(self.EnhancedBitmapImg)
            print('Enhance')
            if self.CheckBoxUseWhiteBalance.GetValue()==True:
                self.EnhanceImg.ClearAll()
                self.EnhanceImg.AddObject(self.EnhancedWhiteBalanceBitmapImg)
                print('EnhanceWhite')
            else:
                pass
        elif self.CheckBoxUseWhiteBalance.GetValue()==True:
            self.EnhanceImg.AddObject(self.WhiteBalanceBitmapImg)
            print('EnhanceWhite')
        else:
            self.EnhanceImg.AddObject(self.BitmapImg)

        self.EnhanceImg.Draw(Force=True)
        self.OriginalImg.Draw(Force=True)

        #讀取圖片
        im = cv2.imdecode(np.fromfile(self.ImgPath, dtype=np.uint8), -1)
        im = cv2.cvtColor(im, cv2.COLOR_BGR2RGB)
        self.img = im

        self.Ctrl_stride_threshold = int(self.InputValueTxtCtrlLineSt.GetValue())
        self.Ctrl_PN_Threshold = float(self.InputValueTxtCtrlLinePN.GetValue())
        self.Ctrl_start_interval = int(self.InputValueTxtCtrlLineRS.GetValue())
        self.Ctrl_end_interval = int(self.InputValueTxtCtrlLineRE.GetValue())
        self.Ctrl_RGB_Index = self.ChoiceForCtrlLineRGB.GetCurrentSelection()

        self.Test_stride_threshold = int(self.InputValueTxtTestLineSt.GetValue())
        self.Test_PN_Threshold = float(self.InputValueTxtTestLinePN.GetValue())
        self.Test_start_interval = int(self.InputValueTxtTestLineRS.GetValue())
        self.Test_end_interval = int(self.InputValueTxtTestLineRE.GetValue())
        self.Test_RGB_Index = self.ChoiceForTestLineRGB.GetCurrentSelection()

        if self.Ctrl_RGB_Index == 0:
            self.Ctrl_color = 'red'
        elif self.Ctrl_RGB_Index == 1:
            self.Ctrl_color = 'green'
        else:
            self.Ctrl_color = 'blue'

        if self.Test_RGB_Index == 0:
            self.Test_color = 'red'
        elif self.Test_RGB_Index == 1:
            self.Test_color = 'green'
        else:
            self.Test_color = 'blue'

        #宣告parameters參數
        self.Ctrl_para = [self.Ctrl_RGB_Index, self.Ctrl_start_interval, self.Ctrl_end_interval, self.Ctrl_stride_threshold, self.Ctrl_PN_Threshold]
        self.Test_para = [self.Test_RGB_Index, self.Test_start_interval, self.Test_end_interval, self.Test_stride_threshold, self.Test_PN_Threshold]
        self.line_para = [self.Ctrl_para, self.Test_para]

        #宣告TestDFArr
        if self.CheckBoxEnhance.GetValue()==True:
            self.TestLineMultiDFArr = gamma_enhance(self.img)
        else:
            self.TestLineMultiDFArr = self.img

        if self.CheckBoxEnhance.GetValue()==True and self.CheckBoxBlocks.GetValue() == False:
            self.CtrlResult, self.result1, self.result2 = algorithm3_with_slope(self.img, self.line_para, True, self.CheckBoxUseWhiteBalance.GetValue(), self.CheckBoxUseSmoothFilter.GetValue(), int(self.ComboBoxSmoothFilter.GetValue()), True, False) #Check

            if self.CtrlResult[0] == 1:
                self.TestDFArr = self.result1[6]
                self.TestMaxIndex = self.result1[2]
                self.TestMaxValue = self.result1[3]
                self.TestMinIndex = self.result1[4]
                self.TestMinValue = self.result1[5]
                self.FinalTestResult = self.ResultTextConvert(self.result1[0])
            else:
                self.TestDFArr = self.CtrlResult[6]
                self.TestMaxIndex = self.CtrlResult[2]
                self.TestMaxValue = self.CtrlResult[3]
                self.TestMinIndex = self.CtrlResult[4]
                self.TestMinValue = self.CtrlResult[5]

        elif self.CheckBoxEnhance.GetValue()==True and self.CheckBoxBlocks.GetValue() == True:
            self.CtrlResult, self.result1, self.result2, self.test_result1_pred, self.test_result2_pred = algorithm3_with_slope_4block(self.img, self.line_para, True, self.CheckBoxUseWhiteBalance.GetValue() ,self.CheckBoxUseSmoothFilter.GetValue(), int(self.ComboBoxSmoothFilter.GetValue()), True, False, num_positive=int(self.BlockNum.GetValue())) #Check
            if self.CtrlResult[0] == 1:
                pass
            else:
                self.TestDFArr = self.CtrlResult[6]
                self.TestMaxIndex = self.CtrlResult[2]
                self.TestMaxValue = self.CtrlResult[3]
                self.TestMinIndex = self.CtrlResult[4]
                self.TestMinValue = self.CtrlResult[5]
            self.SetBoundaryLineForBlocks(self.OriginalImg, self.EnhanceImg, int(self.InputValueTxtTestLineRS.GetValue()), int(self.InputValueTxtTestLineRE.GetValue()))

        elif self.CheckBoxEnhance.GetValue() == False and self.CheckBoxBlocks.GetValue() == False:
            self.CtrlResult, self.result1, self.result2 = algorithm3_with_slope(self.img, self.line_para, False, self.CheckBoxUseWhiteBalance.GetValue(), self.CheckBoxUseSmoothFilter.GetValue(), int(self.ComboBoxSmoothFilter.GetValue()), True, False) #Check
            if self.CtrlResult[0] == 1:
                self.TestDFArr = self.result1[6]
                self.TestMaxIndex = self.result1[2]
                self.TestMaxValue = self.result1[3]
                self.TestMinIndex = self.result1[4]
                self.TestMinValue = self.result1[5]
                self.FinalTestResult = self.ResultTextConvert(self.result1[0])
            else:
                self.TestDFArr = self.CtrlResult[6]
                self.TestMaxIndex = self.CtrlResult[2]
                self.TestMaxValue = self.CtrlResult[3]
                self.TestMinIndex = self.CtrlResult[4]
                self.TestMinValue = self.CtrlResult[5]

        else:# self.CheckBoxEnhance.GetValue() == False and self.CheckBoxBlocks.GetValue() == True:
            self.CtrlResult, self.result1, self.result2, self.test_result1_pred, self.test_result2_pred = algorithm3_with_slope_4block(self.img, self.line_para, False, self.CheckBoxUseWhiteBalance.GetValue(), self.CheckBoxUseSmoothFilter.GetValue(), int(self.ComboBoxSmoothFilter.GetValue()), True, False, num_positive=int(self.BlockNum.GetValue())) #Check
            if self.CtrlResult[0] == 1:
                pass
            else:
                self.TestDFArr = self.CtrlResult[6]
                self.TestMaxIndex = self.CtrlResult[2]
                self.TestMaxValue = self.CtrlResult[3]
                self.TestMinIndex = self.CtrlResult[4]
                self.TestMinValue = self.CtrlResult[5]
            self.SetBoundaryLineForBlocks(self.OriginalImg, self.EnhanceImg, int(self.InputValueTxtTestLineRS.GetValue()), int(self.InputValueTxtTestLineRE.GetValue()))


        if self.CtrlResult[0]==1:
            self.ctrl_result = 'Positive'
        else:
            self.ctrl_result = 'Negative'

        CtrlMaxValue = np.around(self.CtrlResult[3], decimals=3)
        CtrlMinValue = np.around(self.CtrlResult[5], decimals=3)
        CtrlMaxPeak = np.around(self.CtrlResult[1], decimals=3)

        if self.ctrl_result == 'Positive':
            CtrlString = 'Result :'+self.ctrl_result+'\n'+'Max Value :'+str(CtrlMaxValue)+'\n'+'Mini Value :'+str(CtrlMinValue)+'\n'+'MaxPeak :'+str(CtrlMaxPeak)
            self.TextCtrlLineResult.SetValue(CtrlString)
        else:
            CtrlString = 'Result :'+'Control Line ERROR'+'\n'+'Max Value :'+str(CtrlMaxValue)+'\n'+'Mini Value :'+str(CtrlMinValue)+'\n'+'MaxPeak :'+str(CtrlMaxPeak)
            self.TextCtrlLineResult.SetValue(CtrlString)
            self.ResultText.SetLabel('Result : Control Line ERROR')
        #4色統計圖
        self.ShowOriginalImgChartForCtrlLine(self.Ctrl_start_interval, self.Ctrl_end_interval, 0, 250)
        self.ShowOriginalImgChartForTestLine(self.Test_start_interval, self.Test_end_interval, 0, 250)
        self.ShowEnhancedImgChartForCtrlLine(self.Ctrl_start_interval, self.Ctrl_end_interval, 0, 250)
        self.ShowEnhancedImgChartForTestLine(self.Test_start_interval, self.Test_end_interval, 0, 250)

    def TestLineWithEnhanceComboBox(self, event):
        self.CtrlLineWithComboBox()

        if self.ctrl_result == 'Positive':
            if self.CheckBoxBlocks.GetValue() == True and self.CheckBoxEnhance.GetValue() == True:
                self.Rect5.Bind(FloatCanvas.EVT_FC_LEFT_DOWN, self.Block5Event)
                self.Rect6.Bind(FloatCanvas.EVT_FC_LEFT_DOWN, self.Block6Event)
                self.Rect7.Bind(FloatCanvas.EVT_FC_LEFT_DOWN, self.Block7Event)
                self.Rect8.Bind(FloatCanvas.EVT_FC_LEFT_DOWN, self.Block8Event)
                self.PlotCtrlLineBoundary()
                if self.test_result1_pred == 1:
                    self.FinalTestResult = 'Positive'
                else:
                    self.FinalTestResult = 'Negative'
                self.ResultText.SetLabel('Result : ' + self.FinalTestResult)
                self.SlopeStatisticsChartForCtrlLine(self.Ctrl_color, self.Ctrl_start_interval,
                                                     self.Ctrl_end_interval,
                                                     -20, 20)
            elif self.CheckBoxBlocks.GetValue() == True and self.CheckBoxEnhance.GetValue() == False:
                self.Rect1.Bind(FloatCanvas.EVT_FC_LEFT_DOWN, self.Block1Event)
                self.Rect2.Bind(FloatCanvas.EVT_FC_LEFT_DOWN, self.Block2Event)
                self.Rect3.Bind(FloatCanvas.EVT_FC_LEFT_DOWN, self.Block3Event)
                self.Rect4.Bind(FloatCanvas.EVT_FC_LEFT_DOWN, self.Block4Event)
                self.PlotCtrlLineBoundary()
                if self.test_result1_pred == 1:
                    self.FinalTestResult = 'Positive'
                else:
                    self.FinalTestResult = 'Negative'
                self.ResultText.SetLabel('Result : ' + self.FinalTestResult)
                self.SlopeStatisticsChartForCtrlLine(self.Ctrl_color, self.Ctrl_start_interval,
                                                     self.Ctrl_end_interval, -20, 20)
            else:
                print(np.mean(self.TestDFArr))
                self.SlopeStatisticsChartForCtrlLine(self.Ctrl_color, self.Ctrl_start_interval,
                                                     self.Ctrl_end_interval, -20, 20)
                self.SlopeStatisticsChartForTestLine(self.Test_color, self.Test_start_interval,
                                                     self.Test_end_interval, -20, 20)
                TestString = 'Result :' + self.FinalTestResult + '\n' + 'Max Value :' + str(
                    np.round(self.result1[3], decimals=3)) + '\n' + 'Mini Value :' + str(
                    np.round(self.result1[5], decimals=3)) + '\n' + 'MaxPeak :' + str(
                    np.round(self.result1[1], decimals=3))
                self.ResultText.SetLabel('Result : ' + self.FinalTestResult)
                self.TextTestLineResult.SetValue(TestString)
                self.PlotCtrlLineBoundary()
                self.PlotTestLineBoundary()
        else:
            # print(np.mean(self.TestDFArr))
            self.PlotCtrlLineBoundary()
            # self.PlotTestLineBoundary()
            self.SlopeStatisticsChartForCtrlLine(self.Ctrl_color, self.Ctrl_start_interval, self.Ctrl_end_interval,
                                                 -20, 20)
            self.SlopeStatisticsChartForTestLine(self.Test_color, self.Ctrl_start_interval, self.Ctrl_end_interval,
                                                 -20, 20)
            self.TextTestLineResult.SetValue('')

    def TestLineWithWhiteBlanceComboBox(self, event):
        self.CtrlLineWithComboBox()

        if self.ctrl_result == 'Positive':
            if self.CheckBoxBlocks.GetValue() == True and self.CheckBoxEnhance.GetValue() == True:
                self.Rect5.Bind(FloatCanvas.EVT_FC_LEFT_DOWN, self.Block5Event)
                self.Rect6.Bind(FloatCanvas.EVT_FC_LEFT_DOWN, self.Block6Event)
                self.Rect7.Bind(FloatCanvas.EVT_FC_LEFT_DOWN, self.Block7Event)
                self.Rect8.Bind(FloatCanvas.EVT_FC_LEFT_DOWN, self.Block8Event)
                self.PlotCtrlLineBoundary()
                if self.test_result1_pred == 1:
                    self.FinalTestResult = 'Positive'
                else:
                    self.FinalTestResult = 'Negative'
                self.ResultText.SetLabel('Result : ' + self.FinalTestResult)
                self.SlopeStatisticsChartForCtrlLine(self.Ctrl_color, self.Ctrl_start_interval,
                                                     self.Ctrl_end_interval,
                                                     -20, 20)
            elif self.CheckBoxBlocks.GetValue() == True and self.CheckBoxEnhance.GetValue() == False:
                self.Rect1.Bind(FloatCanvas.EVT_FC_LEFT_DOWN, self.Block1Event)
                self.Rect2.Bind(FloatCanvas.EVT_FC_LEFT_DOWN, self.Block2Event)
                self.Rect3.Bind(FloatCanvas.EVT_FC_LEFT_DOWN, self.Block3Event)
                self.Rect4.Bind(FloatCanvas.EVT_FC_LEFT_DOWN, self.Block4Event)
                self.PlotCtrlLineBoundary()
                if self.test_result1_pred == 1:
                    self.FinalTestResult = 'Positive'
                else:
                    self.FinalTestResult = 'Negative'
                self.ResultText.SetLabel('Result : ' + self.FinalTestResult)
                self.SlopeStatisticsChartForCtrlLine(self.Ctrl_color, self.Ctrl_start_interval,
                                                     self.Ctrl_end_interval, -20, 20)
            else:
                print(np.mean(self.TestDFArr))
                self.SlopeStatisticsChartForCtrlLine(self.Ctrl_color, self.Ctrl_start_interval,
                                                     self.Ctrl_end_interval, -20, 20)
                self.SlopeStatisticsChartForTestLine(self.Test_color, self.Test_start_interval,
                                                     self.Test_end_interval, -20, 20)
                TestString = 'Result :' + self.FinalTestResult + '\n' + 'Max Value :' + str(
                    np.round(self.result1[3], decimals=3)) + '\n' + 'Mini Value :' + str(
                    np.round(self.result1[5], decimals=3)) + '\n' + 'MaxPeak :' + str(
                    np.round(self.result1[1], decimals=3))
                self.ResultText.SetLabel('Result : ' + self.FinalTestResult)
                self.TextTestLineResult.SetValue(TestString)
                self.PlotCtrlLineBoundary()
                self.PlotTestLineBoundary()
        else:
            # print(np.mean(self.TestDFArr))
            self.PlotCtrlLineBoundary()
            # self.PlotTestLineBoundary()
            self.SlopeStatisticsChartForCtrlLine(self.Ctrl_color, self.Ctrl_start_interval, self.Ctrl_end_interval,
                                                 -20, 20)
            self.SlopeStatisticsChartForTestLine(self.Test_color, self.Ctrl_start_interval, self.Ctrl_end_interval,
                                                 -20, 20)
            self.TextTestLineResult.SetValue('')
####################################################Drawing Chart###################################################################
    def ShowOriginalImgChartForCtrlLine(self, start_interval, end_interval, y_start, y_end):
        df = self.ShowPlot(self.original_image_matrix)
        self.OriginalImgFig.set_figheight(2)
        self.OriginalImgFig.set_figwidth(4.5)
        self.axes_OriginalImg = self.OriginalImgFig.add_subplot(1, 1, 1)
        self.axes_OriginalImg.set_ylim(0, 250)
        self.axes_OriginalImg.plot('x', 'j1', data=df, color='red', linewidth=1, label='r')
        self.axes_OriginalImg.plot('x', 'j2', data=df, color='green', linewidth=1, label='g')
        self.axes_OriginalImg.plot('x', 'j3', data=df, color='blue', linewidth=1, label='b')
        self.axes_OriginalImg.plot('x', 'j4', data=df, color='gray', linewidth=1, label='gray')
        points_start = [(start_interval, y_start), (start_interval , y_end)]
        (xpoint_start, ypoint_start) = zip( * points_start)
        points_end = [(end_interval, y_start), (end_interval, y_end)]
        (xpoint_end, ypoint_end) = zip( * points_end)
        self.axes_OriginalImg.plot(xpoint_start, ypoint_start, 'g', linewidth=1)
        self.axes_OriginalImg.plot(xpoint_end, ypoint_end, 'g', linewidth=1)
        self.axes_OriginalImg.grid(True)
        self.OriginalImgChart.draw()

    def ShowOriginalImgChartForTestLine(self, start_interval, end_interval, y_start, y_end):
        points_start = [(start_interval, y_start), (start_interval , y_end)]
        (xpoint_start, ypoint_start) = zip( * points_start)
        points_end = [(end_interval, y_start), (end_interval, y_end)]
        (xpoint_end, ypoint_end) = zip( * points_end)
        self.axes_OriginalImg.plot(xpoint_start, ypoint_start, 'r', linewidth=1)
        self.axes_OriginalImg.plot(xpoint_end, ypoint_end, 'r', linewidth=1)
        self.OriginalImgChart.draw()

    def ShowEnhancedImgChartForCtrlLine(self, start_interval, end_interval, y_start, y_end):
        df = self.ShowPlot_Enhance(self.original_image_matrix)
        self.EnhancedImgFig.set_figheight(2)
        self.EnhancedImgFig.set_figwidth(4.5)
        self.axes_EnhancedImg = self.EnhancedImgFig.add_subplot(1, 1, 1)
        self.axes_EnhancedImg.set_ylim(0, 250)
        self.axes_EnhancedImg.plot('x', 'j1', data=df, color='red', linewidth=1, label='r')
        self.axes_EnhancedImg.plot('x', 'j2', data=df, color='green', linewidth=1, label='g')
        self.axes_EnhancedImg.plot('x', 'j3', data=df, color='blue', linewidth=1, label='b')
        self.axes_EnhancedImg.plot('x', 'j4', data=df, color='gray', linewidth=1, label='gray')
        points_start = [(start_interval, y_start), (start_interval , y_end)]
        (xpoint_start, ypoint_start) = zip( * points_start)
        points_end = [(end_interval, y_start), (end_interval, y_end)]
        (xpoint_end, ypoint_end) = zip( * points_end)
        self.axes_EnhancedImg.plot(xpoint_start, ypoint_start, 'g', linewidth=1)
        self.axes_EnhancedImg.plot(xpoint_end, ypoint_end, 'g', linewidth=1)
        self.axes_EnhancedImg.grid(True)
        self.EnhancedImgChart.draw()

    def ShowEnhancedImgChartForTestLine(self, start_interval, end_interval, y_start, y_end):
        points_start = [(start_interval, y_start), (start_interval , y_end)]
        (xpoint_start, ypoint_start) = zip( * points_start)
        points_end = [(end_interval, y_start), (end_interval, y_end)]
        (xpoint_end, ypoint_end) = zip( * points_end)
        if self.ctrl_result == 'Positive':
            self.axes_EnhancedImg.plot(xpoint_start, ypoint_start, 'r', linewidth=1)
            self.axes_EnhancedImg.plot(xpoint_end, ypoint_end, 'r', linewidth=1)
        self.EnhancedImgChart.draw()

    def SlopeStatisticsChartForCtrlLine(self, color, start_interval, end_interval, y_start, y_end):
        self.TestLineDfPop = None
        self.TestLineMaxValuePop = None
        self.TestLineMinValuePop = None
        self.TestLineBdLineXPop = None
        self.TestLineBdLineYPop = None
        self.SlopeFigure.set_figheight(2.2)
        self.SlopeFigure.set_figwidth(5)
        self.axes_slope = self.SlopeFigure.add_subplot(1, 1, 1)
        self.axes_slope.set_ylim(-20, 20)
        # if self.CtrlLineResult=='Negative':
        #     df = self.ReturnSlopeDF(self.CtrlDFArr)
        #     self.axes_slope.plot('x', 'j1', data=df, color=color, linewidth=1)
        #########################################################################
        points_start = [(start_interval, y_start), (start_interval , y_end)]
        (xpoint_start, ypoint_start) = zip( * points_start)
        points_end = [(end_interval, y_start), (end_interval, y_end)]
        (xpoint_end, ypoint_end) = zip( * points_end)
        self.axes_slope.plot(xpoint_start, ypoint_start, 'g', linewidth=1)
        self.axes_slope.plot(xpoint_end, ypoint_end, 'g', linewidth=1)
        #########################################################################

    def SlopeStatisticsChartForTestLine(self, color, start_interval, end_interval, y_start, y_end):
        if self.TestLineDfPop and self.TestLineMaxValuePop and self.TestLineMinValuePop and self.TestLineBdLineXPop and self.TestLineBdLineYPop is not None:
            self.TestLineDfPop.remove()
            self.TestLineMaxValuePop.remove()
            self.TestLineMinValuePop.remove()
            self.TestLineBdLineXPop.remove()
            self.TestLineBdLineYPop.remove()

        #########################################################################
        df = self.ReturnSlopeDF(self.TestDFArr)

        self.TestDfLine = self.axes_slope.plot('x', 'j1', data=df, color=color, linewidth=1)

        self.TestLineDfPop = self.TestDfLine.pop(0)
        #########################################################################
        points_start = [(start_interval, y_start), (start_interval, y_end)]
        (xpoint_start, ypoint_start) = zip(*points_start)
        points_end = [(end_interval, y_start), (end_interval, y_end)]
        (xpoint_end, ypoint_end) = zip(*points_end)
        if self.ctrl_result == 'Positive':
            self.TestLineBdLineX = self.axes_slope.plot(xpoint_start, ypoint_start, 'r', linewidth=1)
            self.TestLineBdLineY = self.axes_slope.plot(xpoint_end, ypoint_end, 'r', linewidth=1)
        else:
            self.TestLineBdLineX = self.axes_slope.plot(xpoint_start, ypoint_start, 'g', linewidth=1)
            self.TestLineBdLineY = self.axes_slope.plot(xpoint_end, ypoint_end, 'g', linewidth=1)
        self.TestLineBdLineXPop = self.TestLineBdLineX.pop(0)
        self.TestLineBdLineYPop = self.TestLineBdLineY.pop(0)
        #########################################################################
        self.axes_slope.grid(True)
        if self.ctrl_result == 'Positive':
            self.TestLineMaxValue = self.axes_slope.plot(self.TestMaxIndex + start_interval, self.TestMaxValue, 'ro')
            self.TestLineMinValue = self.axes_slope.plot(self.TestMinIndex + start_interval, self.TestMinValue, 'ro')
        else:
            self.TestLineMaxValue = self.axes_slope.plot(self.TestMaxIndex + start_interval, self.TestMaxValue, 'go')
            self.TestLineMinValue = self.axes_slope.plot(self.TestMinIndex + start_interval, self.TestMinValue, 'go')
        self.TestLineMaxValuePop = self.TestLineMaxValue.pop(0)
        self.TestLineMinValuePop = self.TestLineMinValue.pop(0)
        self.SlopeFigureChart.draw()
####################################################################################################################################


####################################################Set Boundary####################################################################

    def PlotTestLineBoundary(self):
        if self.boundary_original_rect is None:
            self.OriginalImgBoundaryLine(self.OriginalImg, int(self.InputValueTxtTestLineRS.GetValue()), int(self.InputValueTxtTestLineRE.GetValue()))
            self.EnhancedImgBoundaryLine(self.EnhanceImg, int(self.InputValueTxtTestLineRS.GetValue()), int(self.InputValueTxtTestLineRE.GetValue()))
            self.boundary_original_rect.SetColor('red')
            self.boundary_enhanced_rect.SetColor('red')
        if self.boundary_original_rect is not None:
            self.SetBoundaryLine(self.OriginalImg, int(self.InputValueTxtTestLineRS.GetValue()), int(self.InputValueTxtTestLineRE.GetValue()))
            self.boundary_original_rect.SetColor('red')
            self.boundary_enhanced_rect.SetColor('red')

        self.OriginalImg.AddObject(self.boundary_enhanced_rect)
        self.EnhanceImg.AddObject(self.boundary_enhanced_rect)
        self.SetBoundaryLine(self.EnhanceImg, int(self.InputValueTxtTestLineRS.GetValue()), int(self.InputValueTxtTestLineRE.GetValue()))
        self.SetBoundaryLine(self.OriginalImg, int(self.InputValueTxtTestLineRS.GetValue()), int(self.InputValueTxtTestLineRE.GetValue()))
        self.boundary_original_rect.SetColor('red')
        self.boundary_enhanced_rect.SetColor('red')

    def PlotCtrlLineBoundary(self):
        if self.boundary_original_ctrl_rect is None:
            self.OriginalImgBoundaryLineForCtrlLine(self.OriginalImg, int(self.InputValueTxtCtrlLineRS.GetValue()), int(self.InputValueTxtCtrlLineRE.GetValue()))
            self.EnhancedImgBoundaryLineForCtrlLine(self.EnhanceImg, int(self.InputValueTxtCtrlLineRS.GetValue()), int(self.InputValueTxtCtrlLineRE.GetValue()))
            self.boundary_original_ctrl_rect.SetColor('green')
            self.boundary_enhanced_ctrl_rect.SetColor('green')
        if self.boundary_original_ctrl_rect is not None:
            self.SetBoundaryLineForCtrlLine(self.OriginalImg, int(self.InputValueTxtCtrlLineRS.GetValue()), int(self.InputValueTxtCtrlLineRE.GetValue()))
            self.boundary_original_ctrl_rect.SetColor('green')
            self.boundary_enhanced_ctrl_rect.SetColor('green')

    #if self.CheckBoxEnhance.GetValue() == True:
        self.OriginalImg.AddObject(self.boundary_enhanced_ctrl_rect)
        self.EnhanceImg.AddObject(self.boundary_enhanced_ctrl_rect)
        self.SetBoundaryLineForCtrlLine(self.EnhanceImg, int(self.InputValueTxtCtrlLineRS.GetValue()), int(self.InputValueTxtCtrlLineRE.GetValue()))
        self.SetBoundaryLineForCtrlLine(self.OriginalImg, int(self.InputValueTxtCtrlLineRS.GetValue()), int(self.InputValueTxtCtrlLineRE.GetValue()))
        self.boundary_original_ctrl_rect.SetColor('green')
        self.boundary_enhanced_ctrl_rect.SetColor('green')


    def OriginalImgBoundaryLine(self, panel, start_interval, end_interval):
        scale = self.PhotoMaxSize / self.W
        X = start_interval*scale-self.NewW/2
        Y = -self.NewH/2
        XY = np.array([X, Y])
        WH = ((end_interval-start_interval)*scale, self.NewH)
        self.boundary_original_rect = Rectangle(XY, WH, LineColor='Red')
        panel.AddObject(self.boundary_original_rect)
        panel.Draw(True)

    def OriginalImgBoundaryLineForCtrlLine(self, panel, start_interval, end_interval):
        scale = self.PhotoMaxSize / self.W
        X = start_interval*scale-self.NewW/2
        Y = -self.NewH/2
        XY = np.array([X, Y])
        WH = ((end_interval-start_interval)*scale, self.NewH)
        self.boundary_original_ctrl_rect = Rectangle(XY, WH, LineColor='Red')
        panel.AddObject(self.boundary_original_ctrl_rect)
        panel.Draw(True)

    def EnhancedImgBoundaryLine(self, panel, start_interval, end_interval):
        scale = self.PhotoMaxSize / self.W
        X = start_interval*scale-self.NewW/2
        Y = -self.NewH/2
        XY = np.array([X, Y])
        WH = ((end_interval-start_interval)*scale, self.NewH)
        self.boundary_enhanced_rect = Rectangle(XY, WH, LineColor='Red')
        panel.AddObject(self.boundary_enhanced_rect)
        panel.Draw(True)

    def EnhancedImgBoundaryLineForCtrlLine(self, panel, start_interval, end_interval):
        scale = self.PhotoMaxSize / self.W
        X = start_interval*scale-self.NewW/2
        Y = -self.NewH/2
        XY = np.array([X, Y])
        WH = ((end_interval-start_interval)*scale, self.NewH)
        self.boundary_enhanced_ctrl_rect = Rectangle(XY, WH, LineColor='Red')
        panel.AddObject(self.boundary_enhanced_ctrl_rect)
        panel.Draw(True)

    def SetBoundaryLine(self, panel, start_interval, end_interval):
        scale = self.PhotoMaxSize / self.W
        X = start_interval*scale-self.NewW/2
        Y = -self.NewH/2
        XY = np.array([X, Y])
        WH = ((end_interval-start_interval)*scale, self.NewH)
        self.boundary_enhanced_rect.SetShape(XY, WH)
        self.boundary_original_rect.SetShape(XY, WH)
        panel.Draw(True)

    def SetBoundaryLineForCtrlLine(self, panel, start_interval, end_interval):
        scale = self.PhotoMaxSize / self.W
        X = start_interval*scale-self.NewW/2
        Y = -self.NewH/2
        XY = np.array([X, Y])
        WH = ((end_interval-start_interval)*scale, self.NewH)
        self.boundary_enhanced_ctrl_rect.SetShape(XY, WH)
        self.boundary_original_ctrl_rect.SetShape(XY, WH)
        panel.Draw(True)

    def SetBoundaryLineForBlocks(self, OriginalPanel, EnhancedPanel, start_interval, end_interval):
        scale = self.PhotoMaxSize / self.W #縮放比例

        X = start_interval*scale-self.NewW/2
        Y1 = -self.NewH/2
        Y2 = -self.NewH/2 + int(self.NewH/4)
        Y3 = -self.NewH/2 + int(self.NewH/2)
        Y4 = -self.NewH/2 + int(3*self.NewH/4)

        XY1 = np.array([X, Y1])
        XY2 = np.array([X, Y2])
        XY3 = np.array([X, Y3])
        XY4 = np.array([X, Y4])

        WH = ((end_interval-start_interval)*scale, self.NewH/4)

        self.Rect1 = Rectangle(XY1, WH, LineColor = "Red", LineStyle = "Solid", LineWidth = 1, FillColor = 'White', FillStyle="Transparent")
        self.Rect2 = Rectangle(XY2, WH, LineColor="Red", LineStyle="Solid", LineWidth=1, FillColor = 'White', FillStyle="Transparent")
        self.Rect3 = Rectangle(XY3, WH, LineColor="Red", LineStyle="Solid", LineWidth=1, FillColor = 'White', FillStyle="Transparent")
        self.Rect4 = Rectangle(XY4, WH, LineColor="Red", LineStyle="Solid", LineWidth=1, FillColor = 'White', FillStyle="Transparent")
        self.Rect5 = Rectangle(XY1, WH, LineColor="Red", LineStyle="Solid", LineWidth=1, FillColor = 'White', FillStyle="Transparent")
        self.Rect6 = Rectangle(XY2, WH, LineColor="Red", LineStyle="Solid", LineWidth=1, FillColor = 'White', FillStyle="Transparent")
        self.Rect7 = Rectangle(XY3, WH, LineColor="Red", LineStyle="Solid", LineWidth=1, FillColor = 'White', FillStyle="Transparent")
        self.Rect8 = Rectangle(XY4, WH, LineColor="Red", LineStyle="Solid", LineWidth=1, FillColor = 'White', FillStyle="Transparent")

        if self.CheckBoxEnhance.GetValue() == True and self.CtrlResult[0]==1:
            EnhancedPanel.AddObject(self.Rect5)
            EnhancedPanel.AddObject(self.Rect6)
            EnhancedPanel.AddObject(self.Rect7)
            EnhancedPanel.AddObject(self.Rect8)
            EnhancedPanel.Draw(True)
        elif self.CheckBoxEnhance.GetValue() == False and self.CtrlResult[0]==1:
            OriginalPanel.AddObject(self.Rect1)
            OriginalPanel.AddObject(self.Rect2)
            OriginalPanel.AddObject(self.Rect3)
            OriginalPanel.AddObject(self.Rect4)
            OriginalPanel.Draw(True)
        else:
            pass

    def ResultTextConvert(self, text):
        if text == 1:
            text = 'Positive'
        else:
            text = 'Negative'
        return text

    def Block1Event(self, event):
        Result = self.ResultTextConvert(self.result1[3][0])
        TestMaxValue = str(np.round(self.result1[3][3], decimals=3))
        TestMinValue = str(np.round(self.result1[3][5], decimals=3))
        TestMaxDiff = str(np.round(self.result1[3][1], decimals=3))
        self.TestDFArr = self.result1[3][6]

        self.Rect1.SetLineColor('Cyan')
        self.Rect2.SetLineColor('Red')
        self.Rect3.SetLineColor('Red')
        self.Rect4.SetLineColor('Red')
        self.Rect5.SetLineColor('Red')
        self.Rect6.SetLineColor('Red')
        self.Rect7.SetLineColor('Red')
        self.Rect8.SetLineColor('Red')

        self.OriginalImg.Draw(True)
        self.EnhanceImg.Draw(True)


        TestString = 'Result :' + Result + '\n' + 'Max Value :' + TestMaxValue + '\n' + 'Mini Value :' + TestMinValue + '\n'  + 'MaxPeak :' + TestMaxDiff

        self.TestMaxIndex = self.result1[3][2]
        self.TestMaxValue = self.result1[3][3]
        self.TestMinIndex = self.result1[3][4]
        self.TestMinValue = self.result1[3][5]
        if self.ctrl_result == 'Positive':
            self.SlopeStatisticsChartForTestLine(self.Test_color, self.Test_start_interval, self.Test_end_interval, y_start=-20, y_end=20)
            self.TestLineResult.SetValue(Result)
            self.TestLineMaxValueText.SetValue(TestMaxValue)
            self.TestLineMinValueText.SetValue(TestMinValue)
            self.TestLineMaxPeakText.SetValue(TestMaxDiff)
        else:
            pass


    def Block2Event(self, event):
        Result = self.ResultTextConvert(self.result1[2][0])
        TestMaxValue = str(np.round(self.result1[2][3], decimals=3))
        TestMinValue = str(np.round(self.result1[2][5], decimals=3))
        TestMaxDiff = str(np.round(self.result1[2][1], decimals=3))
        self.TestDFArr = self.result1[2][6]

        self.Rect1.SetLineColor('Red')
        self.Rect2.SetLineColor('Cyan')
        self.Rect3.SetLineColor('Red')
        self.Rect4.SetLineColor('Red')
        self.Rect5.SetLineColor('Red')
        self.Rect6.SetLineColor('Red')
        self.Rect7.SetLineColor('Red')
        self.Rect8.SetLineColor('Red')

        self.OriginalImg.Draw(True)
        self.EnhanceImg.Draw(True)

        TestString = 'Result :' + Result + '\n' + 'Max Value :' + TestMaxValue + '\n' + 'Mini Value :' + TestMinValue + '\n' + 'MaxPeak :' + TestMaxDiff

        self.TestMaxIndex = self.result1[2][2]
        self.TestMaxValue = self.result1[2][3]
        self.TestMinIndex = self.result1[2][4]
        self.TestMinValue = self.result1[2][5]

        if self.ctrl_result == 'Positive':
            self.SlopeStatisticsChartForTestLine(self.Test_color, self.Test_start_interval, self.Test_end_interval, y_start=-20, y_end=20)
            self.TestLineResult.SetValue(Result)
            self.TestLineMaxValueText.SetValue(TestMaxValue)
            self.TestLineMinValueText.SetValue(TestMinValue)
            self.TestLineMaxPeakText.SetValue(TestMaxDiff)
        else:
            pass


    def Block3Event(self, event):
        Result = self.ResultTextConvert(self.result1[1][0])
        TestMaxValue = str(np.round(self.result1[1][3], decimals=3))
        TestMinValue = str(np.round(self.result1[1][5], decimals=3))
        TestMaxDiff = str(np.round(self.result1[1][1], decimals=3))
        self.TestDFArr = self.result1[1][6]

        self.Rect1.SetLineColor('Red')
        self.Rect2.SetLineColor('Red')
        self.Rect3.SetLineColor('Cyan')
        self.Rect4.SetLineColor('Red')
        self.Rect5.SetLineColor('Red')
        self.Rect6.SetLineColor('Red')
        self.Rect7.SetLineColor('Red')
        self.Rect8.SetLineColor('Red')
        self.OriginalImg.Draw(True)
        self.EnhanceImg.Draw(True)

        TestString = 'Result :' + Result + '\n' \
                     + 'Max Value :' + TestMaxValue + '\n' \
                     + 'Mini Value :' + TestMinValue + '\n' \
                     + 'MaxPeak :' + TestMaxDiff

        self.TestMaxIndex = self.result1[1][2]
        self.TestMaxValue = self.result1[1][3]
        self.TestMinIndex = self.result1[1][4]
        self.TestMinValue = self.result1[1][5]

        if self.ctrl_result == 'Positive':

            self.SlopeStatisticsChartForTestLine(self.Test_color, self.Test_start_interval, self.Test_end_interval, y_start=-20, y_end=20)
            self.TestLineResult.SetValue(Result)
            self.TestLineMaxValueText.SetValue(TestMaxValue)
            self.TestLineMinValueText.SetValue(TestMinValue)
            self.TestLineMaxPeakText.SetValue(TestMaxDiff)
        else:
            pass


    def Block4Event(self, event):
        Result = self.ResultTextConvert(self.result1[0][0])
        TestMaxValue = str(np.round(self.result1[0][3], decimals=3))
        TestMinValue = str(np.round(self.result1[0][5], decimals=3))
        TestMaxDiff = str(np.round(self.result1[0][1], decimals=3))
        self.TestDFArr = self.result1[0][6]

        self.Rect1.SetLineColor('Red')
        self.Rect2.SetLineColor('Red')
        self.Rect3.SetLineColor('Red')
        self.Rect4.SetLineColor('Cyan')
        self.Rect5.SetLineColor('Red')
        self.Rect6.SetLineColor('Red')
        self.Rect7.SetLineColor('Red')
        self.Rect8.SetLineColor('Red')
        self.OriginalImg.Draw(True)
        self.EnhanceImg.Draw(True)

        TestString = 'Result :' + Result + '\n' \
                     + 'Max Value :' + TestMaxValue + '\n' \
                     + 'Mini Value :' + TestMinValue + '\n' \
                     + 'MaxPeak :' + TestMaxDiff

        self.TestMaxIndex = self.result1[0][2]
        self.TestMaxValue = self.result1[0][3]
        self.TestMinIndex = self.result1[0][4]
        self.TestMinValue = self.result1[0][5]

        if self.ctrl_result == 'Positive':

            self.SlopeStatisticsChartForTestLine(self.Test_color, self.Test_start_interval, self.Test_end_interval, y_start=-20, y_end=20)
            self.TestLineResult.SetValue(Result)
            self.TestLineMaxValueText.SetValue(TestMaxValue)
            self.TestLineMinValueText.SetValue(TestMinValue)
            self.TestLineMaxPeakText.SetValue(TestMaxDiff)
        else:
            pass


    def Block5Event(self, event):
        Result = self.ResultTextConvert(self.result1[3][0])
        TestMaxValue = str(np.round(self.result1[3][3], decimals=3))
        TestMinValue = str(np.round(self.result1[3][5], decimals=3))
        TestMaxDiff = str(np.round(self.result1[3][1], decimals=3))
        self.TestDFArr = self.result1[3][6]

        self.Rect1.SetLineColor('Red')
        self.Rect2.SetLineColor('Red')
        self.Rect3.SetLineColor('Red')
        self.Rect4.SetLineColor('Red')
        self.Rect5.SetLineColor('Cyan')
        self.Rect6.SetLineColor('Red')
        self.Rect7.SetLineColor('Red')
        self.Rect8.SetLineColor('Red')
        self.OriginalImg.Draw(True)
        self.EnhanceImg.Draw(True)

        TestString = 'Result :' + Result + '\n' \
                     + 'Max Value :' + TestMaxValue + '\n' \
                     + 'Mini Value :' + TestMinValue + '\n' \
                     + 'MaxPeak :' + TestMaxDiff

        self.TestMaxIndex = self.result1[3][2]
        self.TestMaxValue = self.result1[3][3]
        self.TestMinIndex = self.result1[3][4]
        self.TestMinValue = self.result1[3][5]

        if self.ctrl_result == 'Positive':
            self.SlopeStatisticsChartForTestLine(self.Test_color, self.Test_start_interval, self.Test_end_interval, y_start=-20, y_end=20)
            self.TestLineResult.SetValue(Result)
            self.TestLineMaxValueText.SetValue(TestMaxValue)
            self.TestLineMinValueText.SetValue(TestMinValue)
            self.TestLineMaxPeakText.SetValue(TestMaxDiff)
        else:
            pass


    def Block6Event(self, event):
        Result = self.ResultTextConvert(self.result1[2][0])
        TestMaxValue = str(np.round(self.result1[2][3], decimals=3))
        TestMinValue = str(np.round(self.result1[2][5], decimals=3))
        TestMaxDiff = str(np.round(self.result1[2][1], decimals=3))
        self.TestDFArr = self.result1[2][6]

        self.Rect1.SetLineColor('Red')
        self.Rect2.SetLineColor('Red')
        self.Rect3.SetLineColor('Red')
        self.Rect4.SetLineColor('Red')
        self.Rect5.SetLineColor('Red')
        self.Rect6.SetLineColor('Cyan')
        self.Rect7.SetLineColor('Red')
        self.Rect8.SetLineColor('Red')
        self.OriginalImg.Draw(True)
        self.EnhanceImg.Draw(True)

        TestString = 'Result :' + Result + '\n' \
                     + 'Max Value :' + TestMaxValue + '\n' \
                     + 'Mini Value :' + TestMinValue + '\n' \
                     + 'MaxPeak :' + TestMaxDiff

        self.TestMaxIndex = self.result1[2][2]
        self.TestMaxValue = self.result1[2][3]
        self.TestMinIndex = self.result1[2][4]
        self.TestMinValue = self.result1[2][5]

        if self.ctrl_result == 'Positive':

            self.SlopeStatisticsChartForTestLine(self.Test_color, self.Test_start_interval, self.Test_end_interval, y_start=-20, y_end=20)
            self.TestLineResult.SetValue(Result)
            self.TestLineMaxValueText.SetValue(TestMaxValue)
            self.TestLineMinValueText.SetValue(TestMinValue)
            self.TestLineMaxPeakText.SetValue(TestMaxDiff)
        else:
            pass


    def Block7Event(self, event):
        Result = self.ResultTextConvert(self.result1[1][0])
        TestMaxValue = str(np.round(self.result1[1][3], decimals=3))
        TestMinValue = str(np.round(self.result1[1][5], decimals=3))
        TestMaxDiff = str(np.round(self.result1[1][1], decimals=3))
        self.TestDFArr = self.result1[1][6]

        self.Rect1.SetLineColor('Red')
        self.Rect2.SetLineColor('Red')
        self.Rect3.SetLineColor('Red')
        self.Rect4.SetLineColor('Red')
        self.Rect5.SetLineColor('Red')
        self.Rect6.SetLineColor('Red')
        self.Rect7.SetLineColor('Cyan')
        self.Rect8.SetLineColor('Red')
        self.OriginalImg.Draw(True)
        self.EnhanceImg.Draw(True)

        TestString = 'Result :' + Result + '\n' \
                     + 'Max Value :' + TestMaxValue + '\n' \
                     + 'Mini Value :' + TestMinValue + '\n' \
                     + 'MaxPeak :' + TestMaxDiff

        self.TestMaxIndex = self.result1[1][2]
        self.TestMaxValue = self.result1[1][3]
        self.TestMinIndex = self.result1[1][4]
        self.TestMinValue = self.result1[1][5]

        if self.ctrl_result == 'Positive':
            self.SlopeStatisticsChartForTestLine(self.Test_color, self.Test_start_interval, self.Test_end_interval, y_start=-20, y_end=20)
            self.TestLineResult.SetValue(Result)
            self.TestLineMaxValueText.SetValue(TestMaxValue)
            self.TestLineMinValueText.SetValue(TestMinValue)
            self.TestLineMaxPeakText.SetValue(TestMaxDiff)
        else:
            pass


    def Block8Event(self, event):
        Result = self.ResultTextConvert(self.result1[0][0])
        TestMaxValue = str(np.round(self.result1[0][3], decimals=3))
        TestMinValue = str(np.round(self.result1[0][5], decimals=3))
        TestMaxDiff = str(np.round(self.result1[0][1], decimals=3))
        self.TestDFArr = self.result1[0][6]

        self.Rect1.SetLineColor('Red')
        self.Rect2.SetLineColor('Red')
        self.Rect3.SetLineColor('Red')
        self.Rect4.SetLineColor('Red')
        self.Rect5.SetLineColor('Red')
        self.Rect6.SetLineColor('Red')
        self.Rect7.SetLineColor('Red')
        self.Rect8.SetLineColor('Cyan')
        self.OriginalImg.Draw(True)
        self.EnhanceImg.Draw(True)

        TestString = 'Result :' + Result + '\n' \
                     + 'Max Value :' + TestMaxValue + '\n' \
                     + 'Mini Value :' + TestMinValue + '\n' \
                     + 'MaxPeak :' + TestMaxDiff

        self.TestMaxIndex = self.result1[0][2]
        self.TestMaxValue = self.result1[0][3]
        self.TestMinIndex = self.result1[0][4]
        self.TestMinValue = self.result1[0][5]

        if self.ctrl_result == 'Positive':

            self.SlopeStatisticsChartForTestLine(self.Test_color, self.Test_start_interval, self.Test_end_interval, y_start=-20, y_end=20)
            self.TestLineResult.SetValue(Result)
            self.TestLineMaxValueText.SetValue(TestMaxValue)
            self.TestLineMinValueText.SetValue(TestMinValue)
            self.TestLineMaxPeakText.SetValue(TestMaxDiff)
        else:
            pass


####################################################################################################################################
    # def GetCurrentPar(self):
    #     #Get Ctrl Para
    #     CtrlRGB_Index = self.ChoiceForCtrlLineRGB.GetCurrentSelection()
    #     Ctrlst = self.InputValueTxtCtrlLineSt.GetValue()
    #     Ctrlpn = self.InputValueTxtCtrlLinePN.GetValue()
    #     CtrlRS = self.InputValueTxtCtrlLineRS.GetValue()
    #     CtrlRE = self.InputValueTxtCtrlLineRE.GetValue()
    #     # Get Test Para
    #     TestRGB_Index = self.ChoiceForTestLineRGB.GetCurrentSelection()
    #     Testst = self.InputValueTxtTestLineSt.GetValue()
    #     Testpn = self.InputValueTxtTestLinePN.GetValue()
    #     TestRS = self.InputValueTxtTestLineRS.GetValue()
    #     TestRE = self.InputValueTxtTestLineRE.GetValue()
    #
    #     if CtrlRGB_Index == 0:
    #         Ctrlcolor = 'red'
    #     elif CtrlRGB_Index == 1:
    #         Ctrlcolor = 'green'
    #     elif CtrlRGB_Index == 2:
    #         Ctrlcolor = 'blue'
    #
    #     if TestRGB_Index == 0:
    #         Testcolor = 'red'
    #     elif TestRGB_Index == 1:
    #         Testcolor = 'green'
    #     elif TestRGB_Index == 2:
    #         Testcolor = 'blue'
    #     '''Call function'''
    #     return CtrlRGB_Index, Ctrlst, Ctrlpn, CtrlRS, CtrlRE, Ctrlcolor, TestRGB_Index, Testst, Testpn, TestRS, TestRE, Testcolor
    #
    # def GetDiseaseParams(self):
    #     Ctrlrgb_Index, Ctrlst, Ctrlpn, CtrlRS, CtrlRE, Ctrlcolor, Testrgb_Index, Testst, Testpn, TestRS, TestRE, Testcolor = self.GetCurrentPar()
    #     #gamma = self.gamma
    #     disease = self.ChoiceForDisease.GetValue()
    #     params = DiseaseParams()
    #     #Ctrl Para
    #     params.CtrlRGB_Index = Ctrlrgb_Index
    #     params.Ctrlst = Ctrlst
    #     params.Ctrlpn = Ctrlpn
    #     params.CtrlRS = CtrlRS
    #     params.CtrlRE = CtrlRE
    #     params.Ctrlcolor = Ctrlcolor
    #     #Test Para
    #     params.TestRGB_Index = Testrgb_Index
    #     params.Testst = Testst
    #     params.Testpn = Testpn
    #     params.TestRS = TestRS
    #     params.TestRE = TestRE
    #     params.Testcolor = Testcolor
    #
    #     params.disease = disease
    #     params.useFilter = self.useFilter
    #     params.usePeakDetection = True
    #     params.useEnhance = self.CheckBoxEnhance.GetValue()
    #     return params
    #
    # def SetDiseaseParams(self, params):
    #     pass
