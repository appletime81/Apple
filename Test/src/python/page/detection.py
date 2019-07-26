import numpy as np
import wx
import os
from .VirusDetectAlgo import *
from .NosieFilter import *
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from matplotlib.figure import Figure
from pandas import DataFrame
from PIL import Image
from wx.lib.scrolledpanel import ScrolledPanel
from .base import BasePanel, DiseaseParams
from wx.lib.floatcanvas import FloatCanvas
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

        self.LoadEnhanceImgPanel = wx.Panel(self.panel, id=wx.ID_ANY, size=(500, 500), pos=(50, 547), style=0)
        #self.LoadEnhanceImgPanel.SetBackgroundColour((0, 255, 0))

        self.EnhancedStatisticsPanel = wx.Panel(self.LoadEnhanceImgPanel, id=wx.ID_ANY, size=(450, 200), pos=(0, 235), style=0)
        #self.EnhancedStatisticsPanel.SetBackgroundColour((255, 0, 0))

        #####Set the right panels#########################
        self.SlopeFigurePanel = wx.Panel(self.panel, id=wx.ID_ANY, size=(2000, 1017), pos=(550, 30), style=wx.TAB_TRAVERSAL)
        #self.SlopeFigurePanel.SetBackgroundColour((0, 255, 0))

        self.SlopeStatisticsPanel = wx.Panel(self.SlopeFigurePanel, id=wx.ID_ANY, size=(650, 350), pos=(0, 0), style=0)
        #self.SlopeStatisticsPanel.SetBackgroundColour((0, 0, 255))

        #####Set Float Cavans#############################
        self.OriginalImg = FloatCanvas.FloatCanvas(self.LoadOriginalImgPanel, -1, size=(500, 190), BackgroundColor='black')
        self.EnhanceImg = FloatCanvas.FloatCanvas(self.LoadEnhanceImgPanel, -1, size=(500, 190), BackgroundColor='black')

        #####Set the buttons##############################
        OkTestLineBut = wx.Button(self.SlopeFigurePanel, label='OK', pos=(320, 630), size=(50, 50))
        OkTestLineBut.Bind(wx.EVT_BUTTON, self.TestLine)

        CalBut = wx.Button(self.SlopeFigurePanel, label='Calculate', pos=(470, 10000))
        CalBut.Bind(wx.EVT_BUTTON, self.Calculate)
        #####Show the StaticText##########################
        self.ShowStaticText()

        #####Show the TextCtrl############################
        self.ShowTextCtrl()
        self.ShowResultTextCtrl()

        #####Show the Virus option########################
        self.VirusColorOption()

        #####Show the CheckBox for enhance################
        self.CheckBoxForEnhance()
        self.CheckBoxForUseFilter()

        #####Set default parameters#######################
        self.DefaultParameters()

        #####Set disease##################################
        self.ChoiceForDisease.Bind(wx.EVT_COMBOBOX, self.SetDefaultParameters)


        #####Set Figure Cavans############################
        self.OriginalImgFig = Figure()
        self.OriginalImgChart = FigureCanvas(self.OriginalStatisticsPanel, -1, self.OriginalImgFig)

        self.EnhancedImgFig = Figure()
        self.EnhancedImgChart = FigureCanvas(self.EnhancedStatisticsPanel, -1, self.EnhancedImgFig)

        self.StaticBoxLeftTop = wx.StaticBox(self.panel, id=wx.ID_ANY, label='Original Image', pos=(45, 13), size=(510, 490))
        self.StaticBoxLeftBot = wx.StaticBox(self.panel, id=wx.ID_ANY, label='Enhanced Image', pos=(45, 525), size=(510, 490))

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
            # c=self.gamma_enhance(im=img, enhance_value=2)

            #####Add the original pic########################
            self.BitmapImg = Bitmap(wx.Bitmap(self.ScaledImg), (0, 0), Position='cc', InForeground=False)
            self.OriginalImg.ClearAll(ResetBB=True)
            self.OriginalImg.AddObject(self.BitmapImg)
            self.OriginalImg.Draw(True)

            #####Call function###############################
            self.EnhanceImage()
            self.numpy2wximage()

            self.boundary_original_rect = None
            self.boundary_enhanced_rect = None
            self.boundary_original_ctrl_rect = None
            self.boundary_enhanced_ctrl_rect = None

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


    def numpy2wximage(self):
        width = self.W
        height = self.H
        image_matrix = self.EnhancedImgMat

        wxbmp = wx.Bitmap.FromBuffer(width, height, image_matrix)
        wxImage = wxbmp.ConvertToImage()

        if width > height:
            NewW = self.PhotoMaxSize
            NewH = self.PhotoMaxSize * height / width
        else:
            NewH = self.PhotoMaxSize
            NewW = self.PhotoMaxSize * width / height
        wxImage = wxImage.Scale(NewW, NewH)

        #####Add the original pic########################

        self.EnhancedBitmapImg = Bitmap(wx.Bitmap(wxImage), (0, 0), Position='cc', InForeground=False)
        self.EnhanceImg.ClearAll(ResetBB=True)
        self.EnhanceImg.AddObject(self.EnhancedBitmapImg)
        self.EnhanceImg.Draw(True)

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

    def ReturnSlopeDF(self, df_array):
        pic_width_pixel = len(df_array)
        df = pd.DataFrame({'x': range(0, pic_width_pixel), 'j1': df_array})
        return df

    def ShowStaticText(self):
        self.statictext_virus_title = wx.StaticText(self.SlopeFigurePanel, label='Disease : ', pos=(50, 390))

        #########Control Line#####
        self.StatictextCtrlLineTitle = wx.StaticText(self.SlopeFigurePanel, label='Control Line', pos=(50, 450))
        self.StatictextCtrlLineColor = wx.StaticText(self.SlopeFigurePanel, label='RGB Color ', pos=(50, 480))
        self.StatictextCtrlLineSt = wx.StaticText(self.SlopeFigurePanel, label='Strides Threshold : ', pos=(50, 510))
        self.StatictextCtrlLinePN = wx.StaticText(self.SlopeFigurePanel, label='PN Threshold : ', pos=(50, 540))
        self.StatictextCtrlLineRS = wx.StaticText(self.SlopeFigurePanel, label='Range of Start : ', pos=(50, 570))
        self.StatictextCtrlLineRE = wx.StaticText(self.SlopeFigurePanel, label='Range of End : ', pos=(50, 600))

        #########Test Line########
        self.StatictextTestLineTitle = wx.StaticText(self.SlopeFigurePanel, label='Test Line', pos=(320, 450))
        self.StatictextTestLineColor = wx.StaticText(self.SlopeFigurePanel, label='RGB Color ', pos=(320, 10000))
        self.StatictextTestLineSt = wx.StaticText(self.SlopeFigurePanel, label='Strides Threshold : ', pos=(320, 510))
        self.StatictextTestLinePN = wx.StaticText(self.SlopeFigurePanel, label='PN Threshold : ', pos=(320, 540))
        self.StatictextTestLineRS = wx.StaticText(self.SlopeFigurePanel, label='Range of Start : ', pos=(320, 570))
        self.StatictextTestLineRE = wx.StaticText(self.SlopeFigurePanel, label='Range of End : ', pos=(320, 600))

        #########Result Title#####
        self.StatictxtResltTitleLeft = wx.StaticText(self.SlopeStatisticsPanel, label='Control Line', pos=(50, 240))
        self.StatictxtResltTitleRight = wx.StaticText(self.SlopeStatisticsPanel, label='Test Line', pos=(320, 240))

    def ShowTextCtrl(self):
        self.InputValueTxtGamma = wx.TextCtrl(parent=self.SlopeFigurePanel, pos=(71, 10000), size=(33, 23))
        #########Control Line#####
        self.InputValueTxtCtrlLineSt = wx.TextCtrl(self.SlopeFigurePanel, pos=(157, 510), size=(33, 23))
        self.InputValueTxtCtrlLinePN = wx.TextCtrl(self.SlopeFigurePanel, pos=(157, 540), size=(33, 25))
        self.InputValueTxtCtrlLineRS = wx.TextCtrl(self.SlopeFigurePanel, pos=(157, 570), size=(33, 23))
        self.InputValueTxtCtrlLineRE = wx.TextCtrl(self.SlopeFigurePanel, pos=(157, 600), size=(33, 23))

        #########Test Line########
        self.InputValueTxtTestLineSt = wx.TextCtrl(self.SlopeFigurePanel, pos=(427, 510), size=(33, 23))
        self.InputValueTxtTestLinePN = wx.TextCtrl(self.SlopeFigurePanel, pos=(427, 540), size=(33, 25))
        self.InputValueTxtTestLineRS = wx.TextCtrl(self.SlopeFigurePanel, pos=(427, 570), size=(33, 23))
        self.InputValueTxtTestLineRE = wx.TextCtrl(self.SlopeFigurePanel, pos=(427, 600), size=(33, 23))

    def ShowResultTextCtrl(self):
        str = 'Result : \nMax Value : \nMini Value : \nMaxPeak : '
        self.TextCtrlLineResult = wx.TextCtrl(self.SlopeStatisticsPanel, style=wx.TE_MULTILINE|wx.TE_READONLY|wx.NO_BORDER, value=str,id=wx.ID_ANY, pos=(50, 259), size=(250, 70))
        self.TextTestLineResult = wx.TextCtrl(self.SlopeStatisticsPanel, style=wx.TE_MULTILINE|wx.TE_READONLY|wx.NO_BORDER, value=str,id=wx.ID_ANY, pos=(320, 259), size=(250, 70))

    def VirusColorOption(self):
        self.ChoiceForDisease = wx.ComboBox(self.SlopeFigurePanel, value='', pos=(114, 390), choices=['Flu A', 'Flu B', 'Myco', 'RSV', 'hMPV', 'StrepA'], size=(100, 20))
        self.ChoiceForCtrlLineRGB = wx.ComboBox(self.SlopeFigurePanel, value='', pos=(114, 480), choices=['R', 'G', 'B'], size=(100, 20))
        self.ChoiceForTestLineRGB = wx.ComboBox(self.SlopeFigurePanel, value='', pos=(320, 480), choices=['R', 'G', 'B'], size=(100, 20))

    def CheckBoxForEnhance(self):
        self.CheckBoxEnhance = wx.CheckBox(self.SlopeFigurePanel, id=wx.ID_ANY, label='Enhance', pos=(50, 420))
        self.CheckBoxEnhance.SetValue(True)

    def CheckBoxForUseFilter(self):
        self.CheckBoxUseFilter = wx.CheckBox(self.SlopeFigurePanel, id=wx.ID_ANY, label='Use Filter', pos=(150, 420))
        self.CheckBoxUseFilter.Bind(wx.EVT_CHECKBOX, self.SetDefaultParameters)
        self.CheckBoxUseFilter.SetValue(True)
        if self.CheckBoxUseFilter.GetValue()==True:
            self.useFilter = True
        else:
            self.useFilter = False

    def DefaultParameters(self):
        self.ChoiceForDisease.SetSelection(0)

        #####Test line default parameters############
        self.ChoiceForTestLineRGB.SetSelection(line_para_map['FluA'][1][0])
        self.InputValueTxtGamma.SetValue('2')
        self.InputValueTxtTestLineSt.SetValue(str(line_para_map['FluA'][1][3]))
        self.InputValueTxtTestLinePN.SetValue(str(line_para_map['FluA'][1][4]))
        self.InputValueTxtTestLineRS.SetValue(str(line_para_map['FluA'][1][1]))
        self.InputValueTxtTestLineRE.SetValue(str(line_para_map['FluA'][1][2]))

        #####Control line default parameters#########
        self.ChoiceForCtrlLineRGB.SetSelection(line_para_map['FluA'][0][0])
        self.InputValueTxtGamma.SetValue('2')
        self.InputValueTxtCtrlLineSt.SetValue(str(line_para_map['FluA'][0][3]))
        self.InputValueTxtCtrlLinePN.SetValue(str(line_para_map['FluA'][0][4]))
        self.InputValueTxtCtrlLineRS.SetValue(str(line_para_map['FluA'][0][1]))
        self.InputValueTxtCtrlLineRE.SetValue(str(line_para_map['FluA'][0][2]))

    def SetDefaultParameters(self, event):
        if self.CheckBoxUseFilter.GetValue()==True:
            self.useFilter = True
            para=line_para_map
        else:
            self.useFilter = False
            para=line_para_map_no_filter
        if self.ChoiceForDisease.GetValue() == 'Flu A':
            self.ChoiceForTestLineRGB.SetSelection(para['FluA'][1][0])
            self.InputValueTxtGamma.SetValue('2')
            self.InputValueTxtTestLineSt.SetValue(str(para['FluA'][1][3]))
            self.InputValueTxtTestLinePN.SetValue(str(para['FluA'][1][4]))
            self.InputValueTxtTestLineRS.SetValue(str(para['FluA'][1][1]))
            self.InputValueTxtTestLineRE.SetValue(str(para['FluA'][1][2]))
            self.ChoiceForCtrlLineRGB
            self.ChoiceForCtrlLineRGB.SetSelection(para['FluA'][0][0])
            self.InputValueTxtCtrlLineSt.SetValue(str(para['FluA'][0][3]))
            self.InputValueTxtCtrlLinePN.SetValue(str(para['FluA'][0][4]))
            self.InputValueTxtCtrlLineRS.SetValue(str(para['FluA'][0][1]))
            self.InputValueTxtCtrlLineRE.SetValue(str(para['FluA'][0][2]))

        if self.ChoiceForDisease.GetValue() == 'Flu B':
            self.ChoiceForCtrlLineRGB.SetSelection(para['FluB'][0][0])
            self.InputValueTxtGamma.SetValue('2')
            self.InputValueTxtCtrlLineSt.SetValue(str(para['FluB'][0][3]))
            self.InputValueTxtCtrlLinePN.SetValue(str(para['FluB'][0][4]))
            self.InputValueTxtCtrlLineRS.SetValue(str(para['FluB'][0][1]))
            self.InputValueTxtCtrlLineRE.SetValue(str(para['FluB'][0][2]))

            self.ChoiceForTestLineRGB.SetSelection(para['FluB'][1][0])
            self.InputValueTxtTestLineSt.SetValue(str(para['FluB'][1][3]))
            self.InputValueTxtTestLinePN.SetValue(str(para['FluB'][1][4]))
            self.InputValueTxtTestLineRS.SetValue(str(para['FluB'][1][1]))
            self.InputValueTxtTestLineRE.SetValue(str(para['FluB'][1][2]))

        if self.ChoiceForDisease.GetValue() == 'Myco':
            self.ChoiceForCtrlLineRGB.SetSelection(para['Myco'][0][0])
            self.InputValueTxtGamma.SetValue('2')
            self.InputValueTxtCtrlLineSt.SetValue(str(para['Myco'][0][3]))
            self.InputValueTxtCtrlLinePN.SetValue(str(para['Myco'][0][4]))
            self.InputValueTxtCtrlLineRS.SetValue(str(para['Myco'][0][1]))
            self.InputValueTxtCtrlLineRE.SetValue(str(para['Myco'][0][2]))

            self.ChoiceForTestLineRGB.SetSelection(line_para_map['Myco'][1][0])
            self.InputValueTxtTestLineSt.SetValue(str(para['Myco'][1][3]))
            self.InputValueTxtTestLinePN.SetValue(str(para['Myco'][1][4]))
            self.InputValueTxtTestLineRS.SetValue(str(para['Myco'][1][1]))
            self.InputValueTxtTestLineRE.SetValue(str(para['Myco'][1][2]))

        if self.ChoiceForDisease.GetValue() == 'RSV':
            self.ChoiceForCtrlLineRGB.SetSelection(para['RSV-hMPV'][0][0])
            self.InputValueTxtGamma.SetValue('2')
            self.InputValueTxtCtrlLineSt.SetValue(str(para['RSV-hMPV'][0][3]))
            self.InputValueTxtCtrlLinePN.SetValue(str(para['RSV-hMPV'][0][4]))
            self.InputValueTxtCtrlLineRS.SetValue(str(para['RSV-hMPV'][0][1]))
            self.InputValueTxtCtrlLineRE.SetValue(str(para['RSV-hMPV'][0][2]))

            self.ChoiceForTestLineRGB.SetSelection(para['RSV-hMPV'][1][0])
            self.InputValueTxtTestLineSt.SetValue(str(para['RSV-hMPV'][1][3]))
            self.InputValueTxtTestLinePN.SetValue(str(para['RSV-hMPV'][1][4]))
            self.InputValueTxtTestLineRS.SetValue(str(para['RSV-hMPV'][1][1]))
            self.InputValueTxtTestLineRE.SetValue(str(para['RSV-hMPV'][1][2]))

        if self.ChoiceForDisease.GetValue() == 'hMPV':
            self.ChoiceForCtrlLineRGB.SetSelection(para['RSV-hMPV'][0][0])
            self.InputValueTxtGamma.SetValue('2')
            self.InputValueTxtCtrlLineSt.SetValue(str(para['RSV-hMPV'][0][3]))
            self.InputValueTxtCtrlLinePN.SetValue(str(para['RSV-hMPV'][0][4]))
            self.InputValueTxtCtrlLineRS.SetValue(str(para['RSV-hMPV'][0][1]))
            self.InputValueTxtCtrlLineRE.SetValue(str(para['RSV-hMPV'][0][2]))

            self.ChoiceForTestLineRGB.SetSelection(para['RSV-hMPV'][2][0])
            self.InputValueTxtTestLineSt.SetValue(str(para['RSV-hMPV'][2][3]))
            self.InputValueTxtTestLinePN.SetValue(str(para['RSV-hMPV'][2][4]))
            self.InputValueTxtTestLineRS.SetValue(str(para['RSV-hMPV'][2][1]))
            self.InputValueTxtTestLineRE.SetValue(str(para['RSV-hMPV'][2][2]))

        if self.ChoiceForDisease.GetValue() == 'StrepA':
            self.ChoiceForCtrlLineRGB.SetSelection(para['StrepA'][0][0])
            self.InputValueTxtGamma.SetValue('2')
            self.InputValueTxtCtrlLineSt.SetValue(str(para['StrepA'][0][3]))
            self.InputValueTxtCtrlLinePN.SetValue(str(para['StrepA'][0][4]))
            self.InputValueTxtCtrlLineRS.SetValue(str(para['StrepA'][0][1]))
            self.InputValueTxtCtrlLineRE.SetValue(str(para['StrepA'][0][2]))

            self.ChoiceForTestLineRGB.SetSelection(line_para_map['StrepA'][1][0])
            self.InputValueTxtTestLineSt.SetValue(str(line_para_map['StrepA'][1][3]))
            self.InputValueTxtTestLinePN.SetValue(str(line_para_map['StrepA'][1][4]))
            self.InputValueTxtTestLineRS.SetValue(str(line_para_map['StrepA'][1][1]))
            self.InputValueTxtTestLineRE.SetValue(str(line_para_map['StrepA'][1][2]))

    def CtrlLine(self):
        if self.CheckBoxUseFilter.GetValue()==True:
            self.useFilter = True
        else:
            self.useFilter = False

        self.PlotCtrlLineBoundary()

        if self.ChoiceForDisease.GetValue() == 'Flu A':
            stride_threshold = int(self.InputValueTxtCtrlLineSt.GetValue())
            pn_threshold = float(self.InputValueTxtCtrlLinePN.GetValue())
            start_interval = int(self.InputValueTxtCtrlLineRS.GetValue())
            end_interval = int(self.InputValueTxtCtrlLineRE.GetValue())
            RGB_Index = self.ChoiceForCtrlLineRGB.GetCurrentSelection()
        if self.ChoiceForDisease.GetValue() == 'Flu B':
            stride_threshold = int(self.InputValueTxtCtrlLineSt.GetValue())
            pn_threshold = float(self.InputValueTxtCtrlLinePN.GetValue())
            start_interval = int(self.InputValueTxtCtrlLineRS.GetValue())
            end_interval = int(self.InputValueTxtCtrlLineRE.GetValue())
            RGB_Index = self.ChoiceForCtrlLineRGB.GetCurrentSelection()
        if self.ChoiceForDisease.GetValue() == 'Myco':
            stride_threshold = int(self.InputValueTxtCtrlLineSt.GetValue())
            pn_threshold = float(self.InputValueTxtCtrlLinePN.GetValue())
            start_interval = int(self.InputValueTxtCtrlLineRS.GetValue())
            end_interval = int(self.InputValueTxtCtrlLineRE.GetValue())
            RGB_Index = self.ChoiceForCtrlLineRGB.GetCurrentSelection()
        if self.ChoiceForDisease.GetValue() == 'RSV' or self.ChoiceForDisease.GetValue() == 'hMPV':
            stride_threshold = int(self.InputValueTxtCtrlLineSt.GetValue())
            pn_threshold = float(self.InputValueTxtCtrlLinePN.GetValue())
            start_interval = int(self.InputValueTxtCtrlLineRS.GetValue())
            end_interval = int(self.InputValueTxtCtrlLineRE.GetValue())
            RGB_Index = self.ChoiceForCtrlLineRGB.GetCurrentSelection()
        if self.ChoiceForDisease.GetValue() == 'StrepA':
            stride_threshold = int(self.InputValueTxtCtrlLineSt.GetValue())
            pn_threshold = float(self.InputValueTxtCtrlLinePN.GetValue())
            start_interval = int(self.InputValueTxtCtrlLineRS.GetValue())
            end_interval = int(self.InputValueTxtCtrlLineRE.GetValue())
            RGB_Index = self.ChoiceForCtrlLineRGB.GetCurrentSelection()
        self.St = stride_threshold

        if RGB_Index == 0:
            color = 'red'
        elif RGB_Index == 1:
            color = 'green'
        else:
            color = 'blue'

        #宣告parameters參數
        parameters = [RGB_Index, start_interval, end_interval, stride_threshold, pn_threshold]
        line_parameters = [parameters, parameters]

        #檢查是否Enhance
        if self.CheckBoxEnhance.GetValue() == True:
            self.CtrlResult, result1, result2 \
            = algorithm3_with_slope(self.OriginalImgMat, line_parameters, True, self.useFilter, True, False)
        else:
            self.CtrlResult, result1, result2 \
            = algorithm3_with_slope(self.OriginalImgMat, line_parameters, False, self.useFilter, True, False)

        if self.CtrlResult[0]==1:
            Result='Positive'
        else:
            Result="Negative"

        #轉換self.CtrlMaxDiff, self.CtrlMaxIndex, self.CtrlMaxValue, self.CtrlMinIndex, self.CtrlMinValue型態
        max_value = np.around(self.CtrlResult[4], decimals=3)
        min_value = np.around(self.CtrlResult[6], decimals=3)
        max_different = np.around(self.CtrlResult[2], decimals=3)

        self.CtrlDFArr = self.CtrlResult[1]

        self.CtrlLineResult = Result

        if Result == 'Positive':
            CtrlString = 'Result :'+Result+'\n'\
                     +'Max Value :'+str(max_value)+'\n'\
                     +'Mini Value :'+str(min_value)+'\n'\
                     +'MaxPeak :'+str(max_different)

            self.TextCtrlLineResult.SetValue(CtrlString)
            if self.OriginalImgFig is not None or self.EnhancedImgFig is not None:
                self.OriginalImgFig.clf()
                self.EnhancedImgFig.clf()
            self.ShowOriginalImgChartForCtrlLine(start_interval, end_interval, 0, 250)
            self.ShowEnhancedImgChartForCtrlLine(start_interval, end_interval, 0, 250)
            self.SlopeStatisticsChartForCtrlLine(color, start_interval, end_interval, -20, 20)
        else:
            CtrlString = 'Result :'+'Control Line ERROR'+'\n'\
                         +'Max Value :'+str(max_value)+'\n'\
                         +'Mini Value :'+str(min_value)+'\n'\
                         +'MaxPeak :'+str(max_different)

            self.TextCtrlLineResult.SetValue(CtrlString)
            if self.OriginalImgFig is not None or self.EnhancedImgFig is not None:
                self.OriginalImgFig.clf()
                self.EnhancedImgFig.clf()
            self.ShowOriginalImgChartForCtrlLine(start_interval, end_interval, 0, 250)
            self.ShowEnhancedImgChartForCtrlLine(start_interval, end_interval, 0, 250)
            self.SlopeStatisticsChartForCtrlLine(color, start_interval, end_interval, -20, 20)


    def TestLine(self, event):
        self.CtrlLine()

        stride_threshold = int(self.InputValueTxtTestLineSt.GetValue())
        pn_threshold = float(self.InputValueTxtTestLinePN.GetValue())
        start_interval = int(self.InputValueTxtTestLineRS.GetValue())
        end_interval = int(self.InputValueTxtTestLineRE.GetValue())
        RGB_Index = self.ChoiceForTestLineRGB.GetCurrentSelection()

        if RGB_Index == 0:
            color = 'red'
        elif RGB_Index == 1:
            color = 'green'
        else:
            color = 'blue'

        parameters = [RGB_Index, start_interval, end_interval, stride_threshold, pn_threshold]
        line_parameters = [parameters, parameters]

        y_start = 0
        y_end = 250

        self.TestMaxDiff = None
        self.TestMaxIndex = None
        self.TestMinIndex = None
        self.TestMinValue = None
        self.TestDFArr = None

        if self.CheckBoxEnhance.GetValue() == True:
            ControlResult, self.TestResult, result2 \
            = algorithm3_with_slope(self.OriginalImgMat, line_parameters, True, self.useFilter, True, False)
        else:
            ControlResult, self.TestResult, result2 \
            = algorithm3_with_slope(self.OriginalImgMat, line_parameters, False, self.useFilter, True, False)

        self.TestMinIndex = self.TestResult[5]
        self.TestMinValue = self.TestResult[6]
        self.TestMaxIndex = self.TestResult[3]
        self.TestMaxValue = self.TestResult[4]
        self.TestMaxDiff = self.TestResult[2]

        self.TestDFArr = self.TestResult[1]

        if self.TestResult[0]==1:
            Result='Positive'
        else:
            Result='Negative'

        TestMaxValue = np.round(self.TestMaxValue, decimals=3)
        TestMinValue = np.round(self.TestMinValue, decimals=3)
        TestMaxDiff = np.round(self.TestMaxDiff, decimals=3)

        if self.CtrlLineResult == 'Positive':

            self.EnhancedCheck()

            TestString = 'Result :' + Result + '\n'\
                         + 'Max Value :' + str(TestMaxValue) + '\n'\
                         + 'Mini Value :' + str(TestMinValue) + '\n'\
                         + 'MaxPeak :' + str(TestMaxDiff)

            #self.TextCtrlLineResult.SetValue(CtrlString)
            self.TextTestLineResult.SetValue(TestString)
            self.ShowEnhancedImgChartForTestLine(start_interval, end_interval, y_start, y_end)
            self.ShowOriginalImgChartForTestLine(start_interval, end_interval, y_start, y_end)
            self.PlotCtrlLineBoundary()
            self.PlotTestLineBoundary()
            self.SlopeStatisticsChartForTestLine(color, start_interval, end_interval, y_start=-20, y_end=20)
        else:
            pass

    def EnhancedCheck(self):
        if self.CheckBoxEnhance.GetValue() == True:
            self.EnhanceImg.ClearAll(ResetBB=True)
            self.EnhanceImg.AddObject(self.EnhancedBitmapImg)
            self.EnhanceImg.Draw(True)
        else:
            self.EnhanceImg.ClearAll(ResetBB=True)
            self.EnhanceImg.AddObject(self.EnhancedBitmapImg)
            self.EnhanceImg.Draw(True)

    def Calculate(self, event):
        abspath = []
        MaxPeak = []
        rsTestLine = int(self.InputValueTxtTestLineRS.GetValue())
        reTestLine = int(self.InputValueTxtTestLineRE.GetValue())
        stTestLine = int(self.InputValueTxtTestLineSt.GetValue())
        pnTestLine = float(self.InputValueTxtTestLinePN.GetValue())
        rgbTestLineIndex = self.ChoiceForTestLineRGB.GetSelection()
        disease = self.ChoiceForDisease.GetValue()

        rsCtrlLine = int(self.InputValueTxtCtrlLineRS.GetValue())
        reCtrlLine = int(self.InputValueTxtCtrlLineRE.GetValue())
        stCtrlLine = int(self.InputValueTxtCtrlLineSt.GetValue())
        pnCtrlLine = float(self.InputValueTxtCtrlLinePN.GetValue())

        CtrlPara = [rgbTestLineIndex, rsCtrlLine, reCtrlLine, stCtrlLine, pnCtrlLine]
        TestPara = [rgbTestLineIndex, rsTestLine, reTestLine, stTestLine, pnTestLine]

        if disease == 'Flu A':
            self.path = './samples/A/0'
            rgbCtrlLineIndex = 2
        elif disease == 'Flu B':
            self.path = './samples/B/0'
            rgbCtrlLineIndex = 2
        elif disease == 'Myco':
            self.path = './samples/Myco/0'
            rgbCtrlLineIndex = 1
        elif disease == 'RSV':
            self.path = './samples/RSV/0'
            rgbCtrlLineIndex = 1
        elif disease == 'StrepA':
            self.path = './samples/StrepA/0'
            rgbCtrlLineIndex = 1
        else:
            self.path = './samples/hMPV/0'
            rgbCtrlLineIndex = 1

        for dirPath, dirNames, fileNames in os.walk(self.path):
            dirPath = dirPath.replace('\\', '/')
            for f in fileNames:
                fartherPath = str(os.path.join(dirPath, f)).replace('\\', '/')
                if os.path.isfile(fartherPath):
                    abspath.append(fartherPath)
                else:
                    pass

        for i in range(len(abspath)):
            img = Image.open(abspath[i])
            img = np.array(img)
            img = np.power(img / float(np.max(img)), 2) * float(np.max(img))
            result, max_different, max_index, max_value, min_index, min_value, df_array = find_peak(img, CtrlPara, self.useFilter, True, True)

            if result == 1:
                result, max_different, max_index, max_value, min_index, min_value, df_array = find_peak(img, TestPara, self.useFilter, True, True)
                MaxPeak.append(max_different)
            else:
                pass

        MaxPeak = np.asarray(MaxPeak)
        stdMaxPeak = np.std(MaxPeak)
        meanMaxPeak = np.mean(MaxPeak)
        recommendPN = meanMaxPeak + 2*stdMaxPeak
        recommendPN = (Decimal(recommendPN).quantize(Decimal('0.000')))
        recommendPN = str(recommendPN)

        self.InputValueTxtTestLinePN.SetValue(recommendPN)
####################################################Drawing Chart###################################################################
    def ShowOriginalImgChartForCtrlLine(self, start_interval, end_interval, y_start, y_end):
        df = self.ShowPlot(self.OriginalImgMat)
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
        df = self.ShowPlot(self.EnhancedImgMat)
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
        self.axes_EnhancedImg.plot(xpoint_start, ypoint_start, 'r', linewidth=1)
        self.axes_EnhancedImg.plot(xpoint_end, ypoint_end, 'r', linewidth=1)
        self.EnhancedImgChart.draw()

    def SlopeStatisticsChartForCtrlLine(self, color, start_interval, end_interval, y_start, y_end):
        self.SlopeFigure = Figure()
        self.SlopeFigure.set_figheight(2.2)
        self.SlopeFigure.set_figwidth(5)
        self.axes_slope = self.SlopeFigure.add_subplot(1, 1, 1)
        self.axes_slope.set_ylim(-20, 20)
        if self.CtrlLineResult=='Negative':
            df = self.ReturnSlopeDF(self.CtrlDFArr)
            self.axes_slope.plot('x', 'j1', data=df, color=color, linewidth=1)
        #########################################################################
        points_start = [(start_interval, y_start), (start_interval , y_end)]
        (xpoint_start, ypoint_start) = zip( * points_start)
        points_end = [(end_interval, y_start), (end_interval, y_end)]
        (xpoint_end, ypoint_end) = zip( * points_end)
        self.axes_slope.plot(xpoint_start, ypoint_start, 'g', linewidth=1)
        self.axes_slope.plot(xpoint_end, ypoint_end, 'g', linewidth=1)
        #########################################################################

    def SlopeStatisticsChartForTestLine(self, color, start_interval, end_interval, y_start, y_end):
        #########################################################################
        df = self.ReturnSlopeDF(self.TestDFArr)
        self.axes_slope.plot('x', 'j1', data=df, color=color, linewidth=1)
        #########################################################################
        points_start = [(start_interval, y_start), (start_interval , y_end)]
        (xpoint_start, ypoint_start) = zip( * points_start)
        points_end = [(end_interval, y_start), (end_interval, y_end)]
        (xpoint_end, ypoint_end) = zip( * points_end)
        self.axes_slope.plot(xpoint_start, ypoint_start, 'r', linewidth=1)
        self.axes_slope.plot(xpoint_end, ypoint_end, 'r', linewidth=1)
        #########################################################################
        self.axes_slope.grid(True)
        self.axes_slope.plot(self.TestMaxIndex+start_interval, self.TestMaxValue, 'ro')
        self.axes_slope.plot(self.TestMinIndex+start_interval, self.TestMinValue, 'ro')
        FigureCanvas(self.SlopeStatisticsPanel, -1, self.SlopeFigure)

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

        if self.CheckBoxEnhance.GetValue() == True:
            self.EnhanceImg.AddObject(self.boundary_enhanced_rect)
            self.SetBoundaryLine(self.EnhanceImg, int(self.InputValueTxtTestLineRS.GetValue()), int(self.InputValueTxtTestLineRE.GetValue()))
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

        if self.CheckBoxEnhance.GetValue() == True:
            self.EnhanceImg.AddObject(self.boundary_enhanced_ctrl_rect)
            self.SetBoundaryLineForCtrlLine(self.EnhanceImg, int(self.InputValueTxtCtrlLineRS.GetValue()), int(self.InputValueTxtCtrlLineRE.GetValue()))
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
####################################################################################################################################
    def GetCurrentPar(self):
        #Get Ctrl Para
        CtrlRGB_Index = self.ChoiceForCtrlLineRGB.GetCurrentSelection()
        Ctrlst = self.InputValueTxtCtrlLineSt.GetValue()
        Ctrlpn = self.InputValueTxtCtrlLinePN.GetValue()
        CtrlRS = self.InputValueTxtCtrlLineRS.GetValue()
        CtrlRE = self.InputValueTxtCtrlLineRE.GetValue()
        # Get Test Para
        TestRGB_Index = self.ChoiceForTestLineRGB.GetCurrentSelection()
        Testst = self.InputValueTxtTestLineSt.GetValue()
        Testpn = self.InputValueTxtTestLinePN.GetValue()
        TestRS = self.InputValueTxtTestLineRS.GetValue()
        TestRE = self.InputValueTxtTestLineRE.GetValue()

        if CtrlRGB_Index == 0:
            Ctrlcolor = 'red'
        elif CtrlRGB_Index == 1:
            Ctrlcolor = 'green'
        elif CtrlRGB_Index == 2:
            Ctrlcolor = 'blue'

        if TestRGB_Index == 0:
            Testcolor = 'red'
        elif TestRGB_Index == 1:
            Testcolor = 'green'
        elif TestRGB_Index == 2:
            Testcolor = 'blue'
        '''Call function'''
        return CtrlRGB_Index, Ctrlst, Ctrlpn, CtrlRS, CtrlRE, Ctrlcolor, TestRGB_Index, Testst, Testpn, TestRS, TestRE, Testcolor

    def GetDiseaseParams(self):
        Ctrlrgb_Index, Ctrlst, Ctrlpn, CtrlRS, CtrlRE, Ctrlcolor, Testrgb_Index, Testst, Testpn, TestRS, TestRE, Testcolor = self.GetCurrentPar()
        #gamma = self.gamma
        disease = self.ChoiceForDisease.GetValue()
        params = DiseaseParams()
        #Ctrl Para
        params.CtrlRGB_Index = Ctrlrgb_Index
        params.Ctrlst = Ctrlst
        params.Ctrlpn = Ctrlpn
        params.CtrlRS = CtrlRS
        params.CtrlRE = CtrlRE
        params.Ctrlcolor = Ctrlcolor
        #Test Para
        params.TestRGB_Index = Testrgb_Index
        params.Testst = Testst
        params.Testpn = Testpn
        params.TestRS = TestRS
        params.TestRE = TestRE
        params.Testcolor = Testcolor

        params.disease = disease
        params.useFilter = self.useFilter
        params.usePeakDetection = True
        params.useEnhance = self.CheckBoxEnhance.GetValue()
        return params

    def SetDiseaseParams(self, params):
        pass