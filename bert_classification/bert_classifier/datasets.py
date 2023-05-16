import torch
from torch.utils.data import Dataset


class PairsDataset(Dataset):

  def __init__(self, pairs, labels, tokenizer, max_len):
    self.pairs = pairs
    self.labels = labels
    self.tokenizer = tokenizer
    self.max_len = max_len
  
  def __len__(self):
    return len(self.pairs)
  
  def __getitem__(self, item):
    pair = str(self.pairs[item])
    label = self.labels[item]

    encoding = self.tokenizer.encode_plus(
      pair,
      add_special_tokens=False,
      max_length=self.max_len,
      return_token_type_ids=False,
      pad_to_max_length=True,
      truncation=True,
      return_attention_mask=True,
      return_tensors='pt',
    )

    return {
      'pair': pair,
      'input_ids': encoding['input_ids'].flatten(),
      'attention_mask': encoding['attention_mask'].flatten(),
      'labels': torch.tensor(label, dtype=torch.long)
    }