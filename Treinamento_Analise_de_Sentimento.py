# Etapa 1: Importação e instalação das bibliotecas
import pip

def install(package):
    pip.main(['install', package])

try:
  import pandas
except ModuleNotFoundError:
    install("pandas==1.5.1")
try:
  import string
except ModuleNotFoundError:
    install("string")
try:
  import spacy
except ModuleNotFoundError:
    install("spacy==2.3.8")
try:
  import numpy    
except ModuleNotFoundError:
    install("numpy==1.23.0")
try:
  import matplotlib    
except ModuleNotFoundError:
    install("matplotlib==3.6.2")
try:
  import sklearn    
except ModuleNotFoundError:
    install("sklearn==0.0")


import pandas as pd
import random
import numpy as np
import matplotlib.pyplot as plt
from spacy.lang.pt.stop_words import STOP_WORDS
from sklearn.metrics import confusion_matrix, accuracy_score

"""# Etapa 2: Carregamento da base de dados"""

base_dados = pd.read_csv('Dataset.txt', encoding = 'utf-8')

"""# Etapa 3: Função para pré-processamento dos textos"""

pontuacoes = string.punctuation
stop_words = STOP_WORDS
len(stop_words)

pln = spacy.load("pt_core_news_sm")

def preprocessamento(texto):
  texto = texto.lower()
  documento = pln(texto)
  
  lista = []
  for token in documento:
    lista.append(token.lemma_)

  lista = [palavra for palavra in lista if palavra not in stop_words and palavra not in pontuacoes]
  lista = ' '.join([str(elemento) for elemento in lista if not elemento.isdigit()])

  return lista

"""# Etapa 4: Pré-processamento da base de dados
"""
# Limpeza dos textos
base_dados['texto'] = base_dados['texto'].apply(preprocessamento)

"""### Tratamento da classe"""

base_dados_final = []
for texto, emocao in zip(base_dados['texto'], base_dados['emocao']): #TODO
  if emocao == 'positivo':
    dic = ({'POSITIVO': True, 'NEGATIVO': False})
  elif emocao == 'negativo':
    dic = ({'POSITIVO': False, 'NEGATIVO': True})

  base_dados_final.append([texto, dic.copy()])

"""# Etapa 5: Criação do classificador"""

modelo = spacy.blank("pt")
categorias = modelo.create_pipe("textcat")
categorias.add_label("POSITIVO")
categorias.add_label("NEGATIVO")
modelo.add_pipe(categorias)
historico = []

modelo.begin_training()
for epoca in range(1000):
  random.shuffle(base_dados_final)
  losses = {}
  for batch in spacy.util.minibatch(base_dados_final, 15):#de 15 em 15 frases para treinamento da IA
    textos = [modelo(texto) for texto, entities in batch]
    annotations = [{'cats': entities} for texto, entities in batch]
    modelo.update(textos, annotations, losses=losses)
  if epoca % 100 == 0:
    print(losses)
    historico.append(losses)


historico_loss = []
for i in historico:
  historico_loss.append(i.get('textcat'))

historico_loss = np.array(historico_loss)

plt.plot(historico_loss)
plt.title('Progressão do erro')
plt.xlabel('Épocas')
plt.ylabel('Erro')

modelo.to_disk("modelo")

"""# Etapa 6: Testes com uma frase"""

modelo_carregado = spacy.load("modelo")

texto_positivo = 'eu adoro cor dos seus olhos'

texto_positivo = preprocessamento(texto_positivo)

previsao = modelo_carregado(texto_positivo)

texto_negativo = 'estou com medo dele'
previsao = modelo_carregado(preprocessamento(texto_negativo))

"""# Etapa 7: Avaliação do modelo

## Avaliação na base de treinamento
"""

previsoes = []
for texto in base_dados['texto']:
  previsao = modelo_carregado(texto)
  previsoes.append(previsao.cats)

previsoes_final = []

for previsao in previsoes: 
  if max(previsao['POSITIVO'],previsao['NEGATIVO']) == previsao['POSITIVO']:
    previsoes_final.append('positivo')
  elif max(previsao['POSITIVO'],previsao['NEGATIVO']) == previsao['NEGATIVO']:
    previsoes_final.append('negativo')

previsoes_final = np.array(previsoes_final)
print (previsoes_final)

respostas_reais = base_dados['emocao'].values
print (respostas_reais)
accuracy_score(respostas_reais, previsoes_final)

cm = confusion_matrix(respostas_reais, previsoes_final)
