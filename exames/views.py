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

@login_required
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

    return redirect('/exames/gerenciar_pedidos/')

@login_required
def gerenciar_pedidos(request):
    pedidos_exames = PedidosExames.objects.filter(usuario=request.user)

    return render(request, 'gerenciar_pedidos.html', {'pedidos_exames': pedidos_exames})

@login_required
def cancelar_pedidos(request, pedido_id):
    pedido = PedidosExames.objects.get(id=pedido_id)

    if not pedido.usuario == request.user:
        messages.add_message(request, constants.ERROR, 'Esse pedido não é seu, portanto você não pode cancelar.')
        return redirect('/exames/gerenciar_pedidos/')
    pedido.agendado = False
    pedido.save()
    messages.add_message(request, constants.SUCCESS, "Pedidos cancelado com sucesso!")
    return redirect('/exames/gerenciar_pedidos/')

@login_required
def gerenciar_exames(request):
    exames = SolicitacaoExame.objects.filter(usuario=request.user)

    return render(request, 'gerenciar_exames.html', {'exames': exames})

@login_required
def permitir_abrir_exame(request, exame_id):
    exame = SolicitacaoExame.objects.get(id=exame_id)
		#TODO: validar se o exame é do usuário
    if not exame.requer_senha:
        # verificar se o pdf existe
        return redirect(exame.resultado.url)

    else: 
        return redirect(f'/exames/solicitar_senha_exame/{exame.id}')

@login_required
def solicitar_senha_exame(request, exame_id):
    exame = SolicitacaoExame.objects.get(id=exame_id)
    if request.method == "GET":
        return render(request, 'solicitar_senha_exame.html', {'exame': exame})
    elif request.method == "POST":
        senha = request.POST.get("senha")
				#TODO: validar se o exame é do usuário
        if senha == exame.senha:
            return redirect(exame.resultado.url)
        else:
            messages.add_message(request, constants.ERROR, 'Senha inválida')
            return redirect(f'/exames/solicitar_senha_exame/{exame.id}')
