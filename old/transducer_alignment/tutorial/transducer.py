import torch
from speechbrain.nnet.loss.transducer_loss import TransducerLoss

from building_blocks import Encoder, Predictor, Joiner, NULL_INDEX

 
# --- Transducer and Loss Function ------------------------------------------------------------------------

class Transducer(torch.nn.Module):
  def __init__(self, num_inputs, num_outputs):
    super(Transducer, self).__init__()
    self.encoder = Encoder(num_inputs)
    self.predictor = Predictor(num_outputs)
    self.joiner = Joiner(num_outputs)

    if torch.cuda.is_available(): self.device = "cuda:0"
    else: self.device = "cpu"
    self.to(self.device)

  def compute_forward_prob(self, joiner_out, T, U, y):
    """
    joiner_out: tensor of shape (B, T_max, U_max+1, #labels)
    T: list of input lengths
    U: list of output lengths 
    y: label tensor (B, U_max+1)
    """
    B = joiner_out.shape[0]
    T_max = joiner_out.shape[1]
    U_max = joiner_out.shape[2] - 1
    log_alpha = torch.zeros(B, T_max, U_max+1).to(self.device)
    for t in range(T_max):
      for u in range(U_max+1):
          if u == 0:
            if t == 0:
              log_alpha[:, t, u] = 0.

            else: #t > 0
              log_alpha[:, t, u] = log_alpha[:, t-1, u] + joiner_out[:, t-1, 0, NULL_INDEX] 
                  
          else: #u > 0
            if t == 0:
              log_alpha[:, t, u] = log_alpha[:, t,u-1] + torch.gather(joiner_out[:, t, u-1], dim=1, index=y[:,u-1].view(-1,1) ).reshape(-1)
            
            else: #t > 0
              log_alpha[:, t, u] = torch.logsumexp(torch.stack([
                  log_alpha[:, t-1, u] + joiner_out[:, t-1, u, NULL_INDEX],
                  log_alpha[:, t, u-1] + torch.gather(joiner_out[:, t, u-1], dim=1, index=y[:,u-1].view(-1,1) ).reshape(-1)
              ]), dim=0)
    
    log_probs = []
    for b in range(B):
      log_prob = log_alpha[b, T[b]-1, U[b]] + joiner_out[b, T[b]-1, U[b], NULL_INDEX]
      log_probs.append(log_prob)
    log_probs = torch.stack(log_probs) 
    return log_prob

  def compute_loss(self, x, y, T, U):
    encoder_out = self.encoder.forward(x)
    predictor_out = self.predictor.forward(y)
    joiner_out = self.joiner.forward(encoder_out.unsqueeze(2), predictor_out.unsqueeze(1)).log_softmax(3)
    loss = -self.compute_forward_prob(joiner_out, T, U, y).mean()
    return loss

# --- Fast ---
transducer_loss = TransducerLoss(0)

def compute_loss(self, x, y, T, U):
    encoder_out = self.encoder.forward(x)
    predictor_out = self.predictor.forward(y)
    joiner_out = self.joiner.forward(encoder_out.unsqueeze(2), predictor_out.unsqueeze(1)).log_softmax(3)
    #loss = -self.compute_forward_prob(joiner_out, T, U, y).mean()
    T = T.to(joiner_out.device)
    U = U.to(joiner_out.device)
    loss = transducer_loss(joiner_out, y, T, U) #, blank_index=NULL_INDEX, reduction="mean")
    return loss

Transducer.compute_loss = compute_loss  



def greedy_search(self, x, T):
  y_batch = []
  B = len(x)
  encoder_out = self.encoder.forward(x)
  U_max = 200
  for b in range(B):
    t = 0; u = 0; y = [self.predictor.start_symbol]; predictor_state = self.predictor.initial_state.unsqueeze(0)
    while t < T[b] and u < U_max:
      predictor_input = torch.tensor([ y[-1] ]).to(x.device)
      g_u, predictor_state = self.predictor.forward_one_step(predictor_input, predictor_state)
      f_t = encoder_out[b, t]
      h_t_u = self.joiner.forward(f_t, g_u)
      argmax = h_t_u.max(-1)[1].item()
      if argmax == NULL_INDEX:
        t += 1
      else: # argmax == a label
        u += 1
        y.append(argmax)
    y_batch.append(y[1:]) # remove start symbol
  return y_batch

Transducer.greedy_search = greedy_search
