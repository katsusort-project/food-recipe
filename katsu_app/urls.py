from django.urls import path
from katsu_app.views import *

app_name = 'katsu_app'

urlpatterns = [
    path('', show_main, name='show_main'),
    path('result/', get_recipe, name='get_recipe')
]