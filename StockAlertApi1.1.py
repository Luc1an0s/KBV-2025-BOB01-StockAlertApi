from fastapi import FastAPI
import requests
import os
from dotenv import load_dotenv
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime

load_dotenv()

app = FastAPI()

WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
WHATSAPP_INSTANCE_ID = os.getenv("WHATSAPP_INSTANCE_ID")
WHATSAPP_PHONE = os.getenv("WHATSAPP_PHONE")


def enviar_mensagem_whatsapp():
    mensagem = """
📦 Produtos com estoque disponível (SIMULADO):

• Produto A (Loja 1) - 10 kg
• Produto B (Loja 2) - 5 kg
• Produto C (Loja 3) - 12.5 kg
"""

    payload = {
        "token": WHATSAPP_TOKEN,
        "to": WHATSAPP_PHONE,
        "body": mensagem
    }

    try:
        response = requests.post(
            f"https://api.ultramsg.com/{WHATSAPP_INSTANCE_ID}/messages/chat",
            data=payload
        )
        print(f"[{datetime.now()}] Mensagem enviada com sucesso!")
        return response.json()

    except Exception as e:
        print(f"[{datetime.now()}] Erro ao enviar mensagem: {e}")
        return None


# Agendador de tarefas
scheduler = BackgroundScheduler()

# ⏰ Agende aqui o horário que quiser (ex: todos os dias às 08:00)
scheduler.add_job(enviar_mensagem_whatsapp, 'cron', hour=10, minute=0)

scheduler.start()


@app.on_event("shutdown")
def shutdown_event():
    scheduler.shutdown()


# Endpoint manual para testar
@app.get("/testar-envio")
def testar_envio():
    resultado = enviar_mensagem_whatsapp()
    return {
        "status": "Mensagem enviada manualmente (simulada)",
        "resposta": resultado
    }
