from django.db.models.signals import post_save
from django.dispatch import receiver
from datetime import date
from dateutil.relativedelta import relativedelta
from .models import Contrato, Parcela, Caixa
import logging

logger = logging.getLogger(__name__)

@receiver(post_save, sender=Contrato)
def gerar_parcelas_contrato(sender, instance, created, **kwargs):
    if created:
        plano = instance.plano
        data_adesao = instance.data_adesao
        dia_vencimento = instance.dia_vencimento
        
        # 1. Calcula o primeiro dia do mês seguinte
        primeiro_dia_mes_seguinte = (data_adesao.replace(day=1) + relativedelta(months=1))
        
        # 2. Tenta definir o dia de vencimento no mês seguinte
        try:
            primeiro_vencimento = primeiro_dia_mes_seguinte.replace(day=dia_vencimento)
        except ValueError:
            # 3. Caso o dia não exista (ex: 31 em meses com menos dias),
            # calcula o último dia do mês
            ultimo_dia_mes = (primeiro_dia_mes_seguinte.replace(day=28) + 
                             relativedelta(days=4)).replace(day=1) - relativedelta(days=1)
            primeiro_vencimento = primeiro_dia_mes_seguinte.replace(day=ultimo_dia_mes.day)
        
        # 4. Gera todas as parcelas com intervalo mensal
        for i in range(plano.periodo):
            data_vencimento = primeiro_vencimento + relativedelta(months=i)
            
            # 5. Cria a parcela no banco de dados
            Parcela.objects.create(
                contrato=instance,
                numero=i+1,
                data_vencimento=data_vencimento,
                valor=plano.valor / plano.periodo,
                status='aberto'
            )

@receiver(post_save, sender=Parcela)
def lancar_entrada_caixa(sender, instance, created, **kwargs):
    if instance.status and not created:
        # Garante que não lance duplicado
        descricao = f"Recebimento do plano {instance.contrato} - Parcela {instance.id}"

        existe = Caixa.objects.filter(
            descricao=descricao,
            valor=instance.valor,
            tipo='entrada',
            forma=instance.forma_pagamento,
        ).exists()

        if not existe:
            Caixa.objects.create(
                data=instance.data_pagamento,
                descricao=descricao,
                valor=instance.valor,
                tipo='entrada',
                forma=instance.forma_pagamento,
                plano_conta='planos',
            )