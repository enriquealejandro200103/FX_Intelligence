# 📈 FX Intelligence & Risk Management Platform

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-App-FF4B4B.svg)
![Prophet](https://img.shields.io/badge/Model-Prophet-00A9E0.svg)

Una plataforma interactiva desarrollada en Python y Streamlit diseñada para ayudar a las empresas (como importadores o corporativos con obligaciones en el extranjero) a gestionar su riesgo cambiario (USD/MXN).

El proyecto simula el entorno de un analista o estratega financiero: fusiona la extracción de datos financieros en tiempo real, el pronóstico estadístico mediante Series de Tiempo y la evaluación matemática de instrumentos de cobertura (Derivados Financieros: Contratos Forwards).

## 🚀 ¿Qué problema resuelve?

Cuando una empresa tiene que pagar facturas en dólares en una fecha futura, está expuesta a la volatilidad del tipo de cambio. Si el dólar sube inesperadamente, la empresa pierde dinero. 

Esta herramienta le permite a la tesorería corporativa:
1. **Modelar matemáticamente** hacia dónde se dirige el tipo de cambio y visualizar el peor escenario estadístico (bandas de volatilidad).
2. **Tomar decisiones estratégicas informadas** para determinar si conviene asegurar el precio del dólar hoy mismo a través de un contrato *Forward*, o si es más barato asumir el riesgo de mercado.

## ⚙️ Arquitectura y Estructura del Código

El proyecto está diseñado bajo buenas prácticas de ingeniería de software, de forma modular y limpia, separando las responsabilidades de conexión a datos, inteligencia artificial, finanzas y la capa visual.

```text
📁 Proyecto de divisas
├── 📄 app.py                  # Entry-point de la aplicación. Interfaz web interactiva (Streamlit).
└── 📁 src/                    # Módulos Core de la lógica de negocio.
    ├── 📄 data_pipeline.py    # ETL: Extracción de datos en vivo desde Yahoo Finance.
    ├── 📄 forecasting.py      # IA: Implementación y entrenamiento del modelo Prophet.
    └── 📄 financial_math.py   # Finanzas: Fórmulas de paridad de tasas de interés y valuación.
```

### 🧠 Módulos Clave
- **`data_pipeline.py`**: Se conecta a la API de `yfinance` para extraer el histórico del par USD/MXN. Realiza la limpieza, el formateo de fechas y el pre-procesamiento requerido para evitar ruido en el algoritmo. Filtra datos a solo el último año para capturar la tendencia de mercado actual.
- **`forecasting.py`**: Utiliza el algoritmo `Prophet`. Calcula una predicción central y devuelve intervalos de confianza parametrizables por el usuario (bandas elásticas de riesgo). Evalúa internamente sus métricas de error (MAE y RMSE).
- **`financial_math.py`**: Calcula el valor de un contrato Forward teórico utilizando el diferencial de las tasas de interés libres de riesgo entre México (TIIE) y Estados Unidos (Fed Funds) a través del tiempo exacto al vencimiento.

## 📊 Paneles de la Plataforma (UI)

1. **Pronóstico Estadístico (Módulo 1)**: Visualización interactiva (vía `Plotly`) del comportamiento histórico real y la proyección a futuro. Detalla explícitamente los límites de optimismo y de riesgo catastrófico.
2. **Simulador de Cobertura (Módulo 2)**: Panel comparativo automático. La plataforma evalúa el costo total de dejar el riesgo abierto (Mercado Spot) vs. asegurarlo (Mercado Forward) y **despliega dinámicamente una recomendación argumentada** en color semaforizado (Comprar cobertura fuerte, defensiva o descartarla).

## 🛠️ Cómo Ejecutar de forma local

1. Clona este repositorio.
2. Instala las dependencias necesarias:
   ```bash
   pip install pandas numpy streamlit plotly yfinance prophet scikit-learn
   ```
3. Levanta el servidor local de Streamlit:
   ```bash
   streamlit run app.py
   ```
   
---
*Elaborado por: **Enrique Alejandro Gallegos Luna***
