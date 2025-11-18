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

    # Esperar a página carregar. Vamos aguardar até que a lista de anúncios esteja presente.
    # O ID 'ad-list' é comumente usado pela OLX para a lista de resultados.
    # NOVA ESTRATÉGIA: Esperar pelo container principal 'main-content' e depois verificar o que há dentro.
    print("Passo 6: Aguardando o conteúdo principal ('main-content') carregar")
    try:
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, "main-content")))
        print("Ok, container principal ('main-content') carregado!")
    except TimeoutException:
        print("ERRO CRÍTICO: O container 'main-content' não foi encontrado. A página pode ter mudado ou houve um erro de carregamento.")
        driver.quit()
        exit()

    # NOVA ESTRATÉGIA: Esperar diretamente pelo primeiro anúncio aparecer.
    # Se ele não aparecer, verificamos se é porque não há resultados.
    print("Passo 7: Aguardando o primeiro anúncio da lista carregar...")
    try:
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, "section[data-testid='ad-card']")))
        print("Ok, primeiro anúncio encontrado!")
    except TimeoutException:
        print("Nenhum anúncio encontrado para os filtros definidos ou a página não carregou. Encerrando a busca.")
        driver.quit()
        exit()

    # Agora que temos certeza que os anúncios carregaram, vamos pegá-los.
    lista_anuncios = driver.find_elements(By.CSS_SELECTOR, "section[data-testid='ad-card']")
    print(f"Encontrados {len(lista_anuncios)} anúncios na primeira página.")

    urls_anuncios = []
    print("\nPasso 7.1: Extraindo as URLs dos anúncios...")
    for anuncio in lista_anuncios:
        try:
            # Usando um seletor CSS mais específico para encontrar o link principal do anúncio.
            link_element = anuncio.find_element(By.CSS_SELECTOR, 'a[data-testid="ad-card-link"]')
            urls_anuncios.append(link_element.get_attribute('href'))
        except Exception as e:
            # Ignora se um dos cards não for um anúncio válido (ex: publicidade)
            pass
    
    print("\n--- URLs Encontradas ---")
    for url_item in urls_anuncios:
        print(url_item)
    print("--------------------------\n")

    time.sleep(5) # Pausa para você poder ver o navegador antes de fechar

finally:
    print("Passo 8: Finalizando o script e fechando o navegador")
    # Fechar o navegador
    driver.quit()
