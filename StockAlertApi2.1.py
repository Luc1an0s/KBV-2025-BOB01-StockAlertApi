import gspread
from oauth2client.service_account import ServiceAccountCredentials
import requests
import os
from collections import defaultdict
from datetime import datetime

print("Iniciando envio de mensagens...")

raw_env = os.environ.get("GET_NUMWPP_ENV", "")
numeros = []

for linha in raw_env.splitlines():
    if "=" in linha:
        _, valor = linha.split("=", 1)
        numero = valor.strip()
        if numero:
            numeros.append(numero)

numero_dev = os.environ.get("WHATSAPP_DEVELOPER")

cred_json = os.environ.get("GOOGLE_CRED_JSON")
with open("credenciais.json", "w") as f:
    f.write(cred_json)

# 📊 Conecta ao Google Sheets
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name("credenciais.json", scope)
client = gspread.authorize(creds)

SHEET_ID = '1FbVt2Ux4ZwtO_cpF0AUS9lO5lrgJJxKMEsyENZG3jXs'
SHEET_TAB_NAME = 'ESTOQUE'

worksheet = client.open_by_key(SHEET_ID).worksheet(SHEET_TAB_NAME)
dados = worksheet.get_all_records()

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
        quantidade = int(quantidade_raw)
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

    chave = f"{n_loja} - {loja} ({estado})"
    lojas[chave].append(f"{quantidade} MT de bobina {produto_formatado}")

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

if numero_dev:
    agora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    mensagem = f"🛠️ Confirmação KBV\n✅ Script rodou com sucesso em {agora} (horário de Manaus)."

    print(f"📌 Número do desenvolvedor lido: {numero_dev}")
    print(f"📨 Mensagem de confirmação: {mensagem}")

    payload = {
        "celular": numero_dev,
        "mensagem": mensagem
    }

    response = requests.post(url, data=payload)
    print(f"📡 Status: {response.status_code}")
    print(f"📨 Resposta: {response.text}")
else:
    print("⚠️ Nenhum número de desenvolvedor encontrado. Confirmação não enviada.")

print("✅ Mensagens enviadas com sucesso!")
