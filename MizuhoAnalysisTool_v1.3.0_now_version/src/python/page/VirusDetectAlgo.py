from PIL import ImageTk, Image, ImageFilter
import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import accuracy_score
import pandas as pd
import cv2

from .NosieFilter import median_filter, mean_filter, midpoint_filter, mean_cut_filter

line_para_map_no_filter = {'FluA': [[2, 350, 550, 25, 80], [2, 80, 200, 25, 8.95]],
                           'FluB': [[2, 350, 550, 25, 80], [1, 80, 200, 25, 8.71]],
                           'Myco': [[1, 600, 900, 25, 70], [1, 100, 250, 25, 9.75]],
                           'RSV-hMPV': [[1, 600, 800, 25, 47], [1, 70, 200, 25, 10.79], [2, 350, 500, 25, 9.48]],
                           'StrepA': [[1, 600, 900, 25, 70], [1, 100, 250, 25, 7.555]]}

line_para_map_float = {'FluA': [[2, 80, 280, 25, 95.657], [1, 370, 500, 25, 8.435]],
                       'FluB': [[2, 350, 550, 25, 98.029], [1, 80, 200, 25, 5.217]],
                       'Myco': [[2, 600, 900, 25, 96.042], [1, 100, 250, 25, 6.638]],
                       'RSV-hMPV': [[2, 600, 800, 25, 74.894], [1, 70, 200, 25, 9.379], [2, 350, 500, 25, 6.529]],
                       'StrepA': [[2, 600, 900, 25, 78.265], [1, 100, 250, 25, 4.950]]}

line_para_map_no_white_balance = {'FluA': [[2, 40, 240, 25, 50], [1, 300, 500, 25, 9.372]],
                                  'FluB': [[2, 350, 550, 25, 50], [1, 80, 280, 25, 5.767]],
                                  'Myco': [[2, 650, 850, 25, 50], [1, 80, 280, 25, 5.783]],
                                  'RSV-hMPV': [[2, 600, 800, 25, 40], [1, 50, 250, 25, 10.211],
                                               [2, 330, 530, 25, 7.261]],
                                  'StrepA': [[2, 650, 850, 25, 40], [1, 80, 280, 25, 5.486]]}

line_para_map = {'FluA': [[2, 40, 240, 25, 50], [1, 300, 500, 25, 9.372]],
                 'FluB': [[2, 350, 550, 25, 50], [1, 80, 280, 25, 5.767]],
                 'Myco': [[2, 650, 850, 25, 50], [1, 80, 280, 25, 5.783]],
                 'RSV-hMPV': [[2, 600, 800, 25, 40], [1, 50, 250, 25, 10.211], [2, 330, 530, 25, 7.261]],
                 'StrepA': [[2, 650, 850, 25, 40], [1, 80, 280, 25, 5.486]]}


def get_line_para_map_no_filter(disease_chosen):
    return line_para_map_no_filter[disease_chosen]


def get_line_para_map(disease_chosen):
    return line_para_map[disease_chosen]


def show_plot(im, image_name=''):
    plt.imshow(im)
    plt.axis('off')
    plt.show()

    image = np.array(im)
    avg_img = np.average(im, axis=2)
    r, g, b = image[:, :, 0], image[:, :, 1], image[:, :, 2]

    r = np.average(r, axis=0)
    g = np.average(g, axis=0)
    b = np.average(b, axis=0)
    gray = np.average(avg_img, axis=0)
    pic_width_pixel = np.size(r, 0)

    figure = plt.figure(image_name)

    plot = figure.add_subplot(111)

    plt.title('RGB')
    df = pd.DataFrame({'x': range(0, pic_width_pixel), 'j1': r, 'j2': g, 'j3': b, 'j4': gray})

    plt.ylim(0, 255)

    plt.plot('x', 'j1', data=df, color='red', linewidth=1, label='r')
    plt.plot('x', 'j2', data=df, color='green', linewidth=1, label='g')
    plt.plot('x', 'j3', data=df, color='blue', linewidth=1, label='b')
    plt.plot('x', 'j4', data=df, color='gray', linewidth=1, label='gray')

    plt.show()


def show_figure(df_array):
    pic_width_pixel = len(df_array)
    figure = plt.figure('NULL')
    plot = figure.add_subplot(111)
    plt.title('dif method')
    df = pd.DataFrame({'x': range(0, pic_width_pixel), 'j1': df_array})
    # matplotlib.pyplot.ylabel("Average value")
    plt.ylim(-20, 20)
    plt.plot('x', 'j1', data=df, color='blue', linewidth=1, label='df_array')
    plt.show()


def evaluate(y_pred, y_test, tags, vis_filename=None):
    accuracy = accuracy_score(y_test, y_pred)

    tp = 0
    tn = 0
    total_n = 0
    for p, t in zip(y_pred, y_test):
        if p == 1 and t == 1:
            tp += 1
        if p == 0 and t == 0:
            tn += 1
        if t == 0:
            total_n += 1

    sensitivity = (float(tp) + np.finfo(np.float32).eps) / (np.sum(y_test) + np.finfo(np.float32).eps)

    specificity = (float(tn) + np.finfo(np.float32).eps) / (total_n + np.finfo(np.float32).eps)
    # print("accuracy:", accuracy)

    # print('y_pred = ', y_pred)
    # print('y_test = ', y_test)
    confusion = np.zeros((len(tags), len(tags)), dtype=np.int32)
    for (predicted_index, actual_index) in zip(y_pred, y_test):
        confusion[predicted_index, actual_index] += 1

    return accuracy, sensitivity, specificity, confusion


def gamma_enhance(im, enhance_value=2):
    im = np.array(im)
    im = np.asarray(im, np.float32)
    im = np.power(im / float(np.max(im)), enhance_value) * float(np.max(im))
    im = np.asarray(im, np.uint8)

    return im


def white_balance(im):
    r, g, b = cv2.split(im)
    r_avg = cv2.mean(r)[0]
    g_avg = cv2.mean(g)[0]
    b_avg = cv2.mean(b)[0]

    k = (r_avg + g_avg + b_avg) / 3
    kr = k / r_avg
    kg = k / g_avg
    kb = k / b_avg

    r = cv2.addWeighted(src1=r, alpha=kr, src2=0, beta=0, gamma=0)
    g = cv2.addWeighted(src1=g, alpha=kg, src2=0, beta=0, gamma=0)
    b = cv2.addWeighted(src1=b, alpha=kb, src2=0, beta=0, gamma=0)

    im = cv2.merge([r, b, g])

    return im


def find_peak(im, parameters, useFliter, usePeakDetection, show):
    rgb_index = parameters[0]
    start_interval = parameters[1]
    end_interval = parameters[2]
    stride_threshold = parameters[3]
    pn_threshold = parameters[4]

    # use all rgb channel
    avg_img = np.average(im[:, :, :], axis=2)
    # use specific channel
    # avg_img = im[:, :, rgb_index]
    current_rgb = np.average(avg_img, axis=0)

    df_array = []
    for index in range(len(current_rgb)):
        if index - stride_threshold > 0 and index < len(current_rgb):
            dif = current_rgb[index - stride_threshold] - current_rgb[index]
            df_array.append(dif)
        else:
            df_array.append(0)

    if useFliter:
        # df_array = mean_cut_filter(df_array, 5, 1)
        df_array = median_filter(df_array, 5)
        # df_array = mean_filter(df_array, 5)

    if show:
        show_figure(df_array)

    result = 0  # Negtive
    min_value = 1000
    min_index = 1000
    max_value = -1000
    max_index = -1000
    max_different = 0
    global_max_index = -1000
    global_max_value = -1000
    global_min_index = 1000
    global_min_value = 1000
    taget_min_point = [0, 0]
    taget_max_point = [0, 0]
    for index, dif in enumerate(df_array[start_interval:end_interval]):
        if usePeakDetection:
            if dif > max_value:
                max_value = dif
                max_index = index
                min_value = 1000
                min_index = -1
                continue
            elif dif < min_value:
                min_value = dif
                min_index = index
                if min_value < global_min_value:
                    global_min_value = min_value
                    globel_min_index = min_index
            else:
                continue
        else:
            if dif < min_value:
                min_value = dif
                min_index = index

            elif dif > max_value:
                max_value = dif
                max_index = index

        current_different = max_value - min_value
        if current_different > max_different:
            max_different = round(current_different, 3)
            taget_min_point = [min_index, min_value]
            taget_max_point = [max_index, max_value]

        if current_different > pn_threshold:
            result = 1

    return result, df_array, max_different, taget_max_point[0], taget_max_point[1], taget_min_point[0], taget_min_point[
        1]


def calculateCutOffValue(all_neg_files, line_parameters, useGammaEnhance, useWhiteBalance, std_rate=4):
    neg_list1 = []
    neg_list2 = []
    for neg_i in all_neg_files:
        im_n = cv2.imread(neg_i, cv2.IMREAD_COLOR)
        im_n = cv2.cvtColor(im_n, cv2.COLOR_BGR2RGB)
        control, test_result1, test_result2 = algorithm3_with_slope(im_n, line_parameters, useGammaEnhance,
                                                                    useWhiteBalance, True, True, False)
        if control[0] == 1:
            print(neg_i)
            print(test_result1[1])
            neg_list1.append(test_result1[1])
            if test_result2 != None:
                print(test_result2[1])
                neg_list2.append(test_result2[1])

    avg_neg_value = np.average(neg_list1)
    std_neg_value = np.std(neg_list1)
    pn1 = avg_neg_value + std_neg_value * std_rate
    print('avg_neg_value1 = ', avg_neg_value)
    print('std_neg_value1 = ', std_neg_value)
    print('P/N thredshold1 = ', pn1)
    print('')

    pn2 = None
    if test_result2 != None:
        avg_neg_value = np.average(neg_list2)
        std_neg_value = np.std(neg_list2)
        pn2 = avg_neg_value + std_neg_value * std_rate
        print('avg_neg_value2 = ', avg_neg_value)
        print('std_neg_value2 = ', std_neg_value)
        print('')

    return pn1, pn2


def calculateCutOffValue4Block(all_neg_files, line_parameters, useGammaEnhance, useWhiteBalance, std_rate=4):
    neg_list1 = []
    neg_list2 = []
    for neg_i in all_neg_files:
        im_n = Image.open(neg_i)
        control, test_result1, test_result2, _, _ = algorithm3_with_slope_4block(im_n, line_parameters, useGammaEnhance,
                                                                                 useWhiteBalance, True, True, False)
        if control[0] == 1:
            for t1 in test_result1:
                neg_list1.append(t1[1])
            if test_result2 != None:
                for t2 in test_result2:
                    neg_list2.append(t2[1])

    avg_neg_value = np.average(neg_list1)
    std_neg_value = np.std(neg_list1)
    pn1 = avg_neg_value + std_neg_value * std_rate
    print('avg_neg_value1 = ', avg_neg_value)
    print('std_neg_value1 = ', std_neg_value)
    print('P/N thredshold1 = ', pn1)
    print('')

    pn2 = None
    if test_result2 != None:
        avg_neg_value = np.average(neg_list2)
        std_neg_value = np.std(neg_list2)
        pn2 = avg_neg_value + std_neg_value * std_rate
        print('avg_neg_value2 = ', avg_neg_value)
        print('std_neg_value2 = ', std_neg_value)
        print('')

    return pn1, pn2


def algorithm3_with_slope(im, line_parameters, useGammaEnhance, useWhiteBalance, useFliter, usePeakDetection,
                          show_figure):
    if useGammaEnhance:
        im = gamma_enhance(im)

    if useWhiteBalance:
        im = white_balance(im)

    # detect control line
    control_line_parameters = line_parameters[0]
    c_result, c_df_array, c_max_different, max_index, max_value, min_index, min_value = find_peak(im,
                                                                                                  control_line_parameters,
                                                                                                  useFliter,
                                                                                                  usePeakDetection,
                                                                                                  False)
    control = [c_result, c_max_different, max_index, max_value, min_index, min_value, c_df_array]
    if c_result == 0:
        return control, None, None

    # detect test line1
    test_line1_parameters = line_parameters[1]
    result1, df_array1, max_different1, max_index1, max_value1, min_index1, min_value1 = find_peak(im,
                                                                                                   test_line1_parameters,
                                                                                                   useFliter,
                                                                                                   usePeakDetection,
                                                                                                   show_figure)

    test_result1 = [result1, max_different1, max_index1, max_value1, min_index1, min_value1, df_array1]
    test_result2 = None
    # detect test line2 if exist
    if len(line_parameters) == 3:
        test_line2_parameters = line_parameters[2]
        result2, df_array2, max_different2, max_index2, max_value2, min_index2, min_value2 = find_peak(im,
                                                                                                       test_line2_parameters,
                                                                                                       useFliter,
                                                                                                       usePeakDetection,
                                                                                                       show_figure)
        test_result2 = [result2, max_different2, max_index2, max_value2, min_index2, min_value2, df_array2]

    return control, test_result1, test_result2


def algorithm3_with_slope_4block(im, line_parameters, useGammaEnhance, useWhiteBalance, useFliter, usePeakDetection,
                                 show_figure, num_positive=4):
    if useGammaEnhance:
        im = gamma_enhance(im)

    if useWhiteBalance:
        im = white_balance(im)

    # detect control line
    control_line_parameters = line_parameters[0]
    c_result, c_df_array, c_max_different, max_index, max_value, min_index, min_value = find_peak(im,
                                                                                                  control_line_parameters,
                                                                                                  useFliter,
                                                                                                  usePeakDetection,
                                                                                                  False)
    control = [c_result, c_max_different, max_index, max_value, min_index, min_value, c_df_array]
    if c_result == 0:
        return control, None, None, None, None

    test_result1 = []
    test_result2 = []
    test_result1_result_list = []
    test_result2_result_list = []

    height = im.shape[0]
    block_height = int(height / 4)
    height_index = 0
    for i in range(4):
        block_im = im[height_index:height_index + block_height, :]
        # detect test line1
        test_line1_parameters = line_parameters[1]
        result1, df_array1, max_different1, max_index1, max_value1, min_index1, min_value1 = find_peak(block_im,
                                                                                                       test_line1_parameters,
                                                                                                       useFliter,
                                                                                                       usePeakDetection,
                                                                                                       show_figure)

        test_result1.append([result1, max_different1, max_index1, max_value1, min_index1, min_value1, df_array1])
        test_result1_result_list.append(result1)
        # detect test line2 if exist
        if len(line_parameters) == 3:
            test_line2_parameters = line_parameters[2]
            result2, df_array2, max_different2, max_index2, max_value2, min_index2, min_value2 = find_peak(block_im,
                                                                                                           test_line2_parameters,
                                                                                                           useFliter,
                                                                                                           usePeakDetection,
                                                                                                           show_figure)
            test_result2.append([result2, max_different2, max_index2, max_value2, min_index2, min_value2, df_array2])
            test_result2_result_list.append(result2)

        height_index += block_height

    test_result1_pred = 0
    if np.sum(test_result1_result_list) >= num_positive:
        test_result1_pred = 1

    test_result2_pred = 0
    if len(line_parameters) == 3:
        if np.sum(test_result2_result_list) >= num_positive:
            test_result2_pred = 1

    return control, test_result1, test_result2, test_result1_pred, test_result2_pred
