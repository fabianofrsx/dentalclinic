from django.shortcuts import render, redirect
from datetime import date
from agendamento.models import Agendamento
from financeiro.models import Contrato, Caixa
from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.contrib.auth import authenticate, login, logout
from .forms import LoginForm
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models import Sum
from django.utils.timezone import localdate

@login_required(login_url='login')
def dashboard(request):
    hoje = localdate()  # timezone-safe

    # CONTRATOS
    status_counts = {
        'ativos': Contrato.objects.filter(status_contrato='ativo').count(),
        'pendentes': Contrato.objects.filter(status_contrato='pendente').count(),
        'cancelados': Contrato.objects.filter(status_contrato='cancelado').count(),
        'total': Contrato.objects.count()
    }

    # AGENDAMENTOS
    agendamentos_hoje = Agendamento.objects.filter(
        data=hoje
    ).select_related('paciente', 'dentista').order_by('hora')

    paginator = Paginator(agendamentos_hoje, 30)
    page_number = request.GET.get('page_agendamentos')
    agendamentos = paginator.get_page(page_number)

    # CAIXA
    movimentacoes = Caixa.objects.filter(data=hoje)

    total_entradas = movimentacoes.filter(tipo='entrada').aggregate(
        Sum('valor'))['valor__sum'] or 0

    total_saidas = movimentacoes.filter(tipo='saida').aggregate(
        Sum('valor'))['valor__sum'] or 0

    saldo = total_entradas - total_saidas

    saldo_por_forma = {}
    formas_pagamento = dict(Caixa.FORMA_CHOICES).keys()

    for forma in formas_pagamento:
        entradas = movimentacoes.filter(
            tipo='entrada', forma=forma
        ).aggregate(Sum('valor'))['valor__sum'] or 0

        saidas = movimentacoes.filter(
            tipo='saida', forma=forma
        ).aggregate(Sum('valor'))['valor__sum'] or 0

        nome_forma = dict(Caixa.FORMA_CHOICES)[forma]
        saldo_por_forma[nome_forma] = entradas - saidas

    # CONTEXTO FINAL
    context = {
        'data_atual': hoje,

        # Contratos
        'contratos_ativos': status_counts['ativos'],
        'contratos_pendentes': status_counts['pendentes'],
        'contratos_cancelados': status_counts['cancelados'],
        'total_contratos': status_counts['total'],

        # Agendamentos
        'agendamentos': agendamentos,
        'total_agendados': agendamentos_hoje.filter(status='agendado').count(),

        # Caixa
        'total_entradas': total_entradas,
        'total_saidas': total_saidas,
        'saldo': saldo,
        'saldo_por_forma': saldo_por_forma,
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

