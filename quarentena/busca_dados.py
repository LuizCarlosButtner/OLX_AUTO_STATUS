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

def extract_element_text(soup, strategy, selector, regex=None):
    """
    Componente genérico para extrair texto de elementos HTML.
    
    Args:
        soup (BeautifulSoup): O objeto soup parseado.
        strategy (str): A estratégia de busca ('id', 'css', 'tag').
        selector (str): O valor do seletor (ex: 'description-title', 'h1', '.classe').
        regex (str, optional): Padrão Regex para filtrar o texto encontrado.
        
    Returns:
        str ou None: O texto encontrado/filtrado ou None se falhar.
    """
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
    
    return None

def get_ad_details(driver, url):
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

        # --- USO DO COMPONENTE GENÉRICO ---

        # # 1. TÍTULO
        # # Tenta pegar pelo ID 'description-title'. Se retornar None, tenta pela TAG 'h1'.
        # # Se ambos falharem, usa o título da aba.
        # print("--> Extraindo Título...")
        # ad_data['titulo'] = (
        #     extract_element_text(soup, strategy='id', selector='description-title') or
        #     extract_element_text(soup, strategy='tag', selector='h1') or
        #     extract_element_text(soup, strategy='tag', selector='title')
        # )

        # 2. PREÇO
        # Tenta pegar pelo ID do container + Regex (para garantir que é dinheiro)
        print("--> Extraindo Preço...")
        regex_preco = r'R\$\s?[\d\.,]+'
        
        ad_data['preco'] = (
            # Estratégia A: Container ID seguro + Regex
            extract_element_text(soup, strategy='id', selector='price-box-container', regex=regex_preco) or
            # Estratégia B: Seletor CSS específico (exemplo do seletor limpo)
            extract_element_text(soup, strategy='css', selector='#price-box-container > div > div:nth-of-type(1) span', regex=regex_preco) or
            # Estratégia C: Fallback genérico (qualquer h2 com R$) - Busca manual ainda necessária para lógica complexa lambda
            "Preço não identificado"
        )
        
        # Exemplo extra: CÓDIGO DO ANÚNCIO (Geralmente fica num span com classe específica ou texto)
        # Vamos tentar pegar algo que tenha apenas números no final da URL ou num ID específico
        ad_data['codigo'] = extract_element_text(soup, strategy='css', selector='span[color="dark"]', regex=r'\d{9,}')

        print(f"--> Título: {ad_data['titulo']}")
        print(f"--> Preço: {ad_data['preco']}")

        return ad_data

    except Exception as e:
        print(f"ERRO CRÍTICO: {e}")
        return None
    finally:
        print("\nPasso 6: Fechando o navegador...")
        driver.quit()

if __name__ == "__main__":
    test_url = "https://rj.olx.com.br/rio-de-janeiro-e-regiao/autos-e-pecas/carros-vans-e-utilitarios/chevrolet-celta-life-ls-1-0-mpfi-8v-flexpower-3p-2008-1455189125"
    dados = get_ad_details(initialize_driver(), test_url)
    print("-" * 30)
    print(dados)