import streamlit as st
import plotly.graph_objects as go
import pandas as pd

# Importar nuestros módulos
from src.data_pipeline import get_historical_data
from src.forecasting import train_and_forecast
from src.financial_math import calculate_forward_rate, calculate_potential_loss

# ==============================================================================
# Configuración inicial de la página en Streamlit
# ==============================================================================
st.set_page_config(
    page_title="FX Intelligence & Risk Platform",
    page_icon="📈",
    layout="wide"
)

# 1. Identidad y Transparencia
st.title("FX Intelligence & Risk Management Platform")
st.markdown("### **Elaborado por: Enrique Alejandro Gallegos Luna**")
st.markdown("---")

# ==============================================================================
# Pipeline de Datos
# ==============================================================================

# Función con caché para optimizar la descarga de datos desde Yahoo Finance
@st.cache_data(ttl=3600) # Cache expira cada hora
def load_data(years_history=3):
    return get_historical_data(years_history=years_history)

# ==============================================================================
# Sidebar: Inputs del Usuario
# ==============================================================================
st.sidebar.header("⚙️ Parámetros del Simulador")

st.sidebar.subheader("0. Configuración de Datos y Modelo")
# Fijo a 1 año de historia para evitar ruido en el forecast
years_history = 1


changepoint_prior = st.sidebar.slider(
    "Flexibilidad a cambios de tendencia", 
    min_value=0.01, max_value=0.5, value=0.05, step=0.01,
    help="Valores más altos hacen que el modelo reaccione más rápido a los cambios bruscos recientes. Valores bajos lo hacen más rígido a largo plazo."
)

interval_width = st.sidebar.slider(
    "Intervalo de confianza (Bandas)", 
    min_value=0.50, max_value=0.99, value=0.80, step=0.05,
    help="Probabilidad de que el tipo de cambio caiga dentro de las bandas. Un valor mayor ensancha las bandas."
)

st.sidebar.markdown("---")

# Descarga de datos
with st.spinner(f"Descargando datos históricos del USD/MXN de los últimos {years_history} años..."):
    try:
        df_historical = load_data(years_history)
        spot_actual = df_historical['y'].iloc[-1]
        fecha_actual = df_historical['ds'].iloc[-1]
    except Exception as e:
        st.error(f"Error al descargar los datos: {e}")
        st.stop()

# ==============================================================================
# Sidebar: Continuación
# ==============================================================================

st.sidebar.subheader("1. Pronóstico Estadístico")
n_days = st.sidebar.slider(
    "Días a predecir a futuro (N)", 
    min_value=1, max_value=30, value=15,
    help="Plazo en días para proyectar el tipo de cambio y sincronizar con el Forward."
)

st.sidebar.markdown("---")
st.sidebar.subheader("2. Parámetros Corporativos (Hedging)")

# Monto en dólares de la obligación
invoice_usd = st.sidebar.number_input(
    "Monto de la Factura (USD)", 
    min_value=1000.0, value=100000.0, step=1000.0
)

st.sidebar.markdown("**Tasas de Interés (Anuales)**")
# Tasas personalizadas para simular diversos escenarios macroeconómicos
tasa_mx = st.sidebar.number_input(
    "Tasa México (TIIE) %", 
    min_value=0.0, value=11.0, step=0.1
)
tasa_us = st.sidebar.number_input(
    "Tasa EUA (Fed Funds) %", 
    min_value=0.0, value=5.0, step=0.1
)

# ==============================================================================
# Ejecución del Modelo de Forecast
# ==============================================================================
with st.spinner("Entrenando modelo matemático de series de tiempo..."):
    model, forecast, metrics = train_and_forecast(
        df_historical, 
        n_days, 
        changepoint_prior_scale=changepoint_prior,
        interval_width=interval_width
    )

# Extraer los datos del último día de la proyección (Día N)
last_forecast = forecast.iloc[-1]
prediccion_central = last_forecast['yhat']
limite_superior = last_forecast['yhat_upper'] # Escenario de riesgo si el dólar se encarece
limite_inferior = last_forecast['yhat_lower']

# ==============================================================================
# Módulos Principales (Pestañas visuales)
# ==============================================================================
tab1, tab2 = st.tabs([
    "📊 Módulo 1: Pronóstico Estadístico y Bandas", 
    "🛡️ Módulo 2: Simulador de Cobertura Cambiaria"
])

# ------------------------------------------------------------------------------
# Pestaña 1: Pronóstico Estadístico
# ------------------------------------------------------------------------------
with tab1:
    st.header("Análisis Predictivo: Tipo de Cambio USD/MXN")
    
    # Explicación del contexto inicial
    st.info("""
    Contexto Inicial: ¿Qué estamos haciendo?
    Esta plataforma está diseñada para ayudar a las empresas (importadores o empresas con obligaciones en moneda extranjera) a gestionar su riesgo cambiario.
    
    Imagina que tienes que pagar una factura en dólares (USD) en un futuro cercano. Si el dólar sube, tendrás que desembolsar más pesos mexicanos (MXN) de lo planeado. 
    Aquí buscamos proteger a la empresa:
    1. En este Módulo 1 pronosticamos estadísticamente el comportamiento futuro del dólar.
    2. En el Módulo 2 decidimos si conviene comprar los dólares hoy a un precio pactado a futuro (contrato Forward) para congelar el precio, o si es mejor esperar y comprarlos al precio del mercado en la fecha de pago.
    """)
    
    # Nota Explicativa de Transparencia (Requerimiento para Banco BASE)
    st.info("""
    **Transparencia del Modelo - Gestión de Riesgos**
    
    Se utiliza el algoritmo **Prophet** (modelo aditivo de series de tiempo) o una aproximación similar. 
    En la gestión de riesgos corporativos, una predicción lineal simple ("point forecast") es 
    insuficiente porque no dimensiona la incertidumbre del mercado. Por ello, empleamos **intervalos de confianza 
    y bandas de volatilidad**, lo cual nos permite visualizar escenarios adversos y justificar matemáticamente 
    la contratación de instrumentos de cobertura como los contratos Forwards.
    """)
    
    # Métricas de validación con split histórico
    st.markdown("### Métricas del Modelo (Out-of-Sample)")
    col_m1, col_m2, col_m3 = st.columns(3)
    col_m1.metric("Tipo de Cambio Spot Actual", f"${spot_actual:.4f} MXN")
    if metrics:
        col_m2.metric("MAE (Error Absoluto Medio)", f"{metrics['MAE']:.4f}")
        col_m3.metric("RMSE (Raíz del Error Cuadrático)", f"{metrics['RMSE']:.4f}")
        
    st.markdown("---")
    st.subheader(f"Proyección a {n_days} días con Bandas de Volatilidad")
    
    # Mostrar los valores exactos de las bandas elásticas
    st.markdown("#### Valores Esperados al final del periodo")
    col_f1, col_f2, col_f3 = st.columns(3)
    col_f1.metric("Límite Inferior (Optimista)", f"${limite_inferior:.4f} MXN")
    col_f2.metric("Predicción Central", f"${prediccion_central:.4f} MXN")
    col_f3.metric("Límite Superior (Riesgo)", f"${limite_superior:.4f} MXN")
    
    st.markdown("<br>", unsafe_allow_html=True)

    # Gráfica interactiva con Plotly
    fig = go.Figure()

    # Filtramos para mostrar los últimos 180 días del histórico para mejor perspectiva visual
    hist_plot = df_historical.iloc[-180:]
    
    # 1. Línea del Histórico Real
    fig.add_trace(go.Scatter(
        x=hist_plot['ds'], y=hist_plot['y'],
        mode='lines', name='Histórico Real',
        line=dict(color='#1E88E5', width=2) # Azul corporativo
    ))

    # Definir la zona futura
    future_plot = forecast.iloc[-n_days:]
    
    # 2. Área de Incertidumbre (Bandas de Volatilidad yhat_upper y yhat_lower)
    fig.add_trace(go.Scatter(
        x=pd.concat([future_plot['ds'], future_plot['ds'][::-1]]),
        y=pd.concat([future_plot['yhat_upper'], future_plot['yhat_lower'][::-1]]),
        fill='toself',
        fillcolor='rgba(229, 57, 53, 0.2)', # Rojo translúcido de riesgo
        line=dict(color='rgba(255,255,255,0)'),
        name='Banda de Volatilidad (Incertidumbre)',
        showlegend=True
    ))

    # 3. Predicción Central
    fig.add_trace(go.Scatter(
        x=future_plot['ds'], y=future_plot['yhat'],
        mode='lines', name='Predicción Central',
        line=dict(color='#E53935', dash='dash', width=2) # Rojo punteado
    ))

    fig.update_layout(
        xaxis_title="Fecha",
        yaxis_title="Tipo de Cambio (MXN/USD)",
        hovermode="x unified",
        template="plotly_white",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    st.plotly_chart(fig, use_container_width=True)

# ------------------------------------------------------------------------------
# Pestaña 2: Simulador de Cobertura Cambiaria
# ------------------------------------------------------------------------------
with tab2:
    st.header("Simulador de Cobertura (Hedging) para Empresas")
    st.markdown("Análisis comparativo entre mantener exposición al mercado spot (riesgo abierto) frente a cerrar el tipo de cambio a futuro mediante un contrato Forward.")
    
    # Despliegue explícito de la Fórmula de Paridad de Tasas en LaTeX
    st.markdown("#### Fórmula Teórica de Paridad de Tasas de Interés")
    st.latex(r"Forward = TC_{Actual} \times \left[ 1 + (Tasa_{MX} - Tasa_{US}) \times \left( \frac{Plazo}{360} \right) \right]")
    
    # Cálculos financieros del Módulo 3
    tasa_mx_dec = tasa_mx / 100.0
    tasa_us_dec = tasa_us / 100.0
    
    forward_rate = calculate_forward_rate(spot_actual, tasa_mx_dec, tasa_us_dec, n_days)
    perdida_potencial = calculate_potential_loss(invoice_usd, spot_actual, limite_superior)
    
    st.markdown("---")
    st.subheader(f"Comparativa de Escenarios Financieros a {n_days} días")
    
    col_sc1, col_sc2 = st.columns(2)
    
    # Escenario 1: Pasivo (Riesgo abierto)
    with col_sc1:
        st.error("📉 **Escenario Pasivo (No hacer nada)**")
        st.write("Si la empresa no cubre la factura y el mercado se comporta de forma adversa (el dólar sube al límite superior proyectado):")
        st.write(f"- **Tipo de Cambio (Peor Escenario):** ${limite_superior:.4f} MXN")
        
        costo_pasivo = invoice_usd * limite_superior
        st.write(f"- **Costo Total Estimado:** ${costo_pasivo:,.2f} MXN")
        st.markdown(f"**⚠️ Pérdida Potencial Estimada (vs Spot):** `${perdida_potencial:,.2f} MXN`")
        
    # Escenario 2: Activo (Cobertura Forward)
    with col_sc2:
        st.success("🛡️ **Escenario Activo (Contratar Forward)**")
        st.write("La empresa fija el precio de la divisa hoy mediante un Forward, usando el diferencial de tasas y asegurando certidumbre.")
        st.write(f"- **Tipo de Cambio Forward pactado:** ${forward_rate:.4f} MXN")
        
        costo_activo = invoice_usd * forward_rate
        st.write(f"- **Costo Total Fijo:** ${costo_activo:,.2f} MXN")
        st.markdown("**✅ Riesgo de volatilidad del mercado:** `$0.00 MXN`")

    # Visualización visual del comparativo de riesgos
    st.markdown("### Visualización de Costos y Exposición al Riesgo")
    costo_spot = invoice_usd * spot_actual
    
    fig_bar = go.Figure()
    
    # Barras para la comparativa
    fig_bar.add_trace(go.Bar(
        x=['Costo Spot (Referencia Hoy)', 'Escenario Pasivo (Riesgo / Peor Caso)', 'Escenario Activo (Forward Seguro)'],
        y=[costo_spot, costo_pasivo, costo_activo],
        marker_color=['#9E9E9E', '#E53935', '#43A047'], # Gris, Rojo, Verde
        text=[f"${costo_spot:,.0f}", f"${costo_pasivo:,.0f}", f"${costo_activo:,.0f}"],
        textposition='auto',
    ))
    
    fig_bar.update_layout(
        title=f"Comparación del Costo de Pago de una Factura de ${invoice_usd:,.0f} USD en MXN",
        yaxis_title="Pesos Mexicanos (MXN)",
        template="plotly_white",
    )
    
    st.plotly_chart(fig_bar, use_container_width=True)
    
    # ------------------------------------------------------------------------------
    # Conclusión Estratégica Automática
    # ------------------------------------------------------------------------------
    st.markdown("---")
    st.subheader("💡 Conclusión y Recomendación Estratégica")
    
    if forward_rate <= prediccion_central:
        st.success(f"Recomendación: CONTRATAR FORWARD AHORA (Fuerte).\n\nArgumento Financiero: El mercado Forward ofrece un precio de \${forward_rate:.4f}, el cual es MÁS BARATO que la predicción central esperada por nuestro modelo estadístico (\${prediccion_central:.4f}) para dentro de {n_days} días. Estás comprando dólares 'con descuento' respecto a la expectativa matemática. Además, eliminas completamente el riesgo de que el tipo de cambio se dispare hasta el límite superior de \${limite_superior:.4f}.")
    elif forward_rate < limite_superior:
        st.warning(f"Recomendación: COBERTURA DEFENSIVA.\n\nArgumento Financiero: El precio Forward de \${forward_rate:.4f} es superior a la expectativa central (\${prediccion_central:.4f}), pero significativamente menor al peor escenario proyectado (\${limite_superior:.4f}). La diferencia actúa como la prima de un seguro; pagas un pequeño sobreprecio hoy debido al diferencial de tasas entre MX y US, pero evitas una pérdida catastrófica de hasta \${perdida_potencial:,.2f} MXN si el mercado sufre un shock imprevisto. Vale la pena cubrirse.")
    else:
        st.error(f"Recomendación: MANTENER EN SPOT (NO CUBRIR O BUSCAR OPCIONES).\n\nArgumento Financiero: El precio del contrato Forward (\${forward_rate:.4f}) es excesivamente caro, ya que supera incluso el peor escenario (límite superior de \${limite_superior:.4f}) proyectado por nuestro modelo estadístico con la volatilidad actual. En este momento, el diferencial de tasas hace que la cobertura tradicional sea estadísticamente perdedora. Es mejor esperar o evaluar opciones cambiarias más complejas.")
