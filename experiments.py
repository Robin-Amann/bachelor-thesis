from pathlib import Path
import os


import utils.file as utils
import utils.constants as c
import utils.console as console

import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

from matplotlib.lines import Line2D

reachable = [(([20796, 18547, 16486, 14753, 13493, 12369, 10979, 9057, 7469, 6371], 1091794), ([15378, 14634, 13844, 13131, 12603, 12018, 11490, 10808, 10021, 9328], 123193)), 
             (([92236, 75135, 64184, 55365, 47973, 40383, 32281, 26327, 21687, 18023], 1093249), ([57874, 56121, 53126, 49240, 45294, 41666, 38017, 34470, 30846, 27565], 121738)), 
             (([129351, 101536, 88219, 76780, 67171, 57473, 47491, 39791, 33496, 28412], 1093249), ([101573, 99453, 95477, 89369, 83078, 77029, 71016, 65078, 59216, 53885], 121738))]

import statistics_complete.visualization as visual

visual.plot_methods_reachable_comparison([ i / 10 for i in range(1, 11)], reachable, c.custom_ctc_labels)
