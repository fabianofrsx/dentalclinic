from django.contrib import admin
from django.urls import path
from django.utils.html import format_html
from django.shortcuts import render
from rangefilter.filters import DateRangeFilter
from .models import Agendamento, Dentista
from .forms import AgendamentoForm
from reportlab.lib.units import cm
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, landscape
from django.db.models import Sum
from decimal import Decimal
from django.db.models import Count


@admin.register(Agendamento)
class AgendamentoAdmin(admin.ModelAdmin):
    list_display = ('paciente', 'dentista', 'data', 'hora', 'status_badge', 'calendario_button')
    fields = ('paciente', 'dentista', 'data', 'hora', 'status')
    list_filter = ('data', 'dentista', 'status')
    search_fields = ('paciente__nome', 'dentista__nome')
    date_hierarchy = ('data')
    list_per_page = 20

    actions = ['exportar_relatorio_agendamentos_pdf']

    def exportar_relatorio_agendamentos_pdf(self, request, queryset):
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="relatorio_agendamentos.pdf"'

        buffer = canvas.Canvas(response, pagesize=landscape(A4))
        width, height = landscape(A4)
        y = height - 2 * cm

        def nova_pagina():
            nonlocal y
            buffer.showPage()
            y = height - 2 * cm
            # Page Header
            buffer.setFont("Helvetica-Bold", 14)
            buffer.drawString(2 * cm, y, "Relatório de Agendamentos")
            y -= 1 * cm

            # Section Header for following pages
            buffer.setFont("Helvetica-Bold", 12)
            buffer.drawString(2 * cm, y, "Agendamentos (continuação):")
            y -= 0.7 * cm
            buffer.setFont("Helvetica", 9)

        # Main Header
        buffer.setFont("Helvetica-Bold", 14)
        buffer.drawString(2 * cm, y, "Relatório de Agendamentos")
        y -= 1 * cm

        # Period
        datas_agendamento = queryset.values_list('data', flat=True) # Assuming 'data_agendamento' is your date field
        if datas_agendamento:
            data_min = min(datas_agendamento).strftime('%d/%m/%Y')
            data_max = max(datas_agendamento).strftime('%d/%m/%Y')
            buffer.setFont("Helvetica", 10)
            buffer.drawString(2 * cm, y, f"Período: {data_min} a {data_max}")
            y -= 1 * cm

        # Totals
        total_agendamentos = queryset.count()
        buffer.drawString(2 * cm, y, f"Total de Agendamentos Selecionados: {total_agendamentos}")
        y -= 1 * cm

        # Totals by Status (Example)
        buffer.setFont("Helvetica-Bold", 11)
        buffer.drawString(2 * cm, y, "Total por Status:")
        y -= 0.8 * cm

        # Assuming 'status' is a field in your Agendamento model
        status_counts = queryset.values('status').annotate(total=Count('id')).order_by('status')
        buffer.setFont("Helvetica", 10)
        for status_item in status_counts:
            buffer.drawString(2.5 * cm, y, f"{status_item['status']}: {status_item['total']}")
            y -= 0.5 * cm
        y -= 1 * cm

        # Header for the Appointments List
        buffer.setFont("Helvetica-Bold", 12)
        buffer.drawString(2 * cm, y, "Detalhes dos Agendamentos:")
        y -= 0.7 * cm

        agendamentos = queryset.order_by('data', 'hora') # Order by date and time
        line_height = 0.6 * cm
        largura_total = width - 4 * cm

        buffer.setFont("Helvetica-Bold", 10)
        # Column Headers
        buffer.drawString(2 * cm, y, "Data")
        buffer.drawString(5 * cm, y, "Hora")
        buffer.drawString(7 * cm, y, "Paciente")
        buffer.drawString(13 * cm, y, "Dentista")
        buffer.drawString(20 * cm, y, "Status")
        y -= line_height

        buffer.setFont("Helvetica", 9)

        for idx, item in enumerate(agendamentos):
            if y < 3 * cm:
                nova_pagina()

            # Alternating background color
            if idx % 2 == 0:
                buffer.setFillColorRGB(0.95, 0.95, 0.95)
            else:
                buffer.setFillColorRGB(1, 1, 1)
            buffer.rect(2 * cm, y - 0.15 * cm, largura_total, line_height, fill=1, stroke=0)

            buffer.setFillColorRGB(0, 0, 0) # Text color

            # Row Data
            buffer.drawString(2 * cm, y, item.data.strftime('%d/%m/%Y'))
            buffer.drawString(5 * cm, y, item.hora.strftime('%H:%M')) # Assuming 'hora_agendamento' field
            buffer.drawString(7 * cm, y, str(item.paciente)) # Assuming a 'cliente' field (ForeignKey to a Client model, for example)
            buffer.drawString(13 * cm, y, str(item.dentista)) # Assuming a 'servico' field
            buffer.drawString(20 * cm, y, item.status.upper())
            
            y -= line_height

        buffer.save()
        return response

    exportar_relatorio_agendamentos_pdf.short_description = "📄 Exportar Relatório de Agendamentos em PDF"

    @admin.display(description='Status')
    def status_badge(self, obj):
        colors = {
            'agendado': 'blue',
            'cancelado': 'red',
            'concluido': 'green',
            'confirmado': 'orange'
        }
        return format_html(
            '<span style="padding: 5px 10px; border-radius: 10px; background: {}; color: white;">{}</span>',
            colors.get(obj.status, 'green'),
            obj.get_status_display().upper()
        )
    
    @admin.display(description='Ações')
    
    def calendario_button(self, obj):
        return format_html(
            '''
            <div class="actions">
                <a class="button" href="{}" style="background: #4CAF50; color: white;">
                    <i class="fas fa-calendar-alt"></i> Calendário
                </a>
              </div>
            ''',
            'agendamento/templates/agendamento/',
            obj.id
        )
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('agendamento/templates/agendamento/', self.admin_site.admin_view(self.calendario_view), 
                 name='admin_calendario'),
        ]
        return custom_urls + urls

    def calendario_view(self, request):
        context = {
            'title': 'Visualização do Calendário',
            'opts': self.model._meta,
            'has_view_permission': self.has_view_permission(request),
        }
        return render(request, 'agendamento/templates/calendario.html', context)


@admin.register(Dentista)
class DentistaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'especialidade')
    search_fields = ('nome', 'especialidade')
    list_filter = ('especialidade',)