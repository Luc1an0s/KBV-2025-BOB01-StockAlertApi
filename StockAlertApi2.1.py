import gspread
from oauth2client.service_account import ServiceAccountCredentials
import requests
import smtplib
from email.mime.text import MIMEText
import os
import locale
from collections import defaultdict
from datetime import datetime

print("🔄 Iniciando envio de mensagens...")

# Configura locale para interpretar números brasileiros
locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')

def parse_quantidade(valor):
    if isinstance(valor, str):
        return locale.atof(valor)
    return float(valor)

# Coleta números de WhatsApp
raw_env = os.environ.get("GET_NUMWPP_ENV", "")
numeros = []

for linha in raw_env.splitlines():
    if "=" in linha:
        _, valor = linha.split("=", 1)
        numero = valor.strip()
        if numero:
            numeros.append(numero)

# Autenticação Google Sheets
cred_json = os.environ.get("GOOGLE_CRED_JSON")
with open("credenciais.json", "w") as f:
    f.write(cred_json)

scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name("credenciais.json", scope)
client = gspread.authorize(creds)

SHEET_ID = '1pP92qnTgU32x44QCM8kCkXl9mSSukKFGwf4qGQUBObs'
SHEET_TAB_NAME = 'ESTOQUE'

worksheet = client.open_by_key(SHEET_ID).worksheet(SHEET_TAB_NAME)
dados = worksheet.get_all_records()

# Processa os dados da planilha
ultima_n_loja = ""
ultima_loja = ""
ultima_estado = ""
lojas = defaultdict(list)

for idx, linha in enumerate(dados, start=2):
    n_loja = linha.get("N_LOJA", "") or ultima_n_loja
    loja = linha.get("LOJA", "") or ultima_loja
    estado = linha.get("ESTADO", "") or ultima_estado
    produto = linha.get("TIPO DE TELHA", "")
    quantidade_raw = linha.get("ESTOQUE A ENVIAR", 0)

    ultima_n_loja = n_loja
    ultima_loja = loja
    ultima_estado = estado

    try:
        quantidade = parse_quantidade(quantidade_raw)
    except (ValueError, TypeError):
        continue

    if quantidade < 1:
        continue

    try:
        if str(produto).isdigit():
            produto_formatado = f"0,{int(produto)}"
        else:
            produto_formatado = str(produto)
    except:
        produto_formatado = str(produto)

    quantidade_formatada = f"{quantidade:.2f}".replace(".", ",")
    chave = f"{n_loja} - {loja} ({estado})"
    lojas[chave].append(f"{quantidade_formatada} MT de bobina {produto_formatado}")

# Envia mensagens via API
url = "https://appbobinaskbv.bubbleapps.io/version-test/api/1.1/wf/enviamensagem"

for chave, produtos in lojas.items():
    mensagem = f"⚠ Loja {chave} precisa de:\n" + "\n".join(produtos)

    for numero in numeros:
        payload = {
            "celular": numero,
            "mensagem": mensagem
        }

        response = requests.post(url, data=payload)
        print(f"📡 Enviado para {numero}: {response.status_code} - {response.text}")

# Envia confirmação por e-mail
remetente = os.environ.get("EMAIL_REMETENTE")
senha = os.environ.get("EMAIL_SENHA")
destinatario = os.environ.get("EMAIL_DESTINATARIO")

if remetente and senha and destinatario:
    agora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    mensagem = f"🛠️ Confirmação KBV\n✅ Script rodou com sucesso em {agora} (horário de Manaus)."

    msg = MIMEText(mensagem)
    msg["Subject"] = "Confirmação KBV"
    msg["From"] = remetente
    msg["To"] = destinatario

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(remetente, senha)
            server.sendmail(remetente, destinatario, msg.as_string())
        print("📧 E-mail de confirmação enviado com sucesso!")
    except Exception as e:
        print(f"⚠️ Erro ao enviar e-mail: {e}")
else:
    print("⚠️ Variáveis de e-mail não configuradas. Confirmação não enviada.")

print("✅ Mensagens enviadas com sucesso!")