import json
import time
import random
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup

# Carregar os parâmetros do arquivo JSON
print("Passo 1: Carregando parâmetros do 'parametros.json'")
with open('parametros.json', 'r', encoding='utf-8') as f:
    parametros = json.load(f)

# Extrair informações da pesquisa
marca = parametros.get('marca')
modelo = parametros.get('modelo')
estado = parametros.get('estado')
valor = parametros.get('valor', {})
valor_min = valor.get('minimo')
valor_max = valor.get('maximo')
filtros = parametros.get('filtros', {})
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


# Construir a URL final respeitando a ordem /marca/modelo/estado
print("Passo 2: Construindo a URL de busca")
url = f"{url_base}/{marca}/{modelo}/estado-{estado}?ps={valor_min}&pe={valor_max}&{ordenar_recentes}&{anunciante_particular}&ms={km_start}&me={km_end}&hgnv={gnv}&rs={ano_start}&re={ano_end}"

print(f"URL de busca: {url}")

# Configurar o Selenium
print("Passo 3: Configurando o Selenium e iniciando o WebDriver")
service = Service(ChromeDriverManager().install())
options = Options()
# Define a estratégia de carregamento da página para 'none', não esperando o carregamento completo.
options.page_load_strategy = 'none'
# options.add_argument('--headless')  # Executar em modo headless (sem abrir a janela do navegador)
driver = webdriver.Chrome(service=service, options=options)

try:
    print("Passo 4: Acessando a URL com o navegador")
    # Acessar a URL
    driver.get(url)

    # Lidar com o banner de cookies
    print("Passo 5: Tentando lidar com o banner de cookies")
    try:
        # Espera dinâmica: aguarda até 30s para o botão ser clicável e então clica.
        # Esta é uma abordagem mais eficiente do que um time.sleep() fixo.
        print("Aguardando o botão de cookies se tornar clicável...")
        cookie_button = WebDriverWait(driver, 30).until(
            EC.element_to_be_clickable((By.ID, "adopt-accept-all-button"))
        )
        cookie_button.click()
        print("Botão de aceitar cookies clicado.")
    except TimeoutException: # Esta exceção é levantada pelo WebDriverWait se o tempo esgotar.
        print("Botão de cookies não apareceu ou não se tornou clicável em 30 segundos.")

    # Passo 7: Iterar 20 vezes mudando o seletor CSS
    print("\nPasso 7: Tentando capturar a URL de 20 anúncios com seletores dinâmicos...")
    try:
        # Espera o container principal carregar para garantir que a busca não seja prematura
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, "main-content")))
        print("Container principal carregado. Iniciando a busca pelos links...")

        urls_encontradas = []
        for i in range(1, 21):  # Loop de 1 a 20
            # Seletor CSS dinâmico com nth-child
            seletor_css = f"#main-content > div.AdListing_adListContainer__ALQla > section:nth-child({i}) > div.olx-adcard__content > div.olx-adcard__topbody > a"
            
            try:
                # Espera o link específico da iteração aparecer e o captura
                link_element = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, seletor_css)))
                url_encontrada = link_element.get_attribute('href')
                urls_encontradas.append(url_encontrada)
                print(f"URL {i}: {url_encontrada}")
            
            except TimeoutException:
                print(f"AVISO: O anúncio com nth-child({i}) não foi encontrado em 5 segundos. Pode não existir ou a página não carregou a tempo.")
                # Continua para a próxima iteração

        print("\n--- URLs Encontradas ---")
        for url_item in urls_encontradas:
            print(url_item)
        print(f"----------------------\nTotal de URLs capturadas: {len(urls_encontradas)}")

    except TimeoutException:
        print("\nERRO: O container principal 'main-content' não foi encontrado. A página pode não ter carregado corretamente.")
    except Exception as e:
        print(f"Ocorreu um erro inesperado durante a busca: {e}")

    time.sleep(5) # Pausa para você poder ver o navegador antes de fechar

finally:
    print("Passo 8: Finalizando o script e fechando o navegador")
    # Fechar o navegador
    driver.quit()
