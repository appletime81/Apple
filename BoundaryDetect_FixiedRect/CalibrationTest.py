# for boudary detection
import cv2
import os
import numpy as np
from matplotlib import pyplot as plt
from calibrationAlgorithm import *

# All the 6 methods for comparison in a list
# methods = ['cv2.TM_CCOEFF', 'cv2.TM_CCOEFF_NORMED', 'cv2.TM_CCORR',
#             'cv2.TM_CCORR_NORMED', 'cv2.TM_SQDIFF', 'cv2.TM_SQDIFF_NORMED']

TEST_FOLDER = 'calibration_samples'
template = cv2.imread(os.path.join(TEST_FOLDER, 'template.bmp'), cv2.IMREAD_COLOR)

img = cv2.imread(os.path.join(TEST_FOLDER, 'B.bmp'), cv2.IMREAD_COLOR)
match_locations, res = detectAndRemoveSame(img, template, 2)
#img = cv2.imread(os.path.join(TEST_FOLDER, 'B.bmp'), cv2.IMREAD_COLOR)
#match_locations, res = detectAndRemoveSame(img, template, 3)

print(match_locations)

# draw template match boxes
w, h, c = template.shape
for i in match_locations:
    x, y = i
    cv2.rectangle(img, (x-int(w/2), y-int(h/2)), (x+int(w/2), y+int(h/2)), [255,255,0], 10) 
    
plt.figure(figsize=(15, 15), dpi=80, facecolor='w', edgecolor='k')

plt.subplot(121),plt.imshow(res)
plt.title('Matching Result'), plt.xticks([]), plt.yticks([])
plt.subplot(122),plt.imshow(img)
plt.title('Detected Point'), plt.xticks([]), plt.yticks([])
 
plt.show()

