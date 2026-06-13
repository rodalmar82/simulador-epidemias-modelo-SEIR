import geopandas as gpd
import pandas as pd
import folium
import numpy as np
from folium import FeatureGroup, LayerControl

def generate_map(geojson_path, results_df, day):
    """
    Genera un mapa de España mostrando la simulación de infectados por región.
    Los círculos están por encima de los polígonos para interactividad correcta.
    """
    # Cargar GeoJSON
    gdf = gpd.read_file(geojson_path)
    
    # Filtrar resultados por día
    day_data = results_df[results_df["day"] == day].copy()
    
    if day_data.empty:
        day_data = results_df[results_df["day"] == results_df["day"].max()].copy()
    
    # Asegurar tipos de datos
    day_data["region_id"] = day_data["region_id"].astype(str)
    gdf["region_id"] = gdf["region_id"].astype(str)
    
    # Unir resultados
    gdf = gdf.merge(day_data, on="region_id", how="left").fillna(0)
    
    # Calcular centroides aproximados
    gdf['centroid_lat'] = gdf.geometry.bounds['miny'] + (gdf.geometry.bounds['maxy'] - gdf.geometry.bounds['miny']) / 2
    gdf['centroid_lon'] = gdf.geometry.bounds['minx'] + (gdf.geometry.bounds['maxx'] - gdf.geometry.bounds['minx']) / 2
    
    # Calcular porcentaje infectado y otras métricas
    gdf["total_pop"] = gdf["susceptible"] + gdf["infected"] + gdf["recovered"] + gdf["dead"]
    gdf["infected_percentage"] = (gdf["infected"] / gdf["total_pop"].clip(lower=1)) * 100
    gdf["recovered_percentage"] = (gdf["recovered"] / gdf["total_pop"].clip(lower=1)) * 100
    gdf["dead_percentage"] = (gdf["dead"] / gdf["total_pop"].clip(lower=1)) * 100
    
    # Crear mapa
    m = folium.Map(location=[40.4, -3.7], zoom_start=6)
    
    # Crear FeatureGroups separados para control de capas
    polygons_layer = FeatureGroup(name='Fronteras', show=True)
    circles_layer = FeatureGroup(name='Infectados', show=True)
    
    # 1. Añadir polígonos (fondo)
    folium.GeoJson(
        gdf[['geometry', 'name']],
        name='Fronteras',
        style_function=lambda x: {
            "fillColor": "lightgray",
            "color": "gray",
            "weight": 1,
            "fillOpacity": 0.03,
            "dashArray": "2, 2"
        },
        tooltip=folium.GeoJsonTooltip(
            fields=['name'],
            aliases=['Región:'],
            style=("background-color: white; color: #333333; font-family: arial; font-size: 11px; padding: 4px;"),
            sticky=False
        )
    ).add_to(polygons_layer)
    
    # 2. Añadir círculos con tooltips completos
    max_infected = max(gdf["infected"].max(), 1)
    
    for idx, row in gdf.iterrows():
        # Tamaño del círculo basado en infectados
        if row["infected"] > 0:
            radius = 5000 + 40000 * (np.log1p(row["infected"]) / np.log1p(max_infected))
            radius = max(5000, min(radius, 80000))
        else:
            radius = 3000
        
        # Color basado en porcentaje
        if row["infected_percentage"] > 20:
            color = '#8B0000'
        elif row["infected_percentage"] > 10:
            color = '#FF0000'
        elif row["infected_percentage"] > 5:
            color = '#FF8C00'
        elif row["infected_percentage"] > 1:
            color = '#FFD700'
        elif row["infected"] > 0:
            color = '#ADFF2F'
        else:
            color = '#32CD32'
        
        # TOOLTIP COMPLETO (aparece al pasar el ratón)
        tooltip_html = f"""
        <div style="font-family: Arial; width: 300px; padding: 8px; background: white; border-radius: 5px; box-shadow: 2px 2px 10px rgba(0,0,0,0.2);">
            <div style="background: {color}; color: white; padding: 8px; margin: -8px -8px 8px -8px; border-radius: 5px 5px 0 0;">
                <h4 style="margin: 0; font-size: 14px;">{row['name']}</h4>
            </div>
            
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin-bottom: 8px;">
                <div style="background: #f0f8ff; padding: 6px; border-radius: 4px; text-align: center;">
                    <div style="font-size: 11px; color: #666;">Infectados</div>
                    <div style="font-size: 16px; font-weight: bold; color: #e74c3c;">{int(row['infected']):,}</div>
                    <div style="font-size: 10px; color: #e74c3c;">({row['infected_percentage']:.1f}%)</div>
                </div>
                
                <div style="background: #f0fff0; padding: 6px; border-radius: 4px; text-align: center;">
                    <div style="font-size: 11px; color: #666;">Recuperados</div>
                    <div style="font-size: 16px; font-weight: bold; color: #27ae60;">{int(row['recovered']):,}</div>
                    <div style="font-size: 10px; color: #27ae60;">({row['recovered_percentage']:.1f}%)</div>
                </div>
                
                <div style="background: #fff8f0; padding: 6px; border-radius: 4px; text-align: center;">
                    <div style="font-size: 11px; color: #666;">Susceptibles</div>
                    <div style="font-size: 16px; font-weight: bold; color: #3498db;">{int(row['susceptible']):,}</div>
                    <div style="font-size: 10px; color: #3498db;">
                        ({(row['susceptible']/max(1, row['total_pop'])*100):.1f}%)
                    </div>
                </div>
                
                <div style="background: #fff0f0; padding: 6px; border-radius: 4px; text-align: center;">
                    <div style="font-size: 11px; color: #666;">Muertos</div>
                    <div style="font-size: 16px; font-weight: bold; color: #7f8c8d;">{int(row['dead']):,}</div>
                    <div style="font-size: 10px; color: #7f8c8d;">({row['dead_percentage']:.1f}%)</div>
                </div>
            </div>
            
            <div style="background: #f8f9fa; padding: 6px; border-radius: 4px; margin-top: 8px;">
                <div style="display: flex; justify-content: space-between; font-size: 11px;">
                    <span style="color: #666;">Población total:</span>
                    <span style="font-weight: bold;">{int(row['total_pop']):,}</span>
                </div>
                <div style="display: flex; justify-content: space-between; font-size: 11px; margin-top: 4px;">
                    <span style="color: #666;">Estado:</span>
                    <span style="font-weight: bold; color: {color};">
                        {row['infected_percentage']:.1f}% infectados
                    </span>
                </div>
            </div>
            
            <div style="font-size: 10px; color: #95a5a6; text-align: center; margin-top: 8px; padding-top: 8px; border-top: 1px solid #eee;">
                💡 Click para más detalles | Día {day}
            </div>
        </div>
        """
        
        # POPUP DETALLADO (aparece al hacer click)
        popup_html = f"""
        <div style="font-family: Arial; width: 350px; padding: 0;">
            <div style="background: linear-gradient(to right, {color}, #4a69bd); color: white; padding: 15px; margin: 0;">
                <h3 style="margin: 0 0 5px 0; font-size: 18px;">{row['name']}</h3>
                <div style="font-size: 12px; opacity: 0.9;">Información epidemiológica completa</div>
            </div>
            
            <div style="padding: 15px;">
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 15px;">
                    <div style="background: linear-gradient(135deg, #ffeaa7, #fab1a0); padding: 10px; border-radius: 8px; text-align: center; box-shadow: 0 2px 5px rgba(0,0,0,0.1);">
                        <div style="font-size: 12px; color: #d63031; font-weight: bold; margin-bottom: 5px;">INFECTADOS</div>
                        <div style="font-size: 24px; font-weight: bold; color: #d63031;">{int(row['infected']):,}</div>
                        <div style="font-size: 14px; color: #d63031; margin-top: 5px;">{row['infected_percentage']:.2f}%</div>
                    </div>
                    
                    <div style="background: linear-gradient(135deg, #81ecec, #74b9ff); padding: 10px; border-radius: 8px; text-align: center; box-shadow: 0 2px 5px rgba(0,0,0,0.1);">
                        <div style="font-size: 12px; color: #0984e3; font-weight: bold; margin-bottom: 5px;">SUSCEPTIBLES</div>
                        <div style="font-size: 24px; font-weight: bold; color: #0984e3;">{int(row['susceptible']):,}</div>
                        <div style="font-size: 14px; color: #0984e3; margin-top: 5px;">{(row['susceptible']/max(1, row['total_pop'])*100):.2f}%</div>
                    </div>
                    
                    <div style="background: linear-gradient(135deg, #55efc4, #00b894); padding: 10px; border-radius: 8px; text-align: center; box-shadow: 0 2px 5px rgba(0,0,0,0.1);">
                        <div style="font-size: 12px; color: #00b894; font-weight: bold; margin-bottom: 5px;">RECUPERADOS</div>
                        <div style="font-size: 24px; font-weight: bold; color: #00b894;">{int(row['recovered']):,}</div>
                        <div style="font-size: 14px; color: #00b894; margin-top: 5px;">{row['recovered_percentage']:.2f}%</div>
                    </div>
                    
                    <div style="background: linear-gradient(135deg, #dfe6e9, #636e72); padding: 10px; border-radius: 8px; text-align: center; box-shadow: 0 2px 5px rgba(0,0,0,0.1);">
                        <div style="font-size: 12px; color: #2d3436; font-weight: bold; margin-bottom: 5px;">FALLECIDOS</div>
                        <div style="font-size: 24px; font-weight: bold; color: #2d3436;">{int(row['dead']):,}</div>
                        <div style="font-size: 14px; color: #2d3436; margin-top: 5px;">{row['dead_percentage']:.2f}%</div>
                    </div>
                </div>
                
                <div style="background: #f8f9fa; padding: 12px; border-radius: 8px; margin-bottom: 15px;">
                    <h4 style="margin: 0 0 10px 0; color: #333; font-size: 14px;">📊 Resumen de la región</h4>
                    <table style="width: 100%; border-collapse: collapse; font-size: 12px;">
                        <tr>
                            <td style="padding: 5px 0; border-bottom: 1px solid #eee; color: #666;">Población total:</td>
                            <td style="padding: 5px 0; border-bottom: 1px solid #eee; text-align: right; font-weight: bold;">{int(row['total_pop']):,}</td>
                        </tr>
                        <tr>
                            <td style="padding: 5px 0; border-bottom: 1px solid #eee; color: #666;">Tasa de infección:</td>
                            <td style="padding: 5px 0; border-bottom: 1px solid #eee; text-align: right; font-weight: bold; color: #e74c3c;">{row['infected_percentage']:.2f}%</td>
                        </tr>
                        <tr>
                            <td style="padding: 5px 0; border-bottom: 1px solid #eee; color: #666;">Tasa de mortalidad:</td>
                            <td style="padding: 5px 0; border-bottom: 1px solid #eee; text-align: right; font-weight: bold; color: #2d3436;">{row['dead_percentage']:.2f}%</td>
                        </tr>
                        <tr>
                            <td style="padding: 5px 0; color: #666;">Tasa de recuperación:</td>
                            <td style="padding: 5px 0; text-align: right; font-weight: bold; color: #00b894;">{row['recovered_percentage']:.2f}%</td>
                        </tr>
                    </table>
                </div>
                
                <div style="background: #fff3cd; border-left: 4px solid #ffc107; padding: 10px; border-radius: 4px; font-size: 11px; color: #856404;">
                    <strong>💡 Información:</strong> Estos datos corresponden al día {day} de la simulación. 
                    Click fuera de este cuadro para cerrar.
                </div>
            </div>
        </div>
        """
        
        # Crear círculo con popup mejorado
        circle = folium.Circle(
            location=[row['centroid_lat'], row['centroid_lon']],
            radius=radius,
            popup=folium.Popup(popup_html, max_width=400),
            color=color,
            fill=True,
            fill_color=color,
            fill_opacity=0.7,
            weight=2.5,
            opacity=0.9
        )
        
        # Añadir tooltip SIMPLIFICADO (solo texto, no HTML)
        tooltip_text = f"""{row['name']}
Infectados: {int(row['infected']):,} ({row['infected_percentage']:.1f}%)
Recuperados: {int(row['recovered']):,} ({row['recovered_percentage']:.1f}%)
Susceptibles: {int(row['susceptible']):,} ({(row['susceptible']/max(1, row['total_pop'])*100):.1f}%)
Muertos: {int(row['dead']):,} ({row['dead_percentage']:.1f}%)
Click para detalles completos"""
        
        folium.Tooltip(
            text=tooltip_text,
            sticky=True,
            permanent=False
        ).add_to(circle)
        
        # Añadir círculo a la capa
        circle.add_to(circles_layer)
        
        # Añadir etiqueta pequeña con nombre
        folium.Marker(
            location=[row['centroid_lat'], row['centroid_lon']],
            icon=folium.DivIcon(
                html=f'<div style="font-size: 9px; font-weight: bold; color: #2c3e50; text-shadow: 1px 1px 2px white, -1px -1px 2px white, 1px -1px 2px white, -1px 1px 2px white; background: rgba(255,255,255,0.7); padding: 2px 4px; border-radius: 3px;">{row["name"][:10]}</div>'
            ),
            tooltip=row['name']
        ).add_to(circles_layer)
    
    # Añadir capas al mapa
    polygons_layer.add_to(m)
    circles_layer.add_to(m)
    
    # Control de capas
    LayerControl().add_to(m)
    
    # Leyenda mejorada (sin JavaScript para evitar problemas)
    legend_html = f'''
    <div style="position: fixed; 
                bottom: 50px; left: 50px; width: 220px; 
                background-color: white; border: 2px solid #3498db; z-index: 1000;
                font-size: 12px; padding: 12px; border-radius: 10px;
                box-shadow: 3px 3px 15px rgba(0,0,0,0.2);">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
            <h4 style="margin: 0; color: #2c3e50; font-size: 14px;">📈 Día {day} - Leyenda</h4>
            <div style="font-size: 10px; color: #7f8c8d; background: #f8f9fa; padding: 2px 6px; border-radius: 10px;">
                🔍 hover + click
            </div>
        </div>
        
        <div style="margin-bottom: 10px;">
            <div style="font-size: 11px; color: #666; margin-bottom: 5px;">Nivel de infección:</div>
            <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 5px;">
                <div style="display: flex; flex-direction: column; align-items: center;">
                    <div style="width: 12px; height: 12px; background-color: #8B0000; border-radius: 50%; margin-bottom: 2px;"></div>
                    <span style="font-size: 9px;">>20%</span>
                </div>
                <div style="display: flex; flex-direction: column; align-items: center;">
                    <div style="width: 12px; height: 12px; background-color: #FF0000; border-radius: 50%; margin-bottom: 2px;"></div>
                    <span style="font-size: 9px;">10-20%</span>
                </div>
                <div style="display: flex; flex-direction: column; align-items: center;">
                    <div style="width: 12px; height: 12px; background-color: #FF8C00; border-radius: 50%; margin-bottom: 2px;"></div>
                    <span style="font-size: 9px;">5-10%</span>
                </div>
                <div style="display: flex; flex-direction: column; align-items: center;">
                    <div style="width: 12px; height: 12px; background-color: #FFD700; border-radius: 50%; margin-bottom: 2px;"></div>
                    <span style="font-size: 9px;">1-5%</span>
                </div>
                <div style="display: flex; flex-direction: column; align-items: center;">
                    <div style="width: 12px; height: 12px; background-color: #ADFF2F; border-radius: 50%; margin-bottom: 2px;"></div>
                    <span style="font-size: 9px;"><1%</span>
                </div>
                <div style="display: flex; flex-direction: column; align-items: center;">
                    <div style="width: 12px; height: 12px; background-color: #32CD32; border-radius: 50%; margin-bottom: 2px;"></div>
                    <span style="font-size: 9px;">0%</span>
                </div>
            </div>
        </div>
        
        <hr style="margin: 10px 0; border-color: #eee;">
        
        <div style="font-size: 11px; color: #666;">
            <div style="display: flex; align-items: center; margin-bottom: 5px;">
                <span style="width: 20px;">🖱️</span>
                <span><strong>Pasar ratón:</strong> Ver resumen</span>
            </div>
            <div style="display: flex; align-items: center;">
                <span style="width: 20px;">💡</span>
                <span><strong>Click:</strong> Ver detalles ampliados</span>
            </div>
        </div>
        
        <div style="margin-top: 10px; padding: 8px; background: linear-gradient(to right, #74b9ff, #0984e3); border-radius: 6px; color: white; font-size: 11px; text-align: center;">
            Tamaño del círculo = Número de infectados
        </div>
    </div>
    '''
    
    m.get_root().html.add_child(folium.Element(legend_html))
    
    # Título con estadísticas globales
    total_infected = gdf["infected"].sum()
    total_dead = gdf["dead"].sum()
    total_recovered = gdf["recovered"].sum()
    total_population = gdf["total_pop"].sum()
    
    title_html = f'''
    <div style="position: fixed; 
                top: 10px; left: 50px; width: 350px; 
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                color: white; border-radius: 10px; z-index: 1000;
                font-size: 14px; padding: 15px; box-shadow: 0 4px 15px rgba(0,0,0,0.2);">
        <h3 style="margin: 0 0 10px 0; font-size: 16px; display: flex; align-items: center;">
            <span style="margin-right: 10px;">🦠</span>
            Simulador Epidemiológico - Día {day}
        </h3>
        <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; font-size: 12px;">
            <div style="text-align: center;">
                <div style="font-size: 10px; opacity: 0.9;">Infectados</div>
                <div style="font-size: 18px; font-weight: bold;">{int(total_infected):,}</div>
                <div style="font-size: 10px;">({(total_infected/max(1, total_population)*100):.1f}%)</div>
            </div>
            <div style="text-align: center;">
                <div style="font-size: 10px; opacity: 0.9;">Recuperados</div>
                <div style="font-size: 18px; font-weight: bold; color: #55efc4;">{int(total_recovered):,}</div>
                <div style="font-size: 10px;">({(total_recovered/max(1, total_population)*100):.1f}%)</div>
            </div>
            <div style="text-align: center;">
                <div style="font-size: 10px; opacity: 0.9;">Fallecidos</div>
                <div style="font-size: 18px; font-weight: bold;">{int(total_dead):,}</div>
                <div style="font-size: 10px;">({(total_dead/max(1, total_population)*100):.1f}%)</div>
            </div>
        </div>
        <div style="margin-top: 10px; font-size: 11px; opacity: 0.8; border-top: 1px solid rgba(255,255,255,0.2); padding-top: 8px;">
            💡 Pasa el ratón sobre cualquier círculo para ver detalles de la región
        </div>
    </div>
    '''
    
    m.get_root().html.add_child(folium.Element(title_html))
    
    return m._repr_html_()