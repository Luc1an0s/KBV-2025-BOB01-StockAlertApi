  <h1>📦 StockAlertApi</h1>
  <p>Sistema automatizado de monitoramento de estoque e envio de alertas via WhatsApp e e-mail, com execução agendada pelo GitHub Actions.</p>

  <h2>🧭 Visão Geral</h2>
  <p>O StockAlertApi verifica os dados de estoque de bobinas em uma planilha do Google Sheets e envia mensagens para os responsáveis informando quais lojas precisam de reposição. O processo é executado automaticamente duas vezes por dia.</p>

  <h2>🏗️ Arquitetura</h2>
  <ul>
    <li><strong>Fonte de dados:</strong> Google Sheets (aba <code>ESTOQUE</code>)</li>
    <li><strong>Processamento:</strong> Script Python (<code>StockAlertApi2.1.py</code>)</li>
    <li><strong>Notificações:</strong> API Bubble para WhatsApp + SMTP para e-mail</li>
    <li><strong>Agendamento:</strong> GitHub Actions com cron</li>
  </ul>

  <h2>🔁 Fluxo de Execução</h2>
  <ol>
    <li>Autentica no Google Sheets usando credenciais do GitHub Secrets</li>
    <li>Lê os dados da aba <code>ESTOQUE</code></li>
    <li>Interpreta os valores de estoque e filtra os que precisam de envio</li>
    <li>Agrupa os dados por loja e estado</li>
    <li>Envia mensagens via WhatsApp para os números definidos</li>
    <li>Envia e-mail de confirmação com horário de execução (fuso de Manaus)</li>
  </ol>

  <h2>⏰ Agendamento</h2>
  <p>Executado automaticamente de segunda a sábado:</p>
  <ul>
    <li>🕔 <strong>17h Manaus</strong> → <code>cron: '0 21 * * 1-5'</code> (21h UTC)</li>
  </ul>
  <p>Também pode ser executado manualmente via <code>workflow_dispatch</code>.</p>

  <h2>🔐 Variáveis de Ambiente</h2>
  <table>
    <thead>
      <tr>
        <th>Nome</th>
        <th>Descrição</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td><code>GOOGLE_CRED_JSON</code></td>
        <td>Credenciais de acesso ao Google Sheets</td>
      </tr>
      <tr>
        <td><code>GET_NUMWPP_ENV</code></td>
        <td>Lista de números de WhatsApp dos gestores</td>
      </tr>
      <tr>
        <td><code>EMAIL_REMETENTE</code></td>
        <td>E-mail usado para enviar confirmação</td>
      </tr>
      <tr>
        <td><code>EMAIL_SENHA</code></td>
        <td>Senha do e-mail remetente</td>
      </tr>
      <tr>
        <td><code>EMAIL_DESTINATARIO</code></td>
        <td>E-mail que recebe a confirmação</td>
      </tr>
    </tbody>
  </table>

  <h2>📲 Mensagens Enviadas</h2>
  <ul>
    <li><strong>WhatsApp:</strong> mensagem por loja com os produtos e quantidades</li>
    <li><strong>E-mail:</strong> confirmação de execução com horário de Manaus</li>
  </ul>

  <h2>📋 Logs e Monitoramento</h2>
  <ul>
    <li>Acesse a aba <strong>Actions</strong> no repositório</li>
    <li>Clique em <strong>StockAlertApi</strong></li>
    <li>Verifique se a execução foi marcada como <code>Scheduled</code></li>
    <li>Confirme o horário de início e conclusão</li>
  </ul>

  <h2>🛠️ Manutenção</h2>
  <ul>
    <li>Para alterar os horários, modifique os valores de <code>cron</code></li>
    <li>Para adicionar novos gestores, edite o segredo <code>GET_NUMWPP_ENV</code></li>
    <li>Para mudar a aba ou estrutura da planilha, atualize os índices no script</li>
  </ul>

  <h2>📌 Observações</h2>
  <ul>
    <li>O script ajusta automaticamente o horário para o fuso de Manaus (<code>America/Manaus</code>)</li>
    <li>Os valores de estoque são interpretados corretamente mesmo com vírgulas e pontos</li>
    <li>O envio de mensagens é feito apenas para os números definidos no segredo <code>GET_NUMWPP_ENV</code></li>
  </ul>
  
  <h2>📦 CHANGELOG - StockAlertApi</h2>
<p>Todas as alterações relevantes neste projeto são documentadas abaixo, seguindo convenções semânticas para facilitar rastreabilidade e manutenção.</p>

<h2>📅 Versões</h2>

<h3>[Bob02.01] - 17/09/2025</h3>
<h4>🔧 Added</h4>
<ul>
  <li>Definição da estratégia de execução automatizada via GitHub Actions.</li>
  <li>Configuração de agendamento com cron para execução periódica.</li>
</ul>

<hr>

<h3>[Bob01.02] - 12/09/2025</h3>
<h4>🔄 Changed</h4>
<ul>
  <li>Substituição da API de mensageria de <strong>Ultramsg</strong> para <strong>Bubble.io</strong>, visando maior estabilidade, suporte a templates e integração simplificada.</li>
</ul>

<hr>

<h3>[Bob01.01] - 12/09/2025</h3>
<h4>🆕 Added</h4>
<ul>
  <li>Definição da API de mensageria baseada em protocolo HTTP RESTful (<strong>Ultramsg</strong>).</li>
  <li>Integração entre script Python e Google Sheets utilizando <strong>Google Cloud SDK</strong>.</li>
  <li>Implementação inicial do fluxo de envio de mensagens via WhatsApp.</li>
</ul>
</body>
</html>
