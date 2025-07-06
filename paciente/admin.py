from django.contrib import admin
from .models import Paciente
from django.utils.html import format_html
from financeiro.models import Contrato, Parcela
from django.utils.safestring import mark_safe

class ContratoInline(admin.StackedInline):
    model = Contrato
    extra = 0
    show_change_link = True
    readonly_fields = (
      'paciente',
      'plano',
      'data_adesao',
      'dia_vencimento',
      'numero_contrato',
      'status_contrato',
      'parcelas_em_html',
    )
    

    def parcelas_em_html(self, obj):
        parcelas_em_aberto = obj.parcelas.filter(status='aberto').order_by('data_vencimento')
        parcelas_pagas = obj.parcelas.filter(status='pago').order_by('data_vencimento')

        html = ""

        if parcelas_em_aberto.exists():
            html += "<h4 style='color: #a94442;'> Parcelas em Aberto</h4>"
    # --- CABEÇALHO PARA PARCELAS EM ABERTO ---
            html += """
                 <div style='background-color:#e0e0e0; padding:10px; border-radius:5px 5px 0 0; margin-bottom: 2px; display: flex; justify-content: space-between; font-weight: bold; width: 450px;'>
                 <div style='flex: 1; min-width: 100px;'>Vencimento</div>
                 <div style='flex: 1; min-width: 100px;'>Valor</div>
                 <div style='flex: 1; min-width: 100px;'>Status</div>
                 <div style='flex: 1; min-width: 100px;'>Ação</div>
                 </div>
                  """
        for p in parcelas_em_aberto:
            link = f"/admin/financeiro/parcela/{p.id}/change/"
            html += (
                f"<div style='margin-bottom: 5px; background-color:#f2dede; padding:10px; border-radius:5px; width: 600px; display: flex; justify-content: space-between; width: 450px;'>"
                f"<div style='flex: 1; min-width: 100px;'> {p.data_vencimento}</div>" # Usando div para controlar melhor a coluna
                f"<div style='flex: 1; min-width: 100px;'> R$ {p.valor}</div>"
                f"<div style='flex: 1; min-width: 100px;'> Em aberto</div>"
                f"<div style='flex: 1; min-width: 100px;'><a href='{link}'>Dar Baixa</a></div></div>"
             )

        if parcelas_pagas.exists():
           html += "<h4 style='color: #3c763d;'> Parcelas Pagas</h4>"
    # --- CABEÇALHO PARA PARCELAS PAGAS ---
           html += """
               <div style='background-color:#e0e0e0; padding:10px; border-radius:5px 5px 0 0; margin-bottom: 2px; display: flex; justify-content: space-between; font-weight: bold; width: 450px;'>
               <div style='flex: 1; min-width: 100px;'>Vencimento</div>
               <div style='flex: 1; min-width: 100px;'>Valor</div>
               <div style='flex: 1; min-width: 100px;'>Status</div>
               <div style='flex: 1; min-width: 100px;'>Ação</div>
               </div>
              """
        for p in parcelas_pagas:
            link = f"/admin/financeiro/parcela/{p.id}/change/"
            html += (
                f"<div style='margin-bottom: 5px; background-color:#dff0d8; padding:10px; border-radius:5px; width: 600px; display: flex; justify-content: space-between; width: 450px;'>"
                f"<div style='flex: 1; min-width: 100px;'> {p.data_vencimento}</div>"
                f"<div style='flex: 1; min-width: 100px;'> R$ {p.valor}</div>"
                f"<div style='flex: 1; min-width: 100px;'> Pago</div>"
                f"<div style='flex: 1; min-width: 100px;'><a href='{link}'>Visualizar</a></div></div>"
             )

        if not html:
            html = "Nenhuma parcela cadastrada."
 
        return mark_safe(html)
    parcelas_em_html.short_description = "Financeiro"
    
    
    
@admin.register(Paciente)
class PacienteAdmin(admin.ModelAdmin):
    inlines = [ContratoInline]
    list_display = ['nome', 'cpf', 'data_nascimento', 'telefone', 'cidade', 'uf']
    search_fields = ['nome', 'cpf']
    list_filter = ['nome', 'cpf', 'cidade', 'telefone']
    ordering = ['nome']

    fieldsets = (
        ('Dados do Paciente', {
            'fields': (
                'nome', 'cpf', 'data_nascimento',
                'nome_pai', 'nome_mae',
                'nacionalidade', 'naturalidade',
                'estado_civil', 'sexo', 'profissao',
            )
        }),
        ('Contatos', {
            'fields': (
                'telefone', 'observacao_contato',
            )
        }),
        ('Endereço do Paciente', {
            'fields': (
                'cep', 'endereco', 'numero', 'bairro',
                'cidade', 'uf', 'complemento', 'ponto_referencia',
            )
        }),
        ('Outras Informações', {
            'fields': (
                'outras_observacoes',
            )
        }),
    )

    class Media:
        js = ('admin/js/input_masks.js',)
 