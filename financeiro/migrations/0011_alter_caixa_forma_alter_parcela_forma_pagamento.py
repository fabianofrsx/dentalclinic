# Generated by Django 5.2.1 on 2025-07-04 03:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('financeiro', '0010_parcela_valor_pago_alter_caixa_plano_conta'),
    ]

    operations = [
        migrations.AlterField(
            model_name='caixa',
            name='forma',
            field=models.CharField(choices=[('dinheiro', 'Dinheiro'), ('pix_pj', 'Pix PJ'), ('pix_pf', 'Pix PF'), ('cartao_credito', 'Cartão de crédito'), ('cartao_debito', 'Cartão de débito')], max_length=20),
        ),
        migrations.AlterField(
            model_name='parcela',
            name='forma_pagamento',
            field=models.CharField(blank=True, choices=[('dinheiro', 'Dinheiro'), ('pix_pj', 'Pix PJ'), ('pix_pf', 'Pix PF'), ('cartao_credito', 'Cartão de crédito'), ('cartao_debito', 'Cartão de débito')], max_length=20, null=True),
        ),
    ]
