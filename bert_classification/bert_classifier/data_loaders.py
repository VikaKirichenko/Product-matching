import numpy
from datasets import PairsDataset
from torch.utils.data import DataLoader


def create_data_loader(X,y, tokenizer, max_len, batch_size):
  ds = PairsDataset(
    pairs=numpy.asarray(X),
    labels=numpy.asarray(y),
    tokenizer=tokenizer,
    max_len=max_len
  )

  return DataLoader(
    ds,
    batch_size=batch_size,
    num_workers=4
  )