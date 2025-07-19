from django.shortcuts import render, redirect
from datetime import date
from agendamento.models import Agendamento, Dentista
from financeiro.models import Contrato, Caixa
from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.contrib.auth import authenticate, login, logout
from .forms import LoginForm
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models import Sum
from django.utils.timezone import localdate
from datetime import datetime, timedelta
import calendar
import locale


@login_required(login_url='login')
def dashboard(request):
    # Data base
    hoje = localdate()

    # Parâmetros GET
    view_type = request.GET.get('view', 'week')
    date_str = request.GET.get('date', hoje.strftime('%Y-%m-%d'))
    dentista_id = request.GET.get('dentista', 'todos')
    page = request.GET.get('page', 1)

    # Conversão da data
    try:
        data_inicio = datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        data_inicio = hoje

    # Determinar intervalo da visualização
    if view_type == 'day':
        data_fim = data_inicio
    elif view_type == 'month':
        primeiro_dia = data_inicio.replace(day=1)
        ultimo_dia = (primeiro_dia + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        data_inicio, data_fim = primeiro_dia, ultimo_dia
    else:  # week
        data_inicio = data_inicio - timedelta(days=data_inicio.weekday())
        data_fim = data_inicio + timedelta(days=6)

    semana_atual = data_inicio.isocalendar()[1]

    # Nomes dos dias abreviados em português
    dias_abreviados = ['Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb', 'Dom']
    dias_semana = []
    for i in range(7):
        dia = data_inicio + timedelta(days=i)
        nome_dia = dias_abreviados[dia.weekday()]
        dias_semana.append({
            'nome': nome_dia,
            'data': dia,
            'ativo': dia == data_inicio
        })

    # Filtro de dentista
    agendamento_filter = {
        'data__range': (data_inicio, data_fim)
    }
    if dentista_id != 'todos':
        agendamento_filter['dentista_id'] = dentista_id

    # Agendamentos filtrados
    agendamentos_filtrados = Agendamento.objects.filter(**agendamento_filter).select_related('paciente', 'dentista').order_by('data', 'hora')
    paginator = Paginator(agendamentos_filtrados, 30)
    agendamentos = paginator.get_page(page)

    # Caixa (entradas/saídas do dia)
    movimentacoes = Caixa.objects.filter(data=hoje)
    total_entradas = movimentacoes.filter(tipo='entrada').aggregate(Sum('valor'))['valor__sum'] or 0
    total_saidas = movimentacoes.filter(tipo='saida').aggregate(Sum('valor'))['valor__sum'] or 0
    saldo = total_entradas - total_saidas

    # Saldo por forma de pagamento
    saldo_por_forma = {}
    formas_pagamento = dict(Caixa.FORMA_CHOICES).keys()
    for forma in formas_pagamento:
        entradas = movimentacoes.filter(tipo='entrada', forma=forma).aggregate(Sum('valor'))['valor__sum'] or 0
        saidas = movimentacoes.filter(tipo='saida', forma=forma).aggregate(Sum('valor'))['valor__sum'] or 0
        nome_forma = dict(Caixa.FORMA_CHOICES)[forma]
        saldo_por_forma[nome_forma] = entradas - saidas

    # Contratos
    contratos_ativos = Contrato.objects.filter(status_contrato='ativo').count()
    contratos_pendentes = Contrato.objects.filter(status_contrato='pendente').count()
    contratos_cancelados = Contrato.objects.filter(status_contrato='cancelado').count()
    total_contratos = Contrato.objects.count()

    dentistas = Dentista.objects.all()

    context = {
        'data_atual': hoje,
        'dentistas': dentistas,
        'dentista_selecionado': dentista_id,
        'data_inicio': data_inicio,
        'data_fim': data_fim,
        'view_type': view_type,
        'semana_atual': semana_atual,
        'dias_semana': dias_semana,

        # Agendamentos
        'agendamentos': agendamentos,
        'total_agendados': agendamentos_filtrados.filter(status='agendado').count(),

        # Caixa
        'total_entradas': total_entradas,
        'total_saidas': total_saidas,
        'saldo': saldo,
        'saldo_por_forma': saldo_por_forma,

        # Contratos
        'contratos_ativos': contratos_ativos,
        'contratos_pendentes': contratos_pendentes,
        'contratos_cancelados': contratos_cancelados,
        'total_contratos': total_contratos,
    }

    return render(request, 'core/dashboard.html', context)

def login_view(request):
    if request.user.is_authenticated:
        return redirect('core:dashboard')  # ou sua página principal

    form = LoginForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = authenticate(
            request,
            username=form.cleaned_data['username'],
            password=form.cleaned_data['password']
        )
        if user:
            login(request, user)
            return redirect('core:dashboard')
        else:
            form.add_error(None, 'Usuário ou senha inválidos.')

    return render(request, 'login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login')

