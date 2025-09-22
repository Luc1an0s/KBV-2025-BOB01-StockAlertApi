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

print("🔄 Iniciando envio de mensagens...")

cred_json = os.environ.get("GOOGLE_CRED_JSON")
if not cred_json:
    raise RuntimeError("Variável GOOGLE_CRED_JSON não definida.")
with open("credentials.json", "w", encoding="utf-8") as f:
    f.write(cred_json)

scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client = gspread.authorize(creds)

SHEET_ID = '1pP92qnTgU32x44QCM8kCkXl9mSSukKFGwf4qGQUBObs'
worksheet = client.open_by_key(SHEET_ID).worksheet('ESTOQUE')

def parse_quantidade(valor):
    if valor is None:
        return 0.0
    if isinstance(valor, (int, float)):
        return float(valor)
    s = str(valor).strip()
    s = re.sub(r"[^\d.,-]", "", s)
    negativo = s.startswith("-")
    s = s.lstrip("-")
    if not s:
        return 0.0
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

raw_env = os.environ.get("GET_NUMWPP_ENV", "")
numeros = []
for linha in raw_env.splitlines():
    if "=" in linha:
        _, valor = linha.split("=", 1)
        numero = valor.strip()
        if numero:
            numeros.append(numero)

values = worksheet.get_all_values()
headers = values[0]
rows = values[1:]

def idx(colname):
    try:
        return headers.index(colname)
    except ValueError:
        raise RuntimeError(f"Coluna '{colname}' não encontrada.")

i_n_loja = idx("N_LOJA")
i_loja = idx("LOJA")
i_estado = idx("ESTADO")
i_produto = idx("TIPO DE TELHA")
i_qtd = idx("ESTOQUE A ENVIAR")
i_estoque_total = idx("ESTOQUE TOTAL")

worksheet_rotas = client.open_by_key(SHEET_ID).worksheet('ROTAS')
rotas_values = worksheet_rotas.get_all_values()
rotas_galpoes = rotas_values[1][2:]
rotas_destinos = [row[1] for row in rotas_values[2:]]
rotas_matriz = [row[2:] for row in rotas_values[2:]]

def get_estoque_galpao_tipo(galpao, tipo_telha):
    for r in rows:
        loja_val = r[i_loja] if i_loja < len(r) else ''
        tipo_val = r[i_produto] if i_produto < len(r) else ''
        if loja_val.strip() == galpao and tipo_val.strip() == tipo_telha:
            qtd_total = r[i_estoque_total] if i_estoque_total < len(r) else ''
            try:
                return parse_quantidade(qtd_total)
            except:
                return 0.0
    return 0.0

ultima_n_loja = ultima_loja = ultima_estado = ""
lojas = defaultdict(list)

for r in rows:
    n_loja = r[i_n_loja].strip() if i_n_loja < len(r) else ""
    loja = r[i_loja].strip() if i_loja < len(r) else ""
    estado = r[i_estado].strip() if i_estado < len(r) else ""
    produto = r[i_produto].strip() if i_produto < len(r) else ""
    quantidade_raw = r[i_qtd].strip() if i_qtd < len(r) else ""

    if not n_loja:
        n_loja = ultima_n_loja
    if not loja:
        loja = ultima_loja
    if not estado:
        estado = ultima_estado

    ultima_n_loja, ultima_loja, ultima_estado = n_loja, loja, estado

    try:
        quantidade = parse_quantidade(quantidade_raw)
    except:
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

url = "https://appbobinaskbv.bubbleapps.io/version-test/api/1.1/wf/enviamensagem"

for chave, produtos in lojas.items():
    mensagem = f"⚠ Loja {chave} precisa de:\n" + "\n".join(produtos)
    destino_nome = chave.split(" - ")[1].split(" (")[0].strip()
    tipo_telha = None
    if produtos:
        match = re.search(r'bobina ([^\n]+)', produtos[0])
        if match:
            tipo_telha = match.group(1).strip()
    if destino_nome in rotas_destinos and tipo_telha:
        idx_destino = rotas_destinos.index(destino_nome)
        rotas_linha = rotas_matriz[idx_destino]
        galpoes_autorizados = [g for g, v in zip(rotas_galpoes, rotas_linha) if v == '1']
        if galpoes_autorizados:
            mensagem += "\n\nEstoque disponível nos galpões autorizados para o tipo de telha:"
            for galpao in galpoes_autorizados:
                qtd = get_estoque_galpao_tipo(galpao, tipo_telha)
                mensagem += f"\n- {galpao}: {qtd:.2f} MT ({tipo_telha})"
    for numero in numeros:
        payload = {
            "celular": numero,
            "mensagem": mensagem
        }
        response = requests.post(url, data=payload)
        print(f"📡 Enviado para {numero}: {response.status_code} - {response.text}")

remetente = os.environ.get("EMAIL_REMETENTE")
senha = os.environ.get("EMAIL_SENHA")
destinatario = os.environ.get("EMAIL_DESTINATARIO")

if remetente and senha and destinatario:
    manaus_tz = pytz.timezone("America/Manaus")
    agora = datetime.now(manaus_tz).strftime("%d/%m/%Y %H:%M:%S")
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