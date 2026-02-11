from django.urls import path
from .views import registro_usuario

urlpatterns = [
    # Asociar la funcion a la vista con url /registro/
    path('registro/', registro_usuario, name='registro'),
]