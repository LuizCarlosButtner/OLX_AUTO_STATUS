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


class OlxUrlReturner:
    def __init__(self, params_file='parametros.json'):
        """
        Inicializa a classe carregando os parâmetros de busca.
        """
        self.params_file = params_file
        self.parametros = self._load_params()

    def _load_params(self):
        """Carrega os parâmetros do arquivo JSON."""
        print(f"Passo 1: Carregando parâmetros do '{self.params_file}'")
        with open(self.params_file, 'r', encoding='utf-8') as f:
            return json.load(f)

    def _build_search_url(self):
        """Constrói a URL de busca com base nos parâmetros carregados."""
        print("Passo 2: Construindo a URL de busca")
        p = self.parametros
        
        marca = p.get('marca')
        modelo = p.get('modelo')
        estado = p.get('estado')
        
        valor = p.get('valor', {})
        valor_min = valor.get('minimo')
        valor_max = valor.get('maximo')
        
        gnv = p.get('gnv')
        anunciante_particular = p.get('anunciante_particular')
        
        kilometragem = p.get('kilometragem', {})
        km_start = kilometragem.get('start')
        km_end = kilometragem.get('end')
        
        ordenar_recentes = p.get('ordenar_recentes')
        
        ano = p.get('ano', {})
        ano_start = ano.get('start')
        ano_end = ano.get('end')
        
        url_base = p.get('url_base', "https://www.olx.com.br/autos-e-pecas/carros-vans-e-utilitarios")

        url = f"{url_base}/{marca}/{modelo}/estado-{estado}?ps={valor_min}&pe={valor_max}&{ordenar_recentes}&{anunciante_particular}&ms={km_start}&me={km_end}&hgnv={gnv}&rs={ano_start}&re={ano_end}"
        print(f"URL de busca: {url}")
        return url

    def _initialize_driver(self):
        """Configura e inicia o WebDriver."""
        print("Passo 3: Configurando o Selenium e iniciando o WebDriver")
        service = Service(ChromeDriverManager().install())
        options = Options()
        options.page_load_strategy = 'none'
        # options.add_argument('--headless')
        return webdriver.Chrome(service=service, options=options)

    def fetch_urls(self):
        """Executa o processo de busca e retorna a lista de URLs encontradas."""
        url = self._build_search_url()
        driver = self._initialize_driver()
        urls_encontradas = []

        try:
            print("Passo 4: Acessando a URL com o navegador")
            driver.get(url)

            print("Passo 5: Tentando lidar com o banner de cookies")
            try:
                print("Aguardando o botão de cookies se tornar clicável...")
                cookie_button = WebDriverWait(driver, 80).until(
                    EC.element_to_be_clickable((By.ID, "adopt-accept-all-button"))
                )
                cookie_button.click()
                print("Botão de aceitar cookies clicado.")
            except TimeoutException:
                print("Botão de cookies não apareceu ou não se tornou clicável em 30 segundos.")

            print("\nPasso 7: Tentando capturar a URLs anúncios com seletores dinâmicos...")
            try:
                WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, "main-content")))
                print("Container principal carregado. Iniciando a busca pelos links...")

                for i in range(1, 5):
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

def get_ad_urls(params_file='parametros.json'):
    """
    Função wrapper para manter compatibilidade com scripts existentes (ex: process_ads.py).
    """
    scraper = OlxUrlReturner(params_file)
    return scraper.fetch_urls()

if __name__ == "__main__":
    # Exemplo de uso direto da classe
    scraper = OlxUrlReturner(params_file='parametros2.json')
    lista_de_urls = scraper.fetch_urls()
    
    print("\n--- Resultado Final da Execução ---")
    if lista_de_urls:
        print(f"Total de {len(lista_de_urls)} URLs obtidas:")
        for url in lista_de_urls:
            print(url)
    else:
        print("Nenhuma URL foi obtida.")
        
        
        
        
        
        
# esse parte do pgm esta sem erros, aqui ela roda o programa usando os parametros do parametros2.json
# apartir desse resultado vamos pegar a lista de urls e processar cada uma delas para extrair titulo 
# e preco usando e enviar resumido para o terminal.pe