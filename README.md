# Preditor algoritmos governamentais

Esse repositório possui os códigos usados para buscar e identificar páginas que tratam de algoritmos utilizados por entidades estatais no Brasil. São 4 scripts diferentes 

|Arquivo|Função|
|--|--|
|buscador.py|Utiliza a API de busca do google para obter os resultados dos termos desejados|
|scraper.py|Irá obter o resultado em texto de sites em HTML ou PDF a partir da lista de uma lista de URLS|
|extrator.py|Necessário para extrair o texto de arquivos em PDF|
|estimador.py|Contém o código do modelo utilizado|

O buscador irá buscar a chave da API no arquivo "login_config".
Os resultados serão salvos na pasta "dados".
