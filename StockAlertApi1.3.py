import requests
from dotenv import load_dotenv
import os

load_dotenv()

INSTANCE_ID = os.getenv('WHATSAPP_INSTANCE_ID')
TOKEN = os.getenv('WHATSAPP_TOKEN')
numero = os.getenv('WHATSAPP_NUMERO1')

mensagem = "Teste de envio"

url = f"https://api.ultramsg.com/{INSTANCE_ID}/messages/chat"
payload = {"token": TOKEN, "to": numero, "body": mensagem}

response = requests.post(url, data=payload)
print("Status:", response.status_code)
print("Resposta:", response.text)