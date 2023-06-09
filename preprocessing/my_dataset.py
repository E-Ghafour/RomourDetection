from torch.utils.data import Dataset
import torch
from torchtext.vocab import GloVe, FastText
import pickle
from transformers import BertTokenizer

class RumorDataset(Dataset):
    def __init__(self, tokenize_data_path, labels_path, pad_len, have_label = True, embedding_type = 'fasttext'):
        self.max_len = pad_len
        self.have_label = have_label
        self.word2vec_type = embedding_type
        with open(tokenize_data_path, 'rb') as ff:
            self.tokenize_data = pickle.load(ff)
        if(have_label):
            with open(labels_path, 'rb') as ff:
                self.labels = pickle.load(ff)
        if(embedding_type == 'fasttext'):
            self.vocab = FastText(language = 'en')
        else:
            self.vocab = GloVe(name = '6B', dim = 100)

    def __len__(self):
        return len(self.tokenize_data)

    def __getitem__(self, idx):
        tokens = self.tokenize_data[idx]

        if(self.have_label):
            labels = torch.tensor([self.labels[idx]], dtype = torch.float)

        tokens = [token if token in self.vocab.stoi else 'unk' for token in tokens]
        indices = [self.vocab.stoi[token] for token in tokens]

        padded_indices = indices[:self.max_len] + [0] * (self.max_len - len(indices[:self.max_len]))
        
        if(self.have_label):
            return torch.tensor(padded_indices), labels
        else: 
            return torch.tensor(padded_indices)
        

class RumourDatasetBert():
    def __init__(self, tokenize_data_path, labels_path, pad_len, have_label = True, bert_type = "bert-base-uncased"):
        self.tokenizer = BertTokenizer.from_pretrained(bert_type)
        self.max_len = pad_len
        self.have_label = have_label
        with open(tokenize_data_path, 'rb') as ff:
            self.tokenize_data = pickle.load(ff)
        if(have_label):
            with open(labels_path, 'rb') as ff:
                self.labels = pickle.load(ff)

    def __len__(self):
        return len(self.tokenize_data)

    def __getitem__(self, idx):
        tokens = self.tokenize_data[idx]
        if(self.have_label):
            labels = torch.tensor([self.labels[idx]], dtype = torch.float)

        padded_indices = self.tokenizer.encode_plus(tokens,
                                           add_special_tokens=True,
                                           padding='max_length',
                                           truncation=True,
                                           max_length=self.max_len,
                                           return_tensors='pt')
        if(self.have_label):
            return (padded_indices['input_ids'][0], padded_indices['attention_mask'][0]), labels
        else: 
            return (padded_indices['input_ids'][0], padded_indices['attention_mask'][0])
