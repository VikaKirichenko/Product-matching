import numpy as np
import pandas as pd
import torch
from data_loaders import create_data_loader
from model import MatchClassifier
from sklearn.model_selection import train_test_split
from torch import nn
from trainer import Trainer
from transformers import AdamW, BertTokenizer, get_linear_schedule_with_warmup

from config import device, model_name
from processing.processing import simple_processing

BATCH_SIZE = 16
MAX_LEN = 100
EPOCHS = 20

tokenizer = BertTokenizer.from_pretrained(model_name)
RANDOM_SEED = 42
np.random.seed(RANDOM_SEED)
torch.manual_seed(RANDOM_SEED)

if __name__ == '__main__':
    df = pd.read_csv('data/dataset_to_model.csv')

    X, y = simple_processing(df)

    X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=42)

    X_train, X_test, y_train, y_test = train_test_split(X_train, y_train, test_size=0.2, random_state=42)
    
    train_data_loader = create_data_loader(X_train,y_train, tokenizer, MAX_LEN, BATCH_SIZE)
    test_data_loader = create_data_loader(X_test,y_test, tokenizer, MAX_LEN, BATCH_SIZE)

    model = MatchClassifier(2)
    model = model.to(device)

    optimizer = AdamW(model.parameters(), lr=1e-5, correct_bias=False) # learning_rate 2e-5
    total_steps = len(train_data_loader) * EPOCHS

    scheduler = get_linear_schedule_with_warmup(
        optimizer,
        num_warmup_steps=0,
        num_training_steps=total_steps
        )

    loss_fn = nn.CrossEntropyLoss().to(device)

    trainer = Trainer(model,train_data_loader,test_data_loader,
                      loss_fn,optimizer,device,
                      len(X_train),scheduler,EPOCHS)
    
    trainer.train()

    











