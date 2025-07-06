from django import forms
from .models import Paciente

class PacienteForm(forms.ModelForm):
    class Meta:
        model = Paciente
        fields = '__all__'
        widgets = {
            'data_nascimento': forms.DateInput(attrs={
                'type': 'date', 
                'class': 'form-control'
            }),
            'observacao_contato': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 2
            }),
            'outras_observacoes': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 3
            }),
            'estado_civil': forms.Select(attrs={'class': 'form-select'}),
            'sexo': forms.Select(attrs={'class': 'form-select'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Adiciona classes padrão para todos os campos
        for field in self.fields:
            if field not in ['estado_civil', 'sexo', 'observacao_contato', 
                           'outras_observacoes', 'data_nascimento']:
                self.fields[field].widget.attrs.update({'class': 'form-control'})
            
            # Adiciona placeholders para alguns campos
            if field in ['telefone', 'cep']:
                self.fields[field].widget.attrs.update({
                    'placeholder': 'Ex: (99) 99999-9999' if field == 'telefone' else 'Ex: 99999-999'
                })