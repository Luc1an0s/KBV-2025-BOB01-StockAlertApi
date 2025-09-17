import requests
import os
from datetime import datetime

print("🧪 Entrando no bloco de confirmação...")

numero_dev = os.environ.get("WHATSAPP_DEVELOPER")
print(f"📌 Número do desenvolvedor lido: {numero_dev}")

if numero_dev:
    agora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    mensagem = f"🛠️ Confirmação KBV\n✅ Script rodou com sucesso em {agora} (horário de Manaus)."

    payload = {
        "celular": numero_dev,
        "mensagem": mensagem
    }

    print(f"📦 Payload de confirmação: {payload}")

    response = requests.post("https://appbobinaskbv.bubbleapps.io/version-test/api/1.1/wf/enviamensagem", data=payload)
    print(f"📡 Status da confirmação: {response.status_code}")
    print(f"📨 Resposta da API: {response.text}")
else:
    print("⚠️ Nenhum número de desenvolvedor encontrado. Confirmação não enviada.")
