from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from .models import TipoExames, PedidosExames, SolicitacaoExame
from datetime import datetime
from django.contrib import messages
from django.contrib.messages import constants

@login_required
def solicitar_exames(request):
    tipos_exames = TipoExames.objects.all()
    if request.method == "GET":
        return render(request, 'solicitar_exames.html', {'tipos_exames': tipos_exames})
    elif request.method == "POST":
        exames_id = request.POST.getlist('exames')
        solicitacao_exames = TipoExames.objects.filter(id__in=exames_id)

        # TODO: Calcular dos dados disponíveis
        preco_total = 0
        for i in solicitacao_exames:
            if i.disponivel:
                preco_total += i.preco
        
        #TODO: Fazer a data de agendamento
        
        return render(request, 'solicitar_exames.html', {'tipos_exames': tipos_exames, 
                                                         'preco_total': preco_total, 
                                                         'solicitacao_exames': solicitacao_exames})

def fechar_pedido(request):
    exames_id = request.POST.getlist('exames')

    solicitacao_exames = TipoExames.objects.filter(id__in=exames_id)
    pedido_exame = PedidosExames(
        usuario = request.user,
        data = datetime.now()
    )
    pedido_exame.save()

    for exame in solicitacao_exames:
        solicitacao_exames_temp = SolicitacaoExame(
            usuario = request.user,
            exame = exame,
            status="E"
        )
        solicitacao_exames_temp.save()
        pedido_exame.exames.add(solicitacao_exames_temp)
    pedido_exame.save()    
    messages.add_message(request, constants.SUCCESS, 'Pedidos de exames realizado com sucesso!')

    return redirect('/exames/ver_pedidos/')
