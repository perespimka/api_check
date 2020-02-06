from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('new_request/', views.new_request, name='new_request'),
    path('my_requests/', views.my_requests, name='my_requests'),
    path('edit_request/<int:rec_id>/', views.edit_request, name='edit_request'),
    path('api/', views.api, name='api')
]