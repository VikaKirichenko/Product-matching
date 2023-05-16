import pickle

import pandas as pd
import torch
import torch.nn.functional as F
from data_loaders import create_data_loader
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split
from train import BATCH_SIZE, MAX_LEN, tokenizer

from config import device
from processing.processing import simple_processing


def get_predictions(model, data_loader):
  model = model.eval()
  
  pairs = []
  predictions = []
  prediction_probs = []
  real_values = []

  with torch.no_grad():
    for d in data_loader:

      texts = d["pair"]
      input_ids = d["input_ids"].to(device)
      attention_mask = d["attention_mask"].to(device)
      targets = d["labels"].to(device)

      outputs = model(
        input_ids=input_ids,
        attention_mask=attention_mask
      )
      _, preds = torch.max(outputs, dim=1)

      probs = F.softmax(outputs, dim=1)

      pairs.extend(texts)
      predictions.extend(preds)
      prediction_probs.extend(probs)
      real_values.extend(targets)

  predictions = torch.stack(predictions).cpu()
  prediction_probs = torch.stack(prediction_probs).cpu()
  real_values = torch.stack(real_values).cpu()
  return pairs, predictions, prediction_probs, real_values

def load_model():
    with open('models/bert_model.pickle', 'rb') as f:
        return pickle.load(f)

if __name__ == '__main__':
    df = pd.read_csv('data/dataset_to_model.csv')
    X, y = simple_processing(df)
    X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=42)
    val_data_loader = create_data_loader(X_train,y_train, tokenizer, MAX_LEN, BATCH_SIZE)

    model = load_model()

    pairs, y_pred, y_pred_probs, y_test = get_predictions(model,val_data_loader)

    print(classification_report(y_test, y_pred))


    

