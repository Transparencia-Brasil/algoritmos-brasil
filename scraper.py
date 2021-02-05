# Importanto as bibliotecas necessárias
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import random
import numpy as np
import datetime
import random
import string
import extrator
from io import BytesIO
import sys
import certifi

class Scraper2():

    def __init__(self, entrada):
        """Essa classe irá analisar o arquivo tomado como argumento, transformá-lo em dataframe e adiciona uma
        coluna com o plain text de cada link. Dependendo do número de websites, pode consumir considerável
        parte da conexão à internet."""

        # Definindo variáveis globais
        tempo = time.time()
        timestamp = datetime.datetime.fromtimestamp(tempo).strftime('%d-%m_%H#%M#%S')
        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}

        print(f"Iniciando arquivo {entrada}")

        # Criar dataframe e inserir colunas de tipo e texto
        df = pd.read_csv(entrada, sep=";", header=None)
        df.insert(6, "texto", np.nan)
        df.insert(7, "tipo", "html")

        print("DF criado!")

        # Abrir sessão
        with requests.Session() as s:

            # Obter a URL de cada linha
            for index, row in df.iterrows():
                url = row[4]

                # Obter conteúdo
                try:
                    r = s.get(url, verify=certifi.where(), timeout=50, headers=headers)
                    content_type = r.headers.get('content-type')

                    # Processar informação com BeautifulSoup caso seja HTML
                    if 'text/html' in content_type:
                        soup = BeautifulSoup(r.content, "html.parser")
                        texto_extraido = soup.get_text()
                        df['texto'][index] = " ".join(texto_extraido.split())

                        print(f"Item {index} obtido corretamente")

                    # Utilizar extrator caso seja PDF
                    elif 'application/pdf' in content_type:
                        t = r.content

                        # Para evitar textos excessivamente longos, definiu-se um limite de tamanho de 8MB
                        if sys.getsizeof(t) < 8000000:

                            extracao = BytesIO(t)
                            texto_ext = extrator.Extrator(extracao)
                            texto_ext = " ".join(texto_ext.split())
                            df['texto'][index] = texto_ext

                        # Caso o tamanho seja excedido, a coluna de texto será preenchida com caracteres aleatórios
                        # para não comprometer o modelo preditivo
                        elif sys.getsizeof(t) > 8000000:
                            x = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
                            df['texto'][index] = f"#PDF_tamanho_excedido_{x}"

                        print(f"Item {index} (pdf) obtido corretamente")
                        df['tipo'][index] = 'pdf'

                    # Caso não seja HTML ou PDF, a coluna de texto também será preenchida com caracteres aleatórios
                    else:
                        x = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
                        df['texto'][index] = f"#Nao_e_HTML{x}"
                        print(f"Item {index} não é HTML: {url}")
                        df['tipo'][index] = content_type

                # Para evitar que o algoritmo seja bruscamente interrompido e os resultados perdidos, em caso de erro
                # será impressa uma mensagem.
                except:
                        x = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
                        df['texto'][index] = f"#Excecao{x}"
                        df['tipo'][index] = "Erro"
                        print(f"Item {index} deu exceção: {url}")

        df.to_csv(f"dados/{entrada}_textos_{timestamp}.csv")
        df.to_pickle("dados/{entrada}_textos_{timestamp}.pickle")