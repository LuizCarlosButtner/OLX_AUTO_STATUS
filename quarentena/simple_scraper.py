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

def extract_title_advanced(soup):
    """
    Extrai o título focando no ID específico (description-title), 
    com fallback para a tag H1 padrão.
    """
    print("   [Debug] Buscando título...")
    
    # ESTRATÉGIA 1 (Prioritária): Buscar pelo ID único '#description-title'
    # Isso é mais seguro que procurar apenas por 'h1', pois garante que estamos
    # pegando o título DA DESCRIÇÃO, e não o título do site ou outro h1 perdido.
    title_container = soup.find(id="description-title")
    
    if title_container:
        print("   [Debug] ID '#description-title' encontrado.")
        # get_text(strip=True) remove espaços extras e quebras de linha,
        # funcionando como uma "limpeza" similar ao Regex
        return title_container.get_text(strip=True)
    
    # ESTRATÉGIA 2 (Fallback): Se o ID não existir (mudança de layout), busca o primeiro h1
    print("   [Debug] ID não encontrado. Tentando fallback para tag <h1>...")
    h1_tag = soup.find("h1")
    if h1_tag:
        return h1_tag.get_text(strip=True)
        
    # ESTRATÉGIA 3 (Último recurso): Título da aba do navegador
    title_tag = soup.find("title")
    if title_tag:
        return title_tag.get_text(strip=True)

    return "Título não encontrado"

def extract_price_advanced(soup):
    """
    Tenta extrair o preço usando múltiplas estratégias, focando no container específico.
    """
    # ESTRATÉGIA 1: Busca pelo ID estável do container de preço
    price_container = soup.find(id="price-box-container")
    
    if price_container:
        print("   [Debug] Container '#price-box-container' encontrado.")
        
        # Opção A: Seletor CSS direto
        element_css = soup.select_one("#price-box-container > div > div:nth-of-type(1) span")
        if element_css and "R$" in element_css.get_text():
             return element_css.get_text(strip=True)

        # Opção B: Regex no texto do container (Mais robusta contra mudanças de tag)
        text_content = price_container.get_text(separator=" ", strip=True)
        match = re.search(r'R\$\s?[\d\.,]+', text_content)
        if match:
            return match.group(0)
            
    return None

def get_ad_details(driver, url):
    try:
        print(f"Passo 2: Acessando a URL: {url}")
        driver.get(url)
        
        print("Passo 3: Aguardando carregamento...")
        try:
            # Atualizamos o Wait para esperar especificamente pelo ID do título que queremos
            WebDriverWait(driver, 15).until(
                lambda d: d.find_element(By.ID, "description-title")
            )
        except TimeoutException:
            print("Aviso: Timeout esperando elementos principais.")

        time.sleep(2) 

        print("Passo 4: Passando HTML para o BeautifulSoup...")
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        ad_data = {}

        # --- TÍTULO (Atualizado com nova função) ---
        ad_data['titulo'] = extract_title_advanced(soup)

        # --- PREÇO ---
        print("--> Tentando extrair preço com estratégia avançada...")
        price = extract_price_advanced(soup)
        
        if price:
            ad_data['preco'] = price
        else:
            fallback = soup.find(lambda tag: tag.name in ['h2', 'h3'] and 'R$' in tag.text)
            ad_data['preco'] = fallback.get_text(strip=True) if fallback else "Preço não identificado"

        print(f"--> Título detectado: {ad_data['titulo']}")
        print(f"--> Preço detectado: {ad_data['preco']}")

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