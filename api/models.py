from django.db import models
from django.contrib.auth.models import User
MIME_TYPES = [('TEXT', 'text'), 
              ('JSON', 'application/json'),
              ('FORM', 'application/x-www-form-urlencoded')
]
                                                            
# Create your models here.
class NodesData(models.Model):
    name = models.CharField(max_length=4)
    hum_read_name = models.CharField(max_length=20)
    key = models.CharField(max_length=20)

class UserRequest(models.Model):
    owner = models.ForeignKey(User, models.CASCADE) # пользователь, владелец запроса
    request_type = models.CharField(max_length=20, choices=(('GET', 'GET'), ('POST', 'POST')), default='POST') # тип запроса пользователя
    nodes = models.ManyToManyField(NodesData) # Узлы
    link = models.URLField() # ссылка на апи клиента
    request_mime = models.CharField(max_length=30, choices=MIME_TYPES, default='JSON') # mime-тип post  запроса
    request_text = models.TextField(blank=True) # текст запроса
    request_headers = models.TextField(blank=True) # заголовки запроса, строка для json
    response_pattern_type = models.CharField(max_length=20, choices=(('TEXT', 'Text'), ('JSON', 'JSON')), default='JSON') # Тип шаблона для проверки ответа апи. 
                                            # Либо текст, скорее всего регулярное выражени для проверки, либо json для десериализации в json
    response_pattern = models.TextField(blank=True) # сам шаблон ответа
    date_added = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)


