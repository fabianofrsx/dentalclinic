from django import forms
from .models import Contrato, Caixa, Parcela, Plano

class ContratoForm(forms.ModelForm):
    class Meta:
        model = Contrato
        fields = ['paciente', 'plano', 'data_adesao', 'dia_vencimento', 'numero_contrato', 'status_contrato']
        widgets = {
            'data_adesao': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'paciente': forms.Select(attrs={'class': 'form-control'}),
            'plano': forms.Select(attrs={'class': 'form-control'}),
            'dia_vencimento': forms.Select(attrs={'class': 'form-control'}),
            'numero_contrato': forms.TextInput(attrs={'class': 'form-control'}),
            'status_contrato': forms.Select(attrs={'class': 'form-control'}),
        }

class CaixaForm(forms.ModelForm):
    class Meta:
        model = Caixa
        fields = ['data', 'descricao', 'valor', 'tipo', 'forma', 'plano_conta', 'observacao']
        widgets = {
            'data': forms.DateInput(attrs={
                'type': 'date', 
                'class': 'form-control',
                'autocomplete': 'off'
            }),
            'descricao': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Descrição do lançamento'
            }),
            'valor': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'placeholder': '0,00'
            }),
            'tipo': forms.Select(attrs={
                'class': 'form-select',
                'id': 'tipo-lancamento'
            }),
            'forma': forms.Select(attrs={
                'class': 'form-select',
                'id': 'forma-pagamento'
            }),
            'plano_conta': forms.Select(attrs={
                'class': 'form-select',
                'id': 'plano-conta'
            }),
            'observacao': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 2,
                'placeholder': 'Observações adicionais'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Defina valores padrão se necessário
        self.fields['tipo'].empty_label = 'Selecione o tipo'
        self.fields['forma'].empty_label = 'Selecione a forma'
        self.fields['plano_conta'].empty_label = 'Selecione o plano'

class ParcelaReceberForm(forms.ModelForm):
    class Meta:
        model = Parcela
        fields = ['status', 'data_pagamento', 'forma_pagamento', 'observacao']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-control'}),
            'data_pagamento': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'forma_pagamento': forms.Select(attrs={'class': 'form-control'}),
            'observacao': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        } 

class PlanoForm(forms.ModelForm):
    class Meta:
        model = Plano
        fields = ['nome', 'descricao', 'valor', 'periodo']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'descricao': forms.TextInput(attrs={'class': 'form-control'}),
            'valor': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'periodo': forms.TextInput(attrs={'class': 'form-control'}),
        }                       
