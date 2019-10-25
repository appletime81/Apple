"""
    Convert coordinates between window and wx.lib.floatcanvas.FloatCanvas
"""

def GetImageCoordinate(canvasSize, xc, yc, sx, sy):
    xw, yw = GetWindowCoordinate(canvasSize, xc, yc)
    xi = int(round(xw / sx))
    yi = int(round(yw / sy))

    return xi, yi

def GetWindowCoordinate(canvasSize, xc, yc):
    w, h = canvasSize
    xw = int(round(xc + w / 2))
    yw = int(round(-yc + h / 2))

    return xw, yw

def GetCanvasCoordinate(canvasSize, xw, yw):
    w, h = canvasSize
    xc = int(round(xw - w / 2))
    yc = int(round(-yw + h / 2))

    return xc, yc