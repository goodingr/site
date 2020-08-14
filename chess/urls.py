from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name = 'index'),
    path('board/move/<move>', views.move, name='move'),
    path('board/legalmoves/<position>', views.legalmoves, name='legalmoves')
]