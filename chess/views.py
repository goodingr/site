from django.shortcuts import render
from django.http import HttpResponse
from chess.utils import chessboard

def index(request):

    new_chessboard = chessboard.Chessboard()

    context = {"board" : new_chessboard.draw_chessboard() }

    return render(request, "index.html", context)