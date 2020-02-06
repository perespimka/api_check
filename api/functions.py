import json
from django.http import Http404


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
    #print(res_params)
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
    for node_name in form.cleaned_data['my_nodes']:
        

    #resform.nodes = json.dumps(form.cleaned_data['my_nodes']) # Сериализуем список с узлами для строкового поля в БД
    resform.owner = request.user
    resform.request_headers = params_splitter(resform.request_headers)
    if resform.request_type == 'GET': # В случае get запроса рассматриваем параметры как ключ/значение
        resform.request_text = params_splitter(resform.request_text)
    resform.save()



'''
with open('params.txt') as f:
    print(paramsSplitter(f.read()))
'''