from django.urls import path
from . import views

# Equivalente a los @app.route de Flask
urlpatterns = [
    path('', views.index, name='index'),
]
