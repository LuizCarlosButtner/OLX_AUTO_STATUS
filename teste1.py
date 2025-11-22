# -*- coding: utf-8 -*-

# Importamos apenas a função principal de 'busca_dados2.py'
import json
from busca_dados2 import get_ad_details

def load_extraction_params(file_path='parametros_extracao.json'):
    """Carrega os parâmetros de extração de um arquivo JSON."""
    print(f">>> Carregando parâmetros de '{file_path}'...")
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def main():
    # 1. Defina a URL que você quer buscar
    url_alvo = "https://rj.olx.com.br/rio-de-janeiro-e-regiao/autos-e-pecas/carros-vans-e-utilitarios/fiat-palio-2007-leia-o-anuncio-1454664719?rec=a&lis=vi_web%7C2020%7Cwho_saw_also_saw%7C0"
    
    # 2. Carrega os parâmetros de extração do arquivo JSON
    parametros_extracao = load_extraction_params()

    print(">>> Iniciando o processo de raspagem...")

    # 3. Chama a função que extrai os detalhes.
    # Ela agora gerencia o navegador internamente.
    dados_retornados = get_ad_details(url_alvo, parametros_extracao)

    # 4. Imprime os resultados formatados
    print("RELATÓRIO DE DADOS EXTRAÍDOS")
    # 4. Verifica se a extração foi bem-sucedida e imprime no formato de alerta
    if dados_retornados:
        print("\n" + "="*40)
        print("RELATÓRIO DE DADOS EXTRAÍDOS")
        print("="*40)

    # Tratamento especial para Lista de Opcionais
    opcionais = dados_retornados.get('opcionais')
    if isinstance(opcionais, list):
        # Se for uma lista, junta tudo com vírgulas
        opcionais_texto = ", ".join(opcionais)
    else:
        # Se for texto ou None, mantém como está
        opcionais_texto = opcionais
        # Adiciona a URL do anúncio ao dicionário para ser usada na mensagem
        dados_retornados['url_anuncio'] = url_alvo

    print(f"OPCIONAIS:         {opcionais_texto}")
    
    if dados_retornados:
        # Verifica se 'titulo' foi um dos parâmetros de extração solicitados
        if 'titulo' in parametros_extracao:
            titulo_completo = dados_retornados.get('titulo')
            texto1 = ""
            texto2 = ""
        # Monta a mensagem formatada usando f-string
        # O .get(chave, 'N/A') garante que o script não quebre se um campo não for encontrado
        mensagem = f"""
🚨 *ALERTA DE MONITORAMENTO* 🚨

            if titulo_completo and '\n' in titulo_completo:
                # Divide o título no primeiro '\n' e limita a 2 partes
                partes = titulo_completo.split('\n', 1)
                texto1 = partes[0]
                texto2 = partes[1].strip() if len(partes) > 1 else ""
            else:
                texto1 = titulo_completo or "N/A"  # Garante que não seja None
🚗 *{dados_retornados.get('titulo', 'N/A')}*

        print(dados_retornados)
💰 *Valor:* {dados_retornados.get('preco', 'N/A')}
📊 *FIPE:* {dados_retornados.get('fipe', 'N/A')}

📅 *Ano:* {dados_retornados.get('ano', 'N/A')}
🛣️ *KM:* {dados_retornados.get('km', 'N/A')}
📍 *Local:* {dados_retornados.get('localizacao', 'N/A')}

👤 {dados_retornados.get('vendedor_desde', 'N/A')}
⏰ Postado: {dados_retornados.get('data_de_postagem', 'N/A')}

🔗 {dados_retornados.get('url_anuncio', 'N/A')}
"""
        print(mensagem)
    else:
        print("Falha: A função retornou None ou dados vazios.")

# Ponto de entrada do script
if __name__ == "__main__":
    main()