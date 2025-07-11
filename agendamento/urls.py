from django.urls import path
from . import views
from .views import lista_agendamentos
from .views import autocomplete_paciente

app_name = 'agendamento'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('agendar/', views.agendar, name='agendar'),
    path('lista/', lista_agendamentos, name='lista_agendamentos'),
    path('lista/pdf/', views.agendamentos_pdf, name='agendamentos_pdf'),
    path('editar/<int:pk>/', views.editar_agenda, name='editar_agenda'),
    path('excluir/<int:pk>/', views.excluir_agenda, name='excluir_agenda'),
    path('autocomplete-paciente/', views.autocomplete_paciente, name='autocomplete_paciente'),
    path('cadastro-dentista/', views.cadastro_dentista, name='cadastro_dentista'),
    path('paciente/<int:paciente_id>/', views.agendar_paciente, name='agendar_paciente'),
    path('<int:agendamento_id>/atualizar_status/', views.atualizar_status_agendamento, name='atualizar_status'),       
]