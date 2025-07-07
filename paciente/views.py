from django.shortcuts import render, redirect
from .forms import PacienteForm
from financeiro.forms import ParcelaReceberForm
from agendamento.forms import AgendamentoForm
from django.shortcuts import render, get_object_or_404, redirect
from .models import Paciente
from django.db.models import Q
from django.http import JsonResponse
from datetime import date
from financeiro.models import Contrato, Parcela
from django.core.paginator import Paginator

def dashboard(request):
    return render(request, 'dashboard.html')

def paciente_cadastrar(request):
    if request.method == 'POST':
        form = PacienteForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('paciente:listar_pacientes')  # ou onde desejar
    else:
        form = PacienteForm()
    
    return render(request, 'paciente/paciente_cadastrar.html', {'form': form})

def listar_pacientes(request):
    pacientes_list = Paciente.objects.all().order_by('nome')
    
    # Filtro por busca
    busca = request.GET.get('busca')
    if busca:
        pacientes_list = pacientes_list.filter(
            Q(nome__icontains=busca) | Q(cpf__icontains=busca)
        )
    
    # Paginação (25 itens por página)
    paginator = Paginator(pacientes_list, 25)
    page_number = request.GET.get('page')
    pacientes = paginator.get_page(page_number)
    
    return render(request, 'paciente/listar_pacientes.html', {
        'pacientes': pacientes,
    })

def editar_paciente(request, pk):
    paciente = get_object_or_404(Paciente, pk=pk)
    if request.method == 'POST':
        form = PacienteForm(request.POST, instance=paciente)
        if form.is_valid():
            form.save()
            return redirect('paciente:listar_pacientes')
    else:
        form = PacienteForm(instance=paciente)
    return render(request, 'paciente/paciente_cadastrar.html', {'form': form})

def excluir_paciente(request, pk):
    paciente = get_object_or_404(Paciente, pk=pk)
    if request.method == 'POST':
        paciente.delete()
        return redirect('paciente:listar_pacientes')
    
    return render(request, 'paciente/paciente_confirmar_excluir.html', {'paciente': paciente})

def autocomplete_paciente(request):
    if 'term' in request.GET:
        termo = request.GET.get('term')
        qs = Paciente.objects.filter(
            Q(nome__icontains=termo) | Q(cpf__icontains=termo)
        )
        resultados = []

        for paciente in qs:
            resultados.append({
                'label': f"{paciente.nome} - {paciente.cpf}",
                'value': paciente.nome,
            })

        return JsonResponse(resultados, safe=False)
    return JsonResponse([], safe=False)

def paciente_editar(request, paciente_id):
    paciente = get_object_or_404(Paciente, id=paciente_id)
    contrato = Contrato.objects.filter(paciente=paciente).first()
    parcelas_aberto = Parcela.objects.filter(contrato__paciente=paciente, status='aberto')
    parcelas_pagas = Parcela.objects.filter(contrato__paciente=paciente, status='pago')

    if request.method == 'POST':
        form = PacienteForm(request.POST, instance=paciente)
        if form.is_valid():
            form.save()
            return redirect('paciente:editar_paciente', paciente_id=paciente.id)
    else:
        form = PacienteForm(instance=paciente)

    context = {
        'paciente': paciente,
        'form': form,
        'contrato': contrato,
        'parcelas_aberto': parcelas_aberto,
        'parcelas_pagas': parcelas_pagas,
    }
    return render(request, 'paciente/paciente_editar.html', context)



