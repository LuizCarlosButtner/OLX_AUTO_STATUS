import time
from OlxUrlReturner import OlxUrlReturner
from OlxAnuncioReturner import OlxAnuncioReturner
from message_templates import montar_mensagem_padrao
from database_manager import get_db_connection, DatabaseManager

def main():
    print(">>> INICIANDO O SISTEMA DE MONITORAMENTO OLX <<<")
    
    db_connection = None
    db_manager = None

    try:
        # --- [FASE 1] Conexão com o Banco de Dados ---
        print("\n[FASE 1] Conectando ao banco de dados...")
        db_connection = get_db_connection()
        if not db_connection:
            print("ERRO: Falha ao conectar ao banco de dados. Encerrando.")
            return

        db_manager = DatabaseManager(db_connection)
        db_manager.ensure_table_exists()
        print("[SUCESSO] Conexão com o banco de dados estabelecida.")

        # --- [FASE 2] Busca de Anúncios ---
        url_fetcher = OlxUrlReturner(params_file='parametros.json')
        print("\n[FASE 2] Buscando anúncios na OLX...")
        lista_dados_brutos = url_fetcher.fetch_urls()
        
        if not lista_dados_brutos:
            print("Nenhum anúncio encontrado na busca. Encerrando.")
            return
        
        print(f"[SUCESSO] {len(lista_dados_brutos)} anúncios encontrados na busca inicial.")

        # --- [FASE 3] Filtragem de Anúncios Novos ---
        print("\n[FASE 3] Filtrando anúncios que já existem no banco de dados...")
        
        # A lista_dados_brutos agora contém apenas URLs
        urls_a_verificar = lista_dados_brutos
        urls_existentes = db_manager.get_existing_urls(urls_a_verificar)
        
        anuncios_novos_urls = [url for url in urls_a_verificar if url not in urls_existentes]

        if not anuncios_novos_urls:
            print("Nenhum anúncio novo para processar. Encerrando.")
            return

        print(f"[SUCESSO] {len(anuncios_novos_urls)} anúncios novos encontrados para processamento.")

        # --- [FASE 4] Processamento dos Anúncios Novos ---
        print("\n[FASE 4] Iniciando processamento detalhado dos novos anúncios...")
        ad_processor = OlxAnuncioReturner()
        
        for i, url_anuncio in enumerate(anuncios_novos_urls, 1):
            print(f"\n--- Processando Anúncio Novo {i}/{len(anuncios_novos_urls)} ---")
            
            # O processar_url agora é a única fonte dos dados detalhados.
            # Ele também extrai o ID a partir da URL.
            dados_anuncio = ad_processor.processar_url(url_anuncio)
            
            if dados_anuncio and 'id_anuncio' in dados_anuncio:
                # O URL já está em dados_anuncio['url_anuncio'], mas garantimos aqui.
                dados_anuncio['url'] = url_anuncio

                print(f"Anúncio (ID: {dados_anuncio['id_anuncio']}) extraído. Tentando salvar no banco...")

                # Insere no banco de dados ANTES de qualquer outra ação
                if db_manager.insert_anuncio(dados_anuncio):
                    print(f"Anúncio {dados_anuncio['id_anuncio']} salvo no banco de dados com sucesso.")
                    
                    # Formata a mensagem para exibição/envio
                    mensagem_final = montar_mensagem_padrao(
                        dados_anuncio, 
                        dados_anuncio['id_anuncio'], 
                        dados_anuncio.get('titulo_principal', 'N/A'), 
                        dados_anuncio.get('descricao_anuncio', 'N/A')
                    )
                    print(mensagem_final)
                else:
                    print(f"ERRO: Falha ao salvar o anúncio {dados_anuncio['id_anuncio']} no banco de dados.")

            else:
                print(f"Falha ao processar a URL: {url_anuncio}")
                
            time.sleep(2)

    except Exception as e:
        print(f"\nOcorreu um erro fatal no processo: {e}")

    finally:
        if db_manager:
            db_manager.close()
        elif db_connection:
            db_connection.close()
            print("Conexão com o banco de dados fechada.")
        
        print("\n>>> SISTEMA DE MONITORAMENTO OLX ENCERRADO <<<")


if __name__ == "__main__":
    main()