import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np

def generar_graficos_evolucion(results_df, enfermedad_nombre):
    """
    Genera gráficos interactivos de la evolución de la epidemia
    
    Args:
        results_df: DataFrame con resultados de simulación
        enfermedad_nombre: Nombre de la enfermedad para el título
    
    Returns:
        HTML string con los gráficos
    """
    # Verificar que hay datos
    if results_df.empty:
        return "<p style='color: red;'>❌ No hay datos para mostrar</p>"
    
    # Datos globales por día
    datos_globales = results_df.groupby('day').agg({
        'susceptible': 'sum',
        'infected': 'sum',
        'recovered': 'sum',
        'dead': 'sum'
    }).reset_index()
    
    # Crear figura con subplots (2x2)
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('📈 Evolución de Infectados', '💀 Acumulado de Muertos',
                       '📊 Curva SIR Completa', '🏆 Top 10 Países Afectados'),
        specs=[[{'secondary_y': False}, {'secondary_y': False}],
               [{'secondary_y': False}, {'secondary_y': False}]]
    )
    
    # Gráfico 1: Infectados en el tiempo
    fig.add_trace(
        go.Scatter(
            x=datos_globales['day'], 
            y=datos_globales['infected'],
            mode='lines+markers', 
            name='Infectados',
            line=dict(color='#FF4444', width=3),
            marker=dict(size=6)
        ),
        row=1, col=1
    )
    
    # Gráfico 2: Muertos acumulados
    fig.add_trace(
        go.Scatter(
            x=datos_globales['day'], 
            y=datos_globales['dead'],
            mode='lines+markers', 
            name='Muertos',
            line=dict(color='#444444', width=3),
            marker=dict(size=6)
        ),
        row=1, col=2
    )
    
    # Gráfico 3: Curva SIR completa
    fig.add_trace(
        go.Scatter(
            x=datos_globales['day'], 
            y=datos_globales['susceptible'],
            mode='lines', 
            name='Susceptibles',
            line=dict(color='#3366CC', width=2)
        ),
        row=2, col=1
    )
    fig.add_trace(
        go.Scatter(
            x=datos_globales['day'], 
            y=datos_globales['infected'],
            mode='lines', 
            name='Infectados',
            line=dict(color='#FF4444', width=2)
        ),
        row=2, col=1
    )
    fig.add_trace(
        go.Scatter(
            x=datos_globales['day'], 
            y=datos_globales['recovered'],
            mode='lines', 
            name='Recuperados',
            line=dict(color='#44AA44', width=2)
        ),
        row=2, col=1
    )
    
    # Gráfico 4: Top 10 países
    ultimo_dia = results_df[results_df['day'] == results_df['day'].max()]
    top10 = ultimo_dia.nlargest(10, 'infected')[['region_id', 'infected', 'dead', 'recovered']].copy()
    
    fig.add_trace(
        go.Bar(
            x=top10['region_id'], 
            y=top10['infected'],
            name='Infectados',
            marker_color='#FF4444',
            text=top10['infected'].apply(lambda x: f'{x:,.0f}'),
            textposition='auto'
        ),
        row=2, col=2
    )
    
    fig.add_trace(
        go.Bar(
            x=top10['region_id'], 
            y=top10['dead'],
            name='Muertos',
            marker_color='#444444',
            text=top10['dead'].apply(lambda x: f'{x:,.0f}'),
            textposition='auto'
        ),
        row=2, col=2
    )
    
    # Actualizar layout
    fig.update_layout(
        height=800, 
        showlegend=True,
        title_text=f"📊 Evolución de {enfermedad_nombre} - Día {results_df['day'].max()}",
        title_font_size=20,
        hovermode='x unified',
        template='plotly_white'
    )
    
    # Actualizar ejes
    fig.update_xaxes(title_text="Días", row=1, col=1)
    fig.update_xaxes(title_text="Días", row=1, col=2)
    fig.update_xaxes(title_text="Días", row=2, col=1)
    fig.update_xaxes(title_text="País", row=2, col=2)
    
    fig.update_yaxes(title_text="Número de personas", row=1, col=1)
    fig.update_yaxes(title_text="Número de personas", row=1, col=2)
    fig.update_yaxes(title_text="Número de personas", row=2, col=1)
    fig.update_yaxes(title_text="Número de personas", row=2, col=2)
    
    return fig.to_html(include_plotlyjs='cdn', config={'responsive': True})