# sua_app/filters.py
import django_filters
from django.forms import widgets # <-- Adicione esta importação
from .models import Agendamento, Paciente, STATUS, Dentista

class AgendamentoFilter(django_filters.FilterSet):
    data_inicio = django_filters.DateFilter(
        field_name='data',
        lookup_expr='gte',
        label='Data Início',
        widget=widgets.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    data_fim = django_filters.DateFilter(
        field_name='data',
        lookup_expr='lte',
        label='Data Fim',
        widget=widgets.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )

    paciente = django_filters.ModelChoiceFilter(
        queryset=Paciente.objects.all(),
        label='Paciente',
        empty_label="Todos os Pacientes",
        widget=widgets.Select(attrs={'class': 'form-select'})
    )

    # Use Dentista diretamente, pois ele já está disponível no escopo da importação de .models
    dentista = django_filters.ModelChoiceFilter(
        queryset=Dentista.objects.all(), # <--- Agora Dentista será reconhecido
        label='Dentista',
        empty_label="Todos os Dentistas",
        widget=widgets.Select(attrs={'class': 'form-select'})
    )

    status = django_filters.ChoiceFilter(
        choices=STATUS, # <--- E STATUS também será reconhecido
        label='Status',
        empty_label="Todos os Status",
        widget=widgets.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model = Agendamento
        fields = []
