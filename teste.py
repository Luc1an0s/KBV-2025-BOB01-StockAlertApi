import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
import re

print("🔎 Diagnóstico iniciado...")

# 1) Parser robusto (não depende de locale)
def parse_quantidade(valor):
    if valor is None:
        raise ValueError("valor vazio")
    if isinstance(valor, (int, float)):
        return float(valor)

    s = str(valor).strip()
    s = re.sub(r"[^\d.,-]", "", s)

    negativo = s.startswith("-")
    s = s.lstrip("-")

    if not s:
        raise ValueError("string vazia após limpeza")

    if "," in s:
        inteiro, _, decimal = s.rpartition(",")
        inteiro = inteiro.replace(".", "")
        decimal = re.sub(r"\D", "", decimal)
        if decimal == "":
            decimal = "00"
        s = f"{inteiro}.{decimal}"
    elif "." in s:
        parts = s.split(".")
        if len(parts) > 2:
            last = parts[-1]
            if last.isdigit() and 1 <= len(last) <= 2:
                inteiro = "".join(parts[:-1])
                decimal = last
                s = f"{inteiro}.{decimal}"
            else:
                s = "".join(parts)
        else:
            left, right = parts
            if right.isdigit() and 1 <= len(right) <= 2:
                s = f"{left}.{right}"
            else:
                s = f"{left}{right}"
    return -float(s) if negativo else float(s)

# 2) Autenticação Google Sheets via caminho direto
cred_path = "C:/Users/Lucius/Documents/GitHub/Credenciais StockAlertApi/credenciais.json"
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name(cred_path, scope)
client = gspread.authorize(creds)

SHEET_ID = '1pP92qnTgU32x44QCM8kCkXl9mSSukKFGwf4qGQUBObs'
SHEET_TAB_NAME = 'ESTOQUE'
worksheet = client.open_by_key(SHEET_ID).worksheet(SHEET_TAB_NAME)

# 3) Ler tudo como texto
values = worksheet.get_all_values()
if not values:
    raise RuntimeError("Planilha vazia")

headers = values[0]
rows = values[1:]

def idx(colname):
    try:
        return headers.index(colname)
    except ValueError:
        raise RuntimeError(f"Coluna '{colname}' não encontrada. Cabeçalhos: {headers}")

i_n_loja = idx("N_LOJA")
i_loja = idx("LOJA")
i_estado = idx("ESTADO")
i_produto = idx("TIPO DE TELHA")
i_qtd = idx("ESTOQUE A ENVIAR")

# 5) Diagnóstico: imprimir até 50 linhas
count = 0
erros = 0
last_n_loja = last_loja = last_estado = ""

for r in rows:
    n_loja = r[i_n_loja].strip() if i_n_loja < len(r) else ""
    loja = r[i_loja].strip() if i_loja < len(r) else ""
    estado = r[i_estado].strip() if i_estado < len(r) else ""
    produto = r[i_produto].strip() if i_produto < len(r) else ""
    quantidade_raw = r[i_qtd].strip() if i_qtd < len(r) else ""

    if not n_loja and count > 0:
        n_loja = last_n_loja
    if not loja and count > 0:
        loja = last_loja
    if not estado and count > 0:
        estado = last_estado

    last_n_loja, last_loja, last_estado = n_loja, loja, estado

    try:
        convertido = parse_quantidade(quantidade_raw)
        formatado_br = f"{convertido:.2f}".replace(".", ",")
        print(f"[{count:03}] Loja: {n_loja} - {loja} ({estado}) | Bruto='{quantidade_raw}' | Parsed={convertido} | BR='{formatado_br}' | Produto='{produto}'")
    except Exception as e:
        erros += 1
        print(f"[{count:03}] ERRO ao converter | Bruto='{quantidade_raw}' | Motivo: {e}")

    count += 1
    if count >= 50:
        break

print(f"✅ Diagnóstico finalizado: {count} linhas inspecionadas, {erros} com erro.")