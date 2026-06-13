# 🦠 Simulador de Epidemias Global — Modelo SEIR

Simulador de propagación de enfermedades usando modelo SEIR con visualización interactiva.

## 🚀 Características

- Modelo epidemiológico SIR (Susceptible-Expuesto-Infectado-Recuperado)
- 42 enfermedades preconfiguradas (COVID-19, Ebola, Sarampión, etc.)
- Visualización con mapas interactivos (Folium)
- Interfaz web con Django
- Datos reales de población mundial
- Movilidad entre distintos paises

## 📦 Instalación

1. Clonar repositorio:
\\\ash
git clone https://github.com/TU_USUARIO/simulador-modelo-SEIR.git
cd simulador-epidemias-espana
\\\

2. Crear entorno virtual:
\\\ash
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate
\\\

3. Instalar dependencias:
\\\ash
pip install -r requirements.txt
\\\

4. Ejecutar aplicación:
\\\ash
python main.py
\\\

5. Abrir navegador en: http://localhost:5000

## 🎯 Uso

1. Seleccionar enfermedad
2. Elegir región inicial
3. Especificar número de infectados iniciales
4. Definir días de simulación
5. Click en 'Ejecutar Simulación'

## 📊 Tecnologías

- **Backend**: Python, Flask
- **Modelo**: Pandas, NumPy
- **Visualización**: Folium, GeoPandas
- **Frontend**: HTML, CSS

## 📁 Estructura del Proyecto

\\\
simulador-epidemias-espana/
├── data/          # Datos CSV y GeoJSON
├── models/        # Modelos Python
├── visualization/ # Generación de mapas
├── main.py        # Aplicación principal
└── requirements.txt
\\\

## 📝 Licencia

MIT License
