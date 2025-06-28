from django.contrib import admin, messages
from django.utils.html import format_html
from django.urls import reverse
from django.utils import timezone
from django.db.models import Sum
from collections import defaultdict
from decimal import Decimal
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import cm
from django.db.models import Count
from rangefilter.filters import DateRangeFilter
from django.template.loader import render_to_string
import tempfile
from django.templatetags.static import static


from .models import Contrato, Parcela, Plano, Caixa

@admin.register(Contrato)
class ContratoAdmin(admin.ModelAdmin):
    list_display = ('paciente', 'plano', 'data_adesao', 'dia_vencimento','status_contrato')
    search_fields = ('paciente__nome', 'plano__nome','numero_contrato')
    list_filter = ('paciente','status_contrato','plano')
    ordering = ('data_adesao',)

    actions = ['gerar_relatorio_pdf']

    def gerar_relatorio_pdf(self, request, queryset):
        if not queryset.exists():
            self.message_user(request, "Nenhum contrato encontrado com os filtros aplicados.")
            return

        html = render_to_string("financeiro/admin/relatorio_contratos.html", {
            "contratos": queryset,
        })
        pdf = HTML(string=html).write_pdf()
        response = HttpResponse(pdf, content_type="application/pdf")
        response['Content-Disposition'] = 'inline; filename="relatorio_contratos.pdf"'
        return response

    gerar_relatorio_pdf.short_description = "📄 Gerar PDF dos contratos filtrados"
    
@admin.register(Plano)
class PlanoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'valor', 'descricao')
    search_fields = ('nome',)


@admin.register(Parcela)
class ParcelaAdmin(admin.ModelAdmin):
    list_display = ['contrato', 'numero', 'data_vencimento', 'valor', 'status', 'data_pagamento']
    list_filter = ['status', 'contrato']
    ordering = ('numero',)
    readonly_fields = ('contrato', 'numero', 'data_vencimento', 'valor')
        
    fieldsets = (
        ('Informações da Parcela', {
            'fields': ('contrato', 'numero', 'data_vencimento', 'valor'),
            'classes': ('show',),     
            }),
        ('Receber', {
            'fields': ('status', 'data_pagamento','forma_pagamento', 'observacao'),
            'classes': ('show',),
        }),
    )

     #Oculta do menu admin
    def has_module_permission(self, request):
        return False  # Isso remove do menu mas mantém acessível por URL
   

@admin.register(Caixa)
class CaixaAdmin(admin.ModelAdmin):
    list_display = ('data', 'descricao', 'valor', 'tipo', 'forma', 'plano_conta')
    list_filter = (
        ('data', DateRangeFilter),
      )
    
    actions = ['exportar_relatorio_pdf']

    def exportar_relatorio_pdf(self, request, queryset):
     
    # Preparar os dados
     datas = queryset.values_list('data', flat=True)
     data_min = min(datas).strftime('%d/%m/%Y') if datas else ''
     data_max = max(datas).strftime('%d/%m/%Y') if datas else ''
     
     total_entradas = queryset.filter(tipo='entrada').aggregate(
        total=Sum('valor'))['total'] or Decimal('0.00')
     total_saidas = queryset.filter(tipo='saida').aggregate(
        total=Sum('valor'))['total'] or Decimal('0.00')
     saldo = total_entradas - total_saidas
    
     formas_totais = defaultdict(lambda: Decimal('0.00'))
     for item in queryset:
        if item.tipo == 'entrada':
            formas_totais[item.forma] += item.valor
        else:
            formas_totais[item.forma] -= item.valor
    
     lancamentos = queryset.order_by('data')
    
     # Contexto para o template
     context = {
        'data_min': data_min,
        'data_max': data_max,
        'total_entradas': total_entradas,
        'total_saidas': total_saidas,
        'saldo': saldo,
        'formas_totais': dict(formas_totais),
        'lancamentos': lancamentos,
     }
    
     # Renderizar o template HTML
     html_string = render_to_string('financeiro/admin/relatorio_caixa_pdf.html', context)
    
     # Criar o PDF
     html = HTML(string=html_string)
     result = html.write_pdf()
    
     #  Criar a resposta
     response = HttpResponse(content_type='application/pdf')
     response['Content-Disposition'] = 'attachment; filename="relatorio_caixa.pdf"'
     response.write(result)
    
     return response

    exportar_relatorio_pdf.short_description = "📄 Exportar Relatório Selecionado em PDF"

    def changelist_view(self, request, extra_context=None):
        response = super().changelist_view(request, extra_context)

        try:
            qs = response.context_data['cl'].queryset

            total_entradas = qs.filter(tipo='entrada').aggregate(Sum('valor'))['valor__sum'] or 0
            total_saidas = qs.filter(tipo='saida').aggregate(Sum('valor'))['valor__sum'] or 0
            saldo = total_entradas - total_saidas

                    
            # Totais por forma de pagamento
            formas = [('dinheiro', 'Dinheiro'),('pix', 'Pix'),('cartao_credito', 'Cartão de crédito'),('cartao_debito', 'Cartão de débito'),]   
            totais_forma = defaultdict(lambda: {'entrada': 0, 'saida': 0})

            for forma in formas:
                for tipo in ['entrada', 'saida']:
                    total = qs.filter(forma=forma, tipo=tipo).aggregate(Sum('valor'))['valor__sum'] or 0
                    totais_forma[forma][tipo] = total

            # Geração da mensagem detalhada
            msg_formas = " | ".join(
                [f"{forma.replace('_', ' ').title()}: +R${valores['entrada']:.2f} / -R${valores['saida']:.2f}"
                 for forma, valores in totais_forma.items()]
            )

            self.message_user(
                request,
                f"📆 Período filtrado — 💰 Entradas: R$ {total_entradas:.2f} | "
                f"💸 Saídas: R$ {total_saidas:.2f} | 📊 Saldo: R$ {saldo:.2f}\n"
                f"🔎 Totais por Forma: {msg_formas}",
                messages.INFO
            )
        except (AttributeError, KeyError):
            pass

        return response
    
    