# Copyright 2020 BULL SAS All rights reserved #
import torch
import torch.nn as nn
from typing import List

class LSTMLayer(nn.Module):
    """Deep learning model

    Args:
        num_classes (int): number of classes
        input_size (int, optional): size of the embedding vector. Defaults to 20.
        hidden_size (int, optional): size of the hidden layer. Defaults to 50.
        num_layers (int, optional):  number of layer. Defaults to 1.
        batch_size (int, optional): size of the batch. Defaults to 128.
        length_sentence (int, optional): size of the window. Defaults to 30.
        unidirectional (bool, optional): Unidirectional or BiDirectional LSTM. Defaults to True.
        test (bool, optional): Testing or training step. During the training step, the value of the attention layer is not returned for performance maximization. Defaults to False.
    """

    def __init__(self, num_classes : int, input_size=20, hidden_size=50, num_layers=1, batch_size=128, length_sentence=30, unidirectional=True, test=False):
        super(LSTMLayer, self).__init__()
        if torch.cuda.is_available():
            self.device = torch.device('cuda')
        else:
            self.device = torch.device('cpu')
        self.input_size = input_size
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        self.num_classes = num_classes
        self.batch_size = batch_size
        self.test = test

        self.fc0 = nn.Linear(hidden_size, num_classes).to(self.device)

        self.cell_LSTM = nn.LSTM(input_size, hidden_size, num_layers, batch_first=True, bidirectional=True).to(self.device)
        self.cell = LSTMCell(input_size, hidden_size).to(self.device)

        self.attention_weight = nn.Linear(2 * hidden_size, 1).to(self.device) # Bi
        # self.attention_weight = nn.Linear(hidden_size, 1).to(device) # Uni
        self.non_learnable_factor = nn.Parameter(torch.ones(1) * 3, requires_grad=False)
        self.sigmoid = nn.Sigmoid().to(self.device)
        self.length_sentence = length_sentence

    def forward(self, x):
        """Forward through the deep learning network

        Args:
            x : list of Tensors forward through the neural network

        Returns:
            torch.Tensor: if Test return the predictions and the values of the attention layer. If Learn, return only the predictions
        """
        x2, _ = self.cell_LSTM(x)
        logits = self.attention_weight(x2)
        attention = self.sigmoid(logits * self.non_learnable_factor.expand_as(logits))
        attention = attention.squeeze(2)
        hidden = torch.zeros(self.num_layers * 1, self.batch_size, self.hidden_size).to(self.device)
        x = x.transpose(0, 1)
        x_cell = []
        for i in range(self.length_sentence):
            hidden = self.cell(x[i], hidden, attention[:,i])
            x_cell.append(hidden)
        x_cell = torch.cat(x_cell, 0)
        x_cell = x_cell.transpose(0, 1)
        out = self.fc0(x_cell[:, -1, :])
        if self.test:
            return out, attention
        else:
            return out


class LSTMCell(nn.Module):
    """LSTM cell to be connected to the attention layer

    Args:
        input_size (int): size of input
        hidden_size (int): size of hidden layer
    """

    def __init__(self, input_size : int, hidden_size : int):
        super(LSTMCell, self).__init__()
        self.input_size = input_size
        self.hidden_size = hidden_size
        self.i2h = nn.Linear(input_size, hidden_size)
        self.h2h = nn.Linear(hidden_size, hidden_size)

        self.relu = nn.ReLU(True)
        self.ones = nn.Parameter(torch.ones(1), requires_grad=False)

    def forward(self, x, hidden, att):
        """Forward through the attention layer

        Args:
            x : input value
            hidden : hidden layer
            att : attention layer

        Returns:
            torch : return the hidden value of the layer
        """
        forget_gate = self.ones.expand_as(att) - att
        in_transform = self.relu(self.i2h(x) + self.h2h(hidden))
        next_h = att.unsqueeze(1).expand_as(in_transform) * in_transform \
                 + forget_gate.unsqueeze(1).expand_as(hidden) * hidden

        return next_h
