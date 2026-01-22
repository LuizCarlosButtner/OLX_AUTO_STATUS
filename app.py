import time
from OlxUrlReturner import OlxUrlReturner
from OlxAnuncioReturner import OlxAnuncioReturner

def main():
    print(">>> INICIANDO O SISTEMA DE MONITORAMENTO OLX <<<")
    
    # 1. Instancia a classe de busca de URLs e obtém os links
    # Você pode alterar 'parametros.json' para o arquivo de configuração desejado
    url_fetcher = OlxUrlReturner(params_file='parametros.json')
    
    print("\n[FASE 1] Buscando URLs de anúncios...")
    lista_urls = url_fetcher.fetch_urls()
    
    if not lista_urls:
        print("Nenhuma URL encontrada. Encerrando.")
        return

    print(f"\n[SUCESSO] {len(lista_urls)} URLs encontradas. Iniciando extração de detalhes...\n")
    
    # 2. Instancia a classe de detalhes do anúncio
    ad_processor = OlxAnuncioReturner()
    
    # 3. Itera sobre cada URL encontrada
    for i, url in enumerate(lista_urls, 1):
        print(f"--- Processando Anúncio {i}/{len(lista_urls)} ---")
        
        # Processa a URL e imprime o resultado formatado
        relatorio = ad_processor.processar_url(url)
        print(relatorio)
            
        # Pausa para evitar bloqueios e dar tempo de fechar/abrir o navegador
        time.sleep(2)

if __name__ == "__main__":
    main()
    
    
    
# aqui temos a aplicação principal que usa as outras duas classes para buscar urls e processar cada uma delas
# primeiro ele busca as urls com a classe OlxUrlReturner e depois processa cada url com a classe OlxAnuncioReturner
