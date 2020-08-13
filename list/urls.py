from django.urls import path

    
from . import views

app_name = 'list'
urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('<int:pk>/', views.taskView, name='detail'),
    path('new/', views.NewTaskView.as_view(), name = 'new'),
    path('tasks/', views.TaskList, name='tasks'),
]

