import cv2
import numpy as np
from matplotlib import pyplot as plt
 
img = cv2.imread('./Test_Strip_Images/FluA.bmp', cv2.IMREAD_UNCHANGED)
img2 = img.copy()
template = cv2.imread('./Test_Strip_Images/001_Template.bmp', 0)
w = template.shape[1]
h = template.shape[0]

methods = ['cv2.TM_CCORR_NORMED']
def point_position(method):
    for meth in methods:
        img = img2.copy()
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        method = eval(meth)

        res = cv2.matchTemplate(gray,template,method)

        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

        min_thresh = (min_val + 1e-6) * 1.2
        match_locations = np.where(res<=min_thresh)

        w, h = template.shape[::-1]
        if method in [cv2.TM_SQDIFF_NORMED]:
            for (x, y) in zip(match_locations[1], match_locations[0]):
                cv2.rectangle(img, (x, y), (x+w, y+h), [255,255,0], 2)
        else:
            max_thresh = (max_val - 1e-6) * 0.99
            match_locations = np.where(res>=max_thresh)
            cnt = 0
            for (x, y) in zip(match_locations[1], match_locations[0]):
                print(cnt)
                cnt = cnt + 1
                cv2.rectangle(img, (x, y), (x + w, y + h), [255,255,0], 2)
                print(x,y)
                if cnt==1:
                    print(x,y)
                    point1 = np.array([int(x+w/2), int(y+h/2)])
                elif cnt==7:
                    print(x, y)
                    point2 = np.array([int(x+w/2), int(y+h/2)])
        #
        plt.subplot(121),plt.imshow(res)
        plt.title('Matching Result'), plt.xticks([]), plt.yticks([])
        plt.subplot(122),plt.imshow(img)
        plt.title('Detected Point'), plt.xticks([]), plt.yticks([])
        plt.suptitle(meth)

        plt.show()
    return point1, point2

a, b = point_position(methods)
print(a, b)


