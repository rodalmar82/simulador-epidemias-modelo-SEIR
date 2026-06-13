import matplotlib.pyplot as plt
import matplotlib.animation as animation
import geopandas as gpd
import numpy as np
from matplotlib.patches import Circle

def crear_animacion(geojson_path, results_df, disease_name, output_file='animacion.gif'):
    """
    Crea una animación GIF de la propagación día a día
    """
    gdf = gpd.read_file(geojson_path)
    fig, ax = plt.subplots(1, 1, figsize=(15, 10))
    
    # Preparar datos
    dias = sorted(results_df['day'].unique())
    max_infectados = results_df['infected'].max()
    
    def update(dia):
        ax.clear()
        
        # Datos del día actual
        day_data = results_df[results_df['day'] == dia].copy()
        day_data['region_id'] = day_data['region_id'].astype(str)
        
        # Unir con geometrías
        gdf_day = gdf.copy()
        gdf_day['region_id'] = gdf_day['region_id'].astype(str)
        gdf_day = gdf_day.merge(day_data, on='region_id', how='left').fillna(0)
        
        # Dibujar países
        gdf_day.plot(ax=ax, color='lightgray', edgecolor='white', linewidth=0.5)
        
        # Añadir círculos para infectados
        for _, row in gdf_day.iterrows():
            if row['infected'] > 0:
                centroid = row.geometry.centroid
                size = (row['infected'] / max_infectados) * 5 + 1
                circle = Circle((centroid.x, centroid.y), 
                              radius=size, 
                              color='red', 
                              alpha=0.5)
                ax.add_patch(circle)
        
        ax.set_title(f'{disease_name} - Día {dia}')
        ax.set_xlim([-180, 180])
        ax.set_ylim([-60, 90])
        ax.axis('off')
    
    ani = animation.FuncAnimation(fig, update, frames=dias, interval=200)
    ani.save(output_file, writer='pillow', fps=5)
    return output_file