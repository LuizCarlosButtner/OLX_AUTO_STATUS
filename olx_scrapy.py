import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

# ----------------------------------------------------
# 1. Configuração e Seletores de Teste
# ----------------------------------------------------
URL_PESQUISA = "https://www.olx.com.br/autos-e-pecas/carros-vans-e-utilitarios/gm-chevrolet/celta/estado-rj?q=celta&sf=1&f=p&hgnv=0"

# Seletores CSS Absolutos para o PRIMEIRO anúncio (apenas para teste!)
SELETOR_TITULO = "#main-content > div.AdListing_adListContainer__ALQla.AdListing_gridLayout__DTjHC > section:nth-child(1) > div.olx-adcard__content > div.olx-adcard__topbody > a > h2"
SELETOR_PRECO = "#main-content > div.AdListing_adListContainer__ALQla.AdListing_gridLayout__DTjHC > section:nth-child(1) > div.olx-adcard__content > div.olx-adcard__mediumbody > h3"

def iniciar_driver():
    """Inicializa o Chrome usando o webdriver-manager."""
    print("🚀 A inicializar o navegador Chrome...")
    try:
        servico = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=servico)
        driver.maximize_window()
        return driver
    except Exception as e:
        print(f"❌ Erro ao inicializar o driver: {e}")
        return None

# ----------------------------------------------------
# 2. Função de Scraping de Teste
# ----------------------------------------------------
def testar_extracao_simples(driver, url):
    """
    Carrega a página e extrai Título e Preço de APENAS UM anúncio 
    usando os seletores CSS absolutos fornecidos.
    """
    print(f"🌍 A carregar a página: {url}")
    driver.get(url)
    
    # Damos um tempo para o JavaScript carregar
    time.sleep(7) # Aumentamos o tempo de espera para maior segurança
    print("⏳ Tempo de espera concluído. A procurar o primeiro anúncio...")

    html_carregado = driver.page_source
    sopa = BeautifulSoup(html_carregado, 'html.parser')
    
    # Usa select_one() para encontrar APENAS o primeiro elemento que corresponde ao seletor
    
    # Título
    titulo_tag = sopa.select_one(SELETOR_TITULO)
    titulo = titulo_tag.text.strip() if titulo_tag else "❌ Título não encontrado com o seletor fornecido."

    # Preço
    preco_tag = sopa.select_one(SELETOR_PRECO)
    preco = preco_tag.text.strip() if preco_tag else "❌ Preço não encontrado com o seletor fornecido."
    
    return titulo, preco

# ----------------------------------------------------
# 3. Execução Principal
# ----------------------------------------------------
if __name__ == '__main__':
    driver = iniciar_driver()
    
    if driver:
        try:
            titulo_teste, preco_teste = testar_extracao_simples(driver, URL_PESQUISA)
            
            print("\n✨ **RESULTADO DO TESTE DE EXTRAÇÃO SIMPLIFICADA** ✨")
            print("-" * 50)
            print(f"Título (1º Anúncio): {titulo_teste}")
            print(f"Preço (1º Anúncio): {preco_teste}")
            print("-" * 50)
            
            # Se o título e o preço foram encontrados, agora sabemos qual é o novo seletor de bloco!
            if not titulo_teste.startswith("❌") and not preco_teste.startswith("❌"):
                print("\n✅ Sucesso! Os seletores CSS estão a funcionar para o primeiro anúncio.")
            else:
                print("\n❌ Atenção: Mesmo no teste simplificado, um ou ambos os elementos não foram encontrados.")

        finally:
            driver.quit()
            print("\nNavegador Chrome fechado.")