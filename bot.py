import smtplib
from email.mime.text import MIMEText
from datetime import datetime, timedelta
import pandas as pd

# CONFIGURACIÓN
EMAIL = "diego.maldonado@uma.es"
PASSWORD = "ibxr uxiw unnl zmfm"

# Emails por defecto (fallback)
DESTINATARIOS_DEFAULT = [
    "diego.maldonado@uma.es",
    "maria.izco@uma.es"
]

# ENVÍO EMAIL
def enviar_email(destinatarios, asunto, mensaje_html):
    msg = MIMEText(mensaje_html, "html")
    msg["Subject"] = asunto
    msg["From"] = EMAIL
    msg["To"] = ", ".join(destinatarios)

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(EMAIL, PASSWORD)
        server.send_message(msg)

# FUNCIÓN PRINCIPAL
def enviar_recordatorios(conn):
    df = pd.read_sql("SELECT * FROM tareas", conn)
    ahora = datetime.now()

    for _, row in df.iterrows():

        if row["estado"] != "pendiente":
            continue

        fecha_evento = datetime.strptime(
            row["fecha"] + " " + row["hora"],
            "%Y-%m-%d %H:%M:%S"
        )

        ultimo_aviso = row["ultimo_aviso"]

        # PRIORIDAD → emoji + texto
        emoji = "🔵"
        prioridad_txt = "BAJA"

        if row["prioridad"] == "alta":
            emoji = "🔴"
            prioridad_txt = "ALTA"
        elif row["prioridad"] == "media":
            emoji = "🟠"
            prioridad_txt = "MEDIA"

        # MENSAJE HTML BONITO
        mensaje_html = f"""
        <h3>{emoji} {row['tarea']}</h3>
        <p><b>📅 Fecha:</b> {fecha_evento.strftime('%d/%m/%Y %H:%M')}</p>
        <p><b>👤 Responsable:</b> {row['responsable']}</p>
        <p><b>📌 Tipo:</b> {row['tipo']}</p>
        <p><b>🔥 Prioridad:</b> {prioridad_txt}</p>
        """

        enviar = False
        tipo_aviso = ""

        # AVISO DÍAS
        if ahora >= fecha_evento - timedelta(days=row["aviso_dias"]) and ahora < fecha_evento:
            tipo_aviso = "Aviso previo"
            enviar = True

        # AVISO HORAS
        if ahora >= fecha_evento - timedelta(hours=row["aviso_horas"]) and ahora < fecha_evento:
            tipo_aviso = "Aviso cercano"
            enviar = True

        # MISMO DÍA
        if ahora.date() == fecha_evento.date() and row["aviso_mismo_dia"] == "sí":
            tipo_aviso = "HOY"
            enviar = True

        # CLAVE ANTI-DUPLICADOS
        clave_aviso = f"{tipo_aviso}_{fecha_evento}"

        if enviar and clave_aviso != ultimo_aviso:

            # DESTINATARIOS INTELIGENTES
            if "@" in row["responsable"]:
                destinatarios = [row["responsable"]]
            else:
                destinatarios = DESTINATARIOS_DEFAULT

            # ASUNTO CON PRIORIDAD
            asunto = f"[{prioridad_txt}] {tipo_aviso} - {row['tarea']}"

            enviar_email(destinatarios, asunto, mensaje_html)

            conn.execute(
                "UPDATE tareas SET ultimo_aviso=? WHERE id=?",
                (clave_aviso, row["id"])
            )
            conn.commit()
