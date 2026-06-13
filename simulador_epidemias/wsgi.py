import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'simulador_epidemias.settings')
application = get_wsgi_application()
