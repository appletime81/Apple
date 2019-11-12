import xlrd
import xlwt
import copy
import os
import openpyxl

# 宣告
Myco_arr = [] ; Myco_time_arr = [] ; Myco_new_name = []
hMPV_arr = [] ; hMPV_time_arr = [] ; hMPV_new_name = []
StrepA_arr = [] ; StrepA_time_arr =[] ; StrepA_new_name = []
string = []
img_path_lst = []
files = []
paths = []
sheet_arr = []

filename = '../ExcelFiles/Correspondence table.xlsx'

book = xlrd.open_workbook(filename)
book_openyxl = openpyxl.load_workbook(filename, data_only=True)

sheet_number = len(book_openyxl.worksheets)
sheet_1 = book.sheet_by_index(0) #Myco
sheet_2 = book.sheet_by_index(1) #hMPV
sheet_3 = book.sheet_by_index(2) #StrepA
sheet_4 = book.sheet_by_index(3) #Req.3

path = os.listdir('../../Mizuho_Feedback_Samples')
path = list(map(str, path))
print(path)

for i in range(len(path)):
    paths.append('../../Mizuho_Feedback_Samples/'+path[i])
print(paths)
for rowx in range(sheet_1.nrows):
    Myco_arr.append(sheet_1.cell_value(rowx=rowx,colx=6))
    Myco_time_arr.append(sheet_1.cell_value(rowx=rowx,colx=5))
    Myco_new_name.append(sheet_1.cell_value(rowx=rowx,colx=3))
for rowx in range(sheet_2.nrows):
    hMPV_arr.append(sheet_2.cell_value(rowx=rowx, colx=6))
    hMPV_time_arr.append(sheet_2.cell_value(rowx=rowx, colx=5))
    hMPV_new_name.append(sheet_2.cell_value(rowx=rowx, colx=3))
for rowx in range(sheet_3.nrows):
    StrepA_arr.append(sheet_3.cell_value(rowx=rowx, colx=6))
    StrepA_time_arr.append(sheet_3.cell_value(rowx=rowx, colx=5))
    StrepA_new_name.append(sheet_3.cell_value(rowx=rowx, colx=3))
print(Myco_arr)

#取出所有檔案路徑
for i in range(len(paths)):
    for dirPath, dirNames, fileNames in os.walk(paths[i]):
        dirPath = dirPath.replace('\\', '/')
        for f in fileNames:
            string = str(os.path.join(dirPath, f)).replace('\\', '/')
            img_path_lst.append(string)
            files.append(f)
print(img_path_lst)
#Myco命名
for j in range(len(Myco_arr)):
    for k in range(len(files)):
        if str(Myco_arr[j]) == str(files[k]):
            oldname = img_path_lst[k]
            newname = img_path_lst[k]+'_Myco_'+str(int(Myco_time_arr[j]))+'min'
            newname = (newname.replace('.bmp', ''))+'.bmp'
            os.rename(oldname, newname)
#hMPV命名
for j in range(len(hMPV_arr)):
    for k in range(len(files)):
        if str(hMPV_arr[j]) == str(files[k]):
            oldname = img_path_lst[k]
            newname = img_path_lst[k]+'_hMPV_'+str(int(hMPV_time_arr[j]))+'min'
            newname = (newname.replace('.bmp', ''))+'.bmp'
            os.rename(oldname, newname)
#StrepA命名
for j in range(len(StrepA_arr)):
    for k in range(len(files)):
        if str(StrepA_arr[j]) == str(files[k]):
            oldname = img_path_lst[k]
            newname = img_path_lst[k]+'_StrepA_'+str(int(StrepA_time_arr[j]))+'min'
            newname = (newname.replace('.bmp', ''))+'.bmp'
            os.rename(oldname, newname)










