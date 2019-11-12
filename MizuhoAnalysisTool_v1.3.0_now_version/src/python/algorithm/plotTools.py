import matplotlib.pyplot as plt
import numpy as np

FLAG_CASES_PICS = 250

def plotCases(raw, liver, tumor):
    case_counter = 0
    for i, (seg_liver_raw, seg_liver_map, seg_tumor_map) in enumerate(zip(raw[:,:,:,0], liver[:,:,:,0], tumor[:,:,:,0])):
        if np.max(seg_tumor_map)==1:
            plt.figure(figsize=(20, 20))
            plt.subplot(1, 3, 1)
            plt.imshow(seg_liver_raw, cmap='gray')
            plt.axis('off')
            plt.subplot(1, 3, 2)
            plt.imshow(seg_liver_map, cmap='bone')
            plt.axis('off')
            plt.subplot(1, 3, 3)
            plt.imshow(seg_tumor_map, cmap='bone')
            plt.axis('off')
            plt.show()
            #plt.hist(seg_liver_raw.flatten(), range=[-150,400], color='black', bins=80)
            #plt.hist(seg_liver_map.flatten(), color='green', bins=80)
            #plt.hist(seg_tumor_map.flatten(), color='red', bins=80)
            #f_seg_liver_raw = seg_liver_raw[(seg_liver_raw>-70) & (seg_liver_raw<200)].flatten()
            #print('Mean =', np.mean(f_seg_liver_raw), 'Median =', np.median(f_seg_liver_raw), 'STD =', np.std(f_seg_liver_raw), 'Variance =', np.var(f_seg_liver_raw))  
            case_counter +=1
        if case_counter > FLAG_CASES_PICS:
            break

def plotCases(raw, tag):
    case_counter = 0
    for i, (seg_liver_pre, seg_liver_raw, seg_liver_pos, seg_liver_bg, seg_liver_map, seg_tumor_map) in enumerate(zip(raw[:,:,:,0], raw[:,:,:,1], raw[:,:,:,2], tag[:,:,:,0], tag[:,:,:,1], tag[:,:,:,2])):
        if np.max(seg_liver_map)==1:
            plt.figure(figsize=(20, 20))
            plt.subplot(2, 3, 1)
            plt.imshow(seg_liver_pre, cmap='gray')
            plt.title('Raw pre data')
            plt.axis('off')
            plt.subplot(2, 3, 2)
            plt.imshow(seg_liver_raw, cmap='gray')
            plt.title('Raw data')
            plt.axis('off')
            plt.subplot(2, 3, 3)
            plt.imshow(seg_liver_pos, cmap='gray')
            plt.title('Raw post data')
            plt.axis('off')            
            plt.subplot(2, 3, 4)
            plt.imshow(seg_liver_bg, cmap='bone')
            plt.title('bg data')
            plt.axis('off')
            plt.subplot(2, 3, 5)
            plt.imshow(seg_liver_map, cmap='bone')
            plt.title('liver data')
            plt.axis('off')
            plt.subplot(2, 3, 6)
            plt.imshow(seg_tumor_map, cmap='bone')
            plt.title('tumor data')
            plt.axis('off')
            plt.show()            
            #plt.hist(seg_liver_raw.flatten(), range=[-150,400], color='black', bins=80)
            #plt.hist(seg_liver_map.flatten(), color='green', bins=80)
            #plt.hist(seg_tumor_map.flatten(), color='red', bins=80)
            #f_seg_liver_raw = seg_liver_raw[(seg_liver_raw>-70) & (seg_liver_raw<200)].flatten()
            #print('Mean =', np.mean(f_seg_liver_raw), 'Median =', np.median(f_seg_liver_raw), 'STD =', np.std(f_seg_liver_raw), 'Variance =', np.var(f_seg_liver_raw))  
            case_counter +=1
        if case_counter > FLAG_CASES_PICS:
            break
            
def plotacclearingcurve(history):
    plt.plot(history.history['acc'])
    plt.plot(history.history['val_acc'])
    plt.title('model accuracy')
    plt.ylabel('accuracy')
    plt.xlabel('epoch')
    plt.legend(['train', 'test'], loc='upper left')
    plt.show()
    
def plotlosslearingcurve(history):
    plt.plot(history.history['loss'])
    plt.plot(history.history['val_loss'])
    plt.title('model loss')
    plt.ylabel('loss')
    plt.xlabel('epoch')
    plt.legend(['train', 'test'], loc='lower left')
    plt.show()