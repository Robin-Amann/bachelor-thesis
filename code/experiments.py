import utils.file as utils
import utils.constants as constants
from collections import Counter
import matplotlib.pyplot as plt
from progress.bar import ChargingBar
from scipy.interpolate import griddata
import numpy as np





# def wer_distribution() :
#     files = utils.get_directory_files(constants.transcript_alignment_dir, 'txt')
#     data = []   # wer, length of transcript, file
#     lengths = []
#     a = 0
#     b = 0
#     for file in ChargingBar("Align Transcripts").iter(files) :
#         operations = utils.read_file(str(file)).split()
#         length = len(operations)
#         if length == 0 : 
#             continue 

#         wer = (operations.count('i') + operations.count('d') + operations.count('r') ) / length
#         l1 = operations.count('i') + operations.count('n') + operations.count('r')
#         l2 = operations.count('n') + operations.count('d') + operations.count('r')
        
#         lengths.append( ( l1, l2 ) )
#         if ( 100 - 10 ) / 100 * l1 + 10 < l2  or 100 / ( 100 - 10 ) * (l1 - 10) > l2 :
#             a += 1
#         else :
#             b += 1
#         data.append( (wer, length, str(file)[len(constants.transcript_alignment_dir) : ]) )
#     print(b, a)
#     return data, lengths


# def plot_wer_over_len(wer, leng, occ) :
#     plt.scatter(wer, leng, s=occ)
#     plt.show()
#     plt.scatter(wer, leng)
#     plt.show()

# def plot_3d(wer, leng, occ) :
#     data = tuple(zip(wer, leng, occ))
#     x, y, z = zip(*data)
#     z = list(map(float, z))
#     grid_x, grid_y = np.mgrid[min(x):max(x):100j, min(y):max(y):100j]
#     grid_z = griddata((x, y), z, (grid_x, grid_y), method='cubic')
#     fig = plt.figure()
#     ax = fig.add_subplot(projection='3d')
#     ax.plot_surface(grid_x, grid_y, grid_z, cmap=plt.cm.Spectral)
#     plt.show()


# data, lengths = wer_distribution()
# wer_len_occ = dict(Counter( [(a, b) for a, b, c in data] )) # (wer, len) --> count
# wer_len = list( wer_len_occ.keys()) 
# occ = [wer_len_occ[x] for x in wer_len]
# wer = [ float(k) for k, v in wer_len]
# leng = [ int(v) for k, v in wer_len]
# # plot_wer_over_len(wer, leng, occ)
# # plot_3d(wer, leng, occ)

# lengths = dict(Counter(lengths))  # (l1, l2) --> c
# l1, l2 = zip(*lengths)
# count = [lengths[(a, b)] for a, b in zip(l1, l2) ]
# plt.scatter(l1, l2, s=count)
# plt.show()

# diff = dict(Counter([abs(a - b) for a, b in lengths]))
# diff = [ (int(k), v) for k, v in diff.items()]

# plt.plot([a for a, b in diff], [b for a, b in diff])
# plt.show()
