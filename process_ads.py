import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from app import get_ad_urls

def process_ads(urls):
    """
    Processes a list of OLX ad URLs to extract title and price using Selenium and BeautifulSoup.

    Args:
        urls (list): A list of OLX ad URLs.
    """
    if not urls:
        print("Nenhuma URL para processar.")
        return

    print(f"\nIniciando o processamento de {len(urls)} anúncios com Selenium...")

    # Configura o Selenium
    service = Service(ChromeDriverManager().install())
    options = Options()
    options.add_argument('--headless')  # Executa em modo headless (sem abrir janela do navegador)
    options.page_load_strategy = 'normal'
    driver = webdriver.Chrome(service=service, options=options)

    try:
        for i, url in enumerate(urls, 1):
            print(f"\n--- Processando Anúncio {i}/{len(urls)} ---")
            print(f"URL: {url}")
            time.sleep(10)  # Pausa antes de acessar a URL
            try:
                driver.get(url)
                # Aguarda um pouco para a página carregar completamente
                time.sleep(3)

                soup = BeautifulSoup(driver.page_source, 'html.parser')

                # Extrair o título
                title_element = soup.select_one("#description-title h1")
                title = title_element.get_text(strip=True) if title_element else "Título não encontrado"

                print(f"Título: {title}")

            except Exception as e:
                print(f"Ocorreu um erro inesperado ao processar a URL: {e}")

            # Pausa para não sobrecarregar o servidor
            time.sleep(2)
    finally:
        print("\nFechando o navegador...")
        driver.quit()

if __name__ == "__main__":
    # Busca as URLs usando a função do app.py com o arquivo de parâmetros desejado
    lista_de_urls = get_ad_urls(params_file='parametros2.json')
    
    # Processa as URLs obtidas
    process_ads(lista_de_urls)

    print("\n--- Processamento de todos os anúncios concluído. ---")
