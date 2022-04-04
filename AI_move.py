import random


piece_score = {"K": 0, "Q": 10, "R": 5, "B": 3, "N": 3, "p": 1}

knight_score = [[1, 1, 1, 1, 1, 1, 1, 1],
                [1, 2, 2, 2, 2, 2, 2, 1],
                [1, 2, 3, 3, 3, 3, 2, 1],
                [1, 2, 3, 4, 4, 3, 2, 1],
                [1, 2, 3, 4, 4, 3, 2, 1],
                [1, 2, 3, 3, 3, 3, 2, 1],
                [1, 2, 2, 2, 2, 2, 2, 1],
                [1, 1, 1, 1, 1, 1, 1, 1]]

bishop_score = [[4, 3, 2, 1, 1, 2, 3, 4],
                [3, 4, 3, 2, 2, 3, 4, 3],
                [2, 3, 4, 3, 3, 4, 3, 2],
                [1, 2, 3, 4, 4, 3, 2, 1],
                [1, 2, 3, 4, 4, 3, 2, 1],
                [2, 3, 4, 3, 3, 4, 3, 2],
                [3, 4, 3, 2, 2, 3, 4, 3],
                [4, 3, 2, 1, 1, 2, 3, 4]]

queen_score =  [[1, 1, 1, 3, 1, 1, 1, 1],
                [1, 2, 3, 3, 3, 1, 1, 1],
                [1, 4, 3, 3, 3, 4, 2, 1],
                [1, 2, 3, 3, 3, 2, 2, 1],
                [1, 2, 3, 3, 3, 2, 2, 1],
                [1, 4, 3, 3, 3, 4, 2, 1],
                [1, 1, 2, 3, 3, 1, 1, 1],
                [1, 1, 1, 3, 1, 1, 1, 1]]

rock_score =   [[4, 3, 4, 4, 4, 4, 3, 4],
                [4, 4, 4, 4, 4, 4, 4, 4],
                [1, 1, 2, 3, 3, 2, 1, 1],
                [1, 2, 3, 4, 4, 3, 2, 1],
                [1, 2, 3, 4, 4, 3, 2, 1],
                [1, 1, 2, 2, 2, 2, 1, 1],
                [4, 4, 4, 4, 4, 4, 4, 4],
                [4, 3, 4, 4, 4, 4, 3, 4]]

white_pawn_score =   [[8, 8, 8, 8, 8, 8, 8, 8],
                      [8, 8, 8, 8, 8, 8, 8, 8],
                      [5, 6, 6, 7, 7, 6, 6, 5],
                      [2, 3, 3, 5, 5, 3, 3, 2],
                      [1, 2, 3, 4, 4, 3, 2, 1],
                      [1, 1, 2, 3, 3, 2, 1, 1],
                      [1, 1, 1, 0, 0, 1, 1, 1],
                      [0, 0, 0, 0, 0, 0, 0, 0]]

black_pawn_score =   [[0, 0, 0, 0, 0, 0, 0, 0],
                      [1, 1, 1, 0, 0, 1, 1, 1],
                      [1, 1, 2, 3, 3, 2, 1, 1],
                      [1, 2, 3, 4, 4, 3, 2, 1],
                      [2, 3, 3, 5, 5, 3, 3, 2],
                      [5, 6, 6, 7, 7, 6, 6, 5],
                      [8, 8, 8, 8, 8, 8, 8, 8],
                      [8, 8, 8, 8, 8, 8, 8, 8]]

piece_position_scores = {"N": knight_score,
                         "Q": queen_score,
                         "B": bishop_score,
                         "R": rock_score,
                         "bp": black_pawn_score,
                         "wp": white_pawn_score}
check_mate = 1000
stale_mate = 0
DEPTH = 4  # depth++ => AI level++

# random moves
def find_random_move(validMoves):
    return validMoves[random.randint(0, len(validMoves)-1)]

# MinMax algorithm with loops
def find_move_min_max_loop(gs, validMoves):
    turn_multiplier = 1 if gs.whiteToMove else -1
    opponent_min_max_score = check_mate
    best_player_move = None
    random.shuffle(validMoves)
    for player_move in validMoves:
        gs.makeMove(player_move)
        opponents_moves = gs.getValidMoves()
        if gs.stalemate:
            opponent_max_score = stale_mate
        elif gs.checkmate:
            opponent_max_score = -check_mate
        else:
            opponent_max_score = -check_mate
            for opponents_move in opponents_moves:
                gs.makeMove(opponents_move)
                gs.getValidMoves()
                if gs.checkmate:
                    score = check_mate
                elif gs.stalemate:
                    score = stale_mate
                else:
                    score = -turn_multiplier * score_material(gs.board)
                if score > opponent_max_score:
                    opponent_max_score = score
                gs.undoMove()

        if opponent_max_score < opponent_min_max_score:
            opponent_min_max_score = opponent_max_score
            best_player_move = player_move
        gs.undoMove()
    return best_player_move

def find_best_move(gs, validMoves, return_queue):
    global nextMove, counter
    nextMove = None
    random.shuffle(validMoves)
    # find_move_min_max(gs, validMoves, DEPTH, gs.whiteToMove)
    # find_move_nega_max(gs, validMoves, DEPTH, 1 if gs.whiteToMove else -1)
    find_move_nega_max_alpha_beta(gs, validMoves, DEPTH, -check_mate, check_mate, 1 if gs.whiteToMove else -1)
    return_queue.put(nextMove) 


# MinMax algorithm recursively
def find_move_min_max(gs, validMoves, depth, whiteToMove):
    global nextMove
    if depth == 0:
        return score_material(gs.board)

    if whiteToMove:
        max_score = -check_mate
        for move in validMoves:
            gs.makeMove(move)
            nextMoves = gs.getValidMoves()
            score = find_move_min_max(gs, nextMoves, depth - 1, False)
            if score > max_score:
                max_score = score
                if depth == DEPTH:
                    nextMove = move
            gs.undoMove()
        return max_score

    else:
        min_score = check_mate
        for move in validMoves:
            gs.makeMove(move)
            nextMoves = gs.getValidMoves()
            score = find_move_min_max(gs, nextMoves, depth - 1, True)
            if score < min_score:
                min_score = score
                if depth == DEPTH:
                    nextMove = move
            gs.undoMove()
        return min_score


def find_move_nega_max(gs, validMoves, depth, turn_multiplier):
    global nextMove
    if depth == 0:
        return turn_multiplier * score_board(gs)

    max_score = -check_mate
    for move in validMoves:
        gs.makeMove(move)
        nextMoves = gs.getValidMoves()
        score = -find_move_nega_max(gs, nextMoves, depth - 1, -turn_multiplier)
        if score > max_score:
            max_score = score
            if depth == DEPTH:
                nextMove = move
        gs.undoMove()
    return max_score

def find_move_nega_max_alpha_beta(gs, validMoves, depth, alpha, beta, turn_multiplier):
    global nextMove
    if depth == 0:
        return turn_multiplier * score_board(gs)


    max_score = -check_mate
    for move in validMoves:
        gs.makeMove(move)
        nextMoves = gs.getValidMoves()
        score = -find_move_nega_max_alpha_beta(gs, nextMoves, depth - 1, -beta, -alpha, -turn_multiplier)
        if score > max_score:
            max_score = score
            if depth == DEPTH:
                nextMove = move
                # print(move,score)
        gs.undoMove()
        if max_score > alpha:
            alpha = max_score
        if alpha >= beta:
            break
    return max_score



def score_board(gs):
    if gs.checkmate:
        if gs.whiteToMove:
            return -check_mate
        else:
            return check_mate
    elif gs.stalemate:
        return stale_mate

    score = 0
    for row in range(len(gs.board)):
        for col in range(len(gs.board[row])):
            square = gs.board[row][col]
            if square != "--":
                piece_position_score = 0
                if square[1] != "K":
                    if square[1] == "p":
                        piece_position_score = piece_position_scores[square][row][col]
                    else:
                        piece_position_score = piece_position_scores[square[1]][row][col]



                if square[0] == "w":
                    score += piece_score[square[1]] + piece_position_score * 0.1
                elif square[0] == "b":
                    score -= piece_score[square[1]] + piece_position_score * 0.1

    return score



def score_material(board):
    score = 0
    for row in board:
        for square in row:
            if square[0] == "w":
                score += piece_score[square[1]]
            elif square[0] == "b":
                score -= piece_score[square[1]]

    return score
