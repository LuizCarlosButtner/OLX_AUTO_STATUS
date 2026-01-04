# -*- coding: utf-8 -*-

def montar_mensagem_padrao(dados_retornados, id_anuncio, titulo_principal, descricao_anuncio):
    """
    Retorna a string formatada do alerta padrão.
    """
    return f"""
🚨 *ALERTA DE MONITORAMENTO* 🚨

🚗 *{titulo_principal}*
🆔 *ID:* {id_anuncio}

📝 *Descrição:*
{descricao_anuncio}

💰 *Valor:* {dados_retornados.get('preco', 'N/A')}
📊 *FIPE:* {dados_retornados.get('fipe', 'N/A')}

📅 *Ano:* {dados_retornados.get('ano', 'N/A')}
🛣️  *KM:* {dados_retornados.get('km', 'N/A')}
📍 *Local:* {dados_retornados.get('localizacao', 'N/A')}

👤 {dados_retornados.get('vendedor_desde', 'N/A')}
⏰ Postado: {dados_retornados.get('data_de_postagem', 'N/A')}

🔗 {dados_retornados.get('url_anuncio', 'N/A')}
"""