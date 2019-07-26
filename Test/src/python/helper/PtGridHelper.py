"""
This is a temp file before subclass of wxPython is done.
"""
from wx import SHOW_SB_NEVER
from wx.grid import EVT_GRID_CELL_CHANGED

def SetupOne(grid, evtOnChanged):
    grid.HideColLabels()
    grid.CreateGrid(2, 1)
    grid.SetRowLabelValue(0, 'X')
    grid.SetRowLabelValue(1, 'Y')
    grid.ShowScrollbars(SHOW_SB_NEVER, SHOW_SB_NEVER)
    grid.Bind(EVT_GRID_CELL_CHANGED, evtOnChanged)

def SetupStartEnd(grid, evtOnChanged):
    grid.CreateGrid(2, 2)
    grid.SetRowLabelValue(0, 'X')
    grid.SetRowLabelValue(1, 'Y')
    grid.SetColLabelValue(0, 'Base')
    grid.SetColLabelValue(1, 'End')
    grid.ShowScrollbars(SHOW_SB_NEVER, SHOW_SB_NEVER)
    grid.Bind(EVT_GRID_CELL_CHANGED, evtOnChanged)

def GetGridPoint(grid, col=0):
    try:
        x = int(grid.GetCellValue(0, col))
        y = int(grid.GetCellValue(1, col))

        return x, y
    except BaseException:
        print('Failed to get point from grid.')

def SetGridPoint(grid, x, y, col=0):
    try:
        grid.SetCellValue(0, col, str(x))
        grid.SetCellValue(1, col, str(y))
    except BaseException:
        print('Failed to set point from grid.')