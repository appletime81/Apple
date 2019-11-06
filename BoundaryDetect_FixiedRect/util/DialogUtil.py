from os import getcwd

from wx import (FD_FILE_MUST_EXIST, FD_OPEN, FD_OVERWRITE_PROMPT, FD_SAVE,
                FileDialog)


"""
This util creates certain dialogs for cases.
"""

def CreateLoadImgDialog(parent):
    title = "Select Sample"
    directory = getcwd() + "/samples"
    fileType = "BMP & PNG files (*.bmp; *.png)|*.bmp;*.png"
    dialogStyle = FD_OPEN | FD_FILE_MUST_EXIST

    return FileDialog(parent, title, defaultDir=directory, wildcard=fileType, style=dialogStyle)

def CreateSaveCsvDialog(parent):
    title = "Export CSV file"
    directory = getcwd() + "/csv"
    fileType = "*.csv"
    dialogStyle = FD_SAVE | FD_OVERWRITE_PROMPT

    return FileDialog(parent, title, defaultDir=directory, wildcard=fileType, style=dialogStyle)
