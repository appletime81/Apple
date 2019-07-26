"""
This is a temp file before subclass of wxPython is done.
"""

def UpdateData(list, logs):
    list.DeleteAllItems()
    for index, item in enumerate(logs):
        AddData(list, index, item)

def AddData(list, index, data):
    list.InsertItem(index, str(data[0]))
    list.SetItem(index, 1, str(data[1]))
    list.SetItem(index, 2, str(data[2]))
    list.SetItem(index, 3, str(data[3]))
