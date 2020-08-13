from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from .models import Task
from django.template import loader
from django.views import generic
from django import forms
from django.views.generic.edit import FormView
from static_precompiler.utils import compile_static
from django.core import serializers
import json


class IndexView(generic.ListView):
    template_name = 'list/index.html'
    context_object_name = 'task_list'

    def get_queryset(self):
        return Task.objects.order_by('-date')

# /list/tasks Returns JSON List of Tasks
def TaskList(request):
    tasks = Task.objects.all();
    print(tasks)
    tasks_list = serializers.serialize('json', tasks)
    return HttpResponse(tasks_list , content_type="text/json-comment-filtered")

class TaskEditForm(forms.Form):
    task_text = forms.CharField(max_length=200)

# Converts "true" to True and "false" to False
def completed_check(completed):
    print("complete check: " + completed)
    return completed == "true"

# Get/Post data for a specific task
def taskView(request, pk):
    task = get_object_or_404(Task, pk=pk)

    print("task view function") 
    if(request.method == 'GET'):
        data = {
            'task_text'     : task.task_text,
            'completed'     : task.completed,
            'date_created'  : task.date_created,
            'date_completed': task.date_completed,
            'id'            : task.id
        }
        print("returning data " + str(data))
        return JsonResponse(data)

    if(request.method == "POST"):
        data = {}    
        print(" updating ")
        print(pk)
        task = get_object_or_404(Task, pk=pk)
        task.task_text = request.POST['task_text']
        task.completed = completed_check(request.POST['completed'])
        task.save()

        serial = serializers.serialize('json', [task, ])
        return HttpResponse(serial, content_type="text/json-comment-filtered")


class NewTaskForm(forms.Form):
    task_text = forms.CharField(max_length=200)

class NewTaskView(FormView):
    template_name = 'list/new.html'
    form_class = NewTaskForm
    success_url = '/list/'

    def form_valid(self, form):
        t = Task(task_text=form.data['task_text'])
        t.save()
        return super().form_valid(form)


# # New Task View
# def new(request):
#     if request.method == 'GET':
#         return render(request, 'list/new.html')
#     if request.method == 'POST':
#         try:
#             task_text = request.POST['task_text']
#         except (KeyError):
#             return render(request, 'list/new.html', {'error_message': "You did not provide a name for the task."})
#         else:
#             t = Task(task_text = task_text)
#             t.save()

#             # Redirect to task detail view
#             # return redirect('/list/%s' %(t.id) )

#             # Redirect to list index
#             return redirect('/list/' )

#     return render(request, 'list/new.html')
