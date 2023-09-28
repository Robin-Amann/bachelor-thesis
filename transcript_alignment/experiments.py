import torch
num_frame = 5
num_tokens = 3

# Trellis has extra diemsions for both time axis and tokens.
# The extra dim for tokens represents <SoS> (start-of-sentence)
# The extra dim for time axis is for simplification of the code.
trellis = torch.empty((num_frame + 1, num_tokens + 1))
trellis[:, :] = 5
trellis[0, 0] = 0
trellis[1:, 0] = 1
trellis[0, -num_tokens:] = -float("inf")
trellis[-num_tokens:, 0] = float("inf")

print(trellis)

[0., -inf, -inf, -inf],
[1., 5., 5., 5.],
[1., 5., 5., 5.],
[inf, 5., 5., 5.],
[inf, 5., 5., 5.],
[inf, 5., 5., 5.]