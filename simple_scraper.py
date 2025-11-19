import requests
from bs4 import BeautifulSoup



url = "https://www.olx.com.br/celulares/estado-rj?ps=100&pe=2000&sf=1&f=p&elcd=1&elcd=3&elcd=4&elcd=2"

print(f"URL de busca: {url}")

# Definir um conjunto de cabeçalhos mais completo para simular um navegador real.
# Isso aumenta a chance de a requisição não ser bloqueada.
headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
    'Cache-Control': 'max-age=0',
    'Connection': 'keep-alive',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'none',
    'Sec-Fetch-User': '?1',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36',
}

print("\nFazendo a requisição HTTP...")
try:
    response = requests.get(url, headers=headers, timeout=15)
    response.raise_for_status()  # Verifica se a requisição foi bem-sucedida (código 2xx)
    print("Requisição bem-sucedida!")

    print("\n--- CONTEÚDO DA PÁGINA (HTML) ---")
    print(response.text)
    print("----------------------------------\n")

except requests.exceptions.RequestException as e:
    print(f"\nERRO: Falha ao fazer a requisição HTTP: {e}")