"""Esse script é utilizado para obter os links de uma busca no google com base em uma lista de palavras, retornando link, título e
descrição. Há a possibilidade de especificar uma expressão constante como por exemplo buscar dentro de uma URL específica. O resultado será salvo no
em um arquivo com timestamp da hora em que ele foi criado. O formato consiste em um  csv encapsulado por aspas e separado por ";". A classe 'Busca_API'
necessita de uma chave da API de busca.

Uso recomendado:
lista = ['site:*.leg.br', 'site:*.jus.br', 'site:*.mp.br']

for i in lista:
    Busca_api('dados/termos.csv', i, paginas=10).buscador()"""

import colorama
colorama.init(autoreset=True)

# Importanto as bibliotecas necessárias
import pandas as pd
import time
import datetime

# API
from googleapiclient import discovery

# Necessário um arquivo com a chave da API e a ID do CSE de busca do google
# from login_config import my_api_key, my_cse_id

tempo = time.time()
timestamp = datetime.datetime.fromtimestamp(tempo).strftime('%d-%m_%H#%M#%S')

class Busca_api():

    def __init__(self, entrada, expressao=None, paginas=None, pag_inicial=None):
        """Essa clase permite que se obtenha resultados de uma busca no google.

            Args:
            entrada (str): arquivo .txt com termos a serem pesquisados
            expressao (str): expressão a ser adicionada em cada pesquisa. Constará no
                nome do arquivo gerado.
            paginas (int): número de páginas a serem buscadas, máximo de 10
            pag_inicial (int): página a partir da qual serão extraídos os resultados"""

        # Definimos a função inicializadora para ler o arquivo onde cada linha será um termo
        # Cada termo será apensado a uma lista acessível por todas as funções da classe

        self.termos = []
        self.resultados = []
        self.expressao = expressao
        self.paginas = paginas
        self.total = []
        self.limite = 0

        # Correção da página inicial necessária para enviar para a API
        if pag_inicial:
            self.pag_inicial = pag_inicial - 1
        else:
            self.pag_inicial = 0

        #Lendo o arquivo com os termos
        with open(entrada, newline='', encoding='UTF-8') as f:
            termos0 = f.read().splitlines()

        # Se o usuário tiver indicado uma expressão constante, ela será adicionada a cada termo na lista
        if expressao:
            for i in termos0:
                self.termos.append(f"{i} {expressao}")

        # Do contrário, a lista global será a mesma de entrada
        else:
            self.termos = termos0

    # Definimos a função de busca e coleta dos resultados
    def buscador(self):
        """Função para executar a busca pela API. Não é necessário nenhum parâmetro de entrada"""

        # Carregar valores da API e iniciar contador
        service = discovery.build("customsearch", "v1", developerKey=my_api_key)
        id_ini = 1
        n_termo = 1

        # Usando a função try para, em caso de erro, salvar o resultado provisório em um csv.
        # Em teoria, erros não deveriam ser possíveis, é uma medida de precaução.
        try:

            for i in self.termos:  # Para cada termo na lista, iremos rodar o seguinte código
                self.limite = 100 # Limitando o número máximo de resultados possíveis

                for pag in range(self.paginas):
                    id_primeiro = pag
                    pag = pag + self.pag_inicial # Corrigindo a subtração anterior
                    time.sleep(1) # Pausa para evitar sobrecarga de pedidos na API
                    n_item = 1
                    id_ini = (1**pag)+(pag*10) # O número do item da busca a ser retornado

                    k = len(str(self.expressao)) # Limpando termo buscado para inserir na tabela
                    termo_limpo = i[:-(k+1)]

                    res = service.cse().list(q=i, cx=my_cse_id, start=id_ini).execute() # Fazendo o pedido na API

                    # Obtendo informações do resultado da busca
                    if id_primeiro == 0:
                        cache = []
                        cache.append(termo_limpo)
                        cache.append(self.expressao)
                        total = int(res['searchInformation']['totalResults'])
                        cache.append(total)
                        self.total.append(cache)

                        self.limite = total

                    # Se não houver resultado, corta o loop
                    if 'items' not in res:
                        break

                    print(id_ini)
                    todos = res['items']
                    cache = []

                    # Loop para cada um dos itens encontrados na página
                    for g in todos:

                        if 'title' not in g:
                            title = "Sem título"
                        else:
                            title = g['title']
                            title = " ".join(title.split())
                        link = g['link']
                        if 'snippet' in g:
                            desc = g['snippet']
                            desc = " ".join(desc.split()) # Limpando a descrição de quebras de linhas
                        else:
                            desc = ""

                        # Criando lista com os resultados
                        cache = []
                        cache.append(termo_limpo)
                        cache.append(self.expressao)
                        cache.append(title)
                        cache.append(link)
                        cache.append(desc)
                        self.resultados.append(cache) # Adicionando lista na lista de resultados

                        num_item = n_item+(id_ini-1)

                        print(f"{colorama.Fore.GREEN}Termo {n_termo}.{num_item} coletado")

                        n_item = n_item + 1

                n_termo = n_termo +1

        except:
            print(f"{colorama.Fore.RED}ERRO!! {n_termo}.{num_item}")

        # Salvando tudo em um df e exportando para dois csvs: um com as urls e outro com o sumário
        finally:
            df = pd.DataFrame(self.resultados)
            df = df.drop_duplicates(subset=3)
            df2 = pd.DataFrame(self.total)

            nome = self.expressao[7:]

            df.to_csv(f"dados/{nome}_{timestamp}.csv", sep=';', header=None)
            df2.to_csv(f"dados/{nome}_resultados_{timestamp}.csv", sep=';', header=None)

