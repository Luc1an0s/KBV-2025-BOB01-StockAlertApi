import gspread
from oauth2client.service_account import ServiceAccountCredentials
import requests
import smtplib
from email.mime.text import MIMEText
import os
import re
import pytz
from collections import defaultdict
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

print("Iniciando processo de verificação e envio...")

# --- CONFIGURAÇÕES DE AMBIENTE ---
CRED_JSON = os.environ.get("GOOGLE_CRED_JSON")
META_TOKEN = os.environ.get("META_WHATSAPP_TOKEN")
PHONE_NUMBER_ID = os.environ.get("META_PHONE_ID")
TEMPLATE_NAME = "alerta_de_estoque_de_bobina"

if not CRED_JSON:
    raise RuntimeError("Variável GOOGLE_CRED_JSON não definida.")

with open("credentials.json", "w", encoding="utf-8") as f:
    f.write(CRED_JSON)

# --- AUTENTICAÇÃO GOOGLE SHEETS ---
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client = gspread.authorize(creds)

SHEET_ID = '1pP92qnTgU32x44QCM8kCkXl9mSSukKFGwf4qGQUBObs'
try:
    worksheet = client.open_by_key(SHEET_ID).worksheet('ESTOQUE')
    worksheet_rotas = client.open_by_key(SHEET_ID).worksheet('ROTAS')
except Exception as e:
    print(f"Erro ao abrir planilhas: {e}")
    exit(1)

# --- FUNÇÕES AUXILIARES ---
def parse_quantidade(valor):
    if valor is None: return 0.0
    if isinstance(valor, (int, float)): return float(valor)
    s = str(valor).strip()
    s = re.sub(r"[^\d.,-]", "", s)
    negativo = s.startswith("-")
    s = s.lstrip("-")
    if not s: return 0.0
    if "," in s:
        inteiro, _, decimal = s.rpartition(",")
        inteiro = inteiro.replace(".", "")
        s = f"{inteiro}.{decimal}"
    elif "." in s:
        parts = s.split(".")
        if len(parts) > 2: s = "".join(parts)
    try:
        return -float(s) if negativo else float(s)
    except:
        return 0.0

def get_estoque_galpao_tipo(galpao, tipo_telha, rows, i_loja, i_produto, i_estoque_total):
    for r in rows:
        loja_val = r[i_loja].strip() if i_loja < len(r) else ''
        tipo_val = r[i_produto].strip() if i_produto < len(r) else ''
        if loja_val == galpao and tipo_val == tipo_telha:
            qtd_total = r[i_estoque_total] if i_estoque_total < len(r) else '0'
            return parse_quantidade(qtd_total)
    return 0.0

# --- LEITURA DOS DADOS ---
values = worksheet.get_all_values()
headers = values[0]
rows = values[1:]

def idx(colname):
    try:
        return headers.index(colname)
    except ValueError:
        print(f"ERRO: Coluna '{colname}' não encontrada na aba ESTOQUE.")
        exit(1)

i_n_loja = idx("N_LOJA")
i_loja = idx("LOJA")
i_estado = idx("ESTADO")
i_produto = idx("TIPO DE TELHA")
i_qtd = idx("ESTOQUE A ENVIAR")
i_estoque_total = idx("ESTOQUE TOTAL")

# Carregar Rotas
rotas_values = worksheet_rotas.get_all_values()
rotas_galpoes = rotas_values[1][2:]
rotas_destinos = [row[1] for row in rotas_values[2:]]
rotas_matriz = [row[2:] for row in rotas_values[2:]]

# --- PROCESSAMENTO LOGÍSTICO ---
ultima_n_loja = ultima_loja = ultima_estado = ""
lojas = defaultdict(list)

for r in rows:
    n_loja = (r[i_n_loja].strip() if i_n_loja < len(r) else "") or ultima_n_loja
    loja = (r[i_loja].strip() if i_loja < len(r) else "") or ultima_loja
    estado = (r[i_estado].strip() if i_estado < len(r) else "") or ultima_estado
    ultima_n_loja, ultima_loja, ultima_estado = n_loja, loja, estado

    produto = r[i_produto].strip() if i_produto < len(r) else ""
    quantidade = parse_quantidade(r[i_qtd]) if i_qtd < len(r) else 0.0

    if quantidade <= 200: continue

    produto_formatado = f"0,{int(produto)}" if str(produto).isdigit() else str(produto)
    quantidade_formatada = f"{quantidade:.2f}".replace(".", ",")
    
    chave = f"{n_loja} - {loja} ({estado})"
    lojas[chave].append({"qtd": quantidade_formatada, "tipo": produto_formatado})

# --- ENVIO WHATSAPP (META API) ---
url_meta = f"https://graph.facebook.com/v25.0/{PHONE_NUMBER_ID}/messages"
headers_meta = {
    "Authorization": f"Bearer {META_TOKEN}",
    "Content-Type": "application/json"
}

raw_env = os.environ.get("GET_NUMWPP_ENV", "")
numeros = [l.split("=", 1)[1].strip() for l in raw_env.splitlines() if "=" in l]

print(f"Lojas com alerta: {len(lojas)}")
print(f"Números de destino: {len(numeros)}")

for chave, lista_produtos in lojas.items():
    for item in lista_produtos:
        p_qtd = item["qtd"]
        p_tipo = item["tipo"]

        galpao_nome, galpao_qtd, galpao_tipo = "N/A", "0,00", p_tipo
        destino_nome = chave.split(" - ")[1].split(" (")[0].strip()

        if destino_nome in rotas_destinos:
            idx_dest = rotas_destinos.index(destino_nome)
            linha_rota = rotas_matriz[idx_dest]
            autorizados = [g for g, v in zip(rotas_galpoes, linha_rota) if v == '1']
            
            if autorizados:
                galpao_nome = autorizados[0]
                q_galpao = get_estoque_galpao_tipo(galpao_nome, p_tipo, rows, i_loja, i_produto, i_estoque_total)
                galpao_qtd = f"{q_galpao:.2f}".replace(".", ",")

        for numero in numeros:
            numero_limpo = re.sub(r"\D", "", numero)
            if not numero_limpo.startswith("55"): numero_limpo = "55" + numero_limpo

            payload = {
                "messaging_product": "whatsapp",
                "to": numero_limpo,
                "type": "template",
                "template": {
                    "name": TEMPLATE_NAME,
                    "language": {"code": "pt_BR"},
                    "components": [
                        {
                            "type": "body",
                            "parameters": [
                                {"type": "text", "text": str(chave)},        # {{1}}
                                {"type": "text", "text": str(p_qtd)},        # {{2}}
                                {"type": "text", "text": str(p_tipo)},       # {{3}}
                                {"type": "text", "text": str(galpao_nome)},  # {{4}}
                                {"type": "text", "text": str(galpao_qtd)},   # {{5}}
                                {"type": "text", "text": str(galpao_tipo)}   # {{6}}
                            ]
                        }
                    ]
                }
            }
            
            res = requests.post(url_meta, headers=headers_meta, json=payload)
            print(f"Envio para {numero_limpo}: {res.status_code}")
            if res.status_code != 200:
                print(f"ERRO DA META: {res.json()}")

# --- E-MAIL DE CONFIRMAÇÃO ---
remetente = os.environ.get("EMAIL_REMETENTE")
senha = os.environ.get("EMAIL_SENHA")
destinatario = os.environ.get("EMAIL_DESTINATARIO")

if remetente and senha and destinatario:
    manaus_tz = pytz.timezone("America/Manaus")
    agora = datetime.now(manaus_tz).strftime("%d/%m/%Y %H:%M:%S")
    msg = MIMEText(f"Script KBV executado com sucesso em {agora}.\nNúmeros notificados:\n" + "\n".join(numeros))
    msg["Subject"] = "Confirmação de Execução KBV"
    msg["From"], msg["To"] = remetente, destinatario
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(remetente, senha)
            server.sendmail(remetente, destinatario, msg.as_string())
        print("E-mail enviado!")
    except Exception as e:
        print(f"Erro e-mail: {e}")

# Limpa o arquivo temporário
if os.path.exists("credentials.json"):
    os.remove("credentials.json")

print("Processo finalizado.")