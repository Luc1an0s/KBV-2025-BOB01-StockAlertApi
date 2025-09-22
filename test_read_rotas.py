import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os

# Configuração das credenciais
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
cred_path = r"C:\Users\Lucius\Documents\GitHub\Credenciais\StockAlertApi\credenciais.json"

scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name(cred_path, scope)
client = gspread.authorize(creds)

SHEET_ID = '1pP92qnTgU32x44QCM8kCkXl9mSSukKFGwf4qGQUBObs'
SHEET_TAB_NAME = 'ROTAS'
worksheet = client.open_by_key(SHEET_ID).worksheet(SHEET_TAB_NAME)

values = worksheet.get_all_values()
for row in values:
    print(row)
