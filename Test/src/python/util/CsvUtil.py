from wx import LogError

def ExportCSV(path, logX, logY):
    try:
        with open(path, 'w') as file:
            linesX, lenX = GetLinesDataAndCount(logX)
            linesY, lenY = GetLinesDataAndCount(logY)

            file.write('Xn, R, G, B, Yn, R, G, B\n')
            for i in range(max(lenX, lenY)):
                lineString = linesX[i] + ', ' if i < lenX else ', , , ,'
                lineString += linesY[i] + '\n' if i < lenY else ', , , \n'
                file.write(lineString)
    except IOError:
        LogError("Cannot save current data in file '%s'." % path)

def GetLinesDataAndCount(log):
    lines = [
        '%f, %f, %f, %f' % (item[0], item[1], item[2], item[3])
        for item in log
    ]

    return lines, len(lines)
