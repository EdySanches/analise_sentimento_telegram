"""
Exemplo de um chatbot para Telegram

Código disponibilizado por Karan Batra
Alterações feitas por Hemerson Pistori (pistori@ucdb.br), principalmente a parte que trata de imagens.

Como executar:
python botTelegram.py COPIE_AQUI_SEU_TOKEN

Funcionalidade: repete as mensagens de texto que alguém envia para o seu chatbot e devolve duas estatísticas das imagens quando o usuário manda uma imagem.
"""
import pip

def install(package):
    pip.main(['install', package])

try:
  import PIL
except ModuleNotFoundError:
    install("Pillow==9.3.0")

try:
  import telegram
except ModuleNotFoundError:
    install("python-telegram-bot==13.14")

try:
    import spacy
except ModuleNotFoundError:
    install("spacy==2.3.8")

from PIL import Image, ImageStat
import os
import logging
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import spacy
import string
from spacy.lang.pt.stop_words import STOP_WORDS

# Lê o token como parâmetro na linha de comando
# Você pode também trocar diretamente aqui sys.argv[1] pelo
# seu token no telegram (ver README.md para saber como
# criar seu bot no telegram)
MEU_TOKEN = "5929662835:AAFOYgvqmVJvbC4JGli9myAtpfcCTHCA8qs"

# Pasta para imagens enviadas pelo usuário
pasta_imgs = './Telegram_Imagens_Recebidas/'

print('Carregando BOT usando o token ', MEU_TOKEN)

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

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
        return ('Sentimento: Positivo')
    elif (max(previsao['POSITIVO'],previsao['NEGATIVO']) == previsao['NEGATIVO']):
        return ('Sentimento: Negativo')

# Define algumas respostas padrão para alguns comandos

# Resposta para quando o usuário digita um texto.
# Apenas responde com o mesmo texto que o usuário entrou
def echo(update,context):
    texto_positivo = update.message.text #recebendo a mensagem do telegram
    texto_positivo = preprocessamento(texto_positivo)

    previsao = modelo_carregado(texto_positivo)

    resposta = classificação(previsao.cats)
    update.message.reply_text(resposta)


# Resposta para quando o usuário mandar uma imagem
def processa_imagem(update, context):
    # Entra na pasta onde ficarão as imagens
    os.chdir(pasta_imgs)

    # Pega o identificador da última imagem enviada
    identificador = update.message.photo[-1].file_id

    # Pega o arquivo
    arquivo = context.bot.get_file(identificador)

    # Baixa o arquivo
    nome_imagem = arquivo.download()
    print('Processando arquivo ', pasta_imgs + nome_imagem)

    # Abre o arquivo como sendo uma imagem usando o PIL
    imagem = Image.open(nome_imagem).convert('RGB')

    # Pega algumas estatísticas dos valores dos pixels da imagem
    stat = ImageStat.Stat(imagem)

    # Devolve para o usuário uma mensagem de texto com duas
    # das estatísticas calculadas
    update.message.reply_text(
        f'Estatísticas da Imagem: valor médio dos pixels no canais R, G e B = {stat.mean}, desvio padrão = {stat.stddev}')


# Resposta para o comando /start
def start(update, context):
    update.message.reply_text('Olá, já comecei, é só escrever qualquer coisa ou mandar uma imagem')


# Resposta para o comando /help
def help(update, context):
    update.message.reply_text('Eu só sei repetir o que me falam por enquanto')


# Salva as mensagens de erro
def error(update, context):
    logger.warning('Operação "%s" causou o erro "%s"', update, context.error)


modelo_carregado = spacy.load("modelo")


def main():
    # Cria o módulo que vai ficar lendo o que está sendo escrito
    # no seu chatbot e respondendo.
    # Troque TOKEN pelo token que o @botfather te passou (se
    # ainda não usou @botfather, leia novamente o README)
    updater = Updater(MEU_TOKEN, use_context=True)

    # Cria o submódulo que vai tratar cada mensagem recebida
    dp = updater.dispatcher

    # Define as funções que vão ser ativadas com /start e /help
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))

    # Define a função que vai tratar os textos
    dp.add_handler(MessageHandler(Filters.text, echo))
    #MessageHandler(echo())

    # Cria pasta para as imagens enviadas pelo usuário
    os.makedirs('./Telegram_Imagens_Recebidas', exist_ok=True)

    # Define a função que vai tratar as imagens
    # dp.add_handler(MessageHandler(Filters.photo, processa_imagem))

    # Define a função que vai tratar os erros
    dp.add_error_handler(error)

    # Inicia o chatbot
    updater.start_polling()

    # Roda o bot até que você dê um CTRL+C
    updater.idle()



if __name__ == '__main__':
    print('Bot respondendo, use CRTL+C para parar')
    main()

