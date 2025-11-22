# Supondo que 'dados' seja o dicionário com os valores já limpos (strings finais)
mensagem = f"""
🚨 *ALERTA DE MONITORAMENTO* 🚨

🚗 *{dados['titulo']}*

💰 *Valor:* {dados['preco']}
📊 *FIPE:* {dados['fipe']}

📅 *Ano:* {dados['ano']}
🛣️ *KM:* {dados['km']}
📍 *Local:* {dados['localizacao']}

👤 {dados['vendedor_desde']}
⏰ Postado: {dados['data_de_postagem']}

🔗 {dados['url_anuncio']}
"""

print(mensagem)