import gspread
from oauth2client.service_account import ServiceAccountCredentials
import requests
import os
from collections import defaultdict

# 🔐 Lê variáveis do ambiente (GitHub Secrets)
numero = os.environ.get("GET_NUMWPP_ENV")
cred_json = os.environ.get("GOOGLE_CRED_JSON")

# 📝 Salva credenciais como arquivo temporário
with open("credenciais.json", "w") as f:
    f.write(cred_json)

# 📊 Configura acesso ao Google Sheets
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name("credenciais.json", scope)
client = gspread.authorize(creds)

SHEET_ID = '1FbVt2Ux4ZwtO_cpF0AUS9lO5lrgJJxKMEsyENZG3jXs'
SHEET_TAB_NAME = 'ESTOQUE'

sheet = client.open_by_key(SHEET_ID)
worksheet = sheet.worksheet(SHEET_TAB_NAME)
dados = worksheet.get_all_records()

# 🏬 Processa os dados da planilha
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

# 📤 Envia mensagens via API
url = "https://appbobinaskbv.bubbleapps.io/version-test/api/1.1/wf/enviamensagem"

for chave, produtos in lojas.items():
    mensagem = f"⚠ Loja {chave} precisa de:\n" + "\n".join(produtos)

    payload = {
        "celular": numero,
        "mensagem": mensagem
    }

    response = requests.post(url, data=payload)
    if response.status_code == 200:
        print(f"✅ Mensagem enviada para {numero}:\n{mensagem}\n")
    else:
        print(f"❌ Erro ao enviar para {numero}: {response.status_code} - {response.text}")
