from django.db import models
from django.contrib.auth import get_user_model
from datetime import date
from paciente.models import Paciente
from django.utils.safestring import mark_safe
from django.urls import reverse


User = get_user_model()

class Plano(models.Model):
    nome = models.CharField(max_length=100, verbose_name="NOME")
    descricao = models.TextField(blank=True, verbose_name="DESCRIÇÃO")
    valor = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="VALOR")
    periodo = models.PositiveIntegerField(default=12, verbose_name="PARCELAS")  # em meses

    def __str__(self):
        return self.nome


class Contrato(models.Model):
    STATUS_CONTRATO_CHOICES = [
        ('ativo', 'ATIVO'),
        ('pendente', 'PENDENTE'),
        ('cancelado', 'CANCELADO'),
        ]
    
    paciente = models.ForeignKey('paciente.Paciente', on_delete=models.CASCADE, verbose_name='Paciente')
    plano = models.ForeignKey(Plano, on_delete=models.CASCADE, verbose_name='Plano')
    data_adesao = models.DateField(default=date.today, verbose_name='Adesão')
    dia_vencimento = models.IntegerField(choices=[(d, f"Dia {d}") for d in [5, 10, 15, 20, 25, 30]], verbose_name='Vencimento')
    numero_contrato = models.CharField(max_length=20, unique=True, verbose_name='Contrato')
    status_contrato = models.CharField(max_length=20, verbose_name='Status', choices=STATUS_CONTRATO_CHOICES, null=True, blank=True)
    
    def __str__(self):
        return f"Contrato {self.numero_contrato} - {self.paciente.nome}"
    
    def parcelas_em_html(self, obj):
     parcelas_em_aberto = obj.parcelas.filter(status='aberto').order_by('data_vencimento')
     parcelas_pagas = obj.parcelas.filter(status='pago').order_by('data_vencimento')

     html = ""

     if parcelas_em_aberto.exists():
        html += "<h4 style='color: #a94442;'>🔴 Parcelas em Aberto</h4>"
        for p in parcelas_em_aberto:
            link = f"/admin/financeiro/parcela/{p.id}/change/"
            html += (
                f"<div style='margin-bottom: 5px; background-color:#f2dede; padding:10px; border-radius:5px;'>"
                f"<strong>Venc:</strong> {p.data_vencimento} | "
                f"<strong>Valor:</strong> R$ {p.valor} | "
                f"<strong>Status:</strong> Em aberto | "
                f"<a href='{link}' target='_blank'>Dar Baixa</a></div>"
            )

     if parcelas_pagas.exists():
        html += "<h4 style='color: #3c763d;'>🟢 Parcelas Pagas</h4>"
        for p in parcelas_pagas:
            link = f"/admin/financeiro/parcela/{p.id}/change/"
            html += (
                f"<div style='margin-bottom: 5px; background-color:#dff0d8; padding:10px; border-radius:5px;'>"
                f"<strong>Venc:</strong> {p.data_vencimento} | "
                f"<strong>Valor:</strong> R$ {p.valor} | "
                f"<strong>Status:</strong> Pago | "
                f"<a href='{link}' target='_blank'>Visualizar</a></div>"
            )

     if not html:
        html = "Nenhuma parcela cadastrada."

     return mark_safe(html)

#parcelas_em_html.short_description = "Financeiro"
    
class Parcela(models.Model):
    FORMA_PAGAMENTO_CHOICES = [
        ('dinheiro', 'Dinheiro'),
        ('pix', 'Pix'),
        ('cartao_credito', 'Cartão de crédito'),
        ('cartao_debito', 'Cartão de débito'),
    ]

    contrato = models.ForeignKey(Contrato, on_delete=models.CASCADE, related_name='parcelas')
    numero = models.PositiveIntegerField(verbose_name="Parcela")
    data_vencimento = models.DateField()
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    valor_pago = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # <== ADICIONADO
    status = models.CharField(max_length=20, choices=[('aberto', 'Aberto'), ('pago', 'Pago')], default="aberto")
    data_pagamento = models.DateField(null=True, blank=True)
    forma_pagamento = models.CharField(max_length=20, choices=FORMA_PAGAMENTO_CHOICES, null=True, blank=True)
    observacao = models.TextField(blank=True)

    def __str__(self):
        return f"Parcela {self.numero} - {self.contrato.numero_contrato}"


class Caixa(models.Model):
    PLANO_DE_CONTAS = [
        ('Consultorio', 'Despesa do Consultório'),
        ('Boletos', 'Boletos'),
        ('Outros', 'Outros'),
        ('Planos', 'Planos'),
        ('Procedimento', 'Procedimento Particular')
    ]

    FORMA_CHOICES = [
        ('dinheiro', 'Dinheiro'),
        ('pix', 'Pix'),
        ('cartao_credito', 'Cartão de crédito'),
        ('cartao_debito', 'Cartão de débito'),
    ]

    TIPO_CHOICES = [
     ('entrada', 'Entrada'), 
     ('saida', 'Saída'),
    ]

    data = models.DateField(default=date.today)
    descricao = models.CharField(max_length=255)
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    tipo = models.CharField(max_length=10, choices=[('entrada', 'Entrada'), ('saida', 'Saída')])
    forma = models.CharField(max_length=20, choices=FORMA_CHOICES)
    plano_conta = models.CharField(max_length=30, choices=PLANO_DE_CONTAS, default='outros')
    observacao = models.TextField(blank=True)

    def __str__(self):
        return f"{self.tipo.upper()} - R$ {self.valor} ({self.get_plano_conta_display()})"


