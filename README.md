# 🦠 Simulador de Epidemias Global — Modelo SEIR

Simulador de propagación de enfermedades usando modelo SEIR con visualización interactiva.

## 🚀 Características

- Modelo epidemiológico SEIR (Susceptible-Expuesto-Infectado-Recuperado)
- 42 enfermedades preconfiguradas (COVID-19, Ebola, Sarampión, etc.)
- Visualización con mapas interactivos (Folium)
- Interfaz web con Django
- Datos reales de población mundial
- Movilidad entre distintos paises

## 📦 Instalación
#### Será necesario clonar el repositorio de Github y crear un entorno vistual.

1. Clonar repositorio:
git clone https://github.com/TU_USUARIO/simulador-modelo-SEIR.git

3. Crear entorno virtual con la versión 3.11 de python:
python -3.11 -m venv venv

- Para abrir el entorno en Windows se utiliza:
venv\Scripts\activate

- Para abrir el entorno en Linux/Mac se utiliza:
source venv/bin/activate

3. Instalar dependencias:
pip install -r requirements.txt

5. Ejecutar aplicación:
python manage.py runserver

7. Abrir navegador en: http://localhost:8000

## 🎯 Uso

1. Seleccionar enfermedad
2. Elegir región inicial
3. Especificar número de infectados iniciales
4. Definir días de simulación
5. Click en 'Ejecutar Simulación'

## 📊 Tecnologías

- **Backend**: Python, Django
- **Modelo**: Pandas, NumPy
- **Visualización**: Folium, GeoPandas
- **Frontend**: HTML, CSS

## 📁 Estructura del Proyecto

\\\
simulador-epidemias-modelo-SEIR/
├── simulador_epidemias/ 
    ├── settings.py
    ├── urls.py
    ├── wsgi.py
├── simulator/        
    ├── data/
        ├── disease.csv
        ├── mobility_global.csv
        ├── mobbility_spain.csv
        ├── population_global.csv
        ├── population_spain.csv
        ├── regions.geojson
        ├── results.csv
    ├── models/
        ├── disease-py
        ├── metrics.py
        ├── simulation.py
    ├── static/
        ├── themes-py
    ├── templates/
        ├── dashboard.html
    ├── utils/
        ├── export.py
    ├── visualization/
        ├── animation.py
        ├── graphics.py
        ├── heat_map
        ├── map_folium.py
    ├── urls.py
    ├── views.py
├── manage.py        # Aplicación principal
└── requirements.txt
\\\

## 📝 Licencia

MIT License
