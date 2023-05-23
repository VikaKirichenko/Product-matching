import torch
from torch import nn
from torch.utils.data import Dataset
from transformers import BertModel

# from utilities import model_name
model_name = 'bert-base-multilingual-uncased'

class FeatureBuilder:

    def __init__(self, columns):
        self.columns = columns

    def get_X(self, dataset):
        X = '[CLS]'+ dataset[f'{self.columns[0]}_1']
        for i in range(1, len(self.columns)):
            X = X + ' ' + dataset[f'{self.columns[i]}_1']
        X = X + ' [SEP]'
        for i in range(len(self.columns)):
            X = X + ' ' + dataset[f'{self.columns[i]}_2']
        X = X + ' [SEP]'
        return X.to_list()

    def get_y(self, dataset):
        return dataset['match_type'].to_list()
    
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
  
class MatchClassifier(nn.Module):

  def __init__(self, n_classes):
    super(MatchClassifier, self).__init__()
    self.bert = BertModel.from_pretrained(model_name)
    self.drop = nn.Dropout(p=0.5)
    self.out = nn.Linear(self.bert.config.hidden_size, n_classes)
  
  def forward(self, input_ids, attention_mask):
    outputs = self.bert(
      input_ids=input_ids,
      attention_mask=attention_mask
    )
    output = self.drop(outputs["pooler_output"])
    return self.out(output)