#!/usr/bin/env python3

import os
import argparse
import torch
from torch import nn
from torch.utils.data import DataLoader
from torch import optim
import torchvision
from torchvision.datasets import MNIST
from torchvision import transforms
import torchtrainer
from torchtrainer import SupervisedTrainer
from torchtrainer.meters import CategoricalAccuracy
from torchtrainer.meters.aggregators.batch import Average
from torchtrainer.meters.aggregators.scale import percentage
from torchtrainer.callbacks import ProgbarLogger as Logger, CSVLogger

class Network(nn.Module):
    def __init__(self):
        super(Network, self).__init__()
        self.filter = nn.Sequential(nn.Conv2d(in_channels=1, out_channels=32, kernel_size=5),
                                    nn.ReLU(inplace=True),
                                    nn.BatchNorm2d(32),
                                    nn.MaxPool2d(2),
                                    nn.Conv2d(in_channels=32, out_channels=64, kernel_size=3),
                                    nn.ReLU(inplace=True),
                                    nn.BatchNorm2d(64),
                                    nn.MaxPool2d(2))
        self.linear = nn.Sequential(nn.Linear(5*5*64, 500),
                                    nn.BatchNorm1d(500),
                                    nn.ReLU(inplace=True),
                                    nn.Linear(500, 10))

    def forward(self, x):
        bs = x.shape[0]
        return self.linear(self.filter(x).view(bs, -1))

def parse_args():
    parser = argparse.ArgumentParser(description='MNIST supervised trainer')
    parser.add_argument('--epochs', type=int, help='Number of epochs to train', default=5)
    parser.add_argument('--batch_size', type=int, help='Training batch size', default=100)
    parser.add_argument('--val_batch_size', type=int, help='Batch size', default=100)
    parser.add_argument('--logging_frecuency', type=int, help='Logging frecuency in batchs', default=10)
    parser.add_argument('--data', type=str, help="Path to data folder", default=os.path.join('data', 'mnist'))
    parser.add_argument('--lr', type=float, help="Learning rate", default=1e-2)
    return parser.parse_args()

def main():
    args = parse_args()
    train_ds = MNIST(root=args.data,
                     download=True,
                     train=True,
                     transform=transforms.Compose([transforms.ToTensor()]))
    test_ds = MNIST(root=args.data,
                    download=False,
                    train=False,
                    transform=transforms.Compose([transforms.ToTensor()]))
    train_dl = DataLoader(train_ds, batch_size=args.batch_size)
    test_dl = DataLoader(test_ds, batch_size=args.val_batch_size)

    model = Network()
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.SGD(model.parameters(), lr=args.lr)

    trainer = SupervisedTrainer(model=model,
                                optimizer=optimizer,
                                criterion=criterion,
                                logging_frecuency=args.logging_frecuency,
                                acc_meter=CategoricalAccuracy(aggregator=percentage(Average())),
                                callbacks=[Logger(),
                                           CSVLogger(output='training_stats.csv')
                                          ])
    trainer.train(dataloader=train_dl,
                  valid_dataloader=test_dl,
                  epochs=args.epochs)

if __name__ == '__main__':
    main()
