🚗 OLX Sniper: Automação de Monitoramento de Veículos
O OLX Sniper é uma ferramenta de inteligência de mercado desenvolvida para detectar oportunidades de compra de veículos de forma instantânea. O sistema elimina a necessidade de buscas manuais, monitorando URLs específicas e notificando o usuário via WhatsApp no exato momento em que um novo anúncio é publicado.

🎯 O Problema
No mercado de revenda de veículos, os melhores negócios (anúncios abaixo da FIPE) duram poucos minutos. A atualização manual do site da OLX é ineficiente e humanamente limitada.

💡 A Solução
O bot automatiza o ciclo de monitoramento e análise:

Monitoramento: Realiza varreduras em intervalos curtos nas URLs configuradas.

Extração de Dados: Identifica marca, modelo, ano, quilometragem e preço.

Inteligência de Preço: Cruza os dados do anúncio com a Tabela FIPE em tempo real.

Notificação Imediata: Se o veículo atende aos parâmetros, envia um alerta detalhado para o WhatsApp do usuário.

🚀 Principais Diferenciais
Velocidade: Detecção de anúncios em "tempo real", garantindo o primeiro contato com o vendedor.

Análise de Margem: O alerta já chega com o cálculo de lucratividade ou desconto em relação à FIPE.

Filtros Inteligentes: Possibilidade de ignorar anúncios profissionais ou focar apenas em CPFs (particulares).

Logs Detalhados: Registro de todos os anúncios processados para evitar notificações duplicadas.

🛠️ Stack Técnica
Linguagem: Python

Extração: BeautifulSoup4 / Selenium (Web Scraping)

Comunicação: Integração via API de WhatsApp (Evolution API/Baileys)

Dados: SQLite/JSON para persistência e controle de duplicatas

📊 Exemplo de Alerta
Ao encontrar uma oportunidade, o bot gera uma mensagem estruturada:

⚡ OPORTUNIDADE DETECTADA!

Modelo: VW Golf 1.4 TSI Highline 2015 Preço Anúncio: R$ 72.000 Tabela FIPE: R$ 79.500 Margem: 🟢 9.43% abaixo da FIPE Local: Curitiba/PR

[🔗 Abrir anúncio agora]

🛡️ Disclaimer
Este projeto foi desenvolvido para fins de estudo e automação pessoal. O uso de scrapers deve respeitar os termos de serviço das plataformas monitoradas.
