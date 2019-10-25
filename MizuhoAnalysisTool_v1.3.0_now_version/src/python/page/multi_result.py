import wx
import os
import numpy as np
import cv2
from .base import BasePanel
from PIL import Image
from decimal import *
from .VirusDetectAlgo import *
from .NosieFilter import *
from matplotlib.figure import Figure
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from wx.lib.floatcanvas import FloatCanvas, FCObjects
from wx.lib.floatcanvas.FCObjects import ScaledBitmap, Rectangle, Bitmap
from pandas import DataFrame

class MultiResultPanel(BasePanel):

    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)
        ##########Set the scroll panel######################
        self.panel = wx.lib.scrolledpanel.ScrolledPanel(parent=self, style = wx.ALL|wx.EXPAND)
        self.panel.SetupScrolling()                        #
        # self.panel.SetScrollbars(wx.VERTICAL, 1, 1, 1200)
        # self.panel.SetScrollbars(wx.HORIZONTAL, 1, 1, 1200)
        # self.panel.SetScrollRate(0, 10)                  #
        #self.panel.SetBackgroundColour('Yellow')          #
                                                           #
        boxSizer = wx.BoxSizer(wx.VERTICAL)                #
        boxSizer.Add(self.panel)                           #
        self.SetSizer(boxSizer)                            #
        ####################################################
        #####Set the photo size###########################
        self.PhotoMaxSize = 350

        ###############Set Panel############################
        self.ScrollPanel = wx.Panel(parent=self.panel, id=wx.ID_ANY, size=(2000, 1000), pos=(0, 0), style=0)

        self.LoadOriginalImgPanel = wx.Panel(parent=self.ScrollPanel, id=wx.ID_ANY, size=(500, 500), pos=(545, 30), style=0)
        #self.LoadOriginalImgPanel.SetBackgroundColour((0, 255, 0))

        self.OriginalStatisticsPanel = wx.Panel(self.LoadOriginalImgPanel, id=wx.ID_ANY, size=(450, 200), pos=(0, 235), style=0)
        #self.OriginalStatisticsPanel.SetBackgroundColour((0, 0, 255))

        self.LoadEnhanceImgPanel = wx.Panel(self.ScrollPanel, id=wx.ID_ANY, size=(500, 500), pos=(545, 547), style=0)
        #self.LoadEnhanceImgPanel.SetBackgroundColour((0, 255, 0))

        self.EnhancedStatisticsPanel = wx.Panel(self.LoadEnhanceImgPanel, id=wx.ID_ANY, size=(450, 200), pos=(0, 235), style=0)
        #self.EnhancedStatisticsPanel.SetBackgroundColour((255, 0, 0))

        self.SlopeFigurePanel = wx.Panel(self.ScrollPanel, id=wx.ID_ANY, size=(2000, 1017), pos=(1045, 50), style=wx.TAB_TRAVERSAL)
        #self.SlopeFigurePanel.SetBackgroundColour((0, 255, 0))

        self.SlopeStatisticsPanel = wx.Panel(self.SlopeFigurePanel, id=wx.ID_ANY, size=(1000, 216), pos=(0, 0), style=0)
        #self.SlopeStatisticsPanel.SetBackgroundColour((0, 0, 255))

        #####Set Float Cavans#############################
        self.OriginalImg = FloatCanvas.FloatCanvas(self.LoadOriginalImgPanel, -1, size=(500, 190), BackgroundColor='black')
        self.EnhanceImg = FloatCanvas.FloatCanvas(self.LoadEnhanceImgPanel, -1, size=(500, 190), BackgroundColor='black')
        ###############Set Button###########################
        StartBut = wx.Button(self.ScrollPanel, label='Start', pos=(50, 50))
        StartBut.Bind(wx.EVT_BUTTON, self.ClickBtn_Start)
        CopyBut = wx.Button(self.ScrollPanel, label='Copy to Clipboard', pos=(146, 50))
        CopyBut.Bind(wx.EVT_BUTTON, self.ClickBtn_Copy)
        #OkTestLineBut = wx.Button(self.SlopeFigurePanel, label='OK', pos=(320, 630), size=(50, 50))
        #OkTestLineBut.Bind(wx.EVT_BUTTON, self.TestLine)
        #PnBut = wx.Button()


        ###############Set TextCtrl Font#####################
        self.textCtrlFont = wx.Font(12, wx.FONTFAMILY_ROMAN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)

        self.strTextCtrl = wx.TextCtrl(self.ScrollPanel, id=wx.ID_ANY, value="", pos=(50, 475), size=(484,375), style=wx.TE_MULTILINE)

        ###############Set ListCtrl##########################
        self.ListCtrl = wx.ListCtrl(self.ScrollPanel, size=(484,375), pos=(50, 80), style=wx.LC_REPORT|wx.BORDER_SUNKEN)
        self.ListCtrl.InsertColumn(0, 'File Name', width=257)
        self.ListCtrl.InsertColumn(1, 'Result', width=136)
        self.ListCtrl.InsertColumn(2, 'Max Peak', width=91)
        self.ListCtrl.InsertColumn(3, 'Sec. 1', width=91)
        self.ListCtrl.InsertColumn(4, 'Sec. 2', width=91)
        self.ListCtrl.InsertColumn(5, 'Sec. 3', width=91)
        self.ListCtrl.InsertColumn(6, 'Sec. 4', width=91)

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
        self.CheckBoxFor4Blocks()
        self.CheckBoxForWhiteBalance()
        self.ScrollMenu()

        #####Set default parameters#######################
        self.DefaultParameters()

        self.ChoiceForDisease.Bind(wx.EVT_COMBOBOX, self.SetDefaultParameters)
        #####Set Figure Cavans############################
        self.OriginalImgFig = Figure()
        self.OriginalImgChart = FigureCanvas(self.OriginalStatisticsPanel, -1, self.OriginalImgFig)

        self.EnhancedImgFig = Figure()
        self.EnhancedImgChart = FigureCanvas(self.EnhancedStatisticsPanel, -1, self.EnhancedImgFig)


        # self.SlopeFigure = Figure()
        # self.SlopeFigureChart = FigureCanvas(self.SlopeStatisticsPanel, -1, self.SlopeFigure)
        #####Build Rect##################################
        self.BuildRect()

        self.boundary_original_rect = None
        self.boundary_enhanced_rect = None
        self.boundary_original_ctrl_rect = None
        self.boundary_enhanced_ctrl_rect = None

        self.StaticBoxLeftTop = wx.StaticBox(self.panel, id=wx.ID_ANY, label='Original Image', pos=(543, 13), size=(510, 490))
        self.StaticBoxLeftBot = wx.StaticBox(self.panel, id=wx.ID_ANY, label='Enhanced Image', pos=(543, 525), size=(510, 490))

        self.ClickBtnPN()

        self.PnThresholdBut.Bind(wx.EVT_BUTTON, self.GeneratePN)
        self.CheckBoxBlocks.Bind(wx.EVT_CHECKBOX, self.CheckBox4BlocksEvent)
        #self.CheckBoxBlocks.Bind(wx.EVT_CHECKBOX, self.GeneratePN4Blocks)


    def ShowStaticText(self):
        self.ResultText = wx.StaticText(self.SlopeFigurePanel, label='Result : ', pos=(50, 480))

        self.statictext_virus_title = wx.StaticText(self.SlopeFigurePanel, label='Disease : ', pos=(50, 505))

        #########Control Line#####
        self.StatictextCtrlLineTitle = wx.StaticText(self.SlopeFigurePanel, label='Control Line', pos=(50, 535))
        self.StatictextCtrlLineColor = wx.StaticText(self.SlopeFigurePanel, label='RGB Color ', pos=(50, 565))
        self.StatictextCtrlLineSt = wx.StaticText(self.SlopeFigurePanel, label='Strides Threshold : ', pos=(50, 595))
        self.StatictextCtrlLinePN = wx.StaticText(self.SlopeFigurePanel, label='PN Threshold : ', pos=(50, 625))
        self.StatictextCtrlLineRS = wx.StaticText(self.SlopeFigurePanel, label='Range of Start : ', pos=(50, 655))
        self.StatictextCtrlLineRE = wx.StaticText(self.SlopeFigurePanel, label='Range of End : ', pos=(50, 685))

        #########Test Line########
        self.StatictextTestLineTitle = wx.StaticText(self.SlopeFigurePanel, label='Test Line', pos=(320, 535))
        self.StatictextTestLineColor = wx.StaticText(self.SlopeFigurePanel, label='RGB Color ', pos=(320, 10000))
        self.StatictextTestLineSt = wx.StaticText(self.SlopeFigurePanel, label='Strides Threshold : ', pos=(320, 595))
        self.StatictextTestLinePN = wx.StaticText(self.SlopeFigurePanel, label='PN Threshold : ', pos=(320, 625))
        self.StatictextTestLineRS = wx.StaticText(self.SlopeFigurePanel, label='Range of Start : ', pos=(320, 655))
        self.StatictextTestLineRE = wx.StaticText(self.SlopeFigurePanel, label='Range of End : ', pos=(320, 685))

        #########Result Title#####
        self.StatictxtResltTitleLeft = wx.StaticText(self.SlopeFigurePanel, label='Control Line', pos=(50, 353))
        #self.StatictxtResltTitleRight = wx.StaticText(self.SlopeFigurePanel, label='Test Line', pos=(180, 353))
        self.StatictxtResltTitleRight = wx.StaticText(self.SlopeFigurePanel, label='Test Line Sec.1', pos=(180, 353))
        self.StatictxtResltTitleRight = wx.StaticText(self.SlopeFigurePanel, label='Test Line Sec.2', pos=(310, 353))
        self.StatictxtResltTitleRight = wx.StaticText(self.SlopeFigurePanel, label='Test Line Sec.3', pos=(440, 353))
        self.StatictxtResltTitleRight = wx.StaticText(self.SlopeFigurePanel, label='Test Line Sec.4', pos=(570, 353))

        self.StatictxtResltTitleLeft_top = wx.StaticText(self.SlopeFigurePanel, label='Control Line', pos=(50, 248))
        self.StatictxtResltTitleRight_top = wx.StaticText(self.SlopeFigurePanel, label='Test Line', pos=(180, 248))


        self.StdTxt = wx.StaticText(self.SlopeFigurePanel, label='Std. Value', pos=(507, 605))

    def ShowTextCtrl(self):
        self.InputValueTxtGamma = wx.TextCtrl(parent=self.SlopeFigurePanel, pos=(71, 10000), size=(33, 23))
        #########Control Line#####
        self.InputValueTxtCtrlLineSt = wx.TextCtrl(self.SlopeFigurePanel, pos=(157, 595), size=(33, 23))
        self.InputValueTxtCtrlLinePN = wx.TextCtrl(self.SlopeFigurePanel, pos=(157, 625), size=(33, 25))
        self.InputValueTxtCtrlLineRS = wx.TextCtrl(self.SlopeFigurePanel, pos=(157, 655), size=(33, 23))
        self.InputValueTxtCtrlLineRE = wx.TextCtrl(self.SlopeFigurePanel, pos=(157, 685), size=(33, 23))

        #########Test Line########
        self.InputValueTxtTestLineSt = wx.TextCtrl(self.SlopeFigurePanel, pos=(427, 595), size=(33, 23))
        self.InputValueTxtTestLinePN = wx.TextCtrl(self.SlopeFigurePanel, pos=(427, 625), size=(33, 25))
        self.InputValueTxtTestLineRS = wx.TextCtrl(self.SlopeFigurePanel, pos=(427, 655), size=(33, 23))
        self.InputValueTxtTestLineRE = wx.TextCtrl(self.SlopeFigurePanel, pos=(427, 685), size=(33, 23))

        #########PN Threshold#####
        #self.ShowCalculatedPN = wx.TextCtrl(self.SlopeFigurePanel, pos=(572, 538), size=(65, 23))

    def ShowResultTextCtrl(self):
        str = 'Result : \nMax Value : \nMini Value : \nMaxPeak : '

        self.TextCtrlLineResult_top = wx.TextCtrl(self.SlopeFigurePanel, style=wx.TE_MULTILINE | wx.TE_READONLY | wx.NO_BORDER | wx.TE_NO_VSCROLL, value=str, id=wx.ID_ANY, pos=(50, 266), size=(145, 70))
        self.TextTestLineResult_top = wx.TextCtrl(self.SlopeFigurePanel, style=wx.TE_MULTILINE | wx.TE_READONLY | wx.NO_BORDER | wx.TE_NO_VSCROLL, value=str, id=wx.ID_ANY, pos=(180, 266), size=(145, 70))

        self.TextCtrlLineResult = wx.TextCtrl(self.SlopeFigurePanel, style=wx.TE_MULTILINE | wx.TE_READONLY | wx.NO_BORDER | wx.TE_NO_VSCROLL, value=str, id=wx.ID_ANY, pos=(50, 369), size=(145, 70))
        #self.TextTestLineResult = wx.TextCtrl(self.SlopeFigurePanel, style=wx.TE_MULTILINE | wx.TE_READONLY | wx.NO_BORDER | wx.TE_NO_VSCROLL, value=str, id=wx.ID_ANY, pos=(180, 369), size=(145, 70))

        self.TextTestLineResultSec1 = wx.TextCtrl(self.SlopeFigurePanel, style=wx.TE_MULTILINE | wx.TE_READONLY | wx.NO_BORDER | wx.TE_NO_VSCROLL, value=str, id=wx.ID_ANY, pos=(180, 369), size=(145, 70))
        self.TextTestLineResultSec2 = wx.TextCtrl(self.SlopeFigurePanel, style=wx.TE_MULTILINE | wx.TE_READONLY | wx.NO_BORDER | wx.TE_NO_VSCROLL, value=str, id=wx.ID_ANY, pos=(310, 369), size=(145, 70))
        self.TextTestLineResultSec3 = wx.TextCtrl(self.SlopeFigurePanel, style=wx.TE_MULTILINE | wx.TE_READONLY | wx.NO_BORDER | wx.TE_NO_VSCROLL, value=str, id=wx.ID_ANY, pos=(440, 369), size=(145, 70))
        self.TextTestLineResultSec4 = wx.TextCtrl(self.SlopeFigurePanel, style=wx.TE_MULTILINE | wx.TE_READONLY | wx.NO_BORDER | wx.TE_NO_VSCROLL, value=str, id=wx.ID_ANY, pos=(570, 369), size=(145, 70))

    def VirusColorOption(self):
        self.ChoiceForDisease = wx.ComboBox(self.SlopeFigurePanel, value='', pos=(114, 505), choices=['Flu A', 'Flu B', 'Myco', 'RSV', 'hMPV', 'StrepA'], size=(100, 20))
        self.ChoiceForCtrlLineRGB = wx.ComboBox(self.SlopeFigurePanel, value='', pos=(114, 565), choices=['R', 'G', 'B'], size=(100, 20))
        self.ChoiceForTestLineRGB = wx.ComboBox(self.SlopeFigurePanel, value='', pos=(320, 565), choices=['R', 'G', 'B'], size=(100, 20))

    def CheckBoxForEnhance(self):
        self.CheckBoxEnhance = wx.CheckBox(self.SlopeFigurePanel, id=wx.ID_ANY, label='Enhance', pos=(50, 455))
        self.CheckBoxEnhance.SetValue(True)

    def CheckBoxForUseFilter(self):
        self.CheckBoxUseFilter = wx.CheckBox(self.SlopeFigurePanel, id=wx.ID_ANY, label='Use Filter', pos=(150, 455))
        self.CheckBoxUseFilter.Bind(wx.EVT_CHECKBOX, self.SetDefaultParameters)
        self.CheckBoxUseFilter.SetValue(True)
        if self.CheckBoxUseFilter.GetValue() == True:
            self.useFilter = True
        else:
            self.useFilter = False

    def CheckBox4BlocksEvent(self, event):
        if self.CheckBoxBlocks.GetValue()==True:
            self.StdValue.SetValue('2')
            self.GeneratePN4Blocks()
            if self.FileExist()==True:
                self.TestLineNoEvent()
            else:
                self.TextCtrlLineResult.SetValue('')
                #self.TextTestLineResult.SetValue('')
                self.TextTestLineResultSec1.SetValue('')
                self.TextTestLineResultSec2.SetValue('')
                self.TextTestLineResultSec3.SetValue('')
                self.TextTestLineResultSec4.SetValue('')
        else:
            self.StdValue.SetValue('4')
            self.GeneratePN4Blocks()
            self.TestLineNoEvent()

    def CheckBoxForWhiteBalance(self):
        self.CheckBoxUseWhiteBalance = wx.CheckBox(self.SlopeFigurePanel, id=wx.ID_ANY, label='White Balance', pos=(245, 455))
        self.CheckBoxUseWhiteBalance.SetValue(True)
        #self.CheckBoxUseWhiteBalance.Bind(wx.EVT_CHECKBOX, self.SetDefaultParameters)

    def ClickBtn_Start(self, event):
        disease  = self.ChoiceForDisease.GetValue()
        self.LoadImage(disease)

        if self.ListCtrl.GetItemCount() > 0:
            self.ListCtrl.DeleteAllItems()
        self.DistinguishProcess()

    def ClickBtn_Copy(self, event):
        self.Copy2TxtCtrl(self.rows)

    def ClickBtnPN(self):
        self.PnThresholdBut = wx.Button(self.SlopeFigurePanel, label='Cal.', pos=(475, 622), size=(30,25))

    def CheckBoxFor4Blocks(self):
        self.CheckBoxBlocks = wx.CheckBox(self.SlopeFigurePanel, id=wx.ID_ANY, label='4 Blocks Detection', pos=(375, 455))
        self.CheckBoxBlocks.SetValue(False)

    def ScrollMenu(self):
        #4Blocks選單
        self.BlockNum = wx.ComboBox(self.SlopeFigurePanel, value='4', choices=['4', '3', '2', '1'], pos=(500, 452))
        #標準差選單
        self.StdValue = wx.ComboBox(self.SlopeFigurePanel, value='4', choices=['5', '4', '3', '2', '1'], pos=(510, 623), size=(51, 22))

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
            #self.pn1, self.pn2 = calculateCutOffValue4Block(ImgPathList, line_parameters, std_rate=int(self.StdValue.GetValue()))
            self.pn1, self.pn2 = calculateCutOffValue4Block(ImgPathList, line_parameters, self.CheckBoxEnhance.GetValue(), self.CheckBoxUseWhiteBalance.GetValue(), std_rate=int(self.StdValue.GetValue())) #Check
        else:
            self.pn1, self.pn2 = calculateCutOffValue(ImgPathList, line_parameters, self.CheckBoxEnhance.GetValue(), self.CheckBoxUseWhiteBalance.GetValue(), std_rate=int(self.StdValue.GetValue())) #Check

        #self.ShowCalculatedPN.SetValue(str(np.round(self.pn1, decimals=3)))
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
            if os.path.exists(NegPath):
                if len([name for name in os.listdir(NegPath) if os.path.isfile(os.path.join(NegPath, name))]) <= 1:
                    self.InputValueTxtTestLinePN.SetValue('NA')
                else:
                    paths = os.listdir(NegPath)
                    for i in range(len(paths)):
                        if paths[i].find('ini') >= 0:
                            pass
                        else:
                            ImgPathList.append(NegPath + '/' + paths[i])

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

                    if self.CheckBoxBlocks.GetValue() == True:
                        self.pn1, self.pn2 = calculateCutOffValue4Block(ImgPathList, line_parameters, self.CheckBoxEnhance.GetValue(), self.CheckBoxUseWhiteBalance.GetValue(), std_rate=int(self.StdValue.GetValue())) #Check
                    else:
                        self.pn1, self.pn2 = calculateCutOffValue(ImgPathList, line_parameters, self.CheckBoxEnhance.GetValue(), self.CheckBoxUseWhiteBalance.GetValue(), std_rate=int(self.StdValue.GetValue()))#Check

                    # self.ShowCalculatedPN.SetValue(str(np.round(self.pn1, decimals=3)))
                    self.InputValueTxtTestLinePN.SetValue(str(np.round(self.pn1, decimals=3)))
            else:
                self.InputValueTxtTestLinePN.SetValue('NA')

        else:
            para = [get_line_para_map('FluA'), get_line_para_map('FluB'), get_line_para_map('Myco'),
                    get_line_para_map('RSV-hMPV'), get_line_para_map('StrepA')]
            if self.ChoiceForDisease.GetValue() == 'Flu A':
                self.InputValueTxtTestLinePN.SetValue(str(para[0][1][4]))
            elif self.ChoiceForDisease.GetValue() == 'Flu B':
                self.InputValueTxtTestLinePN.SetValue(str(para[1][1][4]))
            elif self.ChoiceForDisease.GetValue() == 'Myco':
                self.InputValueTxtTestLinePN.SetValue(str(para[2][1][4]))
            elif self.ChoiceForDisease.GetValue() == 'RSV':
                self.InputValueTxtTestLinePN.SetValue(str(para[3][1][4]))
            elif self.ChoiceForDisease.GetValue() == 'hMPV':
                self.InputValueTxtTestLinePN.SetValue(str(para[3][2][4]))
            else:
                self.InputValueTxtTestLinePN.SetValue(str(para[4][1][4]))

    def BuildRect(self):
        self.Rect1 = None
        self.Rect2 = None
        self.Rect3 = None
        self.Rect4 = None
        self.Rect5 = None
        self.Rect6 = None
        self.Rect7 = None
        self.Rect8 = None

    def LoadImage(self, disease):
        self.imglst = []
        self.files = []
        paths=[]

        if disease == 'Flu A':
            path = os.listdir('./samples/FluA')
            path = list(map(int, path))
            path.sort()
            for i in range(len(path)):
                paths.append('./samples/FluA' + '/' + str(path[i]))
            for i in range(len(paths)):
                for dirPath, dirNames, fileNames in os.walk(paths[i]):
                    dirPath = dirPath.replace('\\', '/')
                    if path[i] != path[i - 1]:
                        self.imglst.append('0')
                        self.files.append('0')
                    for f in fileNames:
                        string = str(os.path.join(dirPath, f)).replace('\\', '/')
                        self.imglst.append(string)
                        self.files.append(f)

            self.NegPath = './samples/FluA/0'

        elif disease == 'Flu B':
            path = os.listdir('./samples/FluB')
            path = list(map(int, path))
            path.sort()
            for i in range(len(path)):
                paths.append('./samples/FluB' + '/' + str(path[i]))
            for i in range(len(paths)):
                for dirPath, dirNames, fileNames in os.walk(paths[i]):
                    dirPath = dirPath.replace('\\', '/')
                    if path[i] != path[i - 1]:
                        self.imglst.append('0')
                        self.files.append('0')
                    for f in fileNames:
                        string = str(os.path.join(dirPath, f)).replace('\\', '/')
                        self.imglst.append(string)
                        self.files.append(f)
            self.NegPath = './samples/FluB/0'

        elif disease == 'Myco':
            path = os.listdir('./samples/Myco')
            path = list(map(int, path))
            path.sort()
            for i in range(len(path)):
                paths.append('./samples/Myco' + '/' + str(path[i]))
            for i in range(len(paths)):
                for dirPath, dirNames, fileNames in os.walk(paths[i]):
                    dirPath = dirPath.replace('\\', '/')
                    if path[i] != path[i - 1]:
                        self.imglst.append('0')
                        self.files.append('0')
                    for f in fileNames:
                        string = str(os.path.join(dirPath, f)).replace('\\', '/')
                        self.imglst.append(string)
                        self.files.append(f)
            self.NegPath = './samples/Myco/0'

        elif disease == 'RSV':
            path = os.listdir('./samples/RSV-hMPV')
            path = list(map(int, path))
            path.sort()
            for i in range(len(path)):
                paths.append('./samples/RSV-hMPV' + '/' + str(path[i]))
            for i in range(len(paths)):
                for dirPath, dirNames, fileNames in os.walk(paths[i]):
                    dirPath = dirPath.replace('\\', '/')
                    if path[i] != path[i - 1]:
                        self.imglst.append('0')
                        self.files.append('0')
                    for f in fileNames:
                        string = str(os.path.join(dirPath, f)).replace('\\', '/')
                        self.imglst.append(string)
                        self.files.append(f)
            self.NegPath = './samples/RSV-hMPV/0'

        elif disease == 'hMPV':
            path = os.listdir('./samples/RSV-hMPV')
            path = list(map(int, path))
            path.sort()
            for i in range(len(path)):
                paths.append('./samples/RSV-hMPV' + '/' + str(path[i]))
            for i in range(len(paths)):
                for dirPath, dirNames, fileNames in os.walk(paths[i]):
                    dirPath = dirPath.replace('\\', '/')
                    if path[i] != path[i - 1]:
                        self.imglst.append('0')
                        self.files.append('0')
                    for f in fileNames:
                        string = str(os.path.join(dirPath, f)).replace('\\', '/')
                        self.imglst.append(string)
                        self.files.append(f)
            self.NegPath = './samples/RSV-hMPV/0'

        else:
            path = os.listdir('./samples/StrepA')
            path = list(map(int, path))
            path.sort()
            for i in range(len(path)):
                paths.append('./samples/StrepA' + '/' + str(path[i]))
            for i in range(len(paths)):
                for dirPath, dirNames, fileNames in os.walk(paths[i]):
                    dirPath = dirPath.replace('\\', '/')
                    if path[i] != path[i - 1]:
                        self.imglst.append('0')
                        self.files.append('0')
                    for f in fileNames:
                        string = str(os.path.join(dirPath, f)).replace('\\', '/')
                        self.imglst.append(string)
                        self.files.append(f)
            self.NegPath = './samples/StrepA/0'

        selfimglst = []
        selffiles = []
        for i in range(len(self.imglst)):
            if self.imglst[i]!=self.imglst[i-1]:
                selfimglst.append(self.imglst[i])
                selffiles.append((self.files[i]))
            elif i==0 and len(self.imglst)==1:
                selfimglst.append(self.imglst[i])
                selffiles.append((self.files[i]))


        self.imglst = selfimglst
        self.files = selffiles
        print(len(self.imglst))

    def CovertResult2Txt(self, Result):
        if Result==1:
            result = 'Positive'
        else:
            result = 'Negative'

        return result

    def GetPara(self):
        self.CtrlRGB_Index = self.ChoiceForCtrlLineRGB.GetCurrentSelection()
        self.Ctrlrs = int(self.InputValueTxtCtrlLineRS.GetValue())
        self.Ctrlre = int(self.InputValueTxtCtrlLineRE.GetValue())
        self.Ctrlst = int(self.InputValueTxtCtrlLineSt.GetValue())
        self.Ctrlpn = float(self.InputValueTxtCtrlLinePN.GetValue())

        self.TestRGB_Index = self.ChoiceForTestLineRGB.GetCurrentSelection()
        self.Testrs = int(self.InputValueTxtTestLineRS.GetValue())
        self.Testre = int(self.InputValueTxtTestLineRE.GetValue())
        self.Testst = int(self.InputValueTxtTestLineSt.GetValue())
        self.Testpn = float(self.InputValueTxtTestLinePN.GetValue())

    def DistinguishProcess(self):
        self.GetPara()

        para_Ctrl = [self.CtrlRGB_Index, self.Ctrlrs, self.Ctrlre, self.Ctrlst, self.Ctrlpn]

        para_Test = [self.TestRGB_Index, self.Testrs, self.Testre, self.Testst, self.Testpn]

        line_parameters = [para_Ctrl, para_Test]

        Ctrl_line_para = [para_Ctrl, para_Ctrl]

        self.usePeakDetection = True

        #####列表矩陣###########################
        self.strFileName = []
        self.strResult = []

        self.strMaxPeak = []

        self.strMaxPeakSec1 = []
        self.strMaxPeakSec2 = []
        self.strMaxPeakSec3 = []
        self.strMaxPeakSec4 = []

        self.strLineColor = []

        rows = []
        #####列表矩陣###########################

        strError = 'Line ERROR'
        for count in range(len(self.imglst)):
            strPath = self.imglst[count]
            if self.imglst[count] == '0':
                self.strFileName.append('')
                self.strResult.append('')
                self.strMaxPeak.append('')
                self.strMaxPeakSec1.append('')
                self.strMaxPeakSec2.append('')
                self.strMaxPeakSec3.append('')
                self.strMaxPeakSec4.append('')
                self.strLineColor.append('')
            else:
                if strPath.find('bmp') > 0 or strPath.find('jpg') > 0:
                    im = cv2.imdecode(np.fromfile(strPath, dtype=np.uint8), -1)
                    im = cv2.cvtColor(im, cv2.COLOR_BGR2RGB)

                    if self.CheckBoxBlocks.GetValue() == True:
                        self.control, self.test_result1, self.test_result2, self.test_result1_pred, self.test_result2_pred = algorithm3_with_slope_4block(im, line_parameters, self.CheckBoxEnhance.GetValue(), self.CheckBoxUseWhiteBalance.GetValue(), self.CheckBoxUseFilter.GetValue(), self.usePeakDetection, False, num_positive=int(self.BlockNum.GetValue())) #Check

                        if self.control[0]==1:
                            self.MaxPeak = (self.test_result1[0][1] + self.test_result1[1][1] + self.test_result1[2][1] + self.test_result1[3][1]) / 4
                            self.MaxPeakSec1 = self.test_result1[0][1]
                            self.MaxPeakSec2 = self.test_result1[1][1]
                            self.MaxPeakSec3 = self.test_result1[2][1]
                            self.MaxPeakSec4 = self.test_result1[3][1]
                        else:
                            self.MaxPeak = self.control[1]
                            self.MaxPeakSec1 = 0
                            self.MaxPeakSec2 = 0
                            self.MaxPeakSec3 = 0
                            self.MaxPeakSec4 = 0
                    else:
                        self.control, self.test_result1, self.test_result2 = algorithm3_with_slope(im, line_parameters, self.CheckBoxEnhance.GetValue(), self.CheckBoxUseWhiteBalance.GetValue(), self.CheckBoxUseFilter.GetValue(), self.usePeakDetection, False) #Check
                        if self.control[0]==1:
                            self.MaxPeak = self.test_result1[1]
                        else:
                            self.MaxPeak = self.control[1]


                    result = self.CovertResult2Txt(self.control[0])

                    if result == 'Positive':
                        if self.CheckBoxBlocks.GetValue() == True:
                            result = self.CovertResult2Txt(self.test_result1_pred)
                        else:
                            result = self.CovertResult2Txt(self.test_result1[0])
                        if result == 'Positive':
                            if os.path.isfile(self.NegPath+'/'+self.files[count]) == True:
                                self.strLineColor.append('Negative')
                                self.strFileName.append(self.files[count])
                                self.strResult.append(result)
                                self.strMaxPeak.append(str(np.round(self.MaxPeak, decimals=3)))
                                if self.CheckBoxBlocks.GetValue() == True:
                                    self.strMaxPeakSec1.append(str(np.round(self.MaxPeakSec1, decimals=3)))
                                    self.strMaxPeakSec2.append(str(np.round(self.MaxPeakSec2, decimals=3)))
                                    self.strMaxPeakSec3.append(str(np.round(self.MaxPeakSec3, decimals=3)))
                                    self.strMaxPeakSec4.append(str(np.round(self.MaxPeakSec4, decimals=3)))
                                else:
                                    self.strMaxPeakSec1.append('')
                                    self.strMaxPeakSec2.append('')
                                    self.strMaxPeakSec3.append('')
                                    self.strMaxPeakSec4.append('')
                            else:
                                self.strLineColor.append('Positive')
                                self.strFileName.append(self.files[count])
                                self.strResult.append(result)
                                self.strMaxPeak.append(str(np.round(self.MaxPeak, decimals=3)))
                                if self.CheckBoxBlocks.GetValue() == True:
                                    self.strMaxPeakSec1.append(str(np.round(self.MaxPeakSec1, decimals=3)))
                                    self.strMaxPeakSec2.append(str(np.round(self.MaxPeakSec2, decimals=3)))
                                    self.strMaxPeakSec3.append(str(np.round(self.MaxPeakSec3, decimals=3)))
                                    self.strMaxPeakSec4.append(str(np.round(self.MaxPeakSec4, decimals=3)))
                                else:
                                    self.strMaxPeakSec1.append('')
                                    self.strMaxPeakSec2.append('')
                                    self.strMaxPeakSec3.append('')
                                    self.strMaxPeakSec4.append('')
                        if result == 'Negative':
                            if os.path.isfile(self.NegPath+'/'+self.files[count]) == True:
                                self.strLineColor.append('Positive')
                                self.strFileName.append(self.files[count])
                                self.strResult.append(result)
                                self.strMaxPeak.append(str(np.round(self.MaxPeak, decimals=3)))
                                if self.CheckBoxBlocks.GetValue() == True:
                                    self.strMaxPeakSec1.append(str(np.round(self.MaxPeakSec1, decimals=3)))
                                    self.strMaxPeakSec2.append(str(np.round(self.MaxPeakSec2, decimals=3)))
                                    self.strMaxPeakSec3.append(str(np.round(self.MaxPeakSec3, decimals=3)))
                                    self.strMaxPeakSec4.append(str(np.round(self.MaxPeakSec4, decimals=3)))
                                else:
                                    self.strMaxPeakSec1.append('')
                                    self.strMaxPeakSec2.append('')
                                    self.strMaxPeakSec3.append('')
                                    self.strMaxPeakSec4.append('')
                            else:
                                self.strLineColor.append('Negative')
                                self.strFileName.append(self.files[count])
                                self.strResult.append(result)
                                self.strMaxPeak.append(str(np.round(self.MaxPeak, decimals=3)))
                                if self.CheckBoxBlocks.GetValue() == True:
                                    self.strMaxPeakSec1.append(str(np.round(self.MaxPeakSec1, decimals=3)))
                                    self.strMaxPeakSec2.append(str(np.round(self.MaxPeakSec2, decimals=3)))
                                    self.strMaxPeakSec3.append(str(np.round(self.MaxPeakSec3, decimals=3)))
                                    self.strMaxPeakSec4.append(str(np.round(self.MaxPeakSec4, decimals=3)))
                                else:
                                    self.strMaxPeakSec1.append('')
                                    self.strMaxPeakSec2.append('')
                                    self.strMaxPeakSec3.append('')
                                    self.strMaxPeakSec4.append('')
                    else:
                        self.strLineColor.append(strError)
                        self.strFileName.append(self.files[count])
                        self.strResult.append(strError)
                        self.strMaxPeak.append(str(np.round(self.control[1], decimals=3)))
                        self.strMaxPeakSec1.append('')
                        self.strMaxPeakSec2.append('')
                        self.strMaxPeakSec3.append('')
                        self.strMaxPeakSec4.append('')


        self.InsertDataList(self.strFileName, self.strResult, self.strMaxPeak, self.strLineColor, self.strMaxPeakSec1, self.strMaxPeakSec2, self.strMaxPeakSec3, self.strMaxPeakSec4)

    def InsertDataList(self, strFileName, strResult, strMaxPeak, strLineColor, strMaxPeakSec1, strMaxPeakSec2, strMaxPeakSec3, strMaxPeakSec4):
        rows = []

        for i in range(len(strFileName)):
            rows.append(strFileName[i])
            rows.append(strResult[i])
            rows.append(strMaxPeak[i])
            rows.append(strMaxPeakSec1[i])
            rows.append(strMaxPeakSec2[i])
            rows.append(strMaxPeakSec3[i])
            rows.append(strMaxPeakSec4[i])

        rows = np.reshape(rows, (len(strFileName), 7))
        self.rows = rows

        index = 0
        for row in rows:
            self.ListCtrl.InsertItem(index, row[0])
            self.ListCtrl.SetItem(index, 1, row[1])
            self.ListCtrl.SetItem(index, 2, row[2])
            self.ListCtrl.SetItem(index, 3, row[3])
            self.ListCtrl.SetItem(index, 4, row[4])
            self.ListCtrl.SetItem(index, 5, row[5])
            self.ListCtrl.SetItem(index, 6, row[6])
            index += 1

        for i in range(len(strFileName)):
            if self.ListCtrl.GetItemText(i, col=1) == 'Positive' and self.strLineColor[i] == 'Positive':
                self.ListCtrl.SetItemBackgroundColour(i, col=wx.Colour(0, 250, 0, 100))
            elif self.ListCtrl.GetItemText(i, col=1) == 'Negative' and self.strLineColor[i] == 'Positive':
                self.ListCtrl.SetItemBackgroundColour(i, col=wx.Colour(0, 250, 0, 100))
            elif self.ListCtrl.GetItemText(i, col=1) == 'Positive' and self.strLineColor[i] == 'Negative':
                self.ListCtrl.SetItemBackgroundColour(i, col=wx.Colour(255, 0, 0, 100))
            elif self.ListCtrl.GetItemText(i, col=1) == 'Negative' and self.strLineColor[i] == 'Negative':
                self.ListCtrl.SetItemBackgroundColour(i, col=wx.Colour(255, 0, 0, 100))
            elif self.ListCtrl.GetItemText(i, col=1) == 'Line ERROR' and self.strLineColor[i] == 'Line ERROR':
                self.ListCtrl.SetItemBackgroundColour(i, col=wx.Colour(250, 250, 0, 100))

        self.ListCtrl.Bind(wx.EVT_RIGHT_DOWN, self.ShowPopup)
        self.ListCtrl.Bind(wx.EVT_LIST_ITEM_SELECTED, self.TestLine)

    def Copy2TxtCtrl(self, strRows):
        strResult = ''
        for i in range(len(strRows)):
            if str(strRows[i][2]) == '0':
                strResult = strResult + str(strRows[i][0]) + '\t\t' + str(strRows[i][1]) + '\n'
            else:
                strResult = strResult + str(strRows[i][0]) + '\t\t' + str(strRows[i][1]) + '\t\t' + str(strRows[i][2]) + '\t' + str(strRows[i][3]) + '\t' + str(strRows[i][4]) + '\t' +str(strRows[i][5]) + '\t' + str(strRows[i][6])
        self.strTextCtrl.SetValue(strResult)

    def ReturnSlopeDF(self, df_array):
        pic_width_pixel = len(df_array)
        df = pd.DataFrame({'x': range(0, pic_width_pixel), 'j1': df_array})
        return df

    def SetDefaultParameters(self, event):
        if self.CheckBoxUseFilter.GetValue()==True:
            self.useFilter = True
            para=[get_line_para_map('FluA'), get_line_para_map('FluB'), get_line_para_map('Myco'), get_line_para_map('RSV-hMPV'), get_line_para_map('StrepA')]
        else:
            self.useFilter = False
            para=[get_line_para_map_no_filter('FluA'), get_line_para_map_no_filter('FluB'), get_line_para_map_no_filter('Myco'), get_line_para_map_no_filter('RSV-hMPV'), get_line_para_map_no_filter('StrepA')]
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

    def ResizeImg(self, W, H):
        if W > H:
            self.NewW = self.PhotoMaxSize
            self.NewH = self.PhotoMaxSize * H / W
        else:
            self.NewH = self.PhotoMaxSize
            self.NewW = self.PhotoMaxSize * W / H
        self.W = W
        self.H = H


    def ShowImage(self, img):

        H, W, nrgb = img.shape
        self.ResizeImg(W, H)

        img = cv2.resize(img, (int(self.NewW), int(self.NewH)))

        img_enhance = gamma_enhance(img)

        wxbmp = wx.Bitmap.FromBuffer(img.shape[1], img.shape[0], img)
        wxbmp_enhance = wx.Bitmap.FromBuffer(img_enhance.shape[1], img_enhance.shape[0], img_enhance)

        self.wxbmp = Bitmap(wxbmp, (0, 0), Position='cc')
        self.wxbmp_enhance = Bitmap(wxbmp_enhance, (0, 0), Position='cc')

        self.EnhanceImg.AddObject(self.wxbmp_enhance)
        self.OriginalImg.AddObject(self.wxbmp)
        self.EnhanceImg.Draw(Force=True)
        self.OriginalImg.Draw(Force=True)

    def FileExist(self):
        # self.ChoiceForDisease = wx.ComboBox(self.SlopeFigurePanel, value='', pos=(114, 505), choices=['Flu A', 'Flu B', 'Myco', 'RSV', 'hMPV', 'StrepA'], size=(100, 20))
        Disease = self.ChoiceForDisease.GetValue()

        if Disease == 'Flu A':
            NegPath = './samples/A/0'
        elif Disease == 'Flu B':
            NegPath = './samples/B/0'
        elif Disease == 'Myco':
            NegPath = './samples/Myco/0'
        elif Disease == 'RSV':
            NegPath = './samples/RSV-hMPV/0'
        elif Disease == 'hMPV':
            NegPath = './samples/RSV-hMPV/0'
        else:
            NegPath = './samples/StrepA/0'

        if os.path.exists(NegPath):
            #print('存在')
            if len([name for name in os.listdir(NegPath) if os.path.isfile(os.path.join(NegPath, name))]) <= 1:
                return False
                #print('無法計算')
            else:
                return True
                #print('可以計算')
        else:
            return False
            #print('不存在')


    def CtrlLine(self):
        self.OriginalImgFig.clf()
        self.EnhancedImgFig.clf()
        self.SlopeFigure = Figure()
        self.SlopeFigureChart = FigureCanvas(self.SlopeStatisticsPanel, -1, self.SlopeFigure)
        self.OriginalImg.ClearAll()
        self.EnhanceImg.ClearAll()

        self.SlectImgLst = []

        for i in range(len(self.imglst)):
            if self.imglst[i].find('.ini') < 0:
                self.SlectImgLst.append(self.imglst[i])
        print(len(self.SlectImgLst))

        #讀取圖片
        self.SelectItemPath = self.SlectImgLst[self.ListCtrl.GetFirstSelected()]
        im = cv2.imdecode(np.fromfile(self.SelectItemPath, dtype=np.uint8), -1)
        im = cv2.cvtColor(im, cv2.COLOR_BGR2RGB)
        self.img = im

        #顯示圖片在FloatCanvas
        self.ShowImage(self.img)

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
        self.TestLineMultiDFArr = gamma_enhance(self.img)
        # if self.CheckBoxEnhance.GetValue()==True:
        #     self.TestLineMultiDFArr = gamma_enhance(self.img)
        # else:
        #     self.TestLineMultiDFArr = self.img

        if self.CheckBoxEnhance.GetValue()==True and self.CheckBoxBlocks.GetValue() == False:
            self.CtrlResult, self.result1, self.result2 = algorithm3_with_slope(self.img, self.line_para, True, self.CheckBoxUseWhiteBalance.GetValue(),self.CheckBoxUseFilter.GetValue(), True, False) #Check
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
            self.CtrlResult, self.result1, self.result2, self.test_result1_pred, self.test_result2_pred = algorithm3_with_slope_4block(self.img, self.line_para, True, self.CheckBoxUseWhiteBalance.GetValue(), self.CheckBoxUseFilter.GetValue(), True, False, num_positive=int(self.BlockNum.GetValue())) #Check
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
            self.CtrlResult, self.result1, self.result2 = algorithm3_with_slope(self.img, self.line_para, False, self.CheckBoxUseWhiteBalance.GetValue(), self.CheckBoxUseFilter.GetValue(), True, False) #Check
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
            self.CtrlResult, self.result1, self.result2, self.test_result1_pred, self.test_result2_pred = algorithm3_with_slope_4block(self.img, self.line_para, False, self.CheckBoxUseWhiteBalance.GetValue(), self.CheckBoxUseFilter.GetValue(), True, False, num_positive=int(self.BlockNum.GetValue())) #Check
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
            if self.CheckBoxBlocks.GetValue()==True:
                self.TextCtrlLineResult.SetValue(CtrlString)
            else:
                self.TextCtrlLineResult_top.SetValue(CtrlString)
        else:
            CtrlString = 'Result :'+'Line ERROR'+'\n'+'Max Value :'+str(CtrlMaxValue)+'\n'+'Mini Value :'+str(CtrlMinValue)+'\n'+'MaxPeak :'+str(CtrlMaxPeak)
            if self.CheckBoxBlocks.GetValue()==True:
                self.TextCtrlLineResult.SetValue(CtrlString)
            else:
                self.TextCtrlLineResult_top.SetValue(CtrlString)
            self.ResultText.SetLabel('Result : Line ERROR')
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

                if self.FileExist() == True:
                    #self.TextTestLineResult.SetValue('')
                    self.TextTestLineResultSec1.SetValue('Result:' + self.ResultTextConvert(self.result1[0][0]) + '\n'
                                                         + 'Max Value:' + str(
                        np.around(self.result1[0][3], decimals=3)) + '\n'
                                                         + 'Min Value:' + str(
                        np.around(self.result1[0][5], decimals=3)) + '\n'
                                                         + 'Max Peak:' + str(np.around(self.result1[0][1], decimals=3)))
                    self.TextTestLineResultSec2.SetValue('Result:' + self.ResultTextConvert(self.result1[1][0]) + '\n'
                                                         + 'Max Value:' + str(
                        np.around(self.result1[1][3], decimals=3)) + '\n'
                                                         + 'Min Value:' + str(
                        np.around(self.result1[1][5], decimals=3)) + '\n'
                                                         + 'Max Peak:' + str(np.around(self.result1[1][1], decimals=3)))
                    self.TextTestLineResultSec3.SetValue('Result:' + self.ResultTextConvert(self.result1[2][0]) + '\n'
                                                         + 'Max Value:' + str(
                        np.around(self.result1[2][3], decimals=3)) + '\n'
                                                         + 'Min Value:' + str(
                        np.around(self.result1[2][5], decimals=3)) + '\n'
                                                         + 'Max Peak:' + str(np.around(self.result1[2][1], decimals=3)))
                    self.TextTestLineResultSec4.SetValue('Result:' + self.ResultTextConvert(self.result1[3][0]) + '\n'
                                                         + 'Max Value:' + str(
                        np.around(self.result1[3][3], decimals=3)) + '\n'
                                                         + 'Min Value:' + str(
                        np.around(self.result1[3][5], decimals=3)) + '\n'
                                                         + 'Max Peak:' + str(np.around(self.result1[3][1], decimals=3)))
                else:
                    #self.TextTestLineResult.SetValue('')
                    self.TextCtrlLineResult.SetValue('')
                    self.TextTestLineResultSec1.SetValue('')
                    self.TextTestLineResultSec2.SetValue('')
                    self.TextTestLineResultSec3.SetValue('')
                    self.TextTestLineResultSec4.SetValue('')


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
                self.ResultText.SetLabel('Result : '+self.FinalTestResult)
                self.SlopeStatisticsChartForCtrlLine(self.Ctrl_color, self.Ctrl_start_interval, self.Ctrl_end_interval, -20, 20)
                if self.FileExist()==True:
                    #self.TextTestLineResult.SetValue('')
                    self.TextTestLineResultSec1.SetValue('Result:'+self.ResultTextConvert(self.result1[0][0])+'\n'
                                                         +'Max Value:'+str(np.around(self.result1[0][3], decimals=3))+'\n'
                                                         +'Min Value:'+str(np.around(self.result1[0][5], decimals=3))+'\n'
                                                         +'Max Peak:'+str(np.around(self.result1[0][1], decimals=3)))
                    self.TextTestLineResultSec2.SetValue('Result:'+self.ResultTextConvert(self.result1[1][0])+'\n'
                                                         +'Max Value:'+str(np.around(self.result1[1][3], decimals=3))+'\n'
                                                         +'Min Value:'+str(np.around(self.result1[1][5], decimals=3))+'\n'
                                                         +'Max Peak:'+str(np.around(self.result1[1][1], decimals=3)))
                    self.TextTestLineResultSec3.SetValue('Result:'+self.ResultTextConvert(self.result1[2][0])+'\n'
                                                         +'Max Value:'+str(np.around(self.result1[2][3], decimals=3))+'\n'
                                                         +'Min Value:'+str(np.around(self.result1[2][5], decimals=3))+'\n'
                                                         +'Max Peak:'+str(np.around(self.result1[2][1], decimals=3)))
                    self.TextTestLineResultSec4.SetValue('Result:'+self.ResultTextConvert(self.result1[3][0])+'\n'
                                                         +'Max Value:'+str(np.around(self.result1[3][3], decimals=3))+'\n'
                                                         +'Min Value:'+str(np.around(self.result1[3][5], decimals=3))+'\n'
                                                         +'Max Peak:'+str(np.around(self.result1[3][1], decimals=3)))
                else:
                    #self.TextTestLineResult.SetValue('')
                    self.TextCtrlLineResult.SetValue('')
                    self.TextTestLineResultSec1.SetValue('')
                    self.TextTestLineResultSec2.SetValue('')
                    self.TextTestLineResultSec3.SetValue('')
                    self.TextTestLineResultSec4.SetValue('')

            else:
                self.SlopeStatisticsChartForCtrlLine(self.Ctrl_color, self.Ctrl_start_interval, self.Ctrl_end_interval, -20, 20)
                self.SlopeStatisticsChartForTestLine(self.Test_color, self.Test_start_interval, self.Test_end_interval, -20, 20)
                TestString = 'Result :' + self.FinalTestResult + '\n'+'Max Value :' + str(np.round(self.result1[3], decimals=3)) + '\n' + 'Mini Value :' + str(np.round(self.result1[5], decimals=3)) + '\n' + 'MaxPeak :' + str(np.round(self.result1[1], decimals=3))
                self.ResultText.SetLabel('Result : ' + self.FinalTestResult)
                self.TextTestLineResult_top.SetValue(TestString)
                self.PlotCtrlLineBoundary()
                self.PlotTestLineBoundary()
                # self.TextTestLineResultSec1.SetValue('')
                # self.TextTestLineResultSec2.SetValue('')
                # self.TextTestLineResultSec3.SetValue('')
                # self.TextTestLineResultSec4.SetValue('')
        else:
            #print(np.mean(self.TestDFArr))
            self.PlotCtrlLineBoundary()
            #self.PlotTestLineBoundary()
            self.SlopeStatisticsChartForCtrlLine(self.Ctrl_color, self.Ctrl_start_interval, self.Ctrl_end_interval, -20,20)
            self.SlopeStatisticsChartForTestLine(self.Test_color, self.Ctrl_start_interval, self.Ctrl_end_interval, -20, 20)
            #self.TextTestLineResult.SetValue('')
            self.TextTestLineResultSec1.SetValue('')
            self.TextTestLineResultSec2.SetValue('')
            self.TextTestLineResultSec3.SetValue('')
            self.TextTestLineResultSec4.SetValue('')

    def TestLineNoEvent(self):
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
                if self.FileExist()==True:
                    #self.TextTestLineResult.SetValue('')
                    self.TextTestLineResultSec1.SetValue('Result:'+self.ResultTextConvert(self.result1[0][0])+'\n'
                                                         +'Max Value:'+str(np.around(self.result1[0][3], decimals=3))+'\n'
                                                         +'Min Value:'+str(np.around(self.result1[0][5], decimals=3))+'\n'
                                                         +'Max Peak:'+str(np.around(self.result1[0][1], decimals=3)))
                    self.TextTestLineResultSec2.SetValue('Result:'+self.ResultTextConvert(self.result1[1][0])+'\n'
                                                         +'Max Value:'+str(np.around(self.result1[1][3], decimals=3))+'\n'
                                                         +'Min Value:'+str(np.around(self.result1[1][5], decimals=3))+'\n'
                                                         +'Max Peak:'+str(np.around(self.result1[1][1], decimals=3)))
                    self.TextTestLineResultSec3.SetValue('Result:'+self.ResultTextConvert(self.result1[2][0])+'\n'
                                                         +'Max Value:'+str(np.around(self.result1[2][3], decimals=3))+'\n'
                                                         +'Min Value:'+str(np.around(self.result1[2][5], decimals=3))+'\n'
                                                         +'Max Peak:'+str(np.around(self.result1[2][1], decimals=3)))
                    self.TextTestLineResultSec4.SetValue('Result:'+self.ResultTextConvert(self.result1[3][0])+'\n'
                                                         +'Max Value:'+str(np.around(self.result1[3][3], decimals=3))+'\n'
                                                         +'Min Value:'+str(np.around(self.result1[3][5], decimals=3))+'\n'
                                                         +'Max Peak:'+str(np.around(self.result1[3][1], decimals=3)))
                else:
                    #self.TextTestLineResult.SetValue('')
                    self.TextCtrlLineResult.SetValue('')
                    self.TextTestLineResultSec1.SetValue('')
                    self.TextTestLineResultSec2.SetValue('')
                    self.TextTestLineResultSec3.SetValue('')
                    self.TextTestLineResultSec4.SetValue('')

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
                self.ResultText.SetLabel('Result : '+self.FinalTestResult)
                self.SlopeStatisticsChartForCtrlLine(self.Ctrl_color, self.Ctrl_start_interval, self.Ctrl_end_interval, -20, 20)
                if self.FileExist()==True:
                    #self.TextTestLineResult.SetValue('')
                    self.TextTestLineResultSec1.SetValue('Result:'+self.ResultTextConvert(self.result1[0][0])+'\n'
                                                         +'Max Value:'+str(np.around(self.result1[0][3], decimals=3))+'\n'
                                                         +'Min Value:'+str(np.around(self.result1[0][5], decimals=3))+'\n'
                                                         +'Max Peak:'+str(np.around(self.result1[0][1], decimals=3)))
                    self.TextTestLineResultSec2.SetValue('Result:'+self.ResultTextConvert(self.result1[1][0])+'\n'
                                                         +'Max Value:'+str(np.around(self.result1[1][3], decimals=3))+'\n'
                                                         +'Min Value:'+str(np.around(self.result1[1][5], decimals=3))+'\n'
                                                         +'Max Peak:'+str(np.around(self.result1[1][1], decimals=3)))
                    self.TextTestLineResultSec3.SetValue('Result:'+self.ResultTextConvert(self.result1[2][0])+'\n'
                                                         +'Max Value:'+str(np.around(self.result1[2][3], decimals=3))+'\n'
                                                         +'Min Value:'+str(np.around(self.result1[2][5], decimals=3))+'\n'
                                                         +'Max Peak:'+str(np.around(self.result1[2][1], decimals=3)))
                    self.TextTestLineResultSec4.SetValue('Result:'+self.ResultTextConvert(self.result1[3][0])+'\n'
                                                         +'Max Value:'+str(np.around(self.result1[3][3], decimals=3))+'\n'
                                                         +'Min Value:'+str(np.around(self.result1[3][5], decimals=3))+'\n'
                                                         +'Max Peak:'+str(np.around(self.result1[3][1], decimals=3)))
                else:
                    #self.TextTestLineResult.SetValue('')
                    self.TextCtrlLineResult.SetValue('')
                    self.TextTestLineResultSec1.SetValue('')
                    self.TextTestLineResultSec2.SetValue('')
                    self.TextTestLineResultSec3.SetValue('')
                    self.TextTestLineResultSec4.SetValue('')

            else:
                self.SlopeStatisticsChartForCtrlLine(self.Ctrl_color, self.Ctrl_start_interval, self.Ctrl_end_interval, -20, 20)
                self.SlopeStatisticsChartForTestLine(self.Test_color, self.Test_start_interval, self.Test_end_interval, -20, 20)
                TestString = 'Result :' + self.FinalTestResult + '\n'+'Max Value :' + str(np.round(self.result1[3], decimals=3)) + '\n' + 'Mini Value :' + str(np.round(self.result1[5], decimals=3)) + '\n' + 'MaxPeak :' + str(np.round(self.result1[1], decimals=3))
                self.ResultText.SetLabel('Result : ' + self.FinalTestResult)
                self.TextTestLineResult_top.SetValue(TestString)
                self.PlotCtrlLineBoundary()
                self.PlotTestLineBoundary()
                # self.TextTestLineResultSec1.SetValue('')
                # self.TextTestLineResultSec2.SetValue('')
                # self.TextTestLineResultSec3.SetValue('')
                # self.TextTestLineResultSec4.SetValue('')
        else:
            #print(np.mean(self.TestDFArr))
            self.PlotCtrlLineBoundary()
            #self.PlotTestLineBoundary()
            self.SlopeStatisticsChartForCtrlLine(self.Ctrl_color, self.Ctrl_start_interval, self.Ctrl_end_interval, -20,20)
            self.SlopeStatisticsChartForTestLine(self.Test_color, self.Ctrl_start_interval, self.Ctrl_end_interval, -20, 20)
            #self.TextTestLineResult.SetValue('')
            self.TextTestLineResultSec1.SetValue('')
            self.TextTestLineResultSec2.SetValue('')
            self.TextTestLineResultSec3.SetValue('')
            self.TextTestLineResultSec4.SetValue('')


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
        #########################################################################
        points_start = [(start_interval, y_start), (start_interval, y_end)]
        (xpoint_start, ypoint_start) = zip(*points_start)
        points_end = [(end_interval, y_start), (end_interval, y_end)]
        (xpoint_end, ypoint_end) = zip(*points_end)
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

    def ShowPopup(self, event):
        menu = wx.Menu()
        menu.Append(1, "Copy selected items")
        menu.Bind(wx.EVT_MENU, self.CopyItems, id=1)
        self.PopupMenu(menu)


    def CopyItems(self, event):
        selectedItems = []
        for i in range(self.ListCtrl.GetItemCount()):
            if self.ListCtrl.IsSelected(i):
                selectedItems.append(self.ListCtrl.GetItemText(i,0)+'\t'+self.ListCtrl.GetItemText(i,1)+'\t'+self.ListCtrl.GetItemText(i,2))

        clipdata = wx.TextDataObject()
        clipdata.SetText("\n".join(selectedItems))
        wx.TheClipboard.Open()
        wx.TheClipboard.SetData(clipdata)
        wx.TheClipboard.Close()

#############Show Image############################################################################
    def ShowOriginalImgChartForCtrlLine(self, start_interval, end_interval, y_start, y_end):
        df = self.ShowPlot(self.img)
        self.OriginalImgFig.set_figheight(2)
        self.OriginalImgFig.set_figwidth(4.5)
        self.axes_OriginalImg = self.OriginalImgFig.add_subplot(1, 1, 1)
        self.axes_OriginalImg.set_ylim(0, 250)
        self.axes_OriginalImg.plot('x', 'j1', data=df, color='red', linewidth=1, label='r')
        self.axes_OriginalImg.plot('x', 'j2', data=df, color='green', linewidth=1, label='g')
        self.axes_OriginalImg.plot('x', 'j3', data=df, color='blue', linewidth=1, label='b')
        self.axes_OriginalImg.plot('x', 'j4', data=df, color='gray', linewidth=1, label='gray')
        points_start = [(start_interval, y_start), (start_interval, y_end)]
        (xpoint_start, ypoint_start) = zip(*points_start)
        points_end = [(end_interval, y_start), (end_interval, y_end)]
        (xpoint_end, ypoint_end) = zip(*points_end)
        self.axes_OriginalImg.plot(xpoint_start, ypoint_start, 'g', linewidth=1)
        self.axes_OriginalImg.plot(xpoint_end, ypoint_end, 'g', linewidth=1)
        self.axes_OriginalImg.grid(True)
        self.OriginalImgChart.draw()

    def ShowOriginalImgChartForTestLine(self, start_interval, end_interval, y_start, y_end):
        points_start = [(start_interval, y_start), (start_interval, y_end)]
        (xpoint_start, ypoint_start) = zip(*points_start)
        points_end = [(end_interval, y_start), (end_interval, y_end)]
        (xpoint_end, ypoint_end) = zip(*points_end)
        if self.ctrl_result == 'Positive':
            self.axes_OriginalImg.plot(xpoint_start, ypoint_start, 'r', linewidth=1)
            self.axes_OriginalImg.plot(xpoint_end, ypoint_end, 'r', linewidth=1)
        self.OriginalImgChart.draw()

    def ShowEnhancedImgChartForCtrlLine(self, start_interval, end_interval, y_start, y_end):
        df = self.ShowPlot(self.TestLineMultiDFArr)
        self.EnhancedImgFig.set_figheight(2)
        self.EnhancedImgFig.set_figwidth(4.5)
        self.axes_EnhancedImg = self.EnhancedImgFig.add_subplot(1, 1, 1)
        self.axes_EnhancedImg.set_ylim(0, 250)
        self.axes_EnhancedImg.plot('x', 'j1', data=df, color='red', linewidth=1, label='r')
        self.axes_EnhancedImg.plot('x', 'j2', data=df, color='green', linewidth=1, label='g')
        self.axes_EnhancedImg.plot('x', 'j3', data=df, color='blue', linewidth=1, label='b')
        self.axes_EnhancedImg.plot('x', 'j4', data=df, color='gray', linewidth=1, label='gray')
        points_start = [(start_interval, y_start), (start_interval, y_end)]
        (xpoint_start, ypoint_start) = zip(*points_start)
        points_end = [(end_interval, y_start), (end_interval, y_end)]
        (xpoint_end, ypoint_end) = zip(*points_end)
        self.axes_EnhancedImg.plot(xpoint_start, ypoint_start, 'g', linewidth=1)
        self.axes_EnhancedImg.plot(xpoint_end, ypoint_end, 'g', linewidth=1)
        self.axes_EnhancedImg.grid(True)

    def ShowEnhancedImgChartForTestLine(self, start_interval, end_interval, y_start, y_end):
        points_start = [(start_interval, y_start), (start_interval, y_end)]
        (xpoint_start, ypoint_start) = zip(*points_start)
        points_end = [(end_interval, y_start), (end_interval, y_end)]
        (xpoint_end, ypoint_end) = zip(*points_end)
        if self.ctrl_result == 'Positive':
            self.axes_EnhancedImg.plot(xpoint_start, ypoint_start, 'r', linewidth=1)
            self.axes_EnhancedImg.plot(xpoint_end, ypoint_end, 'r', linewidth=1)
        self.EnhancedImgChart.draw()

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

    #if self.CheckBoxEnhance.GetValue() == True:
        self.EnhanceImg.AddObject(self.boundary_enhanced_rect)
        self.OriginalImg.AddObject(self.boundary_enhanced_rect)
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
        self.EnhanceImg.AddObject(self.boundary_enhanced_ctrl_rect)
        self.OriginalImg.AddObject(self.boundary_enhanced_ctrl_rect)
        self.SetBoundaryLineForCtrlLine(self.EnhanceImg, int(self.InputValueTxtCtrlLineRS.GetValue()), int(self.InputValueTxtCtrlLineRE.GetValue()))
        self.SetBoundaryLineForCtrlLine(self.OriginalImg, int(self.InputValueTxtCtrlLineRS.GetValue()), int(self.InputValueTxtCtrlLineRE.GetValue()))
        self.boundary_original_ctrl_rect.SetColor('green')
        self.boundary_enhanced_ctrl_rect.SetColor('green')
        self.OriginalImg.Draw(Force=True)

    def OriginalImgBoundaryLine(self, panel, start_interval, end_interval):
        scale = self.PhotoMaxSize / self.W
        X = start_interval * scale - self.NewW / 2
        Y = -self.NewH / 2
        XY = np.array([X, Y])
        WH = ((end_interval - start_interval) * scale, self.NewH)
        self.boundary_original_rect = Rectangle(XY, WH, LineColor='Red')
        panel.AddObject(self.boundary_original_rect)
        panel.Draw(True)

    def OriginalImgBoundaryLineForCtrlLine(self, panel, start_interval, end_interval):
        scale = self.PhotoMaxSize / self.W
        X = start_interval * scale - self.NewW / 2
        Y = -self.NewH / 2
        XY = np.array([X, Y])
        WH = ((end_interval - start_interval) * scale, self.NewH)
        self.boundary_original_ctrl_rect = Rectangle(XY, WH, LineColor='Red')
        panel.AddObject(self.boundary_original_ctrl_rect)
        panel.Draw(True)

    def EnhancedImgBoundaryLine(self, panel, start_interval, end_interval):
        scale = self.PhotoMaxSize / self.W
        X = start_interval * scale - self.NewW / 2
        Y = -self.NewH / 2
        XY = np.array([X, Y])
        WH = ((end_interval - start_interval) * scale, self.NewH)
        self.boundary_enhanced_rect = Rectangle(XY, WH, LineColor='Red')
        panel.AddObject(self.boundary_enhanced_rect)
        panel.Draw(True)

    def EnhancedImgBoundaryLineForCtrlLine(self, panel, start_interval, end_interval):
        scale = self.PhotoMaxSize / self.W
        X = start_interval * scale - self.NewW / 2
        Y = -self.NewH / 2
        XY = np.array([X, Y])
        WH = ((end_interval - start_interval) * scale, self.NewH)
        self.boundary_enhanced_ctrl_rect = Rectangle(XY, WH, LineColor='Red')
        panel.AddObject(self.boundary_enhanced_ctrl_rect)
        panel.Draw(True)

    def SetBoundaryLine(self, panel, start_interval, end_interval):
        scale = self.PhotoMaxSize / self.W
        X = start_interval * scale - self.NewW / 2
        Y = -self.NewH / 2
        XY = np.array([X, Y])
        WH = ((end_interval - start_interval) * scale, self.NewH)
        self.boundary_enhanced_rect.SetShape(XY, WH)
        self.boundary_original_rect.SetShape(XY, WH)
        panel.Draw(True)

    def SetBoundaryLineForCtrlLine(self, panel, start_interval, end_interval):
        scale = self.PhotoMaxSize / self.W
        X = start_interval * scale - self.NewW / 2
        Y = -self.NewH / 2
        XY = np.array([X, Y])
        WH = ((end_interval - start_interval) * scale, self.NewH)
        self.boundary_enhanced_ctrl_rect.SetShape(XY, WH)
        self.boundary_original_ctrl_rect.SetShape(XY, WH)
        panel.Draw(True)

    def SetBoundaryLineForBlocks(self, OriginalPanel, EnhancedPanel, start_interval, end_interval):
        scale = self.PhotoMaxSize / self.W  # 縮放比例

        X = start_interval * scale - self.NewW / 2
        Y1 = -self.NewH / 2
        Y2 = -self.NewH / 2 + int(self.NewH / 4)
        Y3 = -self.NewH / 2 + int(self.NewH / 2)
        Y4 = -self.NewH / 2 + int(3 * self.NewH / 4)

        XY1 = np.array([X, Y1])
        XY2 = np.array([X, Y2])
        XY3 = np.array([X, Y3])
        XY4 = np.array([X, Y4])

        WH = ((end_interval - start_interval) * scale, self.NewH / 4)

        self.Rect1 = Rectangle(XY1, WH, LineColor="Red", LineStyle="Solid", LineWidth=1, FillColor='White', FillStyle="Transparent")
        self.Rect2 = Rectangle(XY2, WH, LineColor="Red", LineStyle="Solid", LineWidth=1, FillColor='White', FillStyle="Transparent")
        self.Rect3 = Rectangle(XY3, WH, LineColor="Red", LineStyle="Solid", LineWidth=1, FillColor='White', FillStyle="Transparent")
        self.Rect4 = Rectangle(XY4, WH, LineColor="Red", LineStyle="Solid", LineWidth=1, FillColor='White', FillStyle="Transparent")
        self.Rect5 = Rectangle(XY1, WH, LineColor="Red", LineStyle="Solid", LineWidth=1, FillColor='White', FillStyle="Transparent")
        self.Rect6 = Rectangle(XY2, WH, LineColor="Red", LineStyle="Solid", LineWidth=1, FillColor='White', FillStyle="Transparent")
        self.Rect7 = Rectangle(XY3, WH, LineColor="Red", LineStyle="Solid", LineWidth=1, FillColor='White', FillStyle="Transparent")
        self.Rect8 = Rectangle(XY4, WH, LineColor="Red", LineStyle="Solid", LineWidth=1, FillColor='White', FillStyle="Transparent")

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
        TestMaxValue = str(np.around(self.result1[3][3], decimals=3))
        TestMinValue = str(np.around(self.result1[3][5], decimals=3))
        TestMaxDiff = str(np.around(self.result1[3][1], decimals=3))
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
            #self.TextTestLineResult.SetValue(TestString)
        else:
            pass

    def Block2Event(self, event):
        Result = self.ResultTextConvert(self.result1[2][0])
        TestMaxValue = str(np.around(self.result1[2][3], decimals=3))
        TestMinValue = str(np.around(self.result1[2][5], decimals=3))
        TestMaxDiff = str(np.around(self.result1[2][1], decimals=3))

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
            #self.TextTestLineResult.SetValue(TestString)
        else:
            pass

    def Block3Event(self, event):
        Result = self.ResultTextConvert(self.result1[1][0])
        TestMaxValue = str(np.around(self.result1[1][3], decimals=3))
        TestMinValue = str(np.around(self.result1[1][5], decimals=3))
        TestMaxDiff = str(np.around(self.result1[1][1], decimals=3))
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
            #self.TextTestLineResult.SetValue(TestString)
        else:
            pass

    def Block4Event(self, event):
        Result = self.ResultTextConvert(self.result1[0][0])
        TestMaxValue = str(np.around(self.result1[0][3], decimals=3))
        TestMinValue = str(np.around(self.result1[0][5], decimals=3))
        TestMaxDiff = str(np.around(self.result1[0][1], decimals=3))
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

            self.SlopeStatisticsChartForTestLine(self.Test_color, self.Test_start_interval, self.Test_end_interval,
                                                 y_start=-20, y_end=20)
            #self.TextTestLineResult.SetValue(TestString)
        else:
            pass

    def Block5Event(self, event):
        Result = self.ResultTextConvert(self.result1[3][0])
        TestMaxValue = str(np.around(self.result1[3][3], decimals=3))
        TestMinValue = str(np.around(self.result1[3][5], decimals=3))
        TestMaxDiff = str(np.around(self.result1[3][1], decimals=3))
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

            self.SlopeStatisticsChartForTestLine(self.Test_color, self.Test_start_interval, self.Test_end_interval,
                                                 y_start=-20, y_end=20)
            #self.TextTestLineResult.SetValue(TestString)
        else:
            pass

    def Block6Event(self, event):
        Result = self.ResultTextConvert(self.result1[2][0])
        TestMaxValue = str(np.around(self.result1[2][3], decimals=3))
        TestMinValue = str(np.around(self.result1[2][5], decimals=3))
        TestMaxDiff = str(np.around(self.result1[2][1], decimals=3))
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

            self.SlopeStatisticsChartForTestLine(self.Test_color, self.Test_start_interval, self.Test_end_interval,
                                                 y_start=-20, y_end=20)
            #self.TextTestLineResult.SetValue(TestString)
        else:
            pass

    def Block7Event(self, event):
        Result = self.ResultTextConvert(self.result1[1][0])
        TestMaxValue = str(np.around(self.result1[1][3], decimals=3))
        TestMinValue = str(np.around(self.result1[1][5], decimals=3))
        TestMaxDiff = str(np.around(self.result1[1][1], decimals=3))
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

            self.SlopeStatisticsChartForTestLine(self.Test_color, self.Test_start_interval, self.Test_end_interval,
                                                 y_start=-20, y_end=20)
            #self.TextTestLineResult.SetValue(TestString)
        else:
            pass

    def Block8Event(self, event):
        Result = self.ResultTextConvert(self.result1[0][0])
        TestMaxValue = str(np.around(self.result1[0][3], decimals=3))
        TestMinValue = str(np.around(self.result1[0][5], decimals=3))
        TestMaxDiff = str(np.around(self.result1[0][1], decimals=3))
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
            #self.TextTestLineResult.SetValue(TestString)
        else:
            pass