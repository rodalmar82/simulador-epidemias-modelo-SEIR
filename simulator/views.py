# simulator/views.py
#
# EQUIVALENCIAS FLASK → DJANGO:
#   @app.route("/")              →  def index(request): + path('', views.index) en urls.py
#   request.method               →  request.method          (igual)
#   request.form.get("x")        →  request.POST.get("x")
#   render_template("x.html", …) →  render(request, "x.html", {…})

import traceback
import pandas as pd
import plotly.graph_objects as go

from django.shortcuts import render

from .models.disease import Disease
from .models.simulation import Simulation
from .models.metrics import EpidemicMetrics
from .visualization.map_folium import generate_map

# ---------------------------------------------------------------------------
# Carga de datos al arrancar el servidor (igual que en Flask)
# ---------------------------------------------------------------------------
# BASE_DIR apunta a la carpeta 'simulator/', donde vive la carpeta 'data/'
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent

population_df  = pd.read_csv(BASE_DIR / "data" / "population_global.csv")
mobility_df    = pd.read_csv(BASE_DIR / "data" / "mobility_global.csv")
diseases_df    = pd.read_csv(BASE_DIR / "data" / "diseases.csv")
geojson_path   = str(BASE_DIR / "data" / "regions.geojson")

regiones_dict = {
    str(row["region_id"]): row["region_name"]
    for _, row in population_df.iterrows()
}


# ---------------------------------------------------------------------------
# Funciones de gráficos (sin cambios respecto a Flask)
# ---------------------------------------------------------------------------

def generar_chart_evolucion(results_df, enfermedad_nombre):
    """Genera gráfico de evolución SEIR global."""
    try:
        agg = {'infected': ('infected', 'sum'), 'recovered': ('recovered', 'sum'), 'dead': ('dead', 'sum')}
        if 'exposed' in results_df.columns:
            agg['exposed'] = ('exposed', 'sum')
        datos_globales = results_df.groupby('day').agg(**agg).reset_index()

        fig = go.Figure()
        if 'exposed' in datos_globales.columns:
            fig.add_trace(go.Scatter(
                x=datos_globales['day'], y=datos_globales['exposed'],
                mode='lines', name='Expuestos',
                line=dict(color='#FF9900', width=2, dash='dot'),
            ))
        fig.add_trace(go.Scatter(
            x=datos_globales['day'], y=datos_globales['infected'],
            mode='lines+markers', name='Infectados',
            line=dict(color='#FF4444', width=3),
        ))
        fig.add_trace(go.Scatter(
            x=datos_globales['day'], y=datos_globales['recovered'],
            mode='lines', name='Recuperados',
            line=dict(color='#44AA44', width=2),
        ))
        fig.add_trace(go.Scatter(
            x=datos_globales['day'], y=datos_globales['dead'],
            mode='lines', name='Fallecidos',
            line=dict(color='#444444', width=2),
        ))
        fig.update_layout(
            title=f'Evolución SEIR - {enfermedad_nombre}',
            xaxis_title='Días', yaxis_title='Número de personas',
            template='plotly_white', height=300,
            margin=dict(l=40, r=20, t=40, b=40),
            legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
        )
        return fig.to_html(include_plotlyjs='cdn', config={'displayModeBar': False})
    except Exception as e:
        print(f"❌ Error en gráfico evolución: {e}")
        return "<p>Error al generar gráfico</p>"


def generar_chart_pie(results_df):
    """Genera gráfico de torta con distribución global."""
    try:
        ultimo_dia = results_df[results_df['day'] == results_df['day'].max()]

        labels = ['Susceptibles', 'Expuestos', 'Infectados', 'Recuperados', 'Fallecidos']
        values = [
            ultimo_dia['susceptible'].sum(),
            ultimo_dia['exposed'].sum() if 'exposed' in ultimo_dia.columns else 0,
            ultimo_dia['infected'].sum(),
            ultimo_dia['recovered'].sum(),
            ultimo_dia['dead'].sum(),
        ]
        fig = go.Figure(data=[go.Pie(
            labels=labels,
            values=values,
            marker_colors=['#3366CC', '#FF9900', '#FF4444', '#44AA44', '#444444'],
            textinfo='percent',
            textposition='inside',
            hovertemplate='<b>%{label}</b><br>%{value:,.0f} personas<br>%{percent}',
            hole=0.3,
        )])
        fig.update_layout(
            title=dict(text='Distribución Global de la Población', y=0.97, x=0.5,
                   xanchor='center', yanchor='top', font=dict(size=13)),
            height=320,
            margin=dict(l=20, r=20, t=60, b=20),
            template='plotly_white',
            showlegend=True,
            legend=dict(orientation='v', x=1.05, y=0.5),
        )
        return fig.to_html(include_plotlyjs='cdn', config={'displayModeBar': False})
    except Exception as e:
        print(f"❌ Error en gráfico pie: {e}")
        return "<p>Error al generar gráfico</p>"


def generar_chart_top10(results_df):
    """Genera gráfico de barras con top 10 países."""
    try:
        ultimo_dia = results_df[results_df['day'] == results_df['day'].max()]
        top10 = ultimo_dia.nlargest(10, 'infected')[['region_id', 'infected', 'dead']].copy()
        top10['nombre'] = top10['region_id'].map(regiones_dict).fillna(top10['region_id'])

        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=top10['nombre'], y=top10['infected'],
            name='Infectados', marker_color='#FF4444',
            text=top10['infected'].apply(lambda x: f'{x:,.0f}'),
            textposition='auto',
        ))
        fig.add_trace(go.Bar(
            x=top10['nombre'], y=top10['dead'],
            name='Fallecidos', marker_color='#444444',
            text=top10['dead'].apply(lambda x: f'{x:,.0f}'),
            textposition='auto',
        ))
        fig.update_layout(
            title='Top 10 Países más Afectados (Mundial)',
            xaxis_title='País', yaxis_title='Número de personas',
            barmode='group', height=300,
            margin=dict(l=40, r=20, t=40, b=80),
            template='plotly_white',
        )
        return fig.to_html(include_plotlyjs='cdn', config={'displayModeBar': False})
    except Exception as e:
        print(f"❌ Error en gráfico top10: {e}")
        return "<p>Error al generar gráfico</p>"


def generar_chart_mortalidad(results_df):
    """Genera gráfico de evolución de mortalidad global."""
    try:
        datos = results_df.groupby('day').agg(
            dead=('dead', 'sum'),
            infected=('infected', 'sum'),
        ).reset_index()
        datos['tasa_mortalidad'] = (
            datos['dead'] / (datos['infected'] + datos['dead'] + 1) * 100
        )

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=datos['day'], y=datos['tasa_mortalidad'],
            mode='lines+markers', name='Tasa mortalidad',
            line=dict(color='#444444', width=3),
            fill='tozeroy', fillcolor='rgba(68,68,68,0.1)',
        ))
        fig.update_layout(
            title='Evolución de la Tasa de Mortalidad (Global)',
            xaxis_title='Días', yaxis_title='Tasa de mortalidad (%)',
            height=300, margin=dict(l=40, r=20, t=40, b=40),
            template='plotly_white',
        )
        return fig.to_html(include_plotlyjs='cdn', config={'displayModeBar': False})
    except Exception as e:
        print(f"❌ Error en gráfico mortalidad: {e}")
        return "<p>Error al generar gráfico</p>"


# ---------------------------------------------------------------------------
# Vista principal (equivalente a @app.route("/") de Flask)
# ---------------------------------------------------------------------------

def index(request):
    """
    En Flask era:  @app.route("/", methods=["GET", "POST"])
    En Django es:  una función normal que recibe `request`
                   y devuelve render(request, "template.html", contexto)
    """
    # Valores por defecto
    selected_disease  = "Measles"
    start_region      = "CHN"
    days              = 60
    initial_infected  = 1000

    error_message         = None
    map_html              = None
    chart_evolucion_html  = "<p>No hay datos suficientes</p>"
    chart_pie_html        = "<p>No hay datos suficientes</p>"
    chart_top10_html      = "<p>No hay datos suficientes</p>"
    chart_mortalidad_html = "<p>No hay datos suficientes</p>"

    stats = {
        'total_infectados_global':    '0',
        'total_muertos_global':       '0',
        'total_recuperados_global':   '0',
        'total_infectados_pais':      '0',
        'total_muertos_pais':         '0',
        'total_recuperados_pais':     '0',
        'porcentaje_poblacion_global': '0.00',
        'porcentaje_poblacion_pais':   '0.00',
        'tasa_mortalidad_global':      '0.00',
        'tasa_mortalidad_pais':        '0.00',
        'rt':                          '0.00',
        'rt_interpretacion':           'Sin datos',
        'nombre_pais_inicial':         regiones_dict.get(start_region, start_region),
    }

    # ------------------------------------------------------------------ POST
    # En Flask: if request.method == "POST"  →  igual en Django
    # En Flask: request.form.get("x")        →  request.POST.get("x")
    # ------------------------------------------------------------------ POST
    if request.method == "POST":
        try:
            selected_disease = request.POST.get("disease", selected_disease)
            start_region     = request.POST.get("start_region", start_region)
            days             = int(request.POST.get("days", days))
            initial_infected = int(request.POST.get("initial_infected", initial_infected))
            stats['nombre_pais_inicial'] = regiones_dict.get(start_region, start_region)
            print(f"📊 Simulación: {selected_disease} desde {start_region} "
                  f"con {initial_infected} infectados durante {days} días")
        except Exception as e:
            error_message = f"Error en parámetros: {str(e)}"

    # --------------------------------------------------------- Simulación
    try:
        row = diseases_df[diseases_df["name"] == selected_disease].iloc[0]
        disease = Disease(
            row["name"], row["infection_rate"], row["mortality_rate"],
            row["incubation_days"], row["recovery_days"],
        )

        sim = Simulation(disease, population_df, mobility_df)
        sim.run(days=days, initial_region=start_region,
                initial_infected=initial_infected)
        results_df = sim.results

        # Mapa
        try:
            map_html = generate_map(geojson_path, results_df, days)
        except Exception as e:
            print(f"❌ Error mapa: {e}")
            map_html = "<p>Error al generar mapa</p>"

        # Gráficos
        chart_evolucion_html  = generar_chart_evolucion(results_df, selected_disease)
        chart_pie_html        = generar_chart_pie(results_df)
        chart_top10_html      = generar_chart_top10(results_df)
        chart_mortalidad_html = generar_chart_mortalidad(results_df)

        # Métricas
        metrics = EpidemicMetrics.get_all_metrics(results_df)

        ultimo_dia            = results_df[results_df['day'] == days]
        total_poblacion_global = population_df['population'].sum()
        pais_row              = population_df[population_df['region_id'] == start_region]
        poblacion_pais_inicial = pais_row['population'].values[0] if not pais_row.empty else 1

        total_infectados_global  = ultimo_dia['infected'].sum()
        total_muertos_global     = ultimo_dia['dead'].sum()
        total_recuperados_global = ultimo_dia['recovered'].sum()

        datos_pais = ultimo_dia[ultimo_dia['region_id'] == start_region]
        if not datos_pais.empty:
            total_infectados_pais  = datos_pais['infected'].values[0]
            total_muertos_pais     = datos_pais['dead'].values[0]
            total_recuperados_pais = datos_pais['recovered'].values[0]
        else:
            total_infectados_pais = total_muertos_pais = total_recuperados_pais = 0

        stats = {
            'total_infectados_global':    f"{int(total_infectados_global):,}",
            'total_muertos_global':       f"{int(total_muertos_global):,}",
            'total_recuperados_global':   f"{int(total_recuperados_global):,}",
            'total_infectados_pais':      f"{int(total_infectados_pais):,}",
            'total_muertos_pais':         f"{int(total_muertos_pais):,}",
            'total_recuperados_pais':     f"{int(total_recuperados_pais):,}",
            'porcentaje_poblacion_global': f"{total_infectados_global / total_poblacion_global * 100:.2f}",
            'porcentaje_poblacion_pais':   f"{total_infectados_pais / max(1, poblacion_pais_inicial) * 100:.2f}",
            'tasa_mortalidad_global':      f"{metrics['cfr']['cfr_global']:.2f}",
            'tasa_mortalidad_pais':        f"{total_muertos_pais / max(1, total_infectados_pais + total_recuperados_pais + total_muertos_pais) * 100:.2f}",
            'rt':                          f"{metrics['rt']['rt_promedio']:.2f}",
            'rt_interpretacion':           metrics['rt']['interpretacion'],
            'nombre_pais_inicial':         stats['nombre_pais_inicial'],
        }

    except Exception as e:
        error_message = f"Error en simulación: {str(e)}"
        traceback.print_exc()

    # ---------------------------------------------------------- Contexto
    # En Flask:  render_template("dashboard.html", diseases=..., ...)
    # En Django: render(request, "dashboard.html", {"diseases": ..., ...})
    context = {
        "diseases":       diseases_df["name"].tolist(),
        "regiones":       regiones_dict,
        "selected_disease": selected_disease,
        "start_region":   start_region,
        "initial_infected": initial_infected,
        "days":           days,
        "error_message":  error_message,
        "map_html":       map_html,
        "chart_evolucion":  chart_evolucion_html,
        "chart_pie":        chart_pie_html,
        "chart_top10":      chart_top10_html,
        "chart_mortalidad": chart_mortalidad_html,
        "stats":          stats,
    }

    # En Flask:  return render_template("dashboard.html", **context)
    # En Django: return render(request, "dashboard.html", context)
    return render(request, "dashboard.html", context)
