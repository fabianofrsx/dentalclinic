from django.db import models

class Paciente(models.Model):
    # Dados do Paciente
    nome = models.CharField(max_length=100)
    cpf = models.CharField(max_length=14, unique=True)
    data_nascimento = models.DateField()
    nome_pai = models.CharField(max_length=150, blank=True, null=True)
    nome_mae = models.CharField(max_length=150, blank=True, null=True)
    nacionalidade = models.CharField(max_length=100, blank=True, null=True)
    naturalidade = models.CharField(max_length=100, blank=True, null=True)
    estado_civil = models.CharField(
        max_length=20,
        choices=[
            ('solteiro', 'Solteiro(a)'),
            ('casado', 'Casado(a)'),
            ('divorciado', 'Divorciado(a)'),
            ('viuvo', 'Viúvo(a)'),
            ('outro', 'Outro'),
        ],
        blank=True,
        null=True
    )
    sexo = models.CharField(
        max_length=10,
        choices=[
            ('masculino', 'Masculino'),
            ('feminino', 'Feminino'),
            ('outro', 'Outro'),
        ],
        blank=True,
        null=True
    )
    profissao = models.CharField(max_length=100, blank=True, null=True)

    # Contatos
    telefone = models.CharField(max_length=20, blank=True, null=True)
    observacao_contato = models.TextField(blank=True, null=True)

    # Endereço
    cep = models.CharField(max_length=9, blank=True, null=True)
    endereco = models.CharField(max_length=150, blank=True, null=True)
    numero = models.CharField(max_length=10, blank=True, null=True)
    bairro = models.CharField(max_length=100, blank=True, null=True)
    cidade = models.CharField(max_length=100, blank=True, null=True)
    uf = models.CharField(max_length=2, blank=True, null=True)
    complemento = models.CharField(max_length=100, blank=True, null=True)
    ponto_referencia = models.CharField(max_length=150, blank=True, null=True)

    # Outras informações
    outras_observacoes = models.TextField(blank=True, null=True)

    data_cadastro = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.nome
    
    

