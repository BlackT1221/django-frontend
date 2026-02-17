from django.urls import path
from . import views

urlpatterns = [
    # Asociar la funcion a la vista con url /registro/
    path('registro/', views.registro_usuario, name='registro'),

    #Ruta para el inicio de sesion
    path('login/', views.iniciar_sesion, name='login'),

    # Ruta para el panel principal (protegido por el decorador)
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # Ruta para cerrar la sesión
    path('logout/', views.cerrar_sesion, name='logout'),

    path('tareas/', views.listar_tareas, name='listar_tareas'),
    path('tareas/crear/', views.crear_tarea, name='crear_tarea'),
    path('tareas/eliminar/<str:tarea_id>/', views.eliminar_tarea, name='eliminar_tarea'),
    path('tareas/editar/<str:tarea_id>/', views.editar_tarea, name='editar_tarea')

]