from django.shortcuts import render
from django.http import HttpResponse
from .models import Hosts


# Create your views here.


def index(request):
    #return HttpResponse('index test')
    return render(request, 'manager/test.html')


def pre(request):
    pres = Hosts.objects.filter(environment='预发布')
    return render(request, 'manager/pre_release2.html', {'pres': pres})
