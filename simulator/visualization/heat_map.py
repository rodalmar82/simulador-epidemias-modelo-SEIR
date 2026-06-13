# visualization/heat_map.py
import folium
from folium.plugins import HeatMap
import geopandas as gpd
import numpy as np
import pandas as pd

def generar_heatmap(geojson_path, results_df, day):
    """
    Genera un mapa de calor mostrando la densidad de infectados
    
    Args:
        geojson_path: Ruta al archivo GeoJSON
        results_df: DataFrame con resultados de simulación
        day: Día a visualizar
    
    Returns:
        HTML string con el mapa de calor
    """
    # Cargar GeoJSON
    gdf = gpd.read_file(geojson_path)
    
    # Filtrar resultados por día
    day_data = results_df[results_df["day"] == day].copy()
    
    if day_data.empty:
        # Si no hay datos para ese día, usar el último día disponible
        day_data = results_df[results_df["day"] == results_df["day"].max()].copy()
        day = results_df["day"].max()
    
    # Asegurar tipos de datos
    day_data["region_id"] = day_data["region_id"].astype(str)
    gdf["region_id"] = gdf["region_id"].astype(str)
    
    # Unir resultados
    gdf = gdf.merge(day_data, on="region_id", how="left").fillna(0)
    
    # Calcular centroides
    gdf['centroid'] = gdf.geometry.centroid
    gdf['lat'] = gdf.centroid.y
    gdf['lon'] = gdf.centroid.x
    
    # Preparar datos para heatmap
    heat_data = []
    max_infectados = gdf['infected'].max()
    
    for _, row in gdf.iterrows():
        if row['infected'] > 0:
            # Escala logarítmica para mejor visualización
            # El peso va de 0.1 a 1
            peso = 0.1 + 0.9 * (np.log1p(row['infected']) / np.log1p(max_infectados))
            heat_data.append([row['lat'], row['lon'], peso])
    
    # Crear mapa base
    m = folium.Map(
        location=[20, 0], 
        zoom_start=2,
        tiles='CartoDB dark_matter'  # Fondo oscuro para mejor contraste
    )
    
    # Añadir heatmap si hay datos
    if heat_data:
        HeatMap(
            heat_data,
            min_opacity=0.3,
            max_val=1,
            radius=20,
            blur=15,
            gradient={
                0.2: 'blue',
                0.4: 'cyan',
                0.6: 'lime',
                0.8: 'yellow',
                0.9: 'orange',
                1.0: 'red'
            }
        ).add_to(m)
    
    # Añadir título
    title_html = f'''
    <div style="position: fixed; 
                top: 10px; left: 50px; width: 300px; height: 60px; 
                background-color: rgba(0,0,0,0.7); 
                color: white; 
                border-radius: 5px;
                z-index:9999; 
                font-size:14px; 
                font-weight: bold; 
                padding: 10px;
                box-shadow: 3px 3px 5px rgba(0,0,0,0.3);">
        <span style="color: #ff4444;">🔥 Mapa de Calor - Día {day}</span><br>
        <span style="font-size: 12px;">Más rojo = Mayor densidad de infectados</span>
    </div>
    '''
    
    m.get_root().html.add_child(folium.Element(title_html))
    
    # Añadir leyenda
    legend_html = '''
    <div style="position: fixed; 
                bottom: 50px; right: 50px; width: 200px; 
                background-color: rgba(0,0,0,0.7); 
                color: white;
                border-radius: 5px;
                z-index:9999; 
                font-size:12px; 
                padding: 10px;
                box-shadow: 3px 3px 5px rgba(0,0,0,0.3);">
        <div style="text-align: center; margin-bottom: 10px; font-weight: bold;">Intensidad</div>
        <div style="display: flex; align-items: center; margin: 5px 0;">
            <div style="width: 20px; height: 20px; background-color: blue; margin-right: 10px;"></div>
            <span>Baja</span>
        </div>
        <div style="display: flex; align-items: center; margin: 5px 0;">
            <div style="width: 20px; height: 20px; background-color: cyan; margin-right: 10px;"></div>
            <span>Media-baja</span>
        </div>
        <div style="display: flex; align-items: center; margin: 5px 0;">
            <div style="width: 20px; height: 20px; background-color: lime; margin-right: 10px;"></div>
            <span>Media</span>
        </div>
        <div style="display: flex; align-items: center; margin: 5px 0;">
            <div style="width: 20px; height: 20px; background-color: yellow; margin-right: 10px;"></div>
            <span>Media-alta</span>
        </div>
        <div style="display: flex; align-items: center; margin: 5px 0;">
            <div style="width: 20px; height: 20px; background-color: orange; margin-right: 10px;"></div>
            <span>Alta</span>
        </div>
        <div style="display: flex; align-items: center; margin: 5px 0;">
            <div style="width: 20px; height: 20px; background-color: red; margin-right: 10px;"></div>
            <span>Muy alta</span>
        </div>
    </div>
    '''
    
    m.get_root().html.add_child(folium.Element(legend_html))
    
    return m._repr_html_()