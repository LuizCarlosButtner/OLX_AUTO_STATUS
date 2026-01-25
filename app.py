import time
from OlxUrlReturner import OlxUrlReturner
from OlxAnuncioReturner import OlxAnuncioReturner
from message_templates import montar_mensagem_padrao  # Importamos o formatador aqui

def main():
    print(">>> INICIANDO O SISTEMA DE MONITORAMENTO OLX <<<")
    
    # 1. Busca URLs
    url_fetcher = OlxUrlReturner(params_file='parametros.json')
    print("\n[FASE 1] Buscando URLs de anúncios...")
    lista_urls = url_fetcher.fetch_urls()
    
    if not lista_urls:
        print("Nenhuma URL encontrada. Encerrando.")
        return

    print(f"\n[SUCESSO] {len(lista_urls)} URLs encontradas. Iniciando extração de detalhes...\n")
    
    # 2. Instancia o extrator de dados
    ad_processor = OlxAnuncioReturner()
    
    # 3. Processamento
    for i, url in enumerate(lista_urls, 1):
        print(f"--- Processando Anúncio {i}/{len(lista_urls)} ---")
        
        # AQUI MUDOU: Agora recebemos um objeto de dados, não um texto
        dados_anuncio = ad_processor.processar_url(url)
        
        if dados_anuncio:
            # ---> AQUI VOCÊ PODE INSERIR LÓGICA DE FILTRO OU BANCO DE DADOS <---
            # Exemplo: if dados_anuncio['preco'] > 50000: continue
            
            # Formata a mensagem para exibição/envio usando os dados extraídos
            mensagem_final = montar_mensagem_padrao(
                dados_anuncio, 
                dados_anuncio['id_anuncio'], 
                dados_anuncio['titulo_principal'], 
                dados_anuncio['descricao_anuncio']
            )
            
            print(mensagem_final)
            
        else:
            print(f"Falha ao processar a URL: {url}")
            
        time.sleep(2)

if __name__ == "__main__":
    main()