import django_filters
from django import forms
from .models import Caixa, Contrato, Paciente
from django.forms import widgets

class CaixaFilter(django_filters.FilterSet):
    data_inicio = django_filters.DateFilter(
        field_name='data', lookup_expr='gte',
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    data_fim = django_filters.DateFilter(
        field_name='data', lookup_expr='lte',
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    tipo = django_filters.ChoiceFilter(
        widget=forms.Select(attrs={'class': 'form-control'}),
        choices=Caixa.TIPO_CHOICES
    )
    forma = django_filters.ChoiceFilter(
        widget=forms.Select(attrs={'class': 'form-control'}),
        choices=Caixa.FORMA_CHOICES
    )
    
    class Meta:
        model = Caixa
        fields = ['data_inicio', 'data_fim', 'tipo', 'forma', 'plano_conta']

class ContratoFilter(django_filters.FilterSet):
    
    paciente = django_filters.CharFilter(
        field_name='paciente__nome', # Use '__nome' para filtrar pelo nome do paciente
        lookup_expr='icontains',     # Busca por "contém" (case-insensitive)
        label='Paciente',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Digite o nome do paciente'})
    )
    
    status_contrato = django_filters.ChoiceFilter(
        choices=Contrato.STATUS_CONTRATO_CHOICES, label="Status",
        widget=widgets.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model = Contrato
        fields = ['paciente', 'status_contrato']

    def filter_paciente(self, queryset, name, value):
        return queryset.filter(paciente=value)

