import pip

def install(package):
    pip.main(['install', package])
try:
  import spacy
except ModuleNotFoundError:
    install("spacy==2.3.8")

import spacy
import string
from spacy.lang.pt.stop_words import STOP_WORDS


pontuacoes = string.punctuation
stop_words = STOP_WORDS

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

def classificação(previsao):
    if max(previsao['POSITIVO'],previsao['NEGATIVO']) == previsao['POSITIVO']:
        print ('Sentimento: Positivo')
    elif (max(previsao['POSITIVO'],previsao['NEGATIVO']) == previsao['NEGATIVO']):
        print ('Sentimento: Negativo')


modelo_carregado = spacy.load("modelo")
texto_positivo = 'estou feliz'
texto_positivo = preprocessamento(texto_positivo)
previsao = modelo_carregado(texto_positivo)

classificação(previsao.cats)