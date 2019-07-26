import wx
import os
import numpy as np
from .base import BasePanel
from PIL import Image
from decimal import *
from .VirusDetectAlgo import *
class MultiResultPanel(BasePanel):

    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)
        ##########Set the scroll panel######################
        self.panel = wx.ScrolledWindow(parent=self)        #
        self.panel.SetScrollbars(1, 1, 1, 1200)            #
        self.panel.SetScrollRate(0, 10)                    #
        boxSizer = wx.BoxSizer(wx.VERTICAL)                #
        boxSizer.Add(self.panel)                           #
        self.SetSizer(boxSizer)                            #
        ####################################################

        ###############Set Panel############################
        self.ScrollPanel = wx.Panel(parent=self.panel, id=wx.ID_ANY, size=(2000, 1000), pos=(0, 0), style=0)

        ###############Set Button###########################
        StartBut = wx.Button(self.ScrollPanel, label='Start', pos=(50, 50))
        StartBut.Bind(wx.EVT_BUTTON, self.ClickBtn_Start)
        CopyBut = wx.Button(self.ScrollPanel, label='Copy to Clipboard', pos=(146, 50))
        CopyBut.Bind(wx.EVT_BUTTON, self.ClickBtn_Copy)

        ###############Set TextCtrl Font#####################
        self.textCtrlFont = wx.Font(12, wx.FONTFAMILY_ROMAN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)

        ###############Set ListCtrl##########################
        self.ListCtrl = wx.ListCtrl(self.ScrollPanel, size=(484,750), pos=(50, 80),
                                    style=wx.LC_REPORT|wx.BORDER_SUNKEN)
        self.ListCtrl.InsertColumn(0, 'File Name', width=257)
        self.ListCtrl.InsertColumn(1, 'Result', width=136)
        self.ListCtrl.InsertColumn(2, 'Max Peak', width=91)

        ###############Set TextCtrl##########################
        self.strTextCtrl = wx.TextCtrl(self.ScrollPanel, style=wx.TE_MULTILINE|wx.TE_READONLY|wx.NO_BORDER,
                                        value='',id=wx.ID_ANY,
                                        pos=(545, 80), size=(1000, 750))

    def GetTabImgRes(self):
        pass

    def SetTabImgRes(self, img):
        pass

    def GetDiseaseParams(self):
        pass

    def SetDiseaseParams(self, params):
        #Set the global parameters
        self.disease = params.disease

        #Ctrl Para
        self.Ctrlst = int(params.Ctrlst)
        self.Ctrlpn = float(params.Ctrlpn)
        self.Ctrlrs = int(params.CtrlRS)
        self.Ctrlre = int(params.CtrlRE)
        self.CtrlRGB_Index = int(params.CtrlRGB_Index)
        #Test Para
        self.disease = params.disease
        self.Testst = int(params.Testst)
        self.Testpn = float(params.Testpn)
        self.Testrs = int(params.TestRS)
        self.Testre = int(params.TestRE)
        self.TestRGB_Index = int(params.TestRGB_Index)

        self.LoadImage(self.disease)
        self.useFilter = params.useFilter
        self.usePeakDetection = params.usePeakDetection
        self.useEnhance = params.useEnhance
        # self.ArrangImgLst()
        print(self.Testpn)

    def ClickBtn_Start(self, event):
        if self.ListCtrl.GetItemCount() > 0:
            self.ListCtrl.DeleteAllItems()
        self.DistinguishProcess()

    def ClickBtn_Copy(self, event):
        self.Copy2TxtCtrl(self.rows)


    def LoadImage(self, disease):

        self.imglst = []
        self.files = []
        paths=[]

        if disease == 'Flu A':
            path = os.listdir('./samples/A')
            path = list(map(int, path))
            path.sort()
            for i in range(len(path)):
                paths.append('./samples/A' + '/' + str(path[i]))
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
            self.NegPath = './samples/A/0'

        elif disease == 'Flu B':
            path = os.listdir('./samples/B')
            path = list(map(int, path))
            path.sort()
            for i in range(len(path)):
                paths.append('./samples/B' + '/' + str(path[i]))
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
            self.NegPath = './samples/B/0'

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
            path = os.listdir('./samples/RSV')
            path = list(map(int, path))
            path.sort()
            for i in range(len(path)):
                paths.append('./samples/RSV' + '/' + str(path[i]))
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
            self.NegPath = './samples/RSV/0'

        elif disease == 'hMPV':
            path = os.listdir('./samples/hMPV')
            path = list(map(int, path))
            path.sort()
            for i in range(len(path)):
                paths.append('./samples/hMPV' + '/' + str(path[i]))
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
            self.NegPath = './samples/hMPV/0'

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
            if self.imglst[i]==self.imglst[i-1]:
                pass
            elif i==0:
                pass
            else:
                selfimglst.append(self.imglst[i])
                selffiles.append((self.files[i]))

        self.imglst = selfimglst
        self.files = selffiles
        print(self.imglst)

    def CovertResult2Txt(self, Result):
        if Result==1:
            result = 'Positive'
        else:
            result = 'Negative'

        return result

    def DistinguishProcess(self):

        para_Ctrl = [self.CtrlRGB_Index, self.Ctrlrs, self.Ctrlre, self.Ctrlst, self.Ctrlpn]

        para_Test = [self.TestRGB_Index, self.Testrs, self.Testre, self.Testst, self.Testpn]

        line_parameters = [para_Ctrl, para_Test]

        useFilter = self.useFilter

        usePeakDetection = self.usePeakDetection

        self.strFileName = []
        self.strResult = []
        self.strMaxPeak = []
        self.strLineColor = []
        rows = []
        strError = 'Control Line ERROR'
        for count in range(len(self.imglst)):
            strPath = self.imglst[count]
            if self.imglst[count] == '0':
                self.strFileName.append('')
                self.strResult.append('')
                self.strMaxPeak.append('')
                self.strLineColor.append('')
            else:
                im = Image.open(strPath)
                im = np.array(im)

                Result, self.TestResult, TestResult = algorithm3_with_slope(im, line_parameters, self.useEnhance, self.useFilter, self.usePeakDetection, False)
                result = self.CovertResult2Txt(Result[0])
                if result == 'Positive':
                    Result, self.TestResult, TestResult = algorithm3_with_slope(im, line_parameters, self.useEnhance, self.useFilter, self.usePeakDetection, False)
                    result = self.CovertResult2Txt(self.TestResult[0])
                    if result == 'Positive':
                        if os.path.isfile(self.NegPath+'/'+self.files[count]) == True:
                            self.strLineColor.append('Negative')
                            self.strFileName.append(self.files[count])
                            self.strResult.append(result)
                            self.strMaxPeak.append(str(np.round(self.TestResult[2], decimals=3)))
                        else:
                            self.strLineColor.append('Positive')
                            self.strFileName.append(self.files[count])
                            self.strResult.append(result)
                            self.strMaxPeak.append(str(np.round(self.TestResult[2], decimals=3)))
                    if result == 'Negative':
                        if os.path.isfile(self.NegPath+'/'+self.files[count]) == True:
                            self.strLineColor.append('Positive')
                            self.strFileName.append(self.files[count])
                            self.strResult.append(result)
                            self.strMaxPeak.append(str(np.round(self.TestResult[2], decimals=3)))
                        else:
                            self.strLineColor.append('Negative')
                            self.strFileName.append(self.files[count])
                            self.strResult.append(result)
                            self.strMaxPeak.append(str(np.round(self.TestResult[2], decimals=3)))
                else:
                    self.strLineColor.append(strError)
                    self.strFileName.append(self.files[count])
                    self.strResult.append(strError)
                    self.strMaxPeak.append(str(np.round(Result[2], decimals=3)))

        self.InsertDataList(self.strFileName, self.strResult, self.strMaxPeak, self.strLineColor)
        self.ListCtrl.Bind(wx.EVT_LIST_ITEM_SELECTED, self.SelectItem)

    def InsertDataList(self, strFileName, strResult, strMaxPeak, strLineColor):
        rows = []

        for i in range(len(strFileName)):
            rows.append(strFileName[i])
            rows.append(strResult[i])
            rows.append(strMaxPeak[i])

        rows = np.reshape(rows, (len(strFileName), 3))
        self.rows = rows

        index = 0
        for row in rows:
            self.ListCtrl.InsertItem(index, row[0])
            self.ListCtrl.SetItem(index, 1, row[1])
            self.ListCtrl.SetItem(index, 2, row[2])
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
            elif self.ListCtrl.GetItemText(i, col=1) == 'Control Line ERROR' and self.strLineColor[i] == 'Control Line ERROR':
                self.ListCtrl.SetItemBackgroundColour(i, col=wx.Colour(250, 250, 0, 100))

    def SelectItem(self, event):
        self.ListCtrl.GetFirstSelected()

    def Copy2TxtCtrl(self, strRows):
        strResult = ''
        for i in range(len(strRows)):
            if str(strRows[i][2]) == '0':
                strResult = strResult + str(strRows[i][0]) + '\t\t' + str(strRows[i][1]) + '\n'
            else:
                strResult = strResult + str(strRows[i][0]) + '\t\t' + str(strRows[i][1]) + '\t\t' + str(strRows[i][2]) + '\n'
        self.strTextCtrl.SetValue(strResult)