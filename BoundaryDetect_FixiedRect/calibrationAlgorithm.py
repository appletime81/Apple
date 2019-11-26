import cv2
import os
import numpy as np

def detectAndRemoveSame(img, template, keep_size):
    methods = {'cv2.TM_SQDIFF_NORMED':0, 'cv2.TM_CCOEFF_NORMED':1, 'cv2.TM_CCORR_NORMED':2}
    method = methods['cv2.TM_CCOEFF_NORMED']
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    gray_img = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    
    template_size = template.shape[1]
    template = cv2.cvtColor(template, cv2.COLOR_BGR2RGB)
    gray_template = cv2.cvtColor(template, cv2.COLOR_RGB2GRAY)    
    
    # Apply template Matching
    res = cv2.matchTemplate(gray_img,gray_template,method)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
    print('min_val = ', min_val)
    print('max_val = ', max_val)
    print('min_loc = ', min_loc)
    print('max_loc = ', max_loc)
    
    candicate_loc = {}
    index = 0
    max_v = 0.35 #(min_val + 1e-6) * 1000
    for i in np.arange(min_val, max_v, 0.05):
        
        match_locations = np.where(res<=i)
        #min_thresh = (max_val - 1e-6) * 0.6
        #match_locations = np.where(res>=min_thresh)
        
        #print('len(match_locations[0]) = ', len(match_locations[0]))
        if len(match_locations[0])>=keep_size:
    
            x_loc, y_loc = match_locations
            
            for x,y in zip(x_loc, y_loc):
                prob = res[x, y]
                if candicate_loc=={}:
                    candicate_loc[index] = [x, y, prob]
                    index+=1
                else:
                    candicate_loc_size = len(candicate_loc)
                    flag_add_new = True
                    for j in range(candicate_loc_size):
                        
                        loc = candicate_loc[j]
                        # means update exist bounding box loc

                        if (x>=(loc[0]-template_size) and x<=(loc[0]+template_size)) and (y>=(loc[1]-template_size) and y<=(loc[1]+template_size)):
                            if prob<=loc[2]:
                                candicate_loc[j] = [x, y, prob]

                            flag_add_new = False
                            break
                                
                    # means just update exist bounding box loc
                    if flag_add_new:
                        #print('x = ', x, ' y = ', y, ' template_size = ', template_size, ' prob = ', prob)
                        #print('loc[0] = ', loc[0], ' loc[1] = ', loc[1], ' loc[2] = ', loc[2])
                        
                        #only keep same size result with keep_size
                        if index >= keep_size:
                            max_prob = 0
                            max_index = -1
                            for j in candicate_loc:
                                if candicate_loc[j][2]> max_prob:
                                    max_prob = candicate_loc[j][2]
                                    max_index = j
                                    
                            if prob < max_prob:
                                candicate_loc[max_index] = [x, y, prob]
                        else:
                            candicate_loc[index] = [x, y, prob]
                            index+=1           
    final_loc = []
    for i in candicate_loc:
        x, y, prob = candicate_loc[i]
        x = int(x + (template_size/2))
        y = int(y + (template_size/2))
        final_loc.append([y,x])
    
    final_loc.sort()
    # print(final_loc)
    return final_loc, res

def variance_of_laplacian(image):
    return round(cv2.Laplacian(image, cv2.CV_64F).var(),1)