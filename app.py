import json
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

def get_ad_urls(params_file='parametros.json'):
    """
    Scrapes OLX ad URLs based on search parameters from a JSON file.

    Args:
        params_file (str): The path to the JSON file with search parameters.

    Returns:
        list: A list of scraped ad URLs.
    """
    print(f"Passo 1: Carregando parâmetros do '{params_file}'")
    with open(params_file, 'r', encoding='utf-8') as f:
        parametros = json.load(f)

    # Extrair informações da pesquisa
    marca = parametros.get('marca')
    modelo = parametros.get('modelo')
    estado = parametros.get('estado')
    valor = parametros.get('valor', {})
    valor_min = valor.get('minimo')
    valor_max = valor.get('maximo')
    gnv = parametros.get('gnv')
    anunciante_particular = parametros.get('anunciante_particular')
    kilometragem = parametros.get('kilometragem', {})
    km_start = kilometragem.get('start')
    km_end = kilometragem.get('end')
    ordenar_recentes = parametros.get('ordenar_recentes')
    ano = parametros.get('ano', {})
    ano_start = ano.get('start')
    ano_end = ano.get('end')
    url_base = parametros.get('url_base', "https://www.olx.com.br/autos-e-pecas/carros-vans-e-utilitarios")

    print("Passo 2: Construindo a URL de busca")
    url = f"{url_base}/{marca}/{modelo}/estado-{estado}?ps={valor_min}&pe={valor_max}&{ordenar_recentes}&{anunciante_particular}&ms={km_start}&me={km_end}&hgnv={gnv}&rs={ano_start}&re={ano_end}"
    print(f"URL de busca: {url}")

    print("Passo 3: Configurando o Selenium e iniciando o WebDriver")
    service = Service(ChromeDriverManager().install())
    options = Options()
    options.page_load_strategy = 'none'
    options.add_argument('--headless')
    driver = webdriver.Chrome(service=service, options=options)
    
    urls_encontradas = []
    try:
        print("Passo 4: Acessando a URL com o navegador")
        driver.get(url)

        print("Passo 5: Tentando lidar com o banner de cookies")
        try:
            print("Aguardando o botão de cookies se tornar clicável...")
            cookie_button = WebDriverWait(driver, 30).until(
                EC.element_to_be_clickable((By.ID, "adopt-accept-all-button"))
            )
            cookie_button.click()
            print("Botão de aceitar cookies clicado.")
        except TimeoutException:
            print("Botão de cookies não apareceu ou não se tornou clicável em 30 segundos.")

        print("\nPasso 7: Tentando capturar a URL de 20 anúncios com seletores dinâmicos...")
        try:
            WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, "main-content")))
            print("Container principal carregado. Iniciando a busca pelos links...")

            for i in range(1, 21):
                seletor_css = f"#main-content > div.AdListing_adListContainer__ALQla > section:nth-child({i}) > div.olx-adcard__content > div.olx-adcard__topbody > a"
                try:
                    link_element = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, seletor_css)))
                    url_encontrada = link_element.get_attribute('href')
                    urls_encontradas.append(url_encontrada)
                    print(f"URL {i}: {url_encontrada}")
                except TimeoutException:
                    print(f"AVISO: O anúncio com nth-child({i}) não foi encontrado em 5 segundos.")
        
        except TimeoutException:
            print("\nERRO: O container principal 'main-content' não foi encontrado.")
        except Exception as e:
            print(f"Ocorreu um erro inesperado durante a busca: {e}")

        time.sleep(5)

    finally:
        print("Passo 8: Finalizando o script e fechando o navegador")
        driver.quit()
        return urls_encontradas

if __name__ == "__main__":
    lista_de_urls = get_ad_urls(params_file='parametros2.json')
    print("\n--- Resultado Final da Execução ---")
    if lista_de_urls:
        print(f"Total de {len(lista_de_urls)} URLs obtidas:")
        for url in lista_de_urls:
            print(url)
    else:
        print("Nenhuma URL foi obtida.")