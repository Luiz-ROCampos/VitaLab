from django.contrib import admin
from .models import TipoExames, SolicitacaoExame, PedidosExames, AcessoMedico

admin.site.register(TipoExames)
admin.site.register(SolicitacaoExame)
admin.site.register(PedidosExames)
admin.site.register(AcessoMedico)