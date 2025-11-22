# -*- coding: utf-8 -*-

# Importamos apenas a função principal de 'busca_dados2.py'
from busca_dados2 import get_ad_details

def main():
    # 1. Defina a URL que você quer buscar
    url_alvo = "https://rj.olx.com.br/rio-de-janeiro-e-regiao/autos-e-pecas/carros-vans-e-utilitarios/fiat-palio-2007-leia-o-anuncio-1454664719?rec=a&lis=vi_web%7C2020%7Cwho_saw_also_saw%7C0"
    
    # 2. Defina os parâmetros de extração
    # Cada chave ('titulo', 'preco') tem uma lista de tentativas (dicionários).
    # A extração para em na primeira tentativa bem-sucedida para cada chave.
    parametros_extracao = {
        # 'titulo': [
        # #     # Estratégia Melhorada: Usar seletor CSS para ser mais específico.
        # #     # Isso busca por um h1 DENTRO do elemento com id 'description-title'.
        # #     # É mais robusto se o site adicionar outros textos dentro do mesmo container.
        # #     {'strategy': 'css', 'selector': '#description-title h1'},
        # #     # Fallback (Plano B): Se o seletor acima falhar, tenta o original.
        #     {'strategy': 'id', 'selector': 'description-title'}
        # ],

        # 'preco': [

        #     {'strategy': 'css', 'selector': '#price-box-container', 'regex': r'R\$\s?[\d\.,]+'},
        # ],

        # 'preco_medio': [
        #     # ESTRATÉGIA 1: Container de Borda (Mais provável)
        #     # O preço médio costuma ficar numa caixa destacada com a classe 'olx-container--outlined'.
        #     # Buscamos por qualquer 'span' lá dentro que pareça um preço.
        #     {'strategy': 'css', 'selector': 'div.olx-d-flex.olx-ai-center span', 'regex': r'R\$\s?[\d\.,]+'}        ],
        # 'preco': [
        #     {'strategy': 'id', 'selector': 'price-box-container', 'regex': r'R\$\s?[\d\.,]+'},
        #     {'strategy': 'css', 'selector': 'h2[aria-label^="Preço"]', 'regex': r'R\$\s?[\d\.,]+'},
        # ]

# 'fipe': [
#             # ESTRATÉGIA: Caminho Hierárquico Completo (Baseado no seu seletor)
#             # Tradução: 
#             # 1. Começa em #adview-teste
#             # 2. Desce até achar a caixa com borda (olx-container--outlined)
#             # 3. Entra na estrutura interna e pega OBRIGATORIAMENTE o 2º filho (nth-child(2))
#             # 4. Pega o span lá dentro.
#             {
#                 'strategy': 'css', 
#                 'selector': '#adview-teste div.olx-container--outlined > div > div > div:nth-child(2) span', 
#                 'regex': r'R\$\s?[\d\.,]+'
#             },
            
#             # FALLBACK: Caso a estrutura mude levemente, tenta pegar pelo atributo de link
#             # (Muitas vezes o preço da Fipe é um link para a tabela).
#             # {
#             #     'strategy': 'css', 
#             #     'selector': 'a[href*="fipe"]', 
#             #     'regex': r'R\$\s?[\d\.,]+'
#             # }
#         ],

    # 'vendedor_desde': [
    #         # ESTRATÉGIA: Hierarquia Rigorosa (Seletor mantido, Regex ajustado)
    #         {
    #             'strategy': 'css', 
    #             # Mantemos o seletor que funcionou para você
    #             'selector': '#adview-teste > div > div > div > div > div:nth-child(3) > div:nth-child(1) span',
    #             # NOVO REGEX: Captura formato "18/11 às 13:16"
    #             'regex': r'\d{2}/\d{2}\sàs\s\d{2}:\d{2}' 
    #         },
            
    #         # FALLBACK: Procura esse padrão de data em qualquer lugar do painel
    #         {
    #             'strategy': 'css',
    #             'selector': '#adview-teste span',
    #             'regex': r'\d{2}/\d{2}\sàs\s\d{2}:\d{2}'
    #         }
    #     ],

        # 'km': [
        #         # ESTRATÉGIA: Posição Fixa (6º item) + Filtro numérico estrito
        #         {
        #             'strategy': 'css', 
        #             'selector': '#details > div > div > div:nth-child(6) span:nth-of-type(2)',                # Regex: Busca de 2 a 9 dígitos consecutivos.
        #             'regex': r'\d{2,9}'            }
        #     ],
    
        # 'ano': [
        #     # ESTRATÉGIA: Posição Fixa (Provavelmente o 5º item, logo antes da KM)
        #     {
        #         'strategy': 'css', 
        #         # Mudamos para nth-child(5) e pegamos o segundo span (o valor)
        #         'selector': '#details > div > div > div:nth-child(5) > div > a', 
        #         # Regex: Procura exatamente 4 dígitos (Ex: 2008)
        #         'regex': r'\d{4}' 
        #     }
        # ],

        'opcionais': [
            # ESTRATÉGIA: Iterar sobre os itens da grade
            # O seletor busca a div container específica (ad__sc-1jr3zuf-0)
            # e pega TODOS os spans que estão dentro das divs filhas.
            {
                'strategy': 'css',
                # Tradução: Dentro da grid de opcionais, entre nas divs e pegue os spans
                'selector': 'div.ad__sc-1jr3zuf-0 > div > div span',
                # Flag personalizada para indicar que queremos múltiplos resultados
                'is_list': True 
            }
        ]

    }

    print(">>> Iniciando o processo de raspagem...")

    # 3. Chama a função que extrai os detalhes.
    # Ela agora gerencia o navegador internamente.
    dados_retornados = get_ad_details(url_alvo, parametros_extracao)

    # 4. Imprime os resultados formatados
    print("RELATÓRIO DE DADOS EXTRAÍDOS")

    # Tratamento especial para Lista de Opcionais
    opcionais = dados_retornados.get('opcionais')
    if isinstance(opcionais, list):
        # Se for uma lista, junta tudo com vírgulas
        opcionais_texto = ", ".join(opcionais)
    else:
        # Se for texto ou None, mantém como está
        opcionais_texto = opcionais

    print(f"OPCIONAIS:         {opcionais_texto}")
    
    if dados_retornados:
        # Verifica se 'titulo' foi um dos parâmetros de extração solicitados
        if 'titulo' in parametros_extracao:
            titulo_completo = dados_retornados.get('titulo')
            texto1 = ""
            texto2 = ""

            if titulo_completo and '\n' in titulo_completo:
                # Divide o título no primeiro '\n' e limita a 2 partes
                partes = titulo_completo.split('\n', 1)
                texto1 = partes[0]
                texto2 = partes[1].strip() if len(partes) > 1 else ""
            else:
                texto1 = titulo_completo or "N/A" # Garante que não seja None

        print(dados_retornados)
    else:
        print("Falha: A função retornou None ou dados vazios.")

# Ponto de entrada do script
if __name__ == "__main__":
    main()