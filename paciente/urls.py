from django.urls import path
from . import views

app_name = 'paciente'

urlpatterns = [
    path('', views.dashboard, name='dashboard.html'),
    path('/paciente/cadastrar/', views.paciente_cadastrar, name='cadastrar_paciente'),
    path('listar/', views.listar_pacientes, name='listar_pacientes'),
    path('editar/<int:pk>/', views.editar_paciente, name='editar_paciente'),
    path('excluir/<int:pk>/', views.excluir_paciente, name='excluir_paciente'),
    path('autocomplete/', views.autocomplete_paciente, name='autocomplete_paciente'),
    path('editar/<int:paciente_id>/', views.paciente_editar, name='paciente_editar'),
    
]