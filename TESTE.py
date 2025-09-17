import requests
from datetime import datetime

numero_dev = "+559285094373"  # substitua pelo seu número real
url = "https://appbobinaskbv.bubbleapps.io/version-test/api/1.1/wf/enviamensagem"
agora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
mensagem = f"🛠️ Confirmação: script rodou com sucesso em {agora} (horário de Manaus)."

payload = {
    "celular": numero_dev,
    "mensagem": mensagem
}

response = requests.post(url, data=payload)
print(f"📡 Status: {response.status_code}")
print(f"📨 Resposta: {response.text}")