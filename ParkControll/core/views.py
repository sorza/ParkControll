from django.shortcuts import render, redirect
from django.contrib import messages
from datetime import datetime
from .models import VeiculoModel, OperacionalModel
from .forms import VeiculoModelForm
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

def index(request):
    if request.method == 'POST':
        usuario = request.POST['usuario']
        senha = request.POST['senha']   
       
        user = authenticate(username=usuario, password=senha)   

        if user:                     
            login(request, user)
            return redirect('operacional')  
        else:           
            return render(request, 'login.html')
    else:           
        return render(request, 'login.html')

@login_required(login_url='/')
def consulta(request):
    veiculos = []
    veiculos = VeiculoModel.objects.all()
    context = {'listaVeiculos': veiculos}

    if request.method == 'POST':       
        pesquisa = request.POST.get('pesquisa')

        if request.POST.get('busca') == 'placa':
            context['listaVeiculos'] = VeiculoModel.objects.filter(placa__icontains=pesquisa)            
            return render(request, 'consulta.html', context)
        else:
            context['listaVeiculos'] = VeiculoModel.objects.filter(proprietario__icontains=pesquisa)            
            return render(request, 'consulta.html', context)
    else:        
        return render(request, 'consulta.html', context)
    
@login_required(login_url='/')
def cadastro(request):
    if request.method == 'POST':
        form = VeiculoModelForm(request.POST)       
        if VeiculoModel.objects.filter(placa=form.data['placa']).exists():
            messages.error(request,'Este veículo já foi cadastrado!') 
        elif len(form.data['placa']) != 7:
             messages.error(request,'A placa informada é inválida!') 
        else:
            veiculo = VeiculoModel()
            veiculo.placa = form.data['placa']
            veiculo.tipo = form.data['tipo']
            veiculo.marca = form.data['marca']
            veiculo.modelo = form.data['modelo']
            veiculo.cor = form.data['cor']
            veiculo.proprietario = form.data['proprietario']
            veiculo.cpf_proprietario = form.data['cpf']
            veiculo.telefone = form.data['telefone']
            veiculo.save()
                      
    return render(request, 'cadastro.html')

@login_required(login_url='/')
def edicao(request, id):    
    veiculo = VeiculoModel.objects.get(placa=id)
    return render(request, 'edicao.html', {'form': veiculo})

@login_required(login_url='/')
def atualizacao(request):
    form = VeiculoModelForm(request.POST)  
    veiculo = VeiculoModel.objects.get(id=form.data['id'])

    veiculo.placa = form.data['placa']
    veiculo.tipo = form.data['tipo']
    veiculo.marca = form.data['marca']
    veiculo.modelo = form.data['modelo']
    veiculo.cor = form.data['cor']
    veiculo.proprietario = form.data['proprietario']
    veiculo.cpf_proprietario = form.data['cpf']
    veiculo.telefone = form.data['telefone']

    veiculo.save()    
    return redirect('consulta')

@login_required(login_url='/')
def edicao(request, id):    
    veiculo = VeiculoModel.objects.get(placa=id)
    return render(request, 'edicao.html', {'form': veiculo})

@login_required(login_url='/')
def historico(request, id):    

    veiculos = []
    context = {'historico': veiculos}

    veiculos = OperacionalModel.objects.all()

    for veiculo in veiculos:       
        if veiculo.placa == id:
            context['historico'].append(veiculo)

    return render(request, 'historico.html', context)

@login_required(login_url='/')
def exclusao(request, id):
    veiculo = VeiculoModel.objects.get(placa=id)
    if veiculo != None:
        veiculo.delete()
    
    return consulta(request)

@login_required(login_url='/')
def operacional(request):

    veiculos = []
    veiculos = VeiculoModel.objects.all().order_by('status')
    context = {'listaVeiculos': veiculos}

    if request.method == 'POST':       
        pesquisa = request.POST.get('placa')
        context['listaVeiculos'] = VeiculoModel.objects.filter(placa__icontains=pesquisa)      
    return render(request, 'operacional.html', context)

@login_required(login_url='/')
def entrada(request, id):       
     veiculo = VeiculoModel.objects.get(placa=id)
     veiculo.status = 'Estacionado'
     veiculo.save()

     operacional = OperacionalModel()
     operacional.placa = id
     operacional.entrada = datetime.now()
     operacional.saida = '3000-12-31 00:00:00'
     operacional.save()

     return redirect('operacional')

@login_required(login_url='/')
def saida(request, id):    
    veiculo = VeiculoModel.objects.get(placa=id)
    veiculo.status = 'Não Estacionado'
    veiculo.save()

    operacional = OperacionalModel.objects.get(placa=veiculo.placa, saida='3000-12-31 00:00:00')
    operacional.saida = datetime.now()
    operacional.save()

    return redirect('operacional')

@login_required(login_url='/')
def sair(request):
    logout(request)
    return render(request, 'login.html')

