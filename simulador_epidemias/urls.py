from django.urls import path, include

urlpatterns = [
    # Toda la web va a la app 'simulator'
    path('', include('simulator.urls')),
]
