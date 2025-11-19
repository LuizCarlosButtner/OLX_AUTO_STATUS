import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup

def extrair_urls_com_selenium_e_bs():
    """
    Usa o Selenium para carregar a página e o BeautifulSoup para extrair as URLs.
    """
    # 1. URL de busca fixa
    url = "https://www.olx.com.br/celulares/estado-rj?ps=100&pe=2000&sf=1&f=p&elcd=1&elcd=3&elcd=4&elcd=2"
    print(f"URL de busca: {url}")

    # 2. Configurar o Selenium
    print("Passo 1: Configurando o Selenium e iniciando o WebDriver")
    service = Service(ChromeDriverManager().install())
    options = Options()
    # Define a estratégia de carregamento para 'none'. O script não vai esperar a página carregar por completo.
    options.page_load_strategy = 'none'
    # options.add_argument('--headless') # Descomente para rodar sem abrir a janela
    driver = webdriver.Chrome(service=service, options=options)

    urls_encontradas = []

    try:
        print("Passo 2: Acessando a URL com o navegador")
        driver.get(url)

        # Passo 3: Esperar o banner de cookie e clicar no botão "aceitar"
        print("Passo 3: Aguardando o botão de cookies para clicar...")
        try:
            # Espera até 15s para o botão ser clicável e então clica.
            cookie_button = WebDriverWait(driver, 15).until(
                EC.element_to_be_clickable((By.ID, "adopt-accept-all-button"))
            )
            cookie_button.click()
            print("Botão de aceitar cookies foi clicado.")
        except TimeoutException:
            print("Botão de cookies não apareceu ou não foi necessário clicar.")

        # Passo 4: Esperar o container principal da página carregar
        print("Passo 4: Aguardando o container principal ('main-content') carregar...")
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.ID, "main-content"))
        )
        print("Ok, container principal carregado!")

        # Passo 5: Agora, esperar os anúncios carregarem dentro do container
        print("Passo 5: Aguardando a lista de anúncios carregar...")
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "section[data-testid='ad-card']"))
        )
        print("Ok, anúncios carregados!")
        # 6. Entregar o HTML para o BeautifulSoup
        print("\nPasso 6: Analisando o HTML com BeautifulSoup")
        soup = BeautifulSoup(driver.page_source, 'html.parser')

        # 6. Encontrar todos os cards de anúncio (usando o seletor mais confiável)
        lista_anuncios = soup.find_all("section", attrs={"data-testid": "ad-card"})
        print(f"Encontrados {len(lista_anuncios)} anúncios na página.")

        # 7. Extrair a URL de cada anúncio
        for i, anuncio in enumerate(lista_anuncios):
            link_tag = anuncio.find('a', attrs={"data-testid": "ad-card-link"})
            if link_tag and link_tag.has_attr('href'):
                urls_encontradas.append(link_tag['href'])

    except TimeoutException:
        print("ERRO: A página demorou muito para carregar ou os anúncios não foram encontrados.")
    except Exception as e:
        print(f"Ocorreu um erro inesperado: {e}")
    finally:
        print("Passo 10: Finalizando e fechando o navegador.")
        driver.quit()

    return urls_encontradas

# --- Execução do Script ---
if __name__ == "__main__":
    urls = extrair_urls_com_selenium_e_bs()
    print("\n--- URLs Extraídas ---")
    for url_item in urls:
        print(url_item)
    print("----------------------")
    print(f"\nTotal de URLs extraídas: {len(urls)}")