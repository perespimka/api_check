from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.urls import reverse
from .forms import URForm
import json
import requests
import logging
from django.views.decorators.csrf import csrf_exempt
from .models import UserRequest, NodesData
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from .serializers import UserRequestSerializer

logging.basicConfig( level=logging.DEBUG, format='%(asctime)s %(message)s')

# Functions

def params_splitter(text, is_json=True):
    '''Создает словарь параметров. text - ввод параметров ключ:значение разделяются ":", параметры разделяются новой строкой  '''
    params = text.split('\n')
    params = [param.split(':') for param in params]
    res_params = []
    for keyval in params:
        if len(keyval) != 2: # здесь мы просто пропустим параметр в том случае, если это не пара ключ:значение. Нигде не обозначается ошибка :(
            continue
        for i in range(2):
            keyval[i] = keyval[i].strip()
        res_params.append(keyval)
    if is_json:
        return json.dumps(dict(res_params))
    return dict(res_params)

def trueuser(request, user):
    '''Проверим, является ли юзер на странице владельцем записей '''
    if request.user != user:
        raise Http404

def params_from_json(text):
    '''Переписываем text из json в формат key: value\n '''
    if text:
        result = ''
        params = json.loads(text)
        for key, value in params.items():
            result+='{}: {}\n'.format(key, value)
        return result

def form_filling(request, form):
    '''Обрабатываем запрос, сохраняем запись в модели '''
    resform = form.save(commit=False)
    list_of_nodes = [NodesData.objects.get(name=node_name) for node_name in form.cleaned_data['my_nodes']]
    resform.nodes.set(list_of_nodes)    
    resform.owner = request.user
    resform.request_headers = params_splitter(resform.request_headers)
    if resform.request_type == 'GET': # В случае get запроса рассматриваем параметры как ключ/значение
        resform.request_text = params_splitter(resform.request_text)
    resform.save()

def from_nodes_field_to_list(nodes_field):
    '''Возвращает список названий (.name) узлов для вывода для редактирования формы '''
    return [node.name for node in nodes_field.all()]

def node_auth(req_content):
    '''Проверка, есть ли айди в запросе, и есть ли базе данных узел с таким айди, возвращает объект узла, если есть '''
    if 'id' in req_content:
        try:
            node = NodesData.objects.get(key=req_content['id'])
        except:
            logging.info('node is not in nodes db')
            return None
        return node
# Create your views here.




def index(request):
   
    if request.method != 'POST':

        resp_data = ()
    else:
        req_type = request.POST['type']
        req_link = request.POST['link']
        req_post_type = request.POST['post_type']
        req_data = request.POST['request']
        if req_data:
            try:
                #Проверим, собирается ли json, также на всякий случай сменим одинарные кавычки, которые не котируются, на двойные
                req_data = req_data.replace("'", '"')
                req_data = json.loads(req_data)
            except:
                req_data ={}
        if req_type == 'get':
            response_ = requests.get(req_link, params=req_data)
        elif req_type == 'post':
            if req_post_type == 'text':
                if not req_data: req_data = ''
                response_ = requests.post(req_link, req_data)
            elif req_post_type == 'application/json':
                response_ = requests.post(req_link, json=req_data)
            elif req_post_type == 'multipart/form-data':
                response_ = requests.post(req_link, data=req_data)

        resp_data = (response_.status_code, response_.text)
        
    context = {'resp_data' : resp_data}
    return render(request, 'api/index.html', context)



@login_required
def new_request(request):
    if request.method != 'POST':
        form = URForm()
    else:
        form = URForm(data=request.POST)
        if form.is_valid():
            form_filling(request, form)
            return HttpResponseRedirect(reverse('my_requests'))
    context = {'form' : form}
    return render(request, 'api/new_request.html', context)

@login_required
def my_requests(request):
    user_recs = UserRequest.objects.filter(owner=request.user).order_by('-date_added')
    context = {'user_recs': user_recs}
    return render(request, 'api/my_requests.html', context)


@login_required
def edit_request(request, rec_id):
    user_request = UserRequest.objects.get(id=rec_id)
    trueuser(request, user_request.owner)
    if request.method != 'POST':
        my_nodes = from_nodes_field_to_list(user_request.nodes) #в список из поля модели, содержащего объекты узлов NodesData
        headers = params_from_json(user_request.request_headers) # переписываем заголовки из json в формат key: value\n
        initial = {'my_nodes': my_nodes, 'request_headers': headers}
        if user_request.request_type == 'GET':
            params = params_from_json(user_request.request_text)
            initial['request_text'] = params
        form = URForm(instance=user_request, initial=initial)
        
    else:
        form = URForm(data=request.POST, instance=user_request)
        if form.is_valid():
            form_filling(request, form)
            return HttpResponseRedirect(reverse('my_requests'))
    context = {'form': form, 'user_request': user_request }
    return render(request, 'api/edit_request.html', context)




@csrf_exempt
def api(request):
    try:
        req_content = json.loads(request.body)
    except:
        logging.warning('Not json')
        return HttpResponse('Not json')

    node = node_auth(req_content)
    if not node: 
        return HttpResponse('Wrong key')
    if req_content['state'] == 'data_request': # если узел запрашивает данные для рассылки
        requests_for_node = node.userrequest_set.filter(is_active=True) # queryset с объектами запросов, принадлежащими к узлу node и активным статусом
        serializer = UserRequestSerializer(requests_for_node, many=True)
        return JsonResponse(serializer.data, safe=False)
        #logging.debug(requests_for_node)

    return HttpResponse(json.dumps(req_content, indent=4))