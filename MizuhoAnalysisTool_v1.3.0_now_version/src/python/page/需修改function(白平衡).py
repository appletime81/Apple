def calculateCutOffValue(all_neg_files, line_parameters, useGammaEnhance, useWhiteBalance, std_rate=4): #Check
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

def calculateCutOffValue4Block(all_neg_files, line_parameters, useGammaEnhance, useWhiteBalance, std_rate=4): #Check
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


def algorithm3_with_slope( ):
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




