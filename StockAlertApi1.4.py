import gspread
from oauth2client.service_account import ServiceAccountCredentials
import requests
from dotenv import load_dotenv
import os

# Carrega variáveis de ambiente
load_dotenv()

INSTANCE_ID = os.getenv('WHATSAPP_INSTANCE_ID')
TOKEN = os.getenv('WHATSAPP_TOKEN')

# Lista de números de destino
numeros_destino = []
for i in range(1, 2):  # ajuste se tiver mais números
    numero = os.getenv(f'WHATSAPP_NUMERO{i}')
    if numero:
        numeros_destino.append(numero.strip())

# Conexão com a planilha
CRED_FILE = 'credenciais.json'
SHEET_ID = '1FbVt2Ux4ZwtO_cpF0AUS9lO5lrgJJxKMEsyENZG3jXs'
SHEET_TAB_NAME = 'ESTOQUE'

scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name(CRED_FILE, scope)
client = gspread.authorize(creds)

sheet = client.open_by_key(SHEET_ID)
worksheet = sheet.worksheet(SHEET_TAB_NAME)

# Pega todos os registros como lista de dicionários
dados = worksheet.get_all_records()

print(f"Linhas lidas: {len(dados)}")

# Variáveis para herdar valores de células mescladas
ultima_n_loja = ""
ultima_loja = ""
ultima_estado = ""

for idx, linha in enumerate(dados, start=2):  # start=2 porque o cabeçalho é a linha 1
    try:
        # Preenche valores vazios com os últimos valores (para células mescladas)
        n_loja = linha.get("N_LOJA", "") or ultima_n_loja
        loja = linha.get("LOJA", "") or ultima_loja
        estado = linha.get("ESTADO", "") or ultima_estado
        produto = linha.get("TIPO DE TELHA", "")
        quantidade_raw = linha.get("ESTOQUE A ENVIAR", 0)

        # Atualiza últimos valores
        ultima_n_loja = n_loja
        ultima_loja = loja
        ultima_estado = estado

        # Converte quantidade para inteiro
        try:
            quantidade = int(quantidade_raw)
        except (ValueError, TypeError):
            print(f"⚠️ Linha {idx}: quantidade inválida ('{quantidade_raw}'), pulando.")
            continue

        if quantidade < 1:
            print(f"ℹ️ Linha {idx}: quantidade < 1, pulando.")
            continue

        # Cria a mensagem
        mensagem = (f"⚠️ Loja {n_loja} - {loja} ({estado}): "
                    f"precisa de {quantidade} MT de bobina {produto}.")

        # Envia mensagem para cada número
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

    except Exception as e:
        print(f"❌ Erro inesperado na linha {idx}: {e}")
