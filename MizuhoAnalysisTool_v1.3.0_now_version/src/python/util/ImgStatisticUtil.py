import numpy

def GetHorizontalLogs(data):
    logWidth = data.LogWidth[1]
    y = data.Center[1]
    x1, x2 = data.SpecifiedAreaStart[0], data.SpecifiedAreaEnd[0]
    y1, y2 = GetSecondaryRange(y, logWidth, data.SpecifiedAreaStart[1], data.SpecifiedAreaEnd[1])

    return GetLogs(data.GetTargetImage(), (x1, y1), (x2, y2), 0)

def GetVerticalLogs(data):
    logWidth = data.LogWidth[0]
    x = data.Center[0]
    x1, x2 = GetSecondaryRange(x, logWidth, data.SpecifiedAreaStart[0], data.SpecifiedAreaEnd[0])
    y1, y2 = data.SpecifiedAreaStart[1], data.SpecifiedAreaEnd[1]

    return GetLogs(data.GetTargetImage(), (x1, y1), (x2, y2), 1)

'''
    Get secondary range of analysis region.
    The direction is perpendicular to mandatory axis.

    :param center: center value of secondary range
    :param logWidth: log width for secondary range. 0 for center itself (1 pixel), -1 for max range
    :param startMin: min value for secondary range
    :param startMax: max value for secondary range
    :return a tuple of range
'''
def GetSecondaryRange(center, logWidth, startMin, startMax):
    if logWidth == 0:
        return center, center + 1
    elif logWidth == -1:
        return startMin, startMax
    else:
        r1, r2 = center - logWidth, center + logWidth
        if r1 < startMin:
            r1 = startMin
        if r2 > startMax:
            r2 = startMax

        return r1, r2

'''
    Get final logs with the following format:
    [
        [no, r, g, b],
        ...
    ]

    :param iamge: an wx.Image instance
    :param start: tuple of start point
    :param end: tuple of end point
    :param axis: flag for calculating average values. 0 for X axis, and 1 for Y axis
    :return a 2D array of average values, which item format is [no, r, g, b]
'''
def GetLogs(image, start, end, axis):
    rangeX = [x for x in range(start[0], end[0])]
    rangeY = [y for y in range(start[1], end[1])]

    width = abs(end[0] - start[0])
    height = abs(end[1] - start[1])

    r, g, b = GetImagePixelColors(image, rangeX, rangeY)
    avgR, avgG, avgB = GetImageAveragedColor(r, g, b, width, height, axis)

    outputRng = rangeX if axis == 0 else rangeY

    return GetFinalAveragedColorsOutput(avgR, avgG, avgB, outputRng)

def GetImagePixelColors(image, rangeX, rangeY):
    r = []
    g = [] 
    b = []
    
    for yi in rangeY:
        for xi in rangeX:
            r.append(image.GetRed(xi, yi))
            g.append(image.GetGreen(xi, yi))
            b.append(image.GetBlue(xi, yi))

    return r, g, b

def GetImageAveragedColor(r, g, b, width, height, axis):
    avgR = GetAveragedColor(r, width, height, axis)
    avgG = GetAveragedColor(g, width, height, axis)
    avgB = GetAveragedColor(b, width, height, axis)

    return avgR, avgG, avgB

def GetAveragedColor(colorList, width, height, axis):
    reshapedColorList = numpy.array(colorList).reshape(height, width)

    return numpy.mean(reshapedColorList, axis=axis)

def GetFinalAveragedColorsOutput(avgR, avgG, avgB, rng):
    return [
        [rng[i], avgR[i], avgG[i], avgB[i]]
        for i in range(len(rng))
    ]
