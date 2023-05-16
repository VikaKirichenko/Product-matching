import torch

model_name = 'bert-base-multilingual-uncased'

device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

