# Generated by Django 5.2.1 on 2025-07-04 15:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('agendamento', '0002_alter_agendamento_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='agendamento',
            name='confirmacao',
            field=models.BooleanField(choices=[(True, 'Sim'), (False, 'Não')], default=False, verbose_name='Confirmação'),
        ),
        migrations.AlterField(
            model_name='agendamento',
            name='status',
            field=models.CharField(choices=[('agendado', 'Agendado'), ('atendido', 'Atendido'), ('remarcado', 'Remarcado'), ('reagendado', 'Reagendado'), ('faltou', 'Faltou')], default='agendado', max_length=20),
        ),
    ]
