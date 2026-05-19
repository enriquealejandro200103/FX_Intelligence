import pandas as pd
import numpy as np
from prophet import Prophet
from sklearn.metrics import mean_absolute_error, mean_squared_error
import logging

# Desactivar logs innecesarios de Prophet (CmdStanPy) para mantener limpia la consola
logging.getLogger('prophet').setLevel(logging.WARNING)

def train_and_forecast(df, periods, changepoint_prior_scale=0.05, interval_width=0.80):
    """
    Entrena el modelo de series de tiempo Prophet y proyecta N días hacia el futuro.
    
    Parámetros:
    - df: DataFrame con los datos históricos (columnas 'ds' y 'y')
    - periods: Número de días (N) a predecir hacia el futuro
    - changepoint_prior_scale: Flexibilidad del modelo ante cambios de tendencia
    - interval_width: Nivel de confianza para las bandas de volatilidad (ej. 0.80 para 80%)
    
    Retorna:
    - model_final: El modelo Prophet entrenado
    - forecast: DataFrame con predicciones, incluyendo límite superior e inferior
    - metrics: Diccionario con métricas de evaluación (MAE, RMSE)
    """
    
    # 1. Split de validación para calcular métricas (Rigor Metodológico)
    # Tomaremos los últimos 30 días reales para evaluar el modelo internamente
    val_days = 30
    if len(df) > val_days:
        train_df = df.iloc[:-val_days]
        test_df = df.iloc[-val_days:]
    else:
        train_df = df
        test_df = pd.DataFrame()

    metrics = {}
    
    # Si tenemos suficientes datos, calculamos el MAE y RMSE real
    if not test_df.empty:
        # Modelo de validación (entrenado sin los últimos 30 días)
        model_val = Prophet(
            daily_seasonality=False, 
            yearly_seasonality=True, 
            weekly_seasonality=True,
            changepoint_prior_scale=changepoint_prior_scale,
            interval_width=interval_width
        )
        model_val.fit(train_df)
        
        future_val = model_val.make_future_dataframe(periods=val_days)
        forecast_val = model_val.predict(future_val)
        
        y_true = test_df['y'].values
        y_pred = forecast_val.iloc[-val_days:]['yhat'].values
        
        metrics['MAE'] = mean_absolute_error(y_true, y_pred)
        metrics['RMSE'] = np.sqrt(mean_squared_error(y_true, y_pred))

    # 2. Entrenar modelo final con TODOS los datos disponibles para la predicción real
    model_final = Prophet(
        daily_seasonality=False, 
        yearly_seasonality=True, 
        weekly_seasonality=True,
        changepoint_prior_scale=changepoint_prior_scale,
        interval_width=interval_width
    )
    model_final.fit(df)
    
    # 3. Proyectar 'periods' días en el futuro
    future = model_final.make_future_dataframe(periods=periods)
    forecast = model_final.predict(future)
    
    return model_final, forecast, metrics
