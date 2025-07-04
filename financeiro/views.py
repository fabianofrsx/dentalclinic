from django.shortcuts import render, redirect
from .models import Caixa
from .filters import CaixaFilter
from django.db.models import Sum
from .forms import CaixaForm, ContratoForm, PlanoForm
from django.template.loader import get_template
from django.shortcuts import get_object_or_404
from xhtml2pdf import pisa
from .filters import ContratoFilter
from .models import Parcela, Paciente, Plano, Contrato, Caixa
from .forms import ParcelaReceberForm
from datetime import date
from paciente.forms import PacienteForm
from django.http import HttpResponse
from django.db.models import Q
from django.core.paginator import Paginator
from django.http import JsonResponse
from agendamento.models import Agendamento
from django.template.loader import render_to_string
from io import BytesIO
import io
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Spacer, PageBreak, Paragraph
from datetime import datetime
from django.utils.timezone import localdate


def dashboard(request):
    return render(request, 'dashboard.html')

def caixa_cadastrar(request):
    if request.method == 'POST':
        form = CaixaForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('financeiro:lista_caixa')
    else:
        form = CaixaForm()

    return render(request, 'financeiro/caixa/caixa_cadastrar.html', {'form': form})


def lista_caixa(request):
    # Filtros
    queryset = Caixa.objects.all().order_by('-data')
    filtro = CaixaFilter(request.GET, queryset=queryset)
    resultados = filtro.qs
    
    # Cálculos dos totais (usando o queryset completo, não o paginado)
    total_entradas = resultados.filter(tipo='entrada').aggregate(Sum('valor'))['valor__sum'] or 0
    total_saidas = resultados.filter(tipo='saida').aggregate(Sum('valor'))['valor__sum'] or 0
    saldo = total_entradas - total_saidas
    
    # Paginação (25 itens por página)
    paginator = Paginator(resultados, 25)
    page_number = request.GET.get('page')
    lancamentos_paginados = paginator.get_page(page_number)
    
    context = {
        'filter': filtro,
        'lancamentos': lancamentos_paginados,  # Objeto paginado para a tabela
        'total_entradas': total_entradas,
        'total_saidas': total_saidas,
        'saldo': saldo,
        'total_registros': resultados.count()  # Total de registros (não paginado)
    }
    
    return render(request, 'financeiro/caixa/lista_caixa.html', context)

def caixa_pdf(request):
    queryset = Caixa.objects.all().order_by('-data')
    filtro = CaixaFilter(request.GET, queryset=queryset)
    resultados = filtro.qs

    # Total geral de entradas e saídas
    total_entradas = resultados.filter(tipo='entrada').aggregate(Sum('valor'))['valor__sum'] or 0
    total_saidas = resultados.filter(tipo='saida').aggregate(Sum('valor'))['valor__sum'] or 0
    saldo = total_entradas - total_saidas

    # Saldo por forma de pagamento
    formas = resultados.values_list('forma', flat=True).distinct()
    saldo_por_forma = {}

    for forma in formas:
        total_entrada = resultados.filter(tipo='entrada', forma=forma).aggregate(Sum('valor'))['valor__sum'] or 0
        total_saida = resultados.filter(tipo='saida', forma=forma).aggregate(Sum('valor'))['valor__sum'] or 0
        saldo_por_forma[forma] = total_entrada - total_saida

    # Renderização do PDF
    template_path = 'financeiro/caixa/caixa_pdf.html'
    context = {
        'lancamentos': resultados,
        'total_entradas': total_entradas,
        'total_saidas': total_saidas,
        'saldo': saldo,
        'saldo_por_forma': saldo_por_forma,
    }

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="caixa.pdf"'

    template = get_template(template_path)
    html = template.render(context)

    pisa_status = pisa.CreatePDF(html, dest=response)

    if pisa_status.err:
        return HttpResponse('Erro ao gerar PDF: %s' % pisa_status.err)
    return response

def contrato_cadastrar(request):
    if request.method == 'POST':
        form = ContratoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('financeiro:contrato_listar')
    else:
        form = ContratoForm()

    return render(request, 'financeiro/contrato/contrato_cadastrar.html', {'form': form})

def contrato_listar(request):
    # Consulta base com select_related para otimização
    contratos = Contrato.objects.select_related('paciente', 'plano').all().order_by('-data_adesao')

    # Busca por nome ou CPF
    busca = request.GET.get('busca')
    if busca:
        contratos = contratos.filter(
            Q(paciente__nome__icontains=busca) |
            Q(paciente__cpf__icontains=busca)
        )

    # Aplicação do filtro (django-filter)
    contrato_filter = ContratoFilter(request.GET, queryset=contratos)

    # Paginação
    paginator = Paginator(contrato_filter.qs, 25)
    page_number = request.GET.get('page')
    contratos_paginados = paginator.get_page(page_number)

    return render(request, 'financeiro/contrato/contrato_listar.html', {
        'filter': contrato_filter,
        'contratos': contratos_paginados,
    })

def contrato_editar(request, pk):
    contrato = get_object_or_404(Contrato, pk=pk)
    if request.method == 'POST':
        form = ContratoForm(request.POST, instance=contrato)
        if form.is_valid():
            form.save()
            return redirect('financeiro:contrato_listar')
    else:
        form = ContratoForm(instance=contrato)
    
    return render(request, 'financeiro/contrato/contrato_cadastrar.html', {'form': form})

def contrato_excluir(request, pk):
    contrato = get_object_or_404(Contrato, pk=pk)
    if request.method == 'POST':
        contrato.delete()
        return redirect('financeiro:contrato_listar')
    
    return render(request, 'financeiro/contrato/contrato_confirmar_excluir.html', {'contrato': contrato})

def parcela_receber(request, parcela_id):
    parcela = get_object_or_404(Parcela, id=parcela_id)
    paciente = parcela.contrato.paciente

    if request.method == 'POST':
        form = ParcelaReceberForm(request.POST, instance=parcela)
        if form.is_valid():
            form.save()
            return redirect('financeiro:paciente_ficha', paciente_id=paciente.id)
    else:
        form = ParcelaReceberForm(instance=parcela)

    return render(request, 'financeiro/parcela/parcela_receber.html', {
        'form': form,
        'parcela': parcela,
        'paciente_id': paciente.id,
    })

def plano_cadastrar(request):
    if request.method == 'POST':
        form = PlanoForm(request.POST)
        if form.is_valid():
            form.save()
            # Após salvar, redirecione para recarregar a página e exibir o novo plano
            return redirect('financeiro:plano_cadastrar')
    else:
        form = PlanoForm()

    # --- Adicione esta linha para buscar todos os planos ---
    planos = Plano.objects.all()

    # --- E adicione 'planos' ao dicionário de contexto ---
    return render(request, 'financeiro/plano/plano_cadastrar.html', {'form': form, 'planos': planos})

def plano_editar(request, pk):
    plano = get_object_or_404(Plano, pk=pk)
    if request.method == 'POST':
        form = PlanoForm(request.POST, instance=plano)
        if form.is_valid():
            form.save()
            return redirect('financeiro:plano_cadastrar')
    else:
        form = PlanoForm(instance=plano)
    
    return render(request, 'financeiro/plano/plano_cadastrar.html', {'form': form})

def paciente_ficha(request, paciente_id):
    paciente = get_object_or_404(Paciente, id=paciente_id)
    contrato = Contrato.objects.filter(paciente=paciente).first()
    parcelas_aberto = Parcela.objects.filter(contrato=contrato, status='aberto') if contrato else []
    parcelas_pagas = Parcela.objects.filter(contrato=contrato, status='pago') if contrato else []

    # NOVO: Buscar agendamentos do paciente
    agendamentos = Agendamento.objects.filter(paciente=paciente).order_by('-data', '-hora')

    if request.method == 'POST':
        form = PacienteForm(request.POST, instance=paciente)
        if form.is_valid():
            form.save()
            return redirect('financeiro:paciente_ficha', paciente_id=paciente.id)
    else:
        form = PacienteForm(instance=paciente)

    context = {
        'paciente': paciente,
        'form': form,
        'contrato': contrato,
        'parcelas_aberto': parcelas_aberto,
        'parcelas_pagas': parcelas_pagas,
        'agendamentos': agendamentos  # <-- Adiciona os agendamentos ao contexto
    }
    return render(request, 'financeiro/paciente/ficha.html', context)

def buscar_paciente(request):
    query = request.GET.get('q', '').strip()
    pacientes = []

    if query:
        # Busca paciente pelo nome ou CPF (case insensitive)
        pacientes = Paciente.objects.filter(
            Q(nome__icontains=query) | Q(cpf__icontains=query)
        )
                
        if pacientes.count() == 1:
            # Se só encontrar 1 paciente, redireciona direto para ficha
            return redirect('financeiro:paciente_ficha', paciente_id=pacientes.first().id)

    return render(request, 'financeiro/buscar_paciente.html', {'pacientes': pacientes, 'query': query})


def autocomplete_paciente(request):
    if 'term' in request.GET:
        termo = request.GET.get('term')
        qs = Paciente.objects.filter(
            Q(nome__icontains=termo) | Q(cpf__icontains=termo)
        )[:10]  # limitar resultados para não sobrecarregar
        
        resultados = []
        for paciente in qs:
            resultados.append({
                'label': f"{paciente.nome} - {paciente.cpf}",
                'value': paciente.nome,
                'id': paciente.id,
            })
        return JsonResponse(resultados, safe=False)
    return JsonResponse([], safe=False)

def buscar_pacientes(request):
    query = request.GET.get('q', '')
    pacientes = []

    if query:
        pacientes = Paciente.objects.filter(
            nome__icontains=query
        ) | Paciente.objects.filter(
            cpf__icontains=query
        )

    context = {
        'query': query,
        'pacientes': pacientes,
    }
    return render(request, 'financeiro/buscar_paciente.html', context)

def contrato_exportar_pdf(request):
    contratos = Contrato.objects.all()
    contrato_filter = ContratoFilter(request.GET, queryset=contratos)
    template = get_template('financeiro/contrato/contrato_pdf.html')
    html = template.render({'contratos': contrato_filter.qs})

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="contratos.pdf"'

    pisa.CreatePDF(html, dest=response)
    return response

def editar_caixa(request, pk):
    caixa = get_object_or_404(Caixa, pk=pk)
    if request.method == 'POST':
        form = CaixaForm(request.POST, instance=caixa)
        if form.is_valid():
            form.save()
            return redirect('financeiro:lista_caixa')  # Corrigido para usar o nome da URL
    else:
        form = CaixaForm(instance=caixa)
    return render(request, 'financeiro/caixa/caixa_cadastrar.html', {'form': form})

def excluir_caixa(request, pk):
    caixa = get_object_or_404(Caixa, pk=pk)
    if request.method == 'POST':
        caixa.delete()
        return redirect('financeiro:lista_caixa')
    return render(request, 'financeiro/caixa/caixa_confirmar_excluir.html', {'caixa': caixa})

    
def gerar_carne_pdf(request, contrato_id):
    contrato = get_object_or_404(Contrato, id=contrato_id)
    paciente = contrato.paciente  # Supondo que o contrato tem o campo paciente como FK

    # Busca as parcelas reais no banco
    parcelas_queryset = Parcela.objects.filter(contrato=contrato).order_by('data_vencimento')

    # Converte as parcelas em lista de dicionários
    parcelas = [
        {
            "numero": idx + 1,
            "total": parcelas_queryset.count(),
            "data_vencimento": parcela.data_vencimento,
            "valor": parcela.valor
        }
        for idx, parcela in enumerate(parcelas_queryset)
    ]

    # Dados do contrato
    paciente = {
        "nome": paciente.nome,
        "cpf": paciente.cpf,
        "endereco": paciente.endereco
    }

    empresa = {
        "nome": "DENTAL CLINIC",  # Ou busque de uma configuração no sistema
        "cnpj": "00.000.000/0000-00"
    }

    contrato = {
        "numero_contrato": contrato.numero_contrato
    }

    # Buffer de memória para o PDF
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, leftMargin=20, rightMargin=20, topMargin=20, bottomMargin=20)
    elements = []
    styles = getSampleStyleSheet()
    styleN = styles["Normal"]

    def p(text):
        return Paragraph(text, styleN)

    def create_boleto_table(parcela):
    # Conteúdo da coluna 1 (7 linhas)
        col1_data = [
        [p(f'<b>CONTRATO:</b> {contrato["numero_contrato"]}')],
        [p(f'<b>PARCELA:</b> {parcela["numero"]}/{parcela["total"]}')],
        [p(f'<b>VENCIMENTO:</b> {parcela["data_vencimento"].strftime("%d/%m/%Y")}')],
        [p(f'<b>VALOR:</b> R$ {parcela["valor"]:.2f}')],
        [p('<b>(-) DESCONTOS:</b>')],
        [p('<b>(+) MULTA/MORA:</b>')],
        [p('<b>(=) TOTAL:</b>')],
        ]
        col1_table = Table(col1_data, colWidths=[128], rowHeights=[23, 20, 33, 20, 20, 20, 20])  # Altura fixa de 15 pontos para cada linha)
        col1_table.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 0.5, colors.black),
        ('FONTSIZE', (0, 0), (-1, -1), 6),
        ]))

        # Conteúdo da coluna 2 (4 linhas)
        col2_data = [
        [p('<b>LOCAL DE PAGAMENTO:</b> CONSULTÓRIO ODONTOLÓGICO: DENTAL CLINIC')],
        [p(f'<b>CEDENTE:</b> {empresa["nome"]}<br/>CNPJ: {empresa["cnpj"]}')],
        [p('<b>INSTRUÇÕES:</b><br/>(Todas as informações deste carnê são de<br/>responsabilidade do cedente)<br/>Mensalidade Plano odontológico')],
        [p(f'<b>SACADO:</b> {paciente["nome"]}<br/>CPF: {paciente["cpf"]}<br/>Endereço: {paciente["endereco"]}')],
        ]
        col2_table = Table(col2_data, colWidths=[250])
        col2_table.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 0.5, colors.black),
        ('FONTSIZE', (0, 0), (-1, -1), 6),
        ]))

        # Coluna 3: cópia da coluna 1 (7 linhas)
        col3_table = Table(col1_data, colWidths=[128], rowHeights=[23, 20, 33, 20, 20, 20, 20])
        col3_table.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 0.5, colors.black),
        ('FONTSIZE', (0, 0), (-1, -1), 6),
        ]))

        # Junta as 3 colunas em uma linha
        main_table = Table([[col1_table, col2_table, col3_table]], colWidths=[128, 250, 128])
        main_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BOX', (0, 0), (-1, -1), 1, colors.black),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
        ]))

        return main_table

    # Adiciona 4 boletos por página
    for idx, parcela in enumerate(parcelas):
        elements.append(create_boleto_table(parcela))
        elements.append(Spacer(1, 12))
        if (idx + 1) % 4 == 0 and idx + 1 != len(parcelas):
            elements.append(PageBreak())

    # Gera o PDF
    doc.build(elements)
    buffer.seek(0)
    pdf_data = buffer.getvalue()

    # Retorna como resposta no navegador
    response = HttpResponse(pdf_data, content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="carne_contrato_{contrato_id}.pdf"'
    return response

def relatorio_parcelas(request):
    status = request.GET.get('status')
    paciente_id = request.GET.get('paciente')
    data_inicio = request.GET.get('data_inicio')
    data_fim = request.GET.get('data_fim')
    hoje = localdate()

    parcelas = Parcela.objects.select_related('contrato__paciente')

    # Filtrar por status
    if status == 'pagas':
        parcelas = parcelas.filter(status='pago')
    elif status == 'atrasadas':
        parcelas = parcelas.filter(status='aberto', data_vencimento__lt=hoje)
    elif status == 'a_receber':
        parcelas = parcelas.filter(status='aberto', data_vencimento__gte=hoje)

    # Filtrar por paciente
    if paciente_id:
        parcelas = parcelas.filter(contrato__paciente_id=paciente_id)

    # Filtrar por intervalo de datas de vencimento
    if data_inicio:
        parcelas = parcelas.filter(data_vencimento__gte=data_inicio)
    if data_fim:
        parcelas = parcelas.filter(data_vencimento__lte=data_fim)

    # Calcular dias de atraso para cada parcela atrasada
    parcelas_list = []
    for p in parcelas:
        dias_atraso = 0
        if p.status == 'aberto' and p.data_vencimento < hoje:
            dias_atraso = (hoje - p.data_vencimento).days
        parcelas_list.append((p, dias_atraso))

    # Exportar para PDF
    if 'exportar' in request.GET:
        template = get_template('financeiro/parcela/relatorio_parcelas_pdf.html')
        html = template.render({
        'parcelas_list': parcelas_list,
        'today': hoje,
        })
        
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="relatorio_parcelas.pdf"'
        pisa.CreatePDF(io.StringIO(html), dest=response)
        return response

    # Passar pacientes para filtro no template
    pacientes = Paciente.objects.all()

    return render(request, 'financeiro/parcela/relatorio_parcelas.html', {
        'parcelas_list': parcelas_list,
        'status': status,
        'pacientes': pacientes,
        'paciente_selecionado': paciente_id,
        'data_inicio': data_inicio,
        'data_fim': data_fim,
    })