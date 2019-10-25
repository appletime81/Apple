import os
from VirusDetectAlgo import *

line_para_map = {'FluA': [[2, 40, 240, 25, 50], [1, 300, 500, 25, 9.372]],#0
                 'FluB': [[2, 350, 550, 25, 50], [1, 80, 280, 25, 5.767]],#1
                 'Myco': [[2, 650, 850, 25, 50], [1, 80, 280, 25, 5.783]],#2
                 'RSV-hMPV': [[2, 600, 800, 25, 40], [1, 50, 250, 25, 10.211], [2, 330, 530, 25, 7.261]],#3
                 'StrepA': [[2, 650, 850, 25, 40], [1, 80, 280, 25, 5.486]]}#4

parameter = [get_line_para_map('FluA'), get_line_para_map('FluB'), get_line_para_map('Myco'), get_line_para_map('RSV-hMPV'), get_line_para_map('StrepA')]
print(parameter[4][1][0])

def get_line_para_map_no_filter(disease_chosen):
    return line_para_map_no_filter[disease_chosen]


def get_line_para_map(disease_chosen):
    return line_para_map[disease_chosen]
