# все представления ниже берем тут
from django.urls import path, re_path

from .views import *

urlpatterns = [
    path('', index, name='index'),

    path('users/', users, name='users'),

    # other path
    path('hello2/', hello2, name='hello2'),

    # с указанием до параметра
    # напечатает hello количество раз num
    path('hello2/<int:num>/', hello2, name='hello2__num'),

    # hello10 - 10 будет параметром
    # напечатает hello количество раз num
    path('hello<int:num>/', hello2, name='hello2_num'),

    path('hello4/', hello4, name='hello4'),
    path('hello5/', hello5, name='hello5'),

    # /user/vasya-11/
    # любое имя и любое число через дефис
    path('user/<str:name>-<int:num>/', user_num, name='user_num'),

    # передать параметры вручную
    path('user_info/', user_info, kwargs={"name": "Tom", "age": 38}),

    # регулярные выражения - 4 цифры подряд - /data/2004/
    # re_path(r'^data/(?P<year>[0-9]{4})/$', data_year, name='data_year'),
    re_path(r'^data/(?P<year>\d{4})/$', data_year, name='data_year'),

    # несколько вариантов в один path
    # /path1/ или /path2/ или /path3/
    re_path(r'^(path1|path2|path3)/$', multi_path, name='multi_path'),

]