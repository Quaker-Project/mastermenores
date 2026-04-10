import streamlit as st
import sqlite3
import pandas as pd
from bot import enviar_recordatorios

# DB
conn = sqlite3.connect("database.db", check_same_thread=False)
c = conn.cursor()

c.execute('''CREATE TABLE IF NOT EXISTS tareas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tarea TEXT,
    fecha TEXT,
    hora TEXT,
    tipo TEXT,
    prioridad TEXT,
    aviso_dias INTEGER,
    aviso_horas INTEGER,
    aviso_mismo_dia TEXT,
    responsable TEXT,
    estado TEXT,
    ultimo_aviso TEXT
)''')

conn.commit()

st.title("📅 Agenda Máster")

# FORMULARIO
with st.form("form"):
    tarea = st.text_input("Tarea")
    fecha = st.date_input("Fecha")
    hora = st.time_input("Hora")
    tipo = st.selectbox("Tipo", ["deadline","reunión"])
    prioridad = st.selectbox("Prioridad", ["alta","media","baja"])
    aviso_dias = st.number_input("Aviso días antes", 0, 30, 1)
    aviso_horas = st.number_input("Aviso horas antes", 0, 48, 2)
    aviso_mismo_dia = st.selectbox("Aviso mismo día", ["sí","no"])
    responsable = st.text_input("Responsable (email o nombre)")

    if st.form_submit_button("Añadir tarea"):
        c.execute("""
        INSERT INTO tareas 
        (tarea, fecha, hora, tipo, prioridad, aviso_dias, aviso_horas, aviso_mismo_dia, responsable, estado, ultimo_aviso)
        VALUES (?,?,?,?,?,?,?,?,?,?,?)
        """, (
            tarea,
            str(fecha),
            str(hora),
            tipo,
            prioridad,
            aviso_dias,
            aviso_horas,
            aviso_mismo_dia,
            responsable,
            "pendiente",
            ""
        ))
        conn.commit()
        st.success("Tarea añadida")

# TABLA
df = pd.read_sql("SELECT * FROM tareas", conn)

st.subheader("📋 Tareas")

filtro = st.selectbox("Filtrar estado", ["todas","pendiente","hecho"])

if filtro != "todas":
    df = df[df["estado"] == filtro]

st.dataframe(df)

# MARCAR HECHO
id_done = st.number_input("ID tarea completada", 0, 10000, 0)

if st.button("Marcar como hecho"):
    c.execute("UPDATE tareas SET estado='hecho' WHERE id=?", (id_done,))
    conn.commit()
    st.success("Actualizado")

# BOTÓN RECORDATORIOS
if st.button("🔔 Enviar recordatorios"):
    enviar_recordatorios(conn)
    st.success("Recordatorios enviados")
