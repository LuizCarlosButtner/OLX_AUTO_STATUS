# -*- coding: utf-8 -*-

import json
import re
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
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

    def _initialize_driver(self):
        """Configura e inicializa uma instância do WebDriver do Chrome."""
        # print("   [Debug] Inicializando o WebDriver do Chrome...")
        chrome_options = Options()
        chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
        # chrome_options.add_argument("--headless") 
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        return driver

    def _extract_element_text(self, soup, strategy, selector, regex=None, is_list=False):
        """Componente genérico para extrair texto de elementos HTML."""
        if is_list:
            if strategy != 'css':
                return None
            elements = soup.select(selector)
            if not elements:
                return None
            return [el.get_text(strip=True) for el in elements]
        else:
            element = None
            if strategy == 'id':
                element = soup.find(id=selector)
            elif strategy == 'css':
                element = soup.select_one(selector)
            elif strategy == 'tag':
                element = soup.find(selector)
            
            if element:
                text_content = element.get_text(separator=" ", strip=True)
                if regex:
                    match = re.search(regex, text_content)
                    if match:
                        return match.group(0)
                    return None 
                return text_content
        return []

    def _get_ad_details_internal(self, url):
        """
        Acessa a URL e extrai os dados (Lógica trazida do busca_dados2).
        """
        driver = self._initialize_driver()
        try:
            # print(f"   [Debug] Acessando: {url}")
            driver.get(url)
            
            try:
                WebDriverWait(driver, 15).until(
                    lambda d: d.find_element(By.ID, "description-title") or d.find_element(By.TAG_NAME, "h1")
                )
            except TimeoutException:
                print("   [Aviso] Timeout esperando elementos principais.")

            time.sleep(2) 

            soup = BeautifulSoup(driver.page_source, 'html.parser')
            ad_data = {}

            # Itera sobre os campos definidos nos parâmetros
            for field, strategies in self.parametros_extracao.items():
                found_value = None
                for strategy_config in strategies:
                    value = self._extract_element_text(
                        soup,
                        strategy=strategy_config['strategy'],
                        selector=strategy_config['selector'],
                        regex=strategy_config.get('regex'),
                        is_list=strategy_config.get('is_list', False)
                    )
                    if value:
                        found_value = value
                        break 
                
                ad_data[field] = found_value or f"{field.capitalize()} não identificado"

            return ad_data

        except Exception as e:
            print(f"ERRO CRÍTICO NA EXTRAÇÃO: {e}")
            return None
        finally:
            if driver:
                driver.quit()

    def processar_url(self, url_alvo):
        """
        Recebe uma URL, realiza a raspagem e retorna a mensagem formatada.
        """
        print(f">>> Iniciando o processo de raspagem para: {url_alvo}")

        # Chama o método interno da classe agora
        dados_retornados = self._get_ad_details_internal(url_alvo)

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