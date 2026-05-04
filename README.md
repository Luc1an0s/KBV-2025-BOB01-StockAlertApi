<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <title>Documentação StockAlertApi</title>
</head>
<body>
    <h1>📦 StockAlertApi</h1>
    <p>Sistema automatizado de monitoramento de estoque e envio de alertas via WhatsApp e e-mail, com execução agendada pelo GitHub Actions.</p>

    <h2>🧭 Visão Geral</h2>
    <p>O StockAlertApi verifica os dados de estoque de bobinas em uma planilha do Google Sheets e envia mensagens para os responsáveis informando quais lojas precisam de reposição. O processo é executado automaticamente de forma nativa e profissional.</p>

    <h2>🏗️ Arquitetura</h2>
    <ul>
        <li><strong>Fonte de dados:</strong> Google Sheets (aba <code>ESTOQUE</code>)</li>
        <li><strong>Processamento:</strong> Script Python (<code>StockAlertApi3.01.py</code>)</li>
        <li><strong>Notificações:</strong> API Oficial Cloud da Meta (WhatsApp Business) + SMTP para e-mail</li>
        <li><strong>Agendamento:</strong> GitHub Actions com cron</li>
    </ul>

    <h2>🔁 Fluxo de Execução</h2>
    <ol>
        <li>Autentica no Google Sheets usando credenciais do GitHub Secrets.</li>
        <li>Lê os dados da aba <code>ESTOQUE</code> e da aba <code>ROTAS</code> para definir a logística.</li>
        <li>Interpreta os valores de estoque e filtra os que precisam de envio (Qtd > 200).</li>
        <li>Agrupa os dados por loja e busca o galpão de origem autorizado.</li>
        <li>Envia mensagens via WhatsApp usando Templates Oficiais da Meta.</li>
        <li>Envia e-mail de confirmação com log de execução (fuso de Manaus).</li>
    </ol>

    <h2>⏰ Agendamento</h2>
    <p>Executado automaticamente de segunda a sábado:</p>
    <ul>
        <li>🕔 <strong>17h Manaus</strong> → <code>cron: '0 21 * * 1-5'</code> (21h UTC)</li>
    </ul>
    <p>Também pode ser executado manualmente via <code>workflow_dispatch</code> na aba Actions.</p>

    <h2>🔐 Variáveis de Ambiente (GitHub Secrets)</h2>
    <table border="1" style="border-collapse: collapse; width: 100%;">
        <thead>
            <tr style="background-color: #f2f2f2;">
                <th style="padding: 8px;">Nome</th>
                <th style="padding: 8px;">Descrição</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td style="padding: 8px;"><code>GOOGLE_CRED_JSON</code></td>
                <td style="padding: 8px;">JSON completo da Service Account do Google Cloud.</td>
            </tr>
            <tr>
                <td style="padding: 8px;"><code>META_WHATSAPP_TOKEN</code></td>
                <td style="padding: 8px;">Token de acesso permanente gerado no Meta for Developers.</td>
            </tr>
            <tr>
                <td style="padding: 8px;"><code>META_PHONE_ID</code></td>
                <td style="padding: 8px;">Identificador único do número de telefone na API da Meta.</td>
            </tr>
            <tr>
                <td style="padding: 8px;"><code>GET_NUMWPP_ENV</code></td>
                <td style="padding: 8px;">Lista de gestores no formato <code>NOME=55929...</code></td>
            </tr>
            <tr>
                <td style="padding: 8px;"><code>EMAIL_REMETENTE</code></td>
                <td style="padding: 8px;">E-mail Gmail configurado com "Senha de App".</td>
            </tr>
            <tr>
                <td style="padding: 8px;"><code>EMAIL_SENHA</code></td>
                <td style="padding: 8px;">Senha de aplicativo gerada na conta Google.</td>
            </tr>
            <tr>
                <td style="padding: 8px;"><code>EMAIL_DESTINATARIO</code></td>
                <td style="padding: 8px;">E-mail que receberá o relatório de sucesso/falha.</td>
            </tr>
        </tbody>
    </table>

    <h2>📲 Mensagens Enviadas</h2>
    <ul>
        <li><strong>WhatsApp:</strong> Utiliza o template <code>alerta_de_estoque_de_bobina</code> com 6 variáveis dinâmicas (Loja, Qtd necessária, Tipo, Galpão sugerido, Saldo galpão, Tipo galpão).</li>
        <li><strong>E-mail:</strong> Confirmação técnica listando os números notificados e o carimbo de tempo.</li>
    </ul>

    <h2>📋 Logs e Monitoramento</h2>
    <ul>
        <li>Acesse a aba <strong>Actions</strong> no repositório.</li>
        <li>Clique no workflow <strong>StockAlertApi</strong>.</li>
        <li>Em caso de erro no WhatsApp, o log exibirá o JSON detalhado da Meta (Ex: Error 400 ou 100).</li>
    </ul>

    <h2>🛠️ Manutenção</h2>
    <ul>
        <li><strong>Template:</strong> Qualquer alteração no texto da mensagem deve ser feita no Painel da Meta.</li>
        <li><strong>Fuso Horário:</strong> O script força <code>America/Manaus</code> para consistência nos relatórios.</li>
        <li><strong>Segurança:</strong> O arquivo <code>credentials.json</code> é criado e deletado em tempo de execução.</li>
    </ul>

    <hr>

    <h2>📦 CHANGELOG - StockAlertApi</h2>
    <p>Histórico de evolução do projeto.</p>

    <h3>[Bob03.01] - 04/05/2026</h3>
    <h4>🚀 Added</h4>
    <ul>
        <li>Migração completa para a <strong>API Oficial da Meta (WhatsApp Cloud API)</strong>.</li>
        <li>Implementação de tratamento de erros nativo para retornos da Graph API (v25.0).</li>
        <li>Otimização de segurança: criação volátil de credenciais para prevenir vazamentos.</li>
        <li>Refatoração do script para suporte a 6 parâmetros dinâmicos via Templates.</li>
    </ul>

    <h3>[Bob02.01] - 17/09/2025</h3>
    <h4>🔧 Added</h4>
    <ul>
        <li>Definição da estratégia de execução automatizada via GitHub Actions.</li>
        <li>Configuração de agendamento com cron para execução periódica.</li>
    </ul>

    <h3>[Bob01.02] - 12/09/2025</h3>
    <h4>🔄 Changed</h4>
    <ul>
        <li>Substituição da API de mensageria de <strong>Ultramsg</strong> para <strong>Bubble.io</strong>.</li>
    </ul>

    <h3>[Bob01.01] - 12/09/2025</h3>
    <h4>🆕 Added</h4>
    <ul>
        <li>Integração inicial entre script Python e Google Sheets utilizando Google Cloud SDK.</li>
        <li>Implementação do fluxo básico de leitura de estoque.</li>
    </ul>
</body>
</html>