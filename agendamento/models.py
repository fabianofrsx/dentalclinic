from django.db import models
from paciente.models import Paciente

STATUS= [
    ('agendado', 'Agendado'),
    ('atendido', 'Atendido'),
    ('remarcado', 'Remarcado'),
    ('reagendado', 'Reagendado'),
]

STATUS_CORES = {
    'agendado': 'green',
    'atendido': 'blue',
    'remarcado': 'red',
    'reagendado': 'orange',
}

class Dentista(models.Model):
    nome = models.CharField(max_length=150)
    especialidade = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.nome

class Agendamento(models.Model):
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE)
    dentista = models.ForeignKey(Dentista, on_delete=models.SET_NULL, null=True, blank=True)
    data = models.DateField()
    hora = models.TimeField()
    status = models.CharField(max_length=20, choices=STATUS, default='agendado')
    observacoes = models.TextField(blank=True, null=True)

    data_criacao = models.DateTimeField(auto_now_add=True)

    def cor_status(self):
        return STATUS_CORES.get(self.status, 'gray')

    def __str__(self):
        return f'{self.paciente.nome} - {self.data} {self.hora}'
