import numpy as np
import math
from enum import Enum
import cv2


#####
# @para : image -> cv2 read image
# @para : image002.jpg if degree > 70, use gaussian_args = 201 (suggest user could change this value)
# @return : [angle, start_point, end_point ] with format [int, [x:int, y:int], [x:int,y:int]]
###
def getAngle(image, gaussian_args=51):
    height = image.shape[0]
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (gaussian_args, gaussian_args), 0)
    ret, thresh = cv2.threshold(gray, 70, 200, 0)
    image = np.transpose(thresh)
    verify_set = []
    for x, x_data in enumerate(image):
        for y, y_data in enumerate(x_data):
            if y_data > 0:
                verify_set.append([x, height - y])
                break

    data_len = len(verify_set)

    if data_len == 0:
        return [0, 0, 0, 0]
    else:
        start_point = int(data_len * 1 / 4)
        end_point = int(data_len * 3 / 4)
        angle = 0
        if start_point != end_point:
            slope = (verify_set[start_point][1] - verify_set[end_point][1]) / (
                        verify_set[start_point][0] - verify_set[end_point][0])
            angle = math.atan(slope) * 180 / math.pi
        angle = round(angle)
        angle *= -1

        return [angle, verify_set[start_point], verify_set[end_point], thresh]