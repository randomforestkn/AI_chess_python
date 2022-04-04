import pygame as p
import ChessEngine, AI_move
from multiprocessing import Process, Queue


board_width = board_height = 400
move_log_panel_width = 250
move_log_panel_height = board_height
dimension = 8
sq_size = board_height // dimension
max_fps = 15
images = {}


def load_images():
    pieces = ['wp', "wR", "wN", "wB", "wQ", "wK", "bp", "bR", "bN", "bB", "bQ",
              "bK"]
    for piece in pieces:
        images[piece] = p.transform.scale(p.image.load(
            "images/" + piece + ".png"), (sq_size, sq_size))


def main():
    p.init()
    p.display.set_caption('Σκάκι')
    icon = p.image.load('images/bK.png')
    p.display.set_icon(icon)
    screen = p.display.set_mode((board_width + move_log_panel_width, board_height))
    clock = p.time.Clock()
    screen.fill(p.Color("white"))
    moveLogFont = p.font.SysFont("Arial", 12, False, False)
    gs = ChessEngine.GameState()
    validMoves = gs.getValidMoves()
    moveMade = False
    animate = False
    load_images()
    running = True
    sqSelected = ()
    playerClicks = []
    gameOver = False
    playerOne = True  # if false then AI vs AI game
    playerTwo = False
    ai_thinking = False
    move_finder_process = None
    move_undone = False

    while running:
        humanTurn = (gs.whiteToMove and playerOne) or (not gs.whiteToMove and playerTwo)
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False

            elif e.type == p.MOUSEBUTTONDOWN:
                if not gameOver:
                    location = p.mouse.get_pos()
                    col = location[0]//sq_size
                    row = location[1]//sq_size
                    if sqSelected == (row, col) or col >= 8:
                        sqSelected = ()
                        playerClicks = []
                    else:
                        sqSelected = (row, col)
                        playerClicks.append(sqSelected)
                    if len(playerClicks) == 2 and humanTurn:
                        move = ChessEngine.Move(playerClicks[0],
                                                playerClicks[1], gs.board)
                        # print(move.getChessNotation())
                        for i in range(len(validMoves)):
                            if move == validMoves[i]:
                                gs.makeMove(validMoves[i])
                                moveMade = True
                                animate = True
                                sqSelected = ()
                                playerClicks = []
                        if not moveMade:
                            playerClicks = [sqSelected]

            elif e.type == p.KEYDOWN:
                if e.key == p.K_z:
                    gs.undoMove()
                    sqSelected = ()
                    playerClicks = []
                    moveMade = True
                    animate = False
                    gameOver = False
                    if ai_thinking:
                        move_finder_process.terminate()
                        ai_thinking = False
                    move_undone = True


                if e.key == p.K_r:
                    gs = ChessEngine.GameState()
                    validMoves = gs.getValidMoves()
                    sqSelected = ()
                    playerClicks = []
                    moveMade = False
                    animate = False
                    gameOver = False
                    if ai_thinking:
                        move_finder_process.terminate()
                        ai_thinking = False
                    move_undone = True

        # AI move
        if not gameOver and not humanTurn and not move_undone:
            if not ai_thinking:
                ai_thinking = True
                print("Ai thinking")
                return_queue = Queue()
                move_finder_process = Process(target=AI_move.find_best_move, args=(gs, validMoves, return_queue))
                move_finder_process.start()

            if not move_finder_process.is_alive():
                print("finish thinking")
                AIMove = return_queue.get()
                if AIMove is None:
                    AIMove = AI_move.find_random_move(validMoves)
                gs.makeMove(AIMove)
                moveMade = True
                animate = True
                ai_thinking = False

        if moveMade:
            if animate:
                animateMove(gs.moveLog[-1], screen, gs.board, clock)
            validMoves = gs.getValidMoves()
            moveMade = False
            animate = False
            move_undone = False

        draw_game_state(screen, gs, validMoves, sqSelected, moveLogFont)

        if gs.checkmate or gs.stalemate:
            gameOver = True
            drawEndGameText(screen, 'Πατ!' if gs.stalemate else 'Ματ, τα μαύρα νίκησαν!' if gs.whiteToMove else 'Ματ, τα λευκά νίκησαν!')

        clock.tick(max_fps)
        p.display.flip()


def draw_game_state(screen, gs, validMoves, sqSelected, moveLogFont):
    draw_board(screen)
    highlightSquares(screen, gs, validMoves, sqSelected)
    draw_pieces(screen, gs.board)
    draw_move_log(screen, gs, moveLogFont)

def draw_board(screen):
    global colors
    colors = [p.Color(238, 238, 210), p.Color(125, 135, 150)]
    for r in range(dimension):
        for c in range(dimension):
            color = colors[((r+c) % 2)]
            p.draw.rect(screen, color, p.Rect(c*sq_size, r*sq_size,
                                              sq_size, sq_size))

def highlightSquares(screen, gs, validMoves, sqSelected):
    if sqSelected != ():
        r, c = sqSelected
        if gs.board[r][c][0] == ('w' if gs.whiteToMove else 'b'):
            s = p.Surface((sq_size, sq_size))
            s.set_alpha(100)
            s.fill(p.Color('blue'))
            screen.blit(s, (c*sq_size, r*sq_size))
            s.fill(p.Color('yellow'))
            for move in validMoves:
                if move.startRow == r and move.startCol == c:
                    screen.blit(s, (sq_size*move.endCol, sq_size*move.endRow))

def draw_pieces(screen, board):
    for r in range(dimension):
        for c in range(dimension):
            piece = board[r][c]
            if piece != "--":
                screen.blit(images[piece], p.Rect(c*sq_size, r*sq_size,
                                                  sq_size, sq_size))

def draw_move_log(screen, gs, font):
    moveLogRect = p.Rect(board_width, 0, move_log_panel_width, move_log_panel_height)
    p.draw.rect(screen, p.Color("black"), moveLogRect)
    moveLog = gs.moveLog
    moveTexts = []
    for i in range(0, len(moveLog), 2):
        moveString = str(i//2 + 1) + ". " + str(moveLog[i]) + " "
        if i + 1 < len(moveLog):
            moveString += str(moveLog[i+1]) + " "
        moveTexts.append(moveString)

    moves_per_row = 3
    padding = 5
    textY = padding
    line_space = 2
    for i in range(0, len(moveTexts), moves_per_row):
        text = ""
        for j in range(moves_per_row):
            if i + j < len(moveTexts):
                text += moveTexts[i+j]
        textObject = font.render(text, True, p.Color('green'))
        textLocation = moveLogRect.move(padding, textY)
        screen.blit(textObject, textLocation)
        textY += textObject.get_height() + line_space


def animateMove(move, screen, board, clock):
    global colors
    dR = move.endRow - move.startRow
    dC = move.endCol - move.startCol
    framesPerSquare = 10
    frameCount = (abs(dR) + abs(dC)) * framesPerSquare
    for frame in range(frameCount+1):
        r, c = (move.startRow + dR*frame/frameCount, move.startCol + dC*frame/frameCount)
        draw_board(screen)
        draw_pieces(screen, board)
        color = colors[(move.endRow + move.endCol) % 2]
        endSquare = p.Rect(move.endCol*sq_size, move.endRow*sq_size, sq_size, sq_size)
        p.draw.rect(screen, color, endSquare)
        if move.pieceCaptured != '--':
            if move.isEnpassantMove:
                isEnpassantMoveRow = move.endRow + 1 if move.pieceCaptured[0] == 'b' else move.endRow - 1
                endSquare = p.Rect(move.endCol * sq_size, isEnpassantMoveRow * sq_size, sq_size, sq_size)
            screen.blit(images[move.pieceCaptured], endSquare)
        if move.pieceMoved != '--':
            screen.blit(images[move.pieceMoved], p.Rect(c*sq_size, r*sq_size, sq_size, sq_size))
        p.display.flip()
        clock.tick(60)

def drawEndGameText(screen, text):
    font = p.font.SysFont("Arial", 18, True, False)
    textObject = font.render(text, 0, p.Color("black"))
    textLocation = p.Rect(0, 0, board_width, board_height).move(board_width/2 - textObject.get_width()/2, board_height/2 - textObject.get_height()/2)
    screen.blit(textObject, textLocation)
    screen.blit(textObject, textLocation.move(2, 2))


if __name__ == "__main__":
    main()
