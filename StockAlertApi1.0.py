from fastapi import FastAPI
import mysql.connector
import requests
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASS"),
    "database": os.getenv("DB_NAME")
}

WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
WHATSAPP_INSTANCE_ID = os.getenv("WHATSAPP_INSTANCE_ID")
WHATSAPP_PHONE = os.getenv("WHATSAPP_PHONE")


@app.get("/enviar-estoque-wpp")
def enviar_estoque():
    # Conectar ao banco
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor(dictionary=True)

    # Query SQL principal
    cursor.execute("""
        SELECT
    c.Loja,
    c.Codigo,
    c.Produto,
    c.Ha_6_meses,
    c.Ha_5_meses,
    c.Ha_4_meses,
    c.Ha_3_meses,
    c.Ha_2_meses,
    c.Ha_1_mes,
    c.Media_Semestral,
    c.Projecao_Anual,
    c.Projecao_Com_20_Percento,
    c.Viajando,
    COALESCE(stksa.qtty_varejo / 1000, 0) AS Quantidade_Estoque,
    COALESCE(c.Viajando, 0) + COALESCE(stksa.qtty_varejo / 1000, 0) AS Estoque_Parcial

FROM (
    SELECT
        xaprd2.storeno AS Loja,
        xaprd2.prdno AS Codigo,
        prd.name AS Produto,

        SUM(CASE WHEN MONTH(STR_TO_DATE(xaprd2.date, '%Y%m%d')) = MONTH(DATE_SUB(CURDATE(), INTERVAL 6 MONTH))
                  AND YEAR(STR_TO_DATE(xaprd2.date, '%Y%m%d')) = YEAR(DATE_SUB(CURDATE(), INTERVAL 6 MONTH))
             THEN xaprd2.qtty / 1000 ELSE 0 END) AS Ha_6_meses,

        SUM(CASE WHEN MONTH(STR_TO_DATE(xaprd2.date, '%Y%m%d')) = MONTH(DATE_SUB(CURDATE(), INTERVAL 5 MONTH))
                  AND YEAR(STR_TO_DATE(xaprd2.date, '%Y%m%d')) = YEAR(DATE_SUB(CURDATE(), INTERVAL 5 MONTH))
             THEN xaprd2.qtty / 1000 ELSE 0 END) AS Ha_5_meses,

        SUM(CASE WHEN MONTH(STR_TO_DATE(xaprd2.date, '%Y%m%d')) = MONTH(DATE_SUB(CURDATE(), INTERVAL 4 MONTH))
                  AND YEAR(STR_TO_DATE(xaprd2.date, '%Y%m%d')) = YEAR(DATE_SUB(CURDATE(), INTERVAL 4 MONTH))
             THEN xaprd2.qtty / 1000 ELSE 0 END) AS Ha_4_meses,

        SUM(CASE WHEN MONTH(STR_TO_DATE(xaprd2.date, '%Y%m%d')) = MONTH(DATE_SUB(CURDATE(), INTERVAL 3 MONTH))
                  AND YEAR(STR_TO_DATE(xaprd2.date, '%Y%m%d')) = YEAR(DATE_SUB(CURDATE(), INTERVAL 3 MONTH))
             THEN xaprd2.qtty / 1000 ELSE 0 END) AS Ha_3_meses,

        SUM(CASE WHEN MONTH(STR_TO_DATE(xaprd2.date, '%Y%m%d')) = MONTH(DATE_SUB(CURDATE(), INTERVAL 2 MONTH))
                  AND YEAR(STR_TO_DATE(xaprd2.date, '%Y%m%d')) = YEAR(DATE_SUB(CURDATE(), INTERVAL 2 MONTH))
             THEN xaprd2.qtty / 1000 ELSE 0 END) AS Ha_2_meses,

        SUM(CASE WHEN MONTH(STR_TO_DATE(xaprd2.date, '%Y%m%d')) = MONTH(DATE_SUB(CURDATE(), INTERVAL 1 MONTH))
                  AND YEAR(STR_TO_DATE(xaprd2.date, '%Y%m%d')) = YEAR(DATE_SUB(CURDATE(), INTERVAL 1 MONTH))
             THEN xaprd2.qtty / 1000 ELSE 0 END) AS Ha_1_mes,

        SUM(xaprd2.qtty / 1000) / 6 AS Media_Semestral,
        SUM(xaprd2.qtty / 1000) / 6 * 12 AS Projecao_Anual,
        SUM(xaprd2.qtty / 1000) / 6 * 12 * 1.2 AS Projecao_Com_20_Percento,

        COALESCE(v.Viajando, 0) AS Viajando

    FROM
        xaprd2
    INNER JOIN prd ON xaprd2.prdno = prd.no
    LEFT JOIN (
        SELECT
            oprd_agg.prdno,
            TRUNCATE(SUM(oprd_agg.saldo_pendente), 0) AS Viajando
        FROM (
            SELECT
                oprd.prdno,
                oprd.ordno,
                SUM(oprd.qtty - oprd.qttyRcv) AS saldo_pendente
            FROM oprd
            WHERE oprd.storeno in (37, 38, 50, 93, 69, 83, 49, 33, 68, 41, 42, 47, 48, 35, 40, 43, 51, 53)
            GROUP BY oprd.prdno, oprd.ordno
        ) oprd_agg
        JOIN (
            SELECT DISTINCT no
            FROM ords
            WHERE date BETWEEN '20250101' AND DATE_FORMAT(CURDATE(), '%Y%m%d')
        ) ords_filtradas ON oprd_agg.ordno = ords_filtradas.no
        GROUP BY oprd_agg.prdno
    ) v ON v.prdno = xaprd2.prdno

    WHERE
        xaprd2.storeno in (37, 38, 50, 93, 69, 83, 49, 33, 68, 41, 42, 47, 48, 35, 40, 43, 51, 53)
        AND STR_TO_DATE(xaprd2.date, '%Y%m%d') BETWEEN
            DATE_FORMAT(DATE_SUB(CURDATE(), INTERVAL 6 MONTH), '%Y-%m-01')
            AND LAST_DAY(DATE_SUB(CURDATE(), INTERVAL 1 MONTH))
        AND cfo1 IN (5117, 5116, 5101, 5102, 5405, 6102, 6101, 6403, 6116, 6117)

    GROUP BY
        xaprd2.storeno,
        xaprd2.prdno,
        prd.name,
        v.Viajando
    """)
    produtos = cursor.fetchall()
    cursor.close()
    conn.close()

    # Filtrar produtos com estoque
    produtos_com_estoque = [p for p in produtos if p["Estoque_Parcial"] > 0]

    if not produtos_com_estoque:
        return {"status": "Sem produtos com estoque"}

    # Montar mensagem
    mensagem = "📦 Produtos com estoque disponível:\n\n"
    for p in produtos_com_estoque:
        mensagem += f"• {p['Produto']} (Loja {p['Loja']}) - {p['Estoque_Parcial']} kg\n"

    # Enviar mensagem pelo WhatsApp
    payload = {
        "token": WHATSAPP_TOKEN,
        "to": WHATSAPP_PHONE,
        "body": mensagem
    }

    resp = requests.post(
        f"https://api.ultramsg.com/{WHATSAPP_INSTANCE_ID}/messages/chat",
        data=payload
    )

    return {"status": "Mensagem enviada", "resposta_whatsapp": resp.json()}
