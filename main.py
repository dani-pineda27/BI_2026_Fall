import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import streamlit as st
from mplsoccer import Pitch
from statsbombpy import sb

# Configuración inicial de la página
st.set_page_config(page_title="StatsBomb Pass Visualizer", layout="wide")
st.title("⚽ Visualizador de Pases - StatsBomb")

# Carga de datos optimizada con cache para evitar llamadas innecesarias a la API
@st.cache_data
def load_match_events(match_id):
    events = sb.events(match_id=match_id)

    variables = [
        'pass_end_location',
        'pass_recipient',
        'minute',
        'period',
        'location',
        'player',
        'second',
        'team',
        'type',
    ]

    # Filtrar eventos existentes y tipo Pass
    available_vars = [v for v in variables if v in events.columns]
    passes = events[available_vars]
    passes = passes[passes['type'] == 'Pass'].copy()

    # Extraer coordenadas
    passes['x0'] = passes.location.apply(lambda x: x[0])
    passes['y0'] = passes.location.apply(lambda x: x[1])
    passes['x1'] = passes.pass_end_location.apply(lambda x: x[0])
    passes['y1'] = passes.pass_end_location.apply(lambda x: x[1])

    return passes


# Cargar eventos del partido (Japón vs ...)
MATCH_ID = 3857255
df_passes = load_match_events(MATCH_ID)

# Control interactivo en la barra lateral (reemplaza ipywidgets)
st.sidebar.header("Filtros")
min_minute = int(df_passes['minute'].min())
max_minute = int(df_passes['minute'].max())

minuto_seleccionado = st.sidebar.slider(
    "Selecciona el minuto del partido:",
    min_value=min_minute,
    max_value=max_minute,
    value=1,
    step=1,
)

# Renderizar el mapa de pase
st.subheader(f"Pases registrados en el minuto {minuto_seleccionado}")

passes_minuto = df_passes[df_passes['minute'] == minuto_seleccionado]

if passes_minuto.empty:
    st.info("No se registraron pases en este minuto.")
else:
    pitch = Pitch(pitch_color="grass", line_color="white", stripe=True)
    fig, ax = pitch.draw(figsize=(10, 7))

    sns.scatterplot(
        data=passes_minuto,
        x="x0",
        y="y0",
        hue="team",
        s=100,
        ax=ax,
        palette="tab10",
    )
    plt.legend(loc="upper center", bbox_to_anchor=(0.5, 1.05), ncol=2)

    # Mostrar gráfico en Streamlit
    st.pyplot(fig)
