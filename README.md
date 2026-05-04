# 📦 StockAlertApi

Sistema automatizado de monitoramento de estoque e envio de alertas via WhatsApp e e-mail, com execução agendada pelo GitHub Actions.

## 🧭 Visão Geral

O **StockAlertApi** verifica os dados de estoque de bobinas em uma planilha do Google Sheets e envia mensagens para os responsáveis informando quais lojas precisam de reposição. O processo é executado automaticamente de forma nativa e profissional.

## 🏗️ Arquitetura

- **Fonte de dados:** Google Sheets (aba `ESTOQUE`)
- **Processamento:** Script Python (`StockAlertApi3.01.py`)
- **Notificações:** API Oficial Cloud da Meta (WhatsApp Business) + SMTP para e-mail
- **Agendamento:** GitHub Actions com cron

## 🔁 Fluxo de Execução

1.  Autentica no Google Sheets usando credenciais do GitHub Secrets.
2.  Lê os dados da aba `ESTOQUE` e da aba `ROTAS` para definir a logística.
3.  Interpreta os valores de estoque e filtra os que precisam de envio (Qtd > 200).
4.  Agrupa os dados por loja e busca o galpão de origem autorizado.
5.  Envia mensagens via WhatsApp usando Templates Oficiais da Meta.
6.  Envia e-mail de confirmação com log de execução (fuso de Manaus).

## ⏰ Agendamento

Executado automaticamente de segunda a sábado:

- 🕔 **17h Manaus** → `cron: '0 21 * * 1-5'` (21h UTC)

*Também pode ser executado manualmente via `workflow_dispatch` na aba Actions.*

## 🔐 Variáveis de Ambiente (GitHub Secrets)

| Nome | Descrição |
| :--- | :--- |
| `GOOGLE_CRED_JSON` | JSON completo da Service Account do Google Cloud. |
| `META_WHATSAPP_TOKEN` | Token de acesso permanente gerado no Meta for Developers. |
| `META_PHONE_ID` | Identificador único do número de telefone na API da Meta. |
| `GET_NUMWPP_ENV` | Lista de gestores no formato `NOME=55929...` |
| `EMAIL_REMETENTE` | E-mail Gmail configurado com "Senha de App". |
| `EMAIL_SENHA` | Senha de aplicativo gerada na conta Google. |
| `EMAIL_DESTINATARIO` | E-mail que receberá o relatório de sucesso/falha. |

## 📲 Mensagens Enviadas

- **WhatsApp:** Utiliza o template `alerta_de_estoque_de_bobina` com 6 variáveis dinâmicas (Loja, Qtd necessária, Tipo, Galpão sugerido, Saldo galpão, Tipo galpão).
- **E-mail:** Confirmação técnica listando os números notificados e o carimbo de tempo.

## 📋 Logs e Monitoramento

- Acesse a aba **Actions** no repositório.
- Clique no workflow **StockAlertApi**.
- Em caso de erro no WhatsApp, o log exibirá o JSON detalhado da Meta (Ex: Error 400 ou 100).

## 🛠️ Manutenção

- **Template:** Qualquer alteração no texto da mensagem deve ser feita no Painel da Meta.
- **Fuso Horário:** O script força `America/Manaus` para consistência nos relatórios.
- **Segurança:** O arquivo `credentials.json` é criado e deletado em tempo de execução.

---

## 📦 CHANGELOG - StockAlertApi

Histórico de evolução do projeto.

### [Bob03.01] - 04/05/2026

#### 🚀 Added
- Migração completa para a **API Oficial da Meta (WhatsApp Cloud API)**.
- Implementação de tratamento de erros nativo para retornos da Graph API (v25.0).
- Otimização de segurança: criação volátil de credenciais para prevenir vazamentos.
- Refatoração do script para suporte a 6 parâmetros dinâmicos via Templates.

### [Bob02.01] - 17/09/2025

#### 🔧 Added
- Definição da estratégia de execução automatizada via GitHub Actions.
- Configuração de agendamento com cron para execução periódica.

### [Bob01.02] - 12/09/2025

#### 🔄 Changed
- Substituição da API de mensageria de **Ultramsg** para **Bubble.io**.

### [Bob01.01] - 12/09/2025

#### 🆕 Added
- Integração inicial entre script Python e Google Sheets utilizando Google Cloud SDK.
- Implementação do fluxo básico de leitura de estoque.