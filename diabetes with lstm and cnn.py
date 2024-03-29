# -*- coding: utf-8 -*-
"""big.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1to7nprFdBwr5fkzlRJehUV0d4wrmBZLA
"""

from keras.preprocessing.text import Tokenizer
from keras.preprocessing.sequence import pad_sequences
from keras.models import Sequential
from keras.layers import Dense, Flatten, LSTM, Conv1D, MaxPooling1D, Dropout, Activation
from keras.layers.embeddings import Embedding

## Plot
import plotly.offline as py
import plotly.graph_objs as go
py.init_notebook_mode(connected=True)
import matplotlib as plt

# NLTK
import nltk
from nltk.corpus import stopwords 
from nltk.stem import SnowballStemmer
nltk.download('stopwords')
nltk.download('punkt')

# Other
import re
import string
import numpy as np
import pandas as pd
from sklearn.manifold import TSNE

from google.colab import files
uploaded = files.upload()

def clean_text(text):
    
    ## Remove puncuation
    text = text.translate(string.punctuation)
    
    ## Convert words to lower case and split them
    text = text.lower().split()
    
    ## Remove stop words
    stops = set(stopwords.words("english"))
    text = [w for w in text if not w in stops and len(w) >= 3]
    
    text = " ".join(text)

    # Clean the text
    text = re.sub(r"[^A-Za-z0-9^,!.\/'+-=]", " ", text)
    text = re.sub(r"what's", "what is ", text)
    text = re.sub(r"\'s", " ", text)
    text = re.sub(r"\'ve", " have ", text)
    text = re.sub(r"n't", " not ", text)
    text = re.sub(r"i'm", "i am ", text)
    text = re.sub(r"\'re", " are ", text)
    text = re.sub(r"\'d", " would ", text)
    text = re.sub(r"\'ll", " will ", text)
    text = re.sub(r",", " ", text)
    text = re.sub(r"\.", " ", text)
    text = re.sub(r"!", " ! ", text)
    text = re.sub(r"\/", " ", text)
    text = re.sub(r"\^", " ^ ", text)
    text = re.sub(r"\+", " + ", text)
    text = re.sub(r"\-", " - ", text)
    text = re.sub(r"\=", " = ", text)
    text = re.sub(r"'", " ", text)
    text = re.sub(r"(\d+)(k)", r"\g<1>000", text)
    text = re.sub(r":", " : ", text)
    text = re.sub(r" e g ", " eg ", text)
    text = re.sub(r" b g ", " bg ", text)
    text = re.sub(r" u s ", " american ", text)
    text = re.sub(r"\0s", "0", text)
    text = re.sub(r" 9 11 ", "911", text)
    text = re.sub(r"e - mail", "email", text)
    text = re.sub(r"j k", "jk", text)
    text = re.sub(r"\s{2,}", " ", text)
    
    text = text.split()
    stemmer = SnowballStemmer('english')
    stemmed_words = [stemmer.stem(word) for word in text]
    text = " ".join(stemmed_words)

    return text

df = pd.read_csv( 'data.csv', encoding = 'latin1')
df['text'] = df['text'].astype(str)
df['text'] = df['text'].map(lambda x: clean_text(x))
df.head()
df['tokenized'] = df.apply(lambda row : nltk.word_tokenize(row['text']), axis=1)
df.head()

vocabulary_size = 2000
tokenizer = Tokenizer(num_words= vocabulary_size)
tokenizer.fit_on_texts(df['text'])

sequences = tokenizer.texts_to_sequences(df['text'])
data= pad_sequences(sequences, maxlen=50)

# cross-validation 
from sklearn.model_selection import KFold
from sklearn.metrics import accuracy_score
from keras.wrappers.scikit_learn import KerasClassifier
from sklearn.model_selection import cross_val_score
from matplotlib import pyplot
from numpy import mean
from numpy import std
import numpy
from numpy import array
from numpy import argmax

np.random.seed(0)

def create_network():
    model_lstm = Sequential()
    model_lstm.add(Embedding(2000, 100, input_length=50))
    model_lstm.add(LSTM(100, dropout=0.2, recurrent_dropout=0.2))
    model_lstm.add(Dense(1, activation='sigmoid'))
    model_lstm.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])
    return model_lstm   

neural_network = KerasClassifier(build_fn=create_network, 
                                 epochs=10, 
                                 batch_size=100, 
                                 verbose=0)

scores = cross_val_score(neural_network, data, df['label'], cv=10)
scores

print("Accuracy: %0.2f (+/- %0.2f)" % (scores.mean(), scores.std() * 2))

def create_conv_model():
    model_conv = Sequential()
    model_conv.add(Embedding(vocabulary_size, 100, input_length=50))
    model_conv.add(Dropout(0.2))
    model_conv.add(Conv1D(64, 5, activation='relu'))
    model_conv.add(MaxPooling1D(pool_size=4))
    model_conv.add(LSTM(100))
    model_conv.add(Dense(1, activation='sigmoid'))
    model_conv.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])
    return model_conv


neural_network_conv = KerasClassifier(build_fn=create_conv_model, 
                                 epochs=10, 
                                 batch_size=100, 
                                 verbose=0)

scores_conv = cross_val_score(neural_network_conv, data, df['label'], cv=10)

scores_conv

print("Accuracy: %0.2f (+/- %0.2f)" % (scores.mean(), scores.std() * 2))

df_save = pd.DataFrame(data)
df_label = pd.DataFrame(np.array(df['label']))

result = pd.concat([df_save, df_label], axis = 1)

result.to_csv('train_dense_word_vectors.csv', index=False)

model_conv = Sequential()
    model_conv.add(Embedding(vocabulary_size, 100, input_length=50))
    model_conv.add(Dropout(0.2))
    model_conv.add(Conv1D(64, 5, activation='relu'))
    model_conv.add(MaxPooling1D(pool_size=4))
    model_conv.add(LSTM(100))
    model_conv.add(Dense(1, activation='sigmoid'))
    model_conv.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])

conv_embds = model_conv.layers[0].get_weights()[0]

lstm_embds = model_lstm.layers[0].get_weights()[0]

word_list = []
for word, i in tokenizer.word_index.items():
    word_list.append(word)

def configure_plotly_browser_state():
  import IPython
  display (IPython.core.display.HTML('''
  <script src="static/components/requirejs/require.js" ></script>
  <script>
    requirejs.config({
        path: {
            base: 'static/base',
            plotly: 'https://cdn.plot.ly/plotly-1.5.1.min.js?noext',
            },
            });
    </script>
    '''   ) )

def plot_words(data, start, stop, step):
    configure_plotly_browser_state()
    py.init_notebook_mode(connected=False)
    trace = go.Scatter(
        x = data[start:stop:step,0], 
        y = data[start:stop:step, 1],
        mode = 'markers',
        text= word_list[start:stop:step]
    )
    layout = dict(title= 't-SNE 1 vs t-SNE 2',
                  yaxis = dict(title='t-SNE 2'),
                  xaxis = dict(title='t-SNE 1'),
                  hovermode= 'closest')
    fig = dict(data = [trace], layout= layout)
    py.iplot(fig)

#!pip install plotly --upgrade

number_of_words = 2000
lstm_tsne_embds = TSNE(n_components=2).fit_transform(lstm_embds)

plot_words(lstm_tsne_embds, 0, number_of_words, 1)

conv_tsne_embds = TSNE(n_components=2).fit_transform(conv_embds)

plot_words(conv_tsne_embds, 0, number_of_words, 1)