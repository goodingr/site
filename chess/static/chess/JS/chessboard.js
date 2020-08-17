$(document).ready(function() {
    console.log("ready")


    // Add the highlighted class and set square_selected to the position
    // If a square is already selected, deselects it first
    var select_square = function(target) {
        if (select_square) {
            deselect_square()
        }
        square_selected = target.attr('id')
        initial_target = target
        target.addClass('highlighted')
    }
    // Removes the highlight class and sets selected_square to null 
    var deselect_square = function() {
        target = $("#"+square_selected)
        target.removeClass('highlighted')
        square_selected = null
        legal_moves = []
        $(".hint").remove()
    }

    
    var square_selected, square_destination;
    var legal_moves = []
    var initial_target, destination_target

    var get_legal_moves = function() {
        if (!square_selected){
            console.log("ERROR: get_legal_moves NO SQUARE SELECTED")
            return
        }
         // Request legal moves for selected piece and mark them
            url = "board/legalmoves/" + square_selected
            $.ajax({
                url: url,
                success: function(data) {
                    // Read data into legal_moves
                    // should probably call select_square here
                    console.log("legal moves: " + data)
                    legal_moves = data
                    for (i = 0; i < legal_moves.length; i++){
                        hint = "<div class='hint square-" + legal_moves[i] + "' ></div>"
                        $(".board").append(hint)
                    }
                }
            })
    }

    // When a piece is clicked, determine whether to select the square or
    // attemp to move the piece on the selected square to the clicked square (destination)
    $(document).on('click', '.piece', (event) => {
        const target = $(event.target);

        // A square has not been selected yet and the piece clicked is not blank
        if(!square_selected && !target.hasClass('none_')){
            // Set square_selected to the clicked piece and TODO highlight it and it's legal moves
            select_square(target);
            get_legal_moves()

        }
        // A square has already been selected.
        else if(square_selected) {
            destination_target = target
            square_destination = target.attr('id')
            console.log("checking if legal move")
            console.log(legal_moves)
            console.log(square_selected)
            // If the clicked square is a legal move for the selected square, send a move request 
            if (legal_moves.includes(square_destination)){
                console.log("MOVE " + square_selected + " to " + square_destination)
                url = "board/move/" + square_selected + "," + square_destination;
                $.ajax({
                    url: url,
                    success: function(data) {
                        console.log("move response: ")
                        console.log(data)
                        console.log(data.changes[0])
          
                        // // TODO If success, update board display
                        // classes_dest = destination_target.attr("class").split(" ")
                        // classes_init = initial_target.attr("class").split(" ")
                        // classes_dest[1] = classes_init[1]
                        // classes_init[1] = "none_"
                        // destination_target.attr("class", classes_dest.join(" "))
                        // initial_target.attr("class", classes_init.join(" "))

                        deselect_square()
                        square_destination = null;

                        for (i = 0; i < data.changes.length; i++) {
                            let id =  '#' + data.changes[i].position
                            $(id).attr('class', data.changes[i].class)
                        }
                        
                    }
                })
            } 
           // If clicked square is already selected or blank illegal move, deselect square
            else if (square_selected == square_destination){
                deselect_square()
            }
            else if (target.hasClass('none_')) {
                deselect_square()
            }
            // clicked square becomes newly selected piece
            else {
                select_square(target)
                get_legal_moves()
            }
        }
    })


})
