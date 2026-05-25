import streamlit as st
import pandas as pd
import plotly.express as px

# 1. CONFIGURACIÓN DE LA PÁGINA (Debe ser lo primero)
st.set_page_config(page_title="CineData Pro | Business Dashboard", layout="wide")

# 2. FUNCIÓN DE CARGA DE DATOS CON CACHÉ (Optimización Fase 8)
@st.cache_data
def cargar_datos():
    # Carga el archivo desde tu carpeta actual
    df = pd.read_parquet("dataset_final_limpio.parquet")
    
    # --- NORMALIZACIÓN DE COLUMNAS ---
    # Esto evita errores si los nombres vienen en inglés o español
    mapeo_columnas = {
        'revenue': 'ingresos',
        'budget': 'presupuesto',
        'title': 'titulo',
        'release_date': 'fecha_estreno',
        'vote_average': 'puntuacion_media'
    }
    
    # Renombramos solo las que existan en el dataset
    for original, nuevo in mapeo_columnas.items():
        if original in df.columns and nuevo not in df.columns:
            df = df.rename(columns={original: nuevo})

    # --- MANEJO DE FECHAS ---
    col_fecha = 'fecha_estreno'
    df[col_fecha] = pd.to_datetime(df[col_fecha])
    df['Año'] = df[col_fecha].dt.year
    
    # --- CÁLCULO DE GANANCIA NETA ---
    df['ganancia'] = df['ingresos'] - df['presupuesto']
    
    return df

# Ejecutamos la carga
df = cargar_datos()

# --- 3. SIDEBAR (FILTROS) ---
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/2503/2503508.png", width=100)
st.sidebar.title("Filtros")

st.sidebar.markdown("---")
# Filtro de Años
min_year, max_year = int(df['Año'].min()), int(df['Año'].max())
rango_anios = st.sidebar.slider("Rango de Años", min_year, max_year, (1990, 2017))

# Filtro Buscador
pelicula_buscada = st.sidebar.text_input("🔍 Buscar por título")

# Aplicar filtros al DataFrame
df_f = df[(df['Año'] >= rango_anios[0]) & (df['Año'] <= rango_anios[1])]
if pelicula_buscada:
    df_f = df_f[df_f['titulo'].str.contains(pelicula_buscada, case=False, na=False)]

# --- 4. CUERPO PRINCIPAL (DASHBOARD) ---
st.title("🎬 Dashboard de Negocio: Industria del Cine")
st.markdown(f"Mostrando datos de **{len(df_f)}** películas entre **{rango_anios[0]} y {rango_anios[1]}**")

# Métricas Clave
st.info("Resumen Ejecutivo")
m1, m2, m3, m4 = st.columns(4)
with m1:
    st.metric("Recaudación Total", f"${df_f['ingresos'].sum()*1e-9:.2f}B")
with m2:
    st.metric("Presupuesto Medio", f"${df_f['presupuesto'].mean()*1e-6:.1f}M")
with m3:
    st.metric("Ganancia Máxima", f"${df_f['ganancia'].max()*1e-6:.0f}M")
with m4:
    st.metric("Rating Promedio", f"{df_f['puntuacion_media'].mean():.2f} ⭐")

st.markdown("---")

# Gráficos
col_izq, col_der = st.columns(2)

with col_izq:
    st.subheader("🏆 Top 10 Películas por Ingresos")
    top_10 = df_f.sort_values('ingresos', ascending=False).head(10)
    fig_bar = px.bar(top_10, x='ingresos', y='titulo', orientation='h',
                     color='ingresos', color_continuous_scale='Viridis',
                     labels={'ingresos': 'USD', 'titulo': ''})
    fig_bar.update_layout(yaxis={'categoryorder':'total ascending'})
    st.plotly_chart(fig_bar, use_container_width=True)

with col_der:
    st.subheader("💰 Inversión vs Retorno")
    fig_scatter = px.scatter(df_f, x='presupuesto', y='ingresos',
                             hover_name='titulo', color='puntuacion_media',
                             color_continuous_scale='RdYlGn',
                             labels={'presupuesto': 'Presupuesto', 'ingresos': 'Ingresos'})
    st.plotly_chart(fig_scatter, use_container_width=True)

# Evolución Temporal
st.subheader("📈 Evolución de Ingresos y Presupuesto")
evol = df_f.groupby('Año')[['ingresos', 'presupuesto']].sum().reset_index()
fig_area = px.area(evol, x='Año', y=['ingresos', 'presupuesto'],
                   color_discrete_map={'ingresos': '#27ae60', 'presupuesto': '#e74c3c'})
st.plotly_chart(fig_area, use_container_width=True)

# --- 5. CONCLUSIONES ---
st.divider()
st.success(f"**Conclusión de Negocio:** En el rango seleccionado, la industria muestra un crecimiento sólido. "
           f"La película con mayor éxito comercial fue **{top_10.iloc[0]['titulo']}**.")