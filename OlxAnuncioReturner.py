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

# NOTA: Removemos a importação de 'message_templates' daqui.

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
        """Extrai o ID do anúncio a partir da URL."""
        match = re.search(r'-(\d+)(?:\?|$)', url)
        if match:
            return match.group(1)
        
        match_vi = re.search(r'/vi/(\d+)', url)
        if match_vi:
            return match_vi.group(1)
            
        return "N/A"

    def _initialize_driver(self):
        """Configura e inicializa uma instância do WebDriver do Chrome."""
        chrome_options = Options()
        chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
        # chrome_options.add_argument("--headless") 
        service = Service(ChromeDriverManager().install())
        return webdriver.Chrome(service=service, options=chrome_options)

    def _extract_element_text(self, soup, strategy, selector, regex=None, is_list=False):
        """Componente genérico para extrair texto de elementos HTML."""
        if is_list:
            if strategy != 'css': return None
            elements = soup.select(selector)
            if not elements: return None
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
                    if match: return match.group(0)
                    return None 
                return text_content
        return []

    def _get_ad_details_internal(self, url):
        """Acessa a URL e extrai os dados brutos usando BeautifulSoup."""
        driver = self._initialize_driver()
        try:
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
        Acessa a URL, extrai os dados, limpa e RETORNA UM OBJETO (dicionário).
        """
        print(f">>> Iniciando extração de dados para: {url_alvo}")

        # 1. Busca os dados brutos
        dados = self._get_ad_details_internal(url_alvo)

        if not dados:
            return None

        # 2. Adiciona metadados
        dados['id_anuncio'] = self.extrair_id_anuncio(url_alvo)
        dados['url_anuncio'] = url_alvo

        # 3. Tratamento e limpeza do título/descrição
        titulo_completo = dados.get('titulo', '')
        
        if titulo_completo and '\n' in titulo_completo:
            partes = titulo_completo.split('\n', 1)
            dados['titulo_principal'] = partes[0].strip()
            dados['descricao_anuncio'] = partes[1].strip()
        else:
            dados['titulo_principal'] = str(titulo_completo).strip()
            dados['descricao_anuncio'] = ""

        # RETORNA O OBJETO PURO
        print(">>> Extração concluída com sucesso.")
        print(dados)
        return dados

if __name__ == "__main__":
    pass


    # # Codigo de teste abaixo

    # monitor = OlxAnuncioReturner()
    # url_teste = "https://rj.olx.com.br/rio-de-janeiro-e-regiao/autos-e-pecas/carros-vans-e-utilitarios/celta-life-flex-gnv-ano-2006-1466033457"
    # resultado = monitor.processar_url(url_teste)
    # print("DADOS EXTRAÍDOS:", resultado)
