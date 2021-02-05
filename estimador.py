"""Esse script possui o modelo preditivo usado para prever os resultados obtidos. A classe 'modelo' possui duas funções: treino e previsao.
Para treinar o modelo, utilize a primeira. Para prever novos resultados, utilize a segunda. O resultado será salvo no
arquivo "Output.csv" em csv encapsulado por aspas e separado por ";"."""

# Importanto bibliotecas
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
import pickle
import random
import string

class modelo():

    def __init__(self, entrada):

        # Gerar dataframe
        self.df = pd.read_csv(entrada)

        # Limpar NAs
        x = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
        self.df['texto'] = self.df['texto'].fillna(f"#Erro_estimador{x}")
        self.lista = list(self.df.texto)

    def treino(self):
        # Rodar modelo
        text_clf = Pipeline([('vect', CountVectorizer(ngram_range=(1,3), min_df=1, stop_words="english")),
        ('tfidf', TfidfTransformer()),
        ('clf', LogisticRegression(C=5))])
        text_clf.fit(self.df.texto, self.df.relevant)

        # Salvar modelo
        model_file = open("dados/Modelo.pickle", 'wb')
        pickle.dump(text_clf, model_file)

    def previsao(self):
        model_file = open("dados/Modelo.pickle", 'rb')
        text_clf = pickle.load(model_file)

        self.df['previsao'] = text_clf.predict_proba(self.lista)[:,1]

        self.df = self.df.drop('texto', axis=1)
        self.df.to_csv(f"dados/estimativas.csv")
