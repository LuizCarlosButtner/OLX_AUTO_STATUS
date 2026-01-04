# -*- coding: utf-8 -*-

# Importamos apenas a função principal de 'busca_dados2.py'
import json
import re
from busca_dados2 import get_ad_details
from message_templates import montar_mensagem_padrao

class OlxAnuncioReturner:
    def __init__(self, params_file='parametros_extracao.json'):
        """Inicializa a classe carregando os parâmetros de extração (info-base)."""
        self.parametros_extracao = self._load_extraction_params(params_file)

    def _load_extraction_params(self, file_path):
        """Carrega os parâmetros de extração de um arquivo JSON."""
        print(f">>> Carregando parâmetros de '{file_path}'...")
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def extrair_id_anuncio(self, url):
        """
        Extrai o ID do anúncio a partir da URL.
        """
        # Padrão 1: Sequência numérica no final do path (ex: ...-1466033457)
        match = re.search(r'-(\d+)(?:\?|$)', url)
        if match:
            return match.group(1)
        
        # Padrão 2: Link curto (ex: .../vi/1466033457)
        match_vi = re.search(r'/vi/(\d+)', url)
        if match_vi:
            return match_vi.group(1)
            
        return "N/A"

    def processar_url(self, url_alvo):
        """
        Recebe uma URL, realiza a raspagem e retorna a mensagem formatada.
        """
        print(f">>> Iniciando o processo de raspagem para: {url_alvo}")

        # Chama a função que extrai os detalhes usando os parâmetros carregados na inicialização
        dados_retornados = get_ad_details(url_alvo, self.parametros_extracao)

        if not dados_retornados:
            return "Falha: A função retornou None ou dados vazios."

        # Extrai o ID do anúncio usando a nova função
        id_anuncio = self.extrair_id_anuncio(url_alvo)

        # Adiciona a URL do anúncio ao dicionário para ser usada na mensagem
        dados_retornados['url_anuncio'] = url_alvo

        # --- TRATAMENTO DO TÍTULO E DESCRIÇÃO ---
        titulo_completo = dados_retornados.get('titulo', '')
        titulo_principal = titulo_completo
        descricao_anuncio = ""

        if '\n' in titulo_completo:
            partes = titulo_completo.split('\n', 1)
            titulo_principal = partes[0]
            if len(partes) > 1:
                descricao_anuncio = partes[1].strip()

        # Monta a mensagem formatada (Info solicitada)
        mensagem = montar_mensagem_padrao(dados_retornados, id_anuncio, titulo_principal, descricao_anuncio)
        
        return mensagem

def main():
    # Exemplo de uso
    monitor = OlxAnuncioReturner() # Carrega os parâmetros (info-base)
    
    url_teste = "https://rj.olx.com.br/rio-de-janeiro-e-regiao/autos-e-pecas/carros-vans-e-utilitarios/celta-life-flex-gnv-ano-2006-1466033457?rec=u&lis=vi_not_found_web%7C2020%7Cvi_not_found_web%7C0"
    
    resultado = monitor.processar_url(url_teste)
    print(resultado)

# Ponto de entrada do script
if __name__ == "__main__":
    main()