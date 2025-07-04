# agendamento/views.py
from django.shortcuts import render, redirect
from .models import Agendamento, Paciente
from datetime import date
from .forms import AgendamentoForm, DentistaForm
from .filters import AgendamentoFilter
from django.db.models import Count
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from datetime import datetime
from django.shortcuts import get_object_or_404
from django.db.models import Q

def dashboard(request):
    hoje = date.today()
    agendamentos_dia = Agendamento.objects.filter(data=hoje).order_by('hora')
    return render(request, 'core/dashboard.html', {'agendamento': agendamentos_dia})

def agendar(request):
    if request.method == 'POST':
        form = AgendamentoForm(request.POST)
        form_dentista = DentistaForm()  # mantém o form do modal vazio
        if form.is_valid():
            form.save()
            return redirect('agendamento:agendar')
    else:
        form = AgendamentoForm()
        form_dentista = DentistaForm()

    return render(request, 'agendamento/agendar.html', {
        'form': form,
        'form_dentista': form_dentista
    })


def lista_agendamentos(request):
    # Filtro base com todos os agendamentos
    base_queryset = Agendamento.objects.all().order_by('-data', '-hora')

    # Busca por nome ou CPF (antes do filtro)
    busca = request.GET.get('busca')
    if busca:
        base_queryset = base_queryset.filter(
            Q(paciente__nome__icontains=busca) |
            Q(paciente__cpf__icontains=busca)
        )

    # Filtro completo (django-filter usa o queryset já filtrado por busca)
    filtro = AgendamentoFilter(request.GET, queryset=base_queryset)
    agendamentos_filtrados = filtro.qs

    # Paginação
    paginator = Paginator(agendamentos_filtrados, 25)
    page_number = request.GET.get('page')
    agendamentos_paginados = paginator.get_page(page_number)

    # Cálculo de totais com base no queryset final
    total = agendamentos_filtrados.count()
    total_agendado = agendamentos_filtrados.filter(status='agendado').count()
    total_atendido = agendamentos_filtrados.filter(status='atendido').count()
    total_remarcado = agendamentos_filtrados.filter(status='remarcado').count()
    total_reagendado = agendamentos_filtrados.filter(status='reagendado').count()
    total_faltou = agendamentos_filtrados.filter(status='faltou').count()

    context = {
        'agendamentos': agendamentos_paginados,
        'filter': filtro,
        'total': total,
        'total_agendado': total_agendado,
        'total_atendido': total_atendido,
        'total_remarcado': total_remarcado,
        'total_reagendado': total_reagendado,
        'total_faltou': total_faltou
    }

    return render(request, 'agendamento/lista_agendamentos.html', context)

def agendamentos_pdf(request):
    agendamentos_queryset = Agendamento.objects.all()
    filtro_agendamentos = AgendamentoFilter(request.GET, queryset=agendamentos_queryset)
    agendamentos_filtrados = filtro_agendamentos.qs

    # Total de registros filtrados
    total = agendamentos_filtrados.count()

    template_path = 'agendamento/agendamentos_pdf.html'
    context = {
        'agendamentos': agendamentos_filtrados,
        'total': total,
    }

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="agendamentos.pdf"'

    template = get_template(template_path)
    html = template.render(context)

    pisa_status = pisa.CreatePDF(
        html, dest=response
    )

    if pisa_status.err:
        return HttpResponse('Erro ao gerar o PDF', status=500)
    return response

def excluir_agenda(request, pk):
    agendamento = get_object_or_404(Agendamento, pk=pk)
    if request.method == 'POST':
        agendamento.delete()
        return redirect('agendamento:lista_agendamentos')
    
    return render(request, 'agendamento/confirmar_excluir.html', {'agendamento': agendamento})

def editar_agenda(request, pk):
    agendamento = get_object_or_404(Agendamento, pk=pk)
    if request.method == 'POST':
        form = AgendamentoForm(request.POST, instance=agendamento)
        if form.is_valid():
            form.save()
            return redirect('agendamento:lista_agendamentos')  # Corrigido para usar o nome da URL
    else:
        form = AgendamentoForm(instance=agendamento)
    return render(request, 'agendamento/agendar.html', {'form': form})

def autocomplete_paciente(request):
    term = request.GET.get('term', '')
    pacientes = Paciente.objects.filter(
        Q(nome__icontains=term) | Q(cpf__icontains=term)
    ).values('id', 'nome', 'cpf')[:10]
    
    results = [{
        'id': p['id'],
        'label': f"{p['nome']} - {p['cpf']}",
        'value': p['nome']
    } for p in pacientes]
    
    return JsonResponse(results, safe=False)

def cadastro_dentista(request):
    if request.method == 'POST':
        form = DentistaForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect(request.META.get('HTTP_REFERER', 'agendamento:novo_agendamento'))
    else:
        form = DentistaForm()

    return render(request, 'cadastro_dentista_modal.html', {'form_dentista': form})

