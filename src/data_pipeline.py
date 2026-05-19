import yfinance as yf
import pandas as pd
from datetime import datetime

def get_historical_data(ticker="MXN=X", years_history=3):
    """
    Extrae los datos históricos del tipo de cambio.
    
    Parámetros:
    - ticker: Ticker de Yahoo Finance (por defecto MXN=X para Dólar/Peso)
    - years_history: Años de historia a descargar (por defecto 3)
    
    Retorna:
    - pd.DataFrame con columnas 'ds' (fecha) y 'y' (precio de cierre) listos para Prophet.
    """
    # 1. Calcular la fecha de inicio dinámicamente (iniciando siempre en enero del año correspondiente)
    current_year = datetime.now().year
    start_year = current_year - years_history
    start_date = f"{start_year}-01-01"

    
    # 2. Descargar datos usando yfinance
    df = yf.download(ticker, start=start_date, progress=False)
    
    # 3. Limpieza y formateo de datos
    # Recientemente yfinance puede retornar DataFrames con MultiIndex en las columnas.
    # Si detectamos un MultiIndex, lo aplanamos para tomar solo el nombre principal de la métrica (ej. 'Close').
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = [col[0] for col in df.columns]
        
    # El índice suele ser la Fecha (Date o Datetime), lo pasamos a una columna normal
    df.reset_index(inplace=True)
    
    # Seleccionamos la primera columna (que es la Fecha) y la columna de Cierre (Close)
    # Esto evita problemas si la columna se llama 'Date' o 'Datetime'
    df = df[[df.columns[0], 'Close']]
    
    # Eliminamos cualquier valor nulo que pudiera venir en la serie
    df = df.dropna()
    
    # Renombrar columnas para consistencia y uso directo con Prophet
    df.columns = ['ds', 'y']
    
    # Asegurar que 'ds' sea un objeto datetime sin zona horaria para evitar advertencias de Prophet
    df['ds'] = pd.to_datetime(df['ds']).dt.tz_localize(None)
    
    return df
