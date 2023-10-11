import torch

# trellis = torch.empty((10, 5))
# trellis[:, :] = 0
# trellis[1:, 0] = 1
# trellis[0, -4:] = -float("inf")
# trellis[-4:, 0] = float("inf")
# t= 0
# trellis[t + 1, 1:] = 2

# print(trellis)

# a = [i for i in range(10) ]
# print(a[[1,3,2]])


slope = 1.5
peaks = []
i = len(peaks) - 1
while i > 0 :
    index_a = i
    index_b = i-1
    height_a = peaks[index_a]
    height_b = peaks[index_b]
    
    if height_b < height_a :
        if ( height_a - height_b) / ( index_a - index_b ) > slope :
            peaks = peaks[:i-1] + peaks[i:]     # remove i-1
            i -= 1
    else :
        if ( height_b - height_a) / ( index_a - index_b ) > slope :
            peaks = peaks[:i] + peaks[i+1:]     # remove i
    