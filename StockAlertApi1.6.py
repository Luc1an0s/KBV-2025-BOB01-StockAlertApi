import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Caminho do seu arquivo de credenciais - lembre de usar raw string ou barras invertidas duplas
CRED_FILE = r'C:\Users\user\Documents\GitHub\KBV-PROJETOS\api wpp\credenciais.json'

# ID da planilha (pegado da URL)
SHEET_ID = '1V1fOlojpJXme8DPUfPeqIRpJChfkG7ucDfOF294IeUo'

# Nome da aba
SHEET_TAB_NAME = 'ESTOQUE'

# Define o escopo
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']

# Autentica com as credenciais
creds = ServiceAccountCredentials.from_json_keyfile_name(CRED_FILE, scope)
client = gspread.authorize(creds)

# Abre a planilha pelo ID
sheet = client.open_by_key(SHEET_ID)

# Abre a aba ESTOQUE
worksheet = sheet.worksheet(SHEET_TAB_NAME)

# Pega todos os dados
dados = worksheet.get_all_values()

# Exibe os dados
print("Dados da aba ESTOQUE:")
for linha in dados:
    print(linha)