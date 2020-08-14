from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from chess.utils import chessboard
from chess.utils import exceptions
from chess.config import BOARDS

def index(request):


    BOARDS.append(chessboard.Chessboard())

    context = {"board" : BOARDS[0].draw_chessboard() }

    return render(request, "index.html", context)

def move(request, move):
    print("requested move " + move)
    positions = move.split(',')
    destination = positions[1]
    initial = positions[0]

    try:
        BOARDS[0].move(initial, destination)
    except exceptions.InvalidMoveError as error:
        print(error)
        return JsonResponse({'success': False})

    data = { 'success': True }
    return JsonResponse(data)

# Returns list of legal moves for the piece at the position
def legalmoves(request, position):
    # TODO Exceptions for no piece at position
    legal_moves = BOARDS[0].generate_legal_moves(position)
    

    return JsonResponse(legal_moves, safe=False)