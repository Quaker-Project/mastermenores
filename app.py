import smtplib
from email.mime.text import MIMEText
from datetime import datetime, timedelta
import pandas as pd

EMAIL = "tu_email@gmail.com"
PASSWORD = "TU_APP_PASSWORD"
DESTINATARIOS = ["email1@gmail.com", "email2@gmail.com"]

def enviar_email(asunto, mensaje):
    msg = MIMEText(mensaje)
    msg["Subject"] = asunto
    msg["From"] = EMAIL
    msg["To"] = ", ".join(DESTINATARIOS)

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(EMAIL, PASSWORD)
        server.send_message(msg)

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

        # PRIORIDAD
        emoji = "🔵"
        if row["prioridad"] == "alta":
            emoji = "🔴"
        elif row["prioridad"] == "media":
            emoji = "🟠"

        mensaje = f"""
{emoji} {row['tarea']}
Fecha: {fecha_evento.strftime('%d/%m %H:%M')}
Responsable: {row['responsable']}
Tipo: {row['tipo']}
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

        # EVITAR DUPLICADOS
        clave_aviso = f"{tipo_aviso}_{fecha_evento}"

        if enviar and clave_aviso != ultimo_aviso:

            asunto = f"[AGENDA] {tipo_aviso} - {row['tarea']}"

            enviar_email(asunto, mensaje)

            conn.execute(
                "UPDATE tareas SET ultimo_aviso=? WHERE id=?",
                (clave_aviso, row["id"])
            )
            conn.commit()
