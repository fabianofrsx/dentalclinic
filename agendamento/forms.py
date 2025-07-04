from django import forms
from .models import Agendamento, Dentista, Paciente
from datetime import datetime
from datetime import time

# Lista de horários disponíveis (ex: 8:00, 8:30, ..., 17:30)
HORARIOS_DISPONIVEIS = [
    (f"{h:02d}:{m:02d}", f"{h:02d}:{m:02d}")
    for h in range(8, 18)       # Das 8h às 18h
    for m in (0, 15, 30, 45)            # De 15 em 15 minutos
]

class AgendamentoForm(forms.ModelForm):
    paciente = forms.ModelChoiceField(
        queryset=Paciente.objects.all(),
        widget=forms.Select(attrs={
            'class': 'form-control select2',
            'style': 'width: 100%'
        }),
        required=True
    )
    # Horários disponíveis (8:00 às 17:45 em intervalos de 15 minutos)
    HORARIOS = [(time(h, m).strftime('%H:%M'), time(h, m).strftime('%H:%M')) 
               for h in range(8, 18) 
               for m in (0, 15, 30, 45)]

    hora = forms.ChoiceField(
        choices=HORARIOS,
        widget=forms.Select(attrs={
            'class': 'form-select',
            'id': 'id_hora'
        })
    )

    SIM_NAO = [
        (True, 'Sim'),
        (False, 'Não'),
    ]

    confirmacao = forms.ChoiceField(
        choices=SIM_NAO,
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
        label="Confirmação"
    )

    class Meta:
        model = Agendamento
        fields = ['paciente', 'dentista', 'data', 'hora', 'status', 'observacoes']
        widgets = {
            'data': forms.DateInput(
                attrs={
                    'type': 'date',
                    'class': 'form-control',
                    'id': 'id_data'
                },
                format='%Y-%m-%d'  # <- ESSA LINHA É ESSENCIAL
            
            ),
            'paciente': forms.Select(attrs={
                'class': 'form-select',
                'id': 'id_paciente'
            }),
            'dentista': forms.Select(attrs={
                'class': 'form-select',
                'id': 'id_dentista'
            }),
            'status': forms.Select(attrs={
                'class': 'form-select',
                'id': 'id_status'
            }),
           
            'observacoes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Informações relevantes sobre o agendamento'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['data'].input_formats = ['%Y-%m-%d']
        # Adiciona classes e placeholders
        self.fields['paciente'].empty_label = 'Selecione um paciente'
        self.fields['dentista'].empty_label = 'Selecione um dentista'
        self.fields['status'].empty_label = 'Selecione o status'
        
class DentistaForm(forms.ModelForm):
    class Meta:
        model = Dentista
        fields = ['nome', 'especialidade']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'especialidade': forms.TextInput(attrs={'class': 'form-control'}),
            
        }      