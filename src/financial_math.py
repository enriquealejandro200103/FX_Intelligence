def calculate_forward_rate(spot_rate, rate_mx, rate_us, days):
    """
    Calcula el Tipo de Cambio Forward teórico usando la fórmula de paridad de tasas de interés.
    
    Parámetros:
    - spot_rate: Tipo de cambio actual (Spot)
    - rate_mx: Tasa de interés de México (en formato decimal, ej. 0.11 para 11%)
    - rate_us: Tasa de interés de EUA (en formato decimal, ej. 0.05 para 5%)
    - days: Plazo en días del Forward
    
    Retorna:
    - Tipo de Cambio Forward estimado
    """
    forward = spot_rate * (1 + (rate_mx - rate_us) * (days / 360.0))
    return forward

def calculate_potential_loss(invoice_usd, spot_rate, worst_case_rate):
    """
    Calcula la pérdida potencial (en pesos mexicanos) en un escenario pasivo 
    (sin cobertura) si el tipo de cambio sube al límite superior de la volatilidad.
    
    Parámetros:
    - invoice_usd: Monto de la obligación en Dólares
    - spot_rate: Tipo de cambio actual
    - worst_case_rate: Tipo de cambio del peor escenario (Límite superior estimado)
    
    Retorna:
    - El monto extra en MXN que la empresa tendría que pagar
    """
    cost_at_spot = invoice_usd * spot_rate
    cost_at_worst = invoice_usd * worst_case_rate
    
    # Solo consideramos pérdida si el costo en el peor escenario es mayor al actual
    # (Un importador pierde si el dólar sube)
    potential_loss = cost_at_worst - cost_at_spot
    return max(0, potential_loss)
