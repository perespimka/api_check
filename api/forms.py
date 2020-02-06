from django import forms
from .models import UserRequest, NodesData
from django.core.exceptions import ValidationError
import logging
import json

logging.basicConfig( level=logging.DEBUG, format='%(asctime)s %(message)s')
AVAIBLE_NODES = [(node.name, node.hum_read_name) for node in NodesData.objects.all()]
#logging.info(AVAIBLE_NODES)
#AVAIBLE_NODES = [('MSC', 'Moscow'), ('TST1', 'Test1')]

class URForm(forms.ModelForm):
    '''Создание тестирования API зарегистрированным пользователем '''

    my_nodes = forms.MultipleChoiceField(required=False, widget=forms.CheckboxSelectMultiple, 
                                         choices=AVAIBLE_NODES, label='Узлы, с которых будет отправлен запрос'
    )
    
    def clean(self): # Дополняем ошибки полей. Если поле заполнено неправильно, ошибка будет выводится пользователю под полем с ошибкой
        def headers_field_error(fieldname):
            '''Для вывода ошибок полей формы. Проверяет соотвествие формату "ключ:значение\n", добавляет в поле формы ошибку '''
            text = self.cleaned_data[fieldname]
            if len(text) == 0: return
            params = text.split('\n')
            params = [param.split(':') for param in params]
            for keyval in params:
                if len(keyval) != 2:
                    errors[fieldname] = ValidationError('Параметры должны иметь вид "ключ : значение" и разделены новой строкой ')
                elif len(keyval[0]) == 0 or len(keyval[1]) == 0:
                    errors[fieldname] = ValidationError('Значения параметров не должны быть пустыми')
                    
        
        def is_JSON(fieldname):
            if self.cleaned_data[fieldname]:
                logging.info(self.cleaned_data[fieldname])
                logging.info(type(self.cleaned_data[fieldname]))
                try:
                    json.loads(self.cleaned_data[fieldname])
                except:
                    errors[fieldname] = ValidationError('Введенные данные не в формтае JSON')

        super().clean()
        errors = {}
        #Если параметры get запроса не в формате "ключ: значение\n"
        if self.cleaned_data['request_type'] == 'GET':
            headers_field_error('request_text')
        headers_field_error('request_headers')
        if self.cleaned_data['request_type'] == 'POST' and self.cleaned_data['request_mime'] in ['JSON', 'FORM']:
            is_JSON('request_text')
        if self.cleaned_data['response_pattern_type'] == 'JSON':
            is_JSON('response_pattern')
        
        if errors:
            raise ValidationError(errors)


    class Meta():
        model = UserRequest
        fields = ['request_type', 'my_nodes', 'link', 'request_mime', 'request_text', 
                  'request_headers', 'response_pattern_type', 'response_pattern'
        ]
        labels = {'request_type': 'Тип запроса',
                  'link': 'Ссылка на ваш API',
                  'request_mime': 'MIME тип пост запроса',
                  'request_text': 'Параметры запроса',
                  'request_headers': 'Заголовки запроса',
                  'response_pattern_type': 'Тип шаблона для проверки ответа API',
                  'response_pattern': 'Шаблон проверки ответа API'
        }

        #widgets = {'nodes' : forms.CheckboxSelectMultiple()}

