import torch

NULL_INDEX = 0
encoder_dim = 1024
predictor_dim = 1024
joiner_dim = 1024

class Encoder(torch.nn.Module):
  def __init__(self, num_inputs):
    super(Encoder, self).__init__()
    self.embed = torch.nn.Embedding(num_inputs, encoder_dim)
    self.rnn = torch.nn.GRU(input_size=encoder_dim, hidden_size=encoder_dim, num_layers=3, batch_first=True, bidirectional=True, dropout=0.1)
    self.linear = torch.nn.Linear(encoder_dim*2, joiner_dim)

  def forward(self, x):
    out = x
    out = self.embed(out)
    out = self.rnn(out)[0]
    out = self.linear(out)
    return out
  

class Predictor(torch.nn.Module):
  def __init__(self, num_outputs):
    super(Predictor, self).__init__()
    self.embed = torch.nn.Embedding(num_outputs, predictor_dim)
    self.rnn = torch.nn.GRUCell(input_size=predictor_dim, hidden_size=predictor_dim)
    self.linear = torch.nn.Linear(predictor_dim, joiner_dim)
    
    self.initial_state = torch.nn.Parameter(torch.randn(predictor_dim))
    self.start_symbol = NULL_INDEX # In the original paper, a vector of 0s is used; just using the null index instead is easier when using an Embedding layer.

  def forward_one_step(self, input, previous_state):
    embedding = self.embed(input)
    state = self.rnn.forward(embedding, previous_state)
    out = self.linear(state)
    return out, state

  def forward(self, y):
    batch_size = y.shape[0]
    U = y.shape[1]
    outs = []
    state = torch.stack([self.initial_state] * batch_size).to(y.device)
    for u in range(U+1): # need U+1 to get null output for final timestep 
      if u == 0:
        decoder_input = torch.tensor([self.start_symbol] * batch_size).to(y.device)
      else:
        decoder_input = y[:,u-1]
      out, state = self.forward_one_step(decoder_input, state)
      outs.append(out)
    out = torch.stack(outs, dim=1)
    return out
  

class Joiner(torch.nn.Module):
  def __init__(self, num_outputs):
    super(Joiner, self).__init__()
    self.linear = torch.nn.Linear(joiner_dim, num_outputs)

  def forward(self, encoder_out, predictor_out):
    out = encoder_out + predictor_out
    out = torch.nn.functional.relu(out)
    out = self.linear(out)
    return out