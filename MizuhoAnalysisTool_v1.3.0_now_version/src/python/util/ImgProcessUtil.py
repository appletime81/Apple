import numpy as np

from wx import Bitmap

def GetGammaEnhancedImage(img, W, H):
    result_r, result_g, result_b = GetImageColorsByChannels(img, W, H)
    image_matrix = np.hstack((result_r, result_g, result_b))
    image_matrix = np.reshape(image_matrix, (H, W, 3))
    image_matrix = np.asarray(image_matrix, np.float32)

    peak = float(np.max(image_matrix))
    image_matrix = np.power(image_matrix / peak, 2) * peak
    image_matrix = np.asarray(image_matrix, np.uint8)

    return numpy2wximage(image_matrix, width=W, height=H)

def GetImageColorsByChannels(img, W, H):
    r = []
    g = []
    b = []

    for y in range(H):
        for x in range(W):
            r.append((img.GetRed(x, y)))
            g.append((img.GetGreen(x, y)))
            b.append((img.GetBlue(x, y)))

    r = np.array(r).reshape(len(r), 1)
    g = np.array(g).reshape(len(g), 1)
    b = np.array(b).reshape(len(b), 1)

    return (r, g, b)

def numpy2wximage(image_matrix, width, height):
    '''array2PIL'''
    wxbmp = Bitmap.FromBuffer(width, height, image_matrix)
    
    return wxbmp.ConvertToImage()
