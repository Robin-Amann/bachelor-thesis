import torch
import string
from tqdm import tqdm
import unidecode

from building_blocks import NULL_INDEX
from transducer import Transducer

# --- Utilities ------------------------------------------------------------------------

class TextDataset(torch.utils.data.Dataset):
  def __init__(self, lines, batch_size):
    lines = list(filter(("\n").__ne__, lines))

    self.lines = lines # list of strings
    collate = Collate()
    self.loader = torch.utils.data.DataLoader(self, batch_size=batch_size, num_workers=1, shuffle=True, collate_fn=collate)

  def __len__(self):
    return len(self.lines)

  def __getitem__(self, idx):
    line = self.lines[idx].replace("\n", "")
    line = unidecode.unidecode(line) # remove special characters
    x = "".join(c for c in line if c not in "AEIOUaeiou") # remove vowels from input
    y = line
    return (x,y)

def encode_string(s):
  for c in s:
    if c not in string.printable:
      print(s)
  return [string.printable.index(c) + 1 for c in s]

def decode_labels(l):
  return "".join([string.printable[c - 1] for c in l])

class Collate:
  def __call__(self, batch):
    """
    batch: list of tuples (input string, output string)
    Returns a minibatch of strings, encoded as labels and padded to have the same length.
    """
    x = []; y = []
    batch_size = len(batch)
    for index in range(batch_size):
      x_,y_ = batch[index]
      x.append(encode_string(x_))
      y.append(encode_string(y_))

    # pad all sequences to have same length
    T = [len(x_) for x_ in x]
    U = [len(y_) for y_ in y]
    T_max = max(T)
    U_max = max(U)
    for index in range(batch_size):
      x[index] += [NULL_INDEX] * (T_max - len(x[index]))
      x[index] = torch.tensor(x[index])
      y[index] += [NULL_INDEX] * (U_max - len(y[index]))
      y[index] = torch.tensor(y[index])

    # stack into single tensor
    x = torch.stack(x)
    y = torch.stack(y)
    T = torch.tensor(T)
    U = torch.tensor(U)

    return (x,y,T,U)

with open("war_and_peace.txt", "r") as f:
  lines = f.readlines()

end = round(0.9 * len(lines))
train_lines = lines[:end]
test_lines = lines[end:]
train_set = TextDataset(train_lines, batch_size=64) #8)
test_set = TextDataset(test_lines, batch_size=64) #8)
train_set.__getitem__(0)


class Trainer:
  def __init__(self, model, lr):
    self.model = model
    self.lr = lr
    self.optimizer = torch.optim.Adam(model.parameters(), lr=self.lr)
  
  def train(self, dataset, print_interval = 20):
    train_loss = 0
    num_samples = 0
    self.model.train()
    pbar = tqdm(dataset.loader)
    for idx, batch in enumerate(pbar):
      x,y,T,U = batch
      x = x.to(self.model.device); y = y.to(self.model.device)
      batch_size = len(x)
      num_samples += batch_size
      loss = self.model.compute_loss(x,y,T,U)
      self.optimizer.zero_grad()
      pbar.set_description("%.2f" % loss.item())
      loss.backward()
      self.optimizer.step()
      train_loss += loss.item() * batch_size
      if idx % print_interval == 0:
        self.model.eval()
        guesses = self.model.greedy_search(x,T)
        self.model.train()
        print("\n")
        for b in range(2):
          print("input:", decode_labels(x[b,:T[b]]))
          print("guess:", decode_labels(guesses[b]))
          print("truth:", decode_labels(y[b,:U[b]]))
          print("")
    train_loss /= num_samples
    return train_loss

  def test(self, dataset, print_interval=1):
    test_loss = 0
    num_samples = 0
    self.model.eval()
    pbar = tqdm(dataset.loader)
    for idx, batch in enumerate(pbar):
      x,y,T,U = batch
      x = x.to(self.model.device); y = y.to(self.model.device)
      batch_size = len(x)
      num_samples += batch_size
      loss = self.model.compute_loss(x,y,T,U)
      pbar.set_description("%.2f" % loss.item())
      test_loss += loss.item() * batch_size
      if idx % print_interval == 0:
        print("\n")
        print("input:", decode_labels(x[0,:T[0]]))
        print("guess:", decode_labels(self.model.greedy_search(x,T)[0]))
        print("truth:", decode_labels(y[0,:U[0]]))
        print("")
    test_loss /= num_samples
    return test_loss


# --- Training ------------------------------------------------------------------------

num_chars = len(string.printable) # 100
model = Transducer(num_inputs=num_chars+1, num_outputs=num_chars+1)
trainer = Trainer(model=model, lr=0.0003)

num_epochs = 1
train_losses=[]
test_losses=[]

for epoch in range(num_epochs):
    train_loss = trainer.train(train_set)
    test_loss = trainer.test(test_set)
    train_losses.append(train_loss)
    test_losses.append(test_loss)
    print("Epoch %d: train loss = %f, test loss = %f" % (epoch, train_loss, test_loss))

print(train_losses)
print(test_losses)

test_output = "Most people have little difficulty reading this sentence"
test_input = "".join(c for c in test_output if c not in "AEIOUaeiou")
print("input: " + test_input)
x = torch.tensor(encode_string(test_input)).unsqueeze(0).to(model.device)
y = torch.tensor(encode_string(test_output)).unsqueeze(0).to(model.device)
T = torch.tensor([x.shape[1]]).to(model.device)
U = torch.tensor([y.shape[1]]).to(model.device)
guess = model.greedy_search(x,T)[0]
print("truth: " + test_output)
print("guess: " + decode_labels(guess))
print("")
y_guess = torch.tensor(guess).unsqueeze(0).to(model.device)
U_guess = torch.tensor(len(guess)).unsqueeze(0).to(model.device)

print("NLL of truth: " + str(model.compute_loss(x, y, T, U)))
print("NLL of guess: " + str(model.compute_loss(x, y_guess, T, U_guess)))