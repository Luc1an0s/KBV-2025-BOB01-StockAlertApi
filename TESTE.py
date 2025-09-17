import smtplib
from email.mime.text import MIMEText

remetente = "stockalertapi@gmail.com"
senha = "exam vujb dpoz urba"
destinatario = "luciano.maciel@grupokbv.com"

mensagem = "Teste de envio de e-mail via script Python."

msg = MIMEText(mensagem)
msg["Subject"] = "Teste KBV"
msg["From"] = remetente
msg["To"] = destinatario

try:
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(remetente, senha)
        server.sendmail(remetente, destinatario, msg.as_string())
    print("📧 E-mail enviado com sucesso!")
except Exception as e:
    print(f"⚠️ Erro ao enviar e-mail: {e}")
