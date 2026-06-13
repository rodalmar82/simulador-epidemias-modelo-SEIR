# Simulador de Epidemias Global — Django

## Estructura del proyecto

```
simulador_epidemias/
├── manage.py                        ← punto de entrada (como "python app.py" en Flask)
├── simulador_epidemias/             ← configuración del proyecto Django
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
└── simulator/                       ← la app (equivale a tu main.py de Flask)
    ├── views.py                     ← lógica de rutas (antes en main.py)
    ├── urls.py                      ← rutas (antes @app.route)
    ├── templates/
    │   └── dashboard.html
    ├── models/                      ← sin cambios respecto a Flask
    ├── visualization/               ← sin cambios
    ├── utils/                       ← sin cambios
    ├── static/                      ← sin cambios
    └── data/                        ← pon aquí tus CSVs y GeoJSON
```

## Instalación

```bash
pip install django pandas numpy plotly folium openpyxl
```

## Datos necesarios

Copia tu carpeta `data/` dentro de `simulator/`:

```
simulator/data/
├── population_global.csv
├── mobility_global.csv
├── diseases.csv
└── regions.geojson
```

## Arrancar el servidor

```bash
# Desde la carpeta raíz del proyecto (donde está manage.py)
python manage.py runserver
```

Abre el navegador en: **http://127.0.0.1:8000**

---

## Diferencias clave Flask → Django

| Concepto         | Flask                              | Django                                  |
|------------------|------------------------------------|-----------------------------------------|
| Arrancar         | `python main.py`                   | `python manage.py runserver`            |
| Ruta             | `@app.route("/")`                  | `path('', views.index)` en `urls.py`   |
| Leer formulario  | `request.form.get("x")`            | `request.POST.get("x")`                |
| Renderizar       | `render_template("x.html", k=v)`   | `render(request, "x.html", {"k": v})`  |
| HTML sin escapar | `{{ var }}` (Jinja2 escapa igual)  | `{{ var\|safe }}` (filtro explícito)    |
| Seguridad forms  | No requiere nada                   | `{% csrf_token %}` obligatorio en POST  |
