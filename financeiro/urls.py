from django.urls import path
from . import views
from .views import gerar_carne_pdf

app_name = 'financeiro'

urlpatterns = [
    path('caixa/listar/', views.lista_caixa, name='lista_caixa'),# Lista vazia - nenhuma URL definida
    path('caixa/cadastrar/', views.caixa_cadastrar, name='caixa_cadastrar'),
    path('caixa/pdf/', views.caixa_pdf, name='caixa_pdf'),  # Exemplo
    path('contrato/cadastrar/', views.contrato_cadastrar, name='contrato_cadastrar'),
    path('contrato/listar/', views.contrato_listar, name='contrato_listar'),
    path('contrato/editar/<int:pk>/', views.contrato_editar, name='contrato_editar'),
    path('contrato/excluir/<int:pk>/', views.contrato_excluir, name='contrato_excluir'),
    path('parcela/receber/<int:parcela_id>/', views.parcela_receber, name='parcela_receber'),
    path('plano/cadastrar/', views.plano_cadastrar, name='plano_cadastrar'),
    path('paciente/<int:paciente_id>/', views.paciente_ficha, name='paciente_ficha'),
    path('buscar/', views.buscar_paciente, name='buscar_paciente'),
    path('autocomplete-paciente/', views.autocomplete_paciente, name='autocomplete_paciente'),
    path('contrato/exportar-pdf/', views.contrato_exportar_pdf, name='contrato_exportar_pdf'),
    path('caixa/editar/<int:pk>/', views.editar_caixa, name='editar_caixa'),
    path('caixa/excluir/<int:pk>/', views.excluir_caixa, name='excluir_caixa'),
    path('contrato/<int:contrato_id>/carne/', views.gerar_carne_pdf, name='gerar_carne_pdf'),
    path('plano/editar/<int:pk>/', views.plano_editar, name='plano_editar'),
     path('parcela/relatorio-parcelas/', views.relatorio_parcelas, name='relatorio_parcelas'),
]