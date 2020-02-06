from django.shortcuts import render
from django.contrib.auth import logout, login, authenticate
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.contrib.auth.forms import UserCreationForm
import logging

logging.basicConfig(level=logging.DEBUG)

# Create your views here.
def logoutView(request):
    logout(request)
    return HttpResponseRedirect(reverse('index'))

def register(request):
    if request.method != 'POST':
        form = UserCreationForm()
    else:
        form = UserCreationForm(request.POST)
        if form.is_valid():
            new_user = form.save()
            logging.info('-----------------------')
            logging.info('{}: {}'.format(new_user.username, request.POST['password1']))
            user = authenticate(username=new_user.username, password=request.POST['password1'])
            login(request, user)
            return HttpResponseRedirect(reverse('index'))
    context = {'form' : form}
    return render(request, 'registration/register.html', context)    

