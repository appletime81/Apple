from scipy import signal
from pandas.core.frame import DataFrame
import numpy as np


# @description   : 中間值濾波器, 取 kernel data 中位數
# @e.g (refs convert_genernal_kernel_data ): [5, 4, 3 , 3 , 2 ]
def median_filter(data, kernel_size):
    #smooth_data =  signal.medfilt(data, kernel_size)
    #smooth_data = DataFrame(data).rolling(window = kernel_size, center=True).median()
    kernel_data = convert_genernal_kernel_data(data, kernel_size)
    smooth_data = np.sort(kernel_data, axis=1)
    return np.median (smooth_data, axis=1)

# @description   :  中點濾波器, 對  kernel data 最大和最小值取平均
# @e.g (refs convert_genernal_kernel_data ): [4.5, 4, 3.5 , 2.5 , 2.5 ]
def midpoint_filter(data, kernel_size):
    kernel_data = convert_genernal_kernel_data(data, kernel_size)
    kernel_data = np.sort(kernel_data, axis=1)
    smooth_data = np.zeros ((len (data), 2), dtype=int)
    smooth_data[:, 0] = kernel_data[:, 0]
    smooth_data[:, 1] = kernel_data[:, kernel_size -1 ]
    return np.mean (smooth_data, axis=1)

# @description   :  平均濾波器, 對  kernel data 取平均
# @e.g (refs convert_genernal_kernel_data ): [4.66, 4, 3.33 , 2.66 , 2.33 ]
def mean_filter(data, kernel_size):
    #smooth_data = DataFrame(data).rolling(window = kernel_size, center=True).mean()
    smooth_data = mean_cut_filter(data, kernel_size, 0)
    return smooth_data

# +
# @description   :  刪減平均濾波器, 刪除 kernel data 最大 & 最小 cut_size 的個數後取平均
# @para cut_size :  刪除 kernel data 最大 & 最小 cut_size 的個數
# @e.g (refs convert_genernal_kernel_data ): [5, 4, 3 , 3 , 2 ]

def mean_cut_filter(data, kernel_size, cut_size):
    smooth_data = convert_genernal_kernel_data(data, kernel_size)
    # 容錯, 實際上為了減少運算, 不會增加下列if判斷
    if cut_size > 0:
        smooth_data = np.sort(smooth_data, axis=1)
    if (cut_size << 1) > kernel_size:
        return np.mean (smooth_data, axis=1)
    else:
        return np.mean (smooth_data[:,cut_size:kernel_size - cut_size ], axis=1)


# -

# @para data                    : 原始 data
# @para kernel_size(must be odd): 每次 kernel/operation data取的個數（當下運算的點 ＋ 上前後 kernel size / 2個 點 = kernel size）, 
# @e.g, kernel_size = 3 ,  total data = [5 4 3 3 2]
#  each kernel data =  [[5,5,4], [ 5 4 3], [4 3 3], [3 3 2] , [3 2 2]]
#  之後就看使用哪種filter, 對個別 kernel data/set 去運算, output則為實際的value
def convert_genernal_kernel_data(data, kernel_size) :
    assert kernel_size % 2 == 1, "kernel_size must be odd."
    k2 = (kernel_size - 1) // 2
    kernel_data = np.zeros ((len (data), kernel_size), dtype='float32')
    kernel_data[:,k2] = data
    
    #以下註解有加上for迴圈的邏輯,使用 kernel_size = 31 說明
    for i in range (k2):
        j = k2 - i
        # asgin kernel_data 16點以後, 每點需判斷 的 前15筆資料 
        kernel_data[j:,i] = data[:-j]
        # asgin kernel_data 前15點,  每點需判斷 的 前15筆資料 
        kernel_data[:j,i] = data[0]
        # asgin kernel_data 前15點,  每點需判斷  的 後15筆資料 
        kernel_data[:-j,-(i+1)] = data[j:]
       # asgin kernel_data 16點以後, 每點需判斷 的 後15筆資料 
        kernel_data[-j:,-(i+1)] = data[-1]
    return kernel_data
