from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup
import time
import re

def initialize_driver():
    """Configura e inicializa uma instância do WebDriver do Chrome."""
    print("Passo 1: Inicializando o WebDriver do Chrome...")
    chrome_options = Options()
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    # chrome_options.add_argument("--headless") 
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

def extract_element_text(soup, strategy, selector, regex=None, is_list=False):
    """
    Componente genérico para extrair texto de elementos HTML.
    
    Args:
        soup (BeautifulSoup): O objeto soup parseado.
        strategy (str): A estratégia de busca ('id', 'css', 'tag').
        selector (str): O valor do seletor (ex: 'description-title', 'h1', '.classe').
        regex (str, optional): Padrão Regex para filtrar o texto encontrado.
        is_list (bool): Se True, busca todos os elementos e retorna uma lista de textos.
        
    Returns:
        str, list ou None: O texto encontrado, uma lista de textos ou None se falhar.
    """
    if is_list:
        if strategy != 'css':
            print("Aviso: 'is_list' só é suportado com a estratégia 'css'.")
            return None
        elements = soup.select(selector)
        if not elements:
            return None
        return [el.get_text(strip=True) for el in elements]
    else:
        element = None
        # 1. Encontra o elemento baseando-se na estratégia
        if strategy == 'id':
            element = soup.find(id=selector)
        elif strategy == 'css':
            element = soup.select_one(selector)
        elif strategy == 'tag':
            element = soup.find(selector)
        
        # 2. Se encontrou o elemento, extrai e processa o texto
        if element:
            text_content = element.get_text(separator=" ", strip=True)
            
            # 3. Se um regex foi passado, aplica ele sobre o texto
            if regex:
                match = re.search(regex, text_content)
                if match:
                    return match.group(0)
                return None # Elemento existe, mas regex não bateu
                
            return text_content
        
    return []

def get_ad_details(url, extraction_params):
    """
    Acessa a URL de um anúncio e extrai os dados com base nos parâmetros fornecidos.

    Args:
        url (str): A URL do anúncio a ser processado.
        extraction_params (dict): Um dicionário definindo o que extrair.
            Exemplo:
            {
                'titulo': [
                    {'strategy': 'id', 'selector': 'description-title'},
                    {'strategy': 'tag', 'selector': 'h1'}
                ],
                'preco': [
                    {'strategy': 'id', 'selector': 'price-box-container', 'regex': r'R\\$\\s?[\\d\\.,]+'},
                ]
            }

    Returns:
        dict: Um dicionário com os dados extraídos.
    """
    driver = initialize_driver()
    try:

        print(f"Passo 2: Acessando a URL: {url}")
        driver.get(url)
        
        print("Passo 3: Aguardando carregamento...")
        try:
            WebDriverWait(driver, 15).until(
                lambda d: d.find_element(By.ID, "description-title") or d.find_element(By.TAG_NAME, "h1")
            )
        except TimeoutException:
            print("Aviso: Timeout esperando elementos principais.")

        time.sleep(2) 

        print("Passo 4: Passando HTML para o BeautifulSoup...")
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        ad_data = {}

        # Itera sobre os campos definidos nos parâmetros (ex: 'titulo', 'preco')
        for field, strategies in extraction_params.items():
            print(f"--> Extraindo '{field}'...")
            found_value = None
            
            # Tenta cada estratégia de extração para o campo atual
            for strategy_config in strategies:
                value = extract_element_text(
                    soup,
                    strategy=strategy_config['strategy'],
                    selector=strategy_config['selector'],
                    regex=strategy_config.get('regex'),
                    is_list=strategy_config.get('is_list', False)
                )
                if value:
                    found_value = value
                    print(f"    [Sucesso] Valor encontrado para '{field}': {found_value}")
                    break # Para no primeiro sucesso
            
            # Armazena o valor encontrado ou um valor padrão
            ad_data[field] = found_value or f"{field.capitalize()} não identificado"

        return ad_data

    except Exception as e:
        print(f"ERRO CRÍTICO: {e}")
        return None
    finally:
        if 'driver' in locals() and driver:
            print("\nPasso final: Fechando o navegador...")
            driver.quit()

if __name__ == "__main__":
    # URL para teste direto do arquivo
    test_url = "https://rj.olx.com.br/rio-de-janeiro-e-regiao/autos-e-pecas/carros-vans-e-utilitarios/chevrolet-celta-life-ls-1-0-mpfi-8v-flexpower-3p-2008-1455189125"
    
    # Parâmetros de extração para o teste
    # test_params = {
    #     'titulo': [
    #         {'strategy': 'id', 'selector': 'description-title'},
    #         {'strategy': 'tag', 'selector': 'h1'}
    #     ],
    #     'preco': [
    #         {'strategy': 'id', 'selector': 'price-box-container', 'regex': r'R\$\s?[\d\.,]+'},
    #         {'strategy': 'css', 'selector': 'h2[aria-label^="Preço"]', 'regex': r'R\$\s?[\d\.,]+'},
    #     ],
    #     'codigo': [
    #         {'strategy': 'css', 'selector': 'span[color="dark"]', 'regex': r'\d{9,}'}
    #     ]
    # }

    # Executa a função
    # dados = get_ad_details(test_url, test_params)
    
  