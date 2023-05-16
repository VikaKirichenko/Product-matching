import pickle
from collections import defaultdict

import numpy as np
import torch
from torch import nn



class Trainer:
    def __init__(self, model,data_loader,val_data_loader,loss_fn, optimizer,device, n_examples, scheduler,epochs):
        self.model = model
        self.data_loader = data_loader
        self.val_data_loader = val_data_loader
        self.loss_fn = loss_fn
        self.optimizer = optimizer
        self.device = device
        self.n_examples = n_examples
        self.scheduler = scheduler
        self.epochs = epochs 

    def _train_epoch(self):
        
        self.model = self.model.train()

        losses = []
        correct_predictions = 0
        
        for d in self.data_loader:
            input_ids = d["input_ids"].to(self.device)
            attention_mask = d["attention_mask"].to(self.device)
            targets = d["labels"].to(self.device)

            outputs = self.model(
            input_ids=input_ids,
            attention_mask=attention_mask
            )

            _, preds = torch.max(outputs, dim=1)
            loss = self.loss_fn(outputs, targets)

            correct_predictions += torch.sum(preds == targets)
            losses.append(loss.item())

            loss.backward()
            nn.utils.clip_grad_norm_(self.model.parameters(), max_norm=1.0)
            self.optimizer.step()
            self.scheduler.step()
            self.optimizer.zero_grad()

        return correct_predictions.double() / self.n_examples, np.mean(losses)
    
    def train(self):
        history = defaultdict(list)
        best_accuracy = 0
        count = 0

        for epoch in range(self.epochs):

            print(f'Epoch {epoch + 1}/{self.epochs}')
            print('-' * 10)

            train_acc, train_loss = self.train_epoch()

            print(f'Train loss {train_loss} accuracy {train_acc}')

            test_acc, test_loss = self.eval_model()

            print(f'Test   loss {test_loss} accuracy {test_acc}')
            print()

            history['train_acc'].append(train_acc)
            history['train_loss'].append(train_loss)
            history['test_acc'].append(test_acc)
            history['test_loss'].append(test_loss)
            count += 1

            if test_acc > best_accuracy:
                torch.save(self.model.state_dict(), 'models/best_model_state.bin')
                best_accuracy = test_acc
                count = 0
            if count == 4:
                break
            # print(count)
        self.model = self.model.load_state_dict(torch.load('models/best_model_state.bin'))
        with open('models/bert_model.pickle', 'wb') as f:
            pickle.dump(self.model, f)

    def eval_model(self):
        model = self.model.eval()

        losses = []
        correct_predictions = 0

        with torch.no_grad():
            for d in self.val_data_loader:
                input_ids = d["input_ids"].to(self.device)
                attention_mask = d["attention_mask"].to(self.device)
                targets = d["labels"].to(self.device)

                outputs = model(
                    input_ids=input_ids,
                    attention_mask=attention_mask
                )
                _, preds = torch.max(outputs, dim=1)

                loss = self.loss_fn(outputs, targets)

                correct_predictions += torch.sum(preds == targets)
                losses.append(loss.item())

        return correct_predictions.double() / self.n_examples, np.mean(losses)






