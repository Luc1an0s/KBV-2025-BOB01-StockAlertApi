import gspread
from oauth2client.service_account import ServiceAccountCredentials
import requests
from dotenv import load_dotenv
import os

load_dotenv()

INSTANCE_ID = os.getenv('WHATSAPP_INSTANCE_ID')
TOKEN = os.getenv('WHATSAPP_TOKEN')

numeros_destino = []
for i in range(1, 2):
    numero = os.getenv(f'WHATSAPP_NUMERO{i}')
    if numero:
        numeros_destino.append(numero.strip())


CRED_FILE = 'credenciais.json'
SHEET_ID = '1FbVt2Ux4ZwtO_cpF0AUS9lO5lrgJJxKMEsyENZG3jXs'
SHEET_TAB_NAME = 'ESTOQUE'

scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name(CRED_FILE, scope)
client = gspread.authorize(creds)

sheet = client.open_by_key(SHEET_ID)
worksheet = sheet.worksheet(SHEET_TAB_NAME)
dados = worksheet.get_all_values()

cabecalho = dados[0]
linhas = dados[1:]

try:
    idx_n_loja = cabecalho.index("N_LOJA")
    idx_loja = cabecalho.index("LOJA")
    idx_estado = cabecalho.index("ESTADO")
    idx_produto = cabecalho.index("TIPO DE TELHA")
    idx_enviar = cabecalho.index("ESTOQUE A ENVIAR")
except ValueError as e:
    print("Coluna não encontrada:", e)
    exit()

for linha in linhas:
    try:
        quantidade = int(linha[idx_enviar])
        if quantidade >= 1:
            n_loja = linha[idx_n_loja]
            loja = linha[idx_loja]
            estado = linha[idx_estado]
            produto = linha[idx_produto]

            mensagem = (f"⚠️ Loja {n_loja} - {loja} ({estado}): "
                        f"precisa de {quantidade} MT de bobina {produto}.")

            url = f"https://api.ultramsg.com/{INSTANCE_ID}/messages/chat"
            for numero in numeros_destino:
                payload = {
                    "token": TOKEN,
                    "to": numero,
                    "body": mensagem
                }

                response = requests.post(url, data=payload)
                if response.status_code == 200:
                    print(f"✅ Mensagem enviada para {numero}: {mensagem}")
                else:
                    print(f"❌ Erro ao enviar para {numero}: {response.status_code} - {response.text}")

    except (ValueError, IndexError):
        continue
