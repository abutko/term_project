# Alexandra Butko, abutko, Section A
# 15-112 Spring 2013 Term Project - due 5/1/13 at 9 PM

# pvp_new.py
# some functions are excessively long because I replicate checks for white/black
# was easier for some debugging to see different movement behaviors for players
# also some checks like checkmate are required in many places, but I wanted to
# avoid using one function because there are many different 'little' things to
# worry about in the implementation (such as if a piece is being moved for
# testing checkmate or legality, when moves are being undone, etc).

from Tkinter import *
from pieces import *
from PIL import Image, ImageTk
import pickle
import random
import copy
import os
import subprocess

# maxItemLength and print2dList from course notes, week 6
# used to print board for testing purposes

def maxItemLength(a):
    maxLen = 0
    rows = len(a)
    cols = len(a[0])
    for row in xrange(rows):
        for col in xrange(cols):
            maxLen = max(maxLen, len(str(a[row][col])))
    return maxLen

def print2dList(a):
    if (a == []):
        # So we don't crash accessing a[0]
        print []
        return
    rows = len(a)
    cols = len(a[0])
    fieldWidth = maxItemLength(a)
    print "[ ",
    for row in xrange(rows):
        if (row > 0): print "\n  ",
        print "[ ",
        for col in xrange(cols):
            if (col > 0): print ",",
            # The next 2 lines print a[row][col] with the given fieldWidth
            format = "%" + str(fieldWidth) + "s"
            print format % str(a[row][col]),
        print "]",
    print "]"
    print "\n"
    
def rgbString(red, green, blue):
    # function taken from hw2.py writeup
    return "#%02x%02x%02x" % (red, green, blue)

def make2dList(rows, cols):
    # function taken from 2d-list notes
    a=[]
    for row in xrange(rows): a += [[0]*cols]
    return a

def createBoard(canvas):
    rows = cols = 8 # chess board is 8 rows and 8 cols
    board = make2dList(rows, cols)
    # create black pieces - "top" of board
    blackPieces, whitePieces = createBoardPieces(canvas)
    for piece in blackPieces:
        board[piece.row][piece.col] = piece
    for piece in whitePieces:
        board[piece.row][piece.col] = piece
    return board

def createBoardPieces(canvas):
    #create lists of pieces for each player, and then the board
    rows = cols = 8
    blackPieces, whitePieces = [ ], [ ]
    blackPieces.append(Rook("BLACK",0,0))
    blackPieces.append(Knight("BLACK",0,1))
    blackPieces.append(Bishop("BLACK",0,2))
    blackPieces.append(Queen("BLACK",0,3))
    blackPieces.append(King("BLACK",0,4))
    blackPieces.append(Bishop("BLACK",0,5))
    blackPieces.append(Knight("BLACK",0,6))
    blackPieces.append(Rook("BLACK",0,7))
    #pawn
    for col in xrange(cols):
        blackPieces.append(Pawn("BLACK",1,col))
        whitePieces.append(Pawn("WHITE",6,col))
    # create white pieces - "bottom" of board
    whitePieces.append(Rook("WHITE",7,0))
    whitePieces.append(Knight("WHITE",7,1))
    whitePieces.append(Bishop("WHITE",7,2))
    whitePieces.append(Queen("WHITE",7,3))
    whitePieces.append(King("WHITE",7,4))
    whitePieces.append(Bishop("WHITE",7,5))
    whitePieces.append(Knight("WHITE",7,6))
    whitePieces.append(Rook("WHITE",7,7))
    canvas.data.whitePieces = whitePieces
    canvas.data.blackPieces = blackPieces
    return whitePieces, blackPieces
     
def init(canvas):
    board = createBoard(canvas)
    # will keep track of king's position specifically for check
    (canvas.data.kingRowB, canvas.data.kingColB) = (0,4)
    (canvas.data.kingRowW, canvas.data.kingColW) = (7,4)
    canvas.data.board = board
    canvas.data.rows = canvas.data.cols = 8
    canvas.data.selectedPos = None
    (canvas.data.currentPlayer, canvas.data.otherPlayer) = ("WHITE", "BLACK")
    canvas.data.checkmate = False
    canvas.data.capturedPiecesW = [ ] # pieces black has captured
    canvas.data.capturedPiecesB = [ ] # pieces white has captured
    canvas.data.winner = None
    canvas.data.stalemate = False
    canvas.data.moveList = [ ] # (oldPos, movePos, tempPiece)
    canvas.data.checkTest = False
    redrawAll(canvas)

def mousePressed(canvas, event, root):
    currentPlayer = canvas.data.currentPlayer
    board = canvas.data.board
    xMargin, yMargin, cell = 200, 150, 80
    if not canvas.data.checkmate:
        if (canvas.data.selectedPos == None):
            if (((canvas.data.cols)*cell+xMargin >= event.x) and
                     (event.x >= xMargin) and
                    ((canvas.data.rows)*cell+yMargin >= event.y) and
                     (event.y >= yMargin)): # selected pos is on board
                selRow =(event.y - yMargin)/cell
                selCol = (event.x - xMargin)/cell
                if (board[selRow][selCol] != 0 and
                    board[selRow][selCol].player == currentPlayer):
                    canvas.data.selectedPos = ((event.y - yMargin)/cell,
                                               (event.x - xMargin)/cell)
        else:
            (moveRow, moveCol) = ((event.y - yMargin)/cell,
                                  (event.x - xMargin)/cell)
            oldRow, oldCol = canvas.data.selectedPos
            if (onBoard(moveRow, moveCol) and board[moveRow][moveCol] != 0 and
                board[moveRow][moveCol].player == board[oldRow][oldCol].player
                and (moveRow, moveCol) != (oldRow, oldCol)):
                canvas.data.selectedPos = (moveRow, moveCol)
            # checks if the movePos is a legal move, otherwise deselects piece
            else: movePiece(canvas, oldRow, oldCol, moveRow, moveCol)      
    redrawAll(canvas)

def movePiece(canvas, oldRow, oldCol, moveRow, moveCol):
    board = canvas.data.board
    piece = board[oldRow][oldCol]
    if ((moveRow, moveCol) in piece.getLegalMoves(canvas)):
        # selected position is in legalMoveList of the selected piece
            if type(piece) == King: # need to see if castling to move rook too
                if piece.player == "WHITE":
                    (canvas.data.kingRowW, canvas.data.kingColW) = (moveRow, moveCol)
                elif piece.player == "BLACK":
                    (canvas.data.kingRowB, canvas.data.kingColB) = (moveRow, moveCol)
                if piece.canCastle == True: # castling specific movement
                    if (moveRow, moveCol) in piece.castlePos:
                        if moveCol < oldCol: # castle left
                            rook = board[oldRow][0]
                            board[oldRow][3] = rook
                            rook.row, rook.col = oldRow, 3
                            board[oldRow][0] = 0
                        elif moveCol > oldCol: # castle right
                            rook = board[oldRow][7]
                            board[oldRow][5] = rook
                            board[oldRow][7] = 0
                            rook.row, rook.col = oldRow, 5
            tempPiece = board[moveRow][moveCol]
            board[moveRow][moveCol] = piece
            piece.row, piece.col = moveRow, moveCol
            board[oldRow][oldCol] = 0
            canvas.data.selectedPos = None
            if type(piece) == Pawn:
                if moveRow == 0 or moveRow == 7:
                    board[moveRow][moveCol] = PromotedQueen(piece.player,
                    oldRow, oldCol, moveRow, moveCol, True)
            # check for check for current player and checkmate for the other
            endOfTurnCheck(canvas, oldRow, oldCol, moveRow, moveCol, tempPiece)
            # currentPlayer, otherPlayer are switched now if piece has moved
            if not board[oldRow][oldCol] == piece: # if piece has moved
                if not piece.hasMoved:
                    piece.hasMoved = True
                if tempPiece != 0 and tempPiece != board[moveRow][moveCol]: # a piece was captured
                    tempPiece.captured = True
                    if canvas.data.currentPlayer == "WHITE":
                        canvas.data.capturedPiecesW.append(tempPiece)
                    elif canvas.data.currentPlayer == "BLACK":
                        canvas.data.capturedPiecesB.append(tempPiece)
    else: # the selected position is not in legalMoveList of the selected piece
            canvas.data.selectedPos = None

def undoMove(canvas, oldRow, oldCol, moveRow, moveCol, tempPiece):
    board = canvas.data.board
    piece = board[moveRow][moveCol]
    board[oldRow][oldCol] = piece
    board[moveRow][moveCol] = tempPiece
    if piece != 0 and piece != tempPiece:
        piece.row, piece.col = oldRow, oldCol
        if type(piece) == King: # need to see if king had castled
                if piece.player == "WHITE":
                    (canvas.data.kingRowW, canvas.data.kingColW) = (oldRow, oldCol)
                    if piece.initPos == (oldRow, oldCol):
                        if (moveRow, moveCol) in piece.castlePos:
                                piece.hasMoved = False
                                if moveCol < oldCol: # castle left
                                    rook = board[oldRow][3]
                                    rook.hasMoved = False
                                    board[oldRow][0] = rook
                                    rook.row, rook.col = oldRow, 0
                                    board[oldRow][3] = 0
                                elif moveCol > oldCol: # castle right
                                    rook = board[oldRow][5]
                                    board[oldRow][7] = rook
                                    board[oldRow][5] = 0
                                    rook.row, rook.col = oldRow, 7
                elif piece.player == "BLACK":
                    (canvas.data.kingRowB, canvas.data.kingColB) = (oldRow, oldCol)
                    if piece.initPos == (oldRow, oldCol):
                        if (moveRow, moveCol) in piece.castlePos:
                            piece.hasMoved = False
                            if moveCol < oldCol: # castle left
                                rook = board[oldRow][3]
                                rook.hasMoved = False
                                board[oldRow][0] = rook
                                rook.row, rook.col = oldRow, 0
                                board[oldRow][3] = 0
                            elif moveCol > oldCol: # castle right
                                rook = board[oldRow][5]
                                board[oldRow][7] = rook
                                board[oldRow][5] = 0
                                rook.row, rook.col = oldRow, 7
        elif type(piece) == PromotedQueen:
            if (piece.promotedPos == (moveRow, moveCol) and
                piece.oldPos == (oldRow, oldCol)):
                board[oldRow][oldCol] = Pawn(piece.player, piece.row, piece.col, True)
        if (oldRow, oldCol) == piece.initPos: piece.hasMoved = False
    if tempPiece != 0:
        #if tempPiece.captured == True: tempPiece.captured = False
        if not canvas.data.checkTest and tempPiece.captured:
            tempPiece.captured = False
            if tempPiece.player== 'BLACK': canvas.data.capturedPiecesB.pop()
            else: canvas.data.capturedPiecesW.pop()

def endOfTurnCheck(canvas, oldRow, oldCol, moveRow, moveCol, tempPiece):
    # sees if the player's king is in check, and doesn't allow a move unless
    # they are moved out of check
    board = canvas.data.board
    piece = board[moveRow][moveCol]
    if canvas.data.currentPlayer == "WHITE":
        currentKing = board[canvas.data.kingRowW][canvas.data.kingColW]
        currentKing.isKingInCheck(canvas)
        otherKing = board[canvas.data.kingRowB][canvas.data.kingColB]
        if currentKing.inCheck == True:
            if tempPiece != 0: tempPiece.captured = False
            undoMove(canvas, oldRow, oldCol, moveRow, moveCol, tempPiece)
        else:
            canvas.data.currentPlayer, canvas.data.otherPlayer = canvas.data.otherPlayer, canvas.data.currentPlayer
            animateMove(canvas, oldRow, oldCol, moveRow, moveCol, piece)
            otherKing.isKingInCheck(canvas) # king of the new currentPlayer
            canvas.data.moveList.append(((oldRow, oldCol), (moveRow, moveCol), piece, tempPiece))
            checkmateStalemateTest(canvas, "BLACK", otherKing.inCheck) # checks checkmate for new current player
        currentKing.isKingInCheck(canvas)
    elif canvas.data.currentPlayer == "BLACK":
        currentKing = board[canvas.data.kingRowB][canvas.data.kingColB]
        currentKing.isKingInCheck(canvas)
        otherKing = board[canvas.data.kingRowW][canvas.data.kingColW]
        if currentKing.inCheck == True:
            if tempPiece != 0: tempPiece.captured = False
            undoMove(canvas, oldRow, oldCol, moveRow, moveCol, tempPiece)
        else: 
            canvas.data.currentPlayer, canvas.data.otherPlayer = canvas.data.otherPlayer, canvas.data.currentPlayer
            animateMove(canvas, oldRow, oldCol, moveRow, moveCol, piece)
            otherKing.isKingInCheck(canvas) # king of the new currentPlayer
            canvas.data.moveList.append(((oldRow, oldCol), (moveRow, moveCol), piece, tempPiece))
            checkmateStalemateTest(canvas, "WHITE", otherKing.inCheck) # checks checkmate for new current player
        currentKing.isKingInCheck(canvas)
    redrawAll(canvas)


def checkmateStalemateTest(canvas, player, check):
    # try moves for all pieces - if it can't get out of check it's game over
    canvas.data.checkTest = True
    board = canvas.data.board
    rows = cols = 8
    currentCheck = check # is king in check before testing for checkmate
    for row in xrange(rows):
        for col in xrange(cols):
            piece = board[row][col]
            if piece != 0:
                if piece.player == player:
                    for move in piece.getLegalMoves(canvas):
                        oldRow, oldCol = piece.row, piece.col
                        moveRow, moveCol = move
                        tempPiece = board[moveRow][moveCol]
                        board[moveRow][moveCol] = piece
                        piece.row, piece.col = moveRow, moveCol
                        if type(piece) == King:
                            if piece.player == "WHITE":
                                (canvas.data.kingRowW,
                                 canvas.data.kingColW) = (moveRow, moveCol)
                            elif piece.player == "BLACK":
                                (canvas.data.kingRowB,
                                 canvas.data.kingColB) = (moveRow, moveCol)
                        board[oldRow][oldCol] = 0
                        if player == "WHITE":
                            currentKing = board[canvas.data.kingRowW][canvas.data.kingColW]
                            currentKing.isKingInCheck(canvas)
                            if currentKing.inCheck == False:
                                undoMove(canvas, oldRow, oldCol,
                                         moveRow, moveCol, tempPiece)
                                canvas.data.checkTest = False
                                return
                            else: 
                                undoMove(canvas, oldRow, oldCol,
                                         moveRow, moveCol, tempPiece)
                        if player == "BLACK":
                            currentKing = board[canvas.data.kingRowB][canvas.data.kingColB]
                            currentKing.isKingInCheck(canvas)
                            if currentKing.inCheck == False:
                                undoMove(canvas, oldRow, oldCol,
                                         moveRow, moveCol, tempPiece)
                                canvas.data.checkTest = False
                                return
                            else: 
                                undoMove(canvas, oldRow, oldCol,
                                         moveRow, moveCol, tempPiece)

    if currentCheck == True:                               
        canvas.data.checkmate = True
        canvas.data.winner = canvas.data.otherPlayer # current player is in checkmate    else:
    else:
        canvas.data.stalemate = True
    canvas.data.checkTest = False
    return
                    
    
def keyPressed(canvas, event, root):
    if (event.char == 'r'): init(canvas)
    if (event.char == 'u'): # undomove
        canvas.data.selectedPos = None
        moveList = canvas.data.moveList
        if moveList != [ ]:
            ((oldRow, oldCol), (moveRow, moveCol), piece, tempPiece) = moveList[len(moveList)-1]
            undoMove(canvas, oldRow, oldCol, moveRow, moveCol, tempPiece)
            current, other = canvas.data.currentPlayer, canvas.data.otherPlayer
            canvas.data.currentPlayer, canvas.data.otherPlayer = other, current
            moveList.pop()
            #moveList.remove(((oldRow, oldCol), (moveRow, moveCol), tempPiece))
    if (event.char == 's'):
        saveData(canvas)
    if (event.char == 'o'):
        init(canvas)
        loadData(canvas)
    if (event.char == 'm'):
        mainMenu(canvas, event, root)  
    redrawAll(canvas)

def mainMenu(canvas, event, root):
    top = Toplevel()
    top.title("Exiting to main menu...")
    save = 'Do you want to save first?'
    msg = Message(top, text=save)
    msg.pack()
    button1 = Button(top, text="Save")
    button1.bind('<Button-1>', lambda event:
                 saveQuit(event, canvas, top, root))
    button1.pack()
    button2 = Button(top, text='Quit')
    button2.bind('<Button-1>', lambda event:
                 quit(event, canvas, top, root))
    button2.pack()
    top.pack()        
    pwd = os.getcwd() # term_project directory
    path = os.path.join(pwd, 'load_screen.py') # filename
    subprocess.Popen("python %s" % path, shell=True) # run file
    root.destroy()
    

def saveQuit(event, canvas, top, root):
    # after pressing 'm' - save/quit
    saveData(canvas)
    quit(event, canvas, top, root)
    
def quit(event, canvas, top, root):
    # after pressing 'm' - just quit
    top.destroy
    pwd = os.getcwd() # current working directory
    path = os.path.join(pwd, 'load_screen.py') # filename
    subprocess.Popen("python %s" % path, shell=True) # run file
    root.destroy()

def animateMove(canvas, oldRow, oldCol, moveRow, moveCol, piece):
    # movement animation for the piece
    board=canvas.data.board
    xMargin, yMargin, cell = 200, 150, 80
    board[moveRow][moveCol] = 0
    for i in xrange(4): # move made in 4 'steps'
        redrawAll(canvas)
        canvas.create_image(xMargin+oldCol*cell+i*(moveCol-oldCol)*cell/4,
                                        yMargin+oldRow*cell+i*(moveRow-oldRow)*cell/4,
                                        image=piece.image, anchor=NW)
        canvas.update_idletasks()
    board[moveRow][moveCol] = piece
    
def saveData(canvas):
    # uses pickle to store gamestate in a file in directory
    saveData = [ ]
    saveData.append(canvas.data.currentPlayer)
    filehandler = open('save.pc', 'w')
    board = make2dList(8,8)
    capturedW = [ ]
    capturedB = [ ]
    for row in xrange(8):
        for col in xrange(8):
            if canvas.data.board[row][col] == 0: board[row][col] = 0
            else: board[row][col] = canvas.data.board[row][col].__getstate__()
    saveData.append(board)
    for piece in xrange(len(canvas.data.capturedPiecesW)):
        capturedW.append(canvas.data.capturedPiecesW[piece].__getstate__())
    for piece in xrange(len(canvas.data.capturedPiecesB)):
        capturedB.append(canvas.data.capturedPiecesB[piece].__getstate__())
    saveData.append(capturedW)
    saveData.append(capturedB)
    kingPosB = (canvas.data.kingRowB, canvas.data.kingColB)
    kingPosW = (canvas.data.kingRowW, canvas.data.kingColW)
    saveData.append(kingPosB)
    saveData.append(kingPosW)
    pickle.dump(saveData, filehandler)

def loadData(canvas):
    # loads a game that
    # indices taken from saveData function
    filehandler = open('save.pc', 'r') 
    saveData = pickle.load(filehandler)
    canvas.data.currentPlayer = saveData[0]
    if canvas.data.currentPlayer == 'WHITE':
        canvas.data.otherPlayer = 'BLACK'
    else: canvas.data.otherPlayer = 'WHITE'
    whitePieces, blackPieces = [ ], [ ]
    board = saveData[1]
    for row in xrange(8):
        for col in xrange(8):
            if board[row][col] == 0: canvas.data.board[row][col] = 0
            else:
                (piece, player, row, col, hasMoved) = board[row][col]
                newPiece = createPiece(piece, player, row, col, hasMoved)
                canvas.data.board[row][col] = newPiece
                if player == 'WHITE': whitePieces.append(newPiece)
                else: blackPieces.append(newPiece)
    capturedW, capturedB = saveData[2], saveData[3]
    for captured in xrange(len(capturedW)):
        (piece, player, row, col, hasMoved) = capturedW[captured]
        newPiece = createPiece(piece, player, row, col, hasMoved)
        newPiece.captured = True
        whitePieces.append(newPiece)
        canvas.data.capturedPiecesW.append(newPiece)
    for captured in xrange(len(capturedB)):
        (piece, player, row, col, hasMoved) = capturedB[captured]
        newPiece =createPiece(piece, player, row, col, hasMoved)
        blackPieces.append(newPiece)
        newPiece.captured = True
        canvas.data.capturedPiecesB.append(newPiece)
    (canvas.data.kingRowB, canvas.data.kingColB) = saveData[4]
    (canvas.data.kingRowW, canvas.data.kingColW) = saveData[5]
    canvas.data.whitePieces, canvas.data.blackPieces = whitePieces, blackPieces
    redrawAll(canvas)


def drawBoard(canvas):
    # structure taken from my hw2 writeup
    xMargin, yMargin = 200, 150
    width = height = 640 #board width/height
    cell = 80
    # draw the board - the pieces are represented outside of this function
    for row in xrange(8):
        for col in xrange(8):
            rowNum, colLetter = row+1, chr(ord('A')+col)
            left, top = xMargin + col * cell, yMargin + row * cell
            if row % 2 == 0:
                if col % 2 == 0: fill = rgbString(255,196,135)
                elif col % 2 == 1: fill = rgbString(200,120,50)
            elif row % 2 == 1:
                if col % 2 == 1: fill = rgbString(255,196,135)
                elif col % 2 == 0: fill = rgbString(200,120,50)
            canvas.create_rectangle(left, top, left + cell, top + cell,
                                    fill=fill,width=0)
            n = 5 # 'nudge' the text over 5 pixels
    #draw border around the board: needed here so it covers the legal moves
    canvas.create_rectangle(xMargin, yMargin,
                            xMargin + width, yMargin + height,
                            width = 4, outline = rgbString(120, 120, 120))
    
def drawText(canvas):
    # draws the row/col description on the board
    xMargin, yMargin = 200, 150
    cell = 80
    for row in xrange(8):
        for col in xrange(8):
            rowNum, colLetter = 8-row, chr(ord('A')+col)
            left, top = xMargin + col * cell, yMargin + row * cell
            n = 5 # 'nudge' the text over 5 pixels
            canvas.create_text(left+n, top, text ="%s%d" % (colLetter, rowNum), anchor=NW, font='Times')

    
def drawPieces(canvas):
    # takes image from instance of piece class and draws it
    board = canvas.data.board
    xMargin, yMargin = 200, 150
    width = height = 640 #board width/height
    cell = width/8
    (rows, cols) = (len(board), len(board[0]))
    #if canvas.data.currentPlayer == "WHITE":
    for row in xrange(rows):
        for col in xrange(cols):
            if board[row][col] != 0:
                piece = board[row][col]
                canvas.create_image(xMargin+col*cell, yMargin+row*cell,
                                    image=piece.image, anchor=NW)


def drawMoves(canvas):
    # draws the legal moves for each piece
    board = canvas.data.board
    xMargin, yMargin, cell = 200, 150, 80
    if canvas.data.selectedPos != None:
        (selRow, selCol) = canvas.data.selectedPos
        # highlight legal move positions, with color matching checkered pattern
        for position in board[selRow][selCol].getLegalMoves(canvas):
            row, col = position[0], position[1]
            if row % 2 == 0:
                if col % 2 == 0: fill = rgbString(51,123,255)
                elif col % 2 == 1: fill = rgbString(0,102,204)
            elif row % 2 == 1:
                if col % 2 == 1: fill = rgbString(51,123,255)
                elif col % 2 == 0: fill = rgbString(0,102,204)
            left, top = xMargin + col * cell, yMargin + row * cell
            canvas.create_rectangle(left, top, left+cell, top+cell,
                                    width = 0, fill=fill)
        left, top = xMargin + selCol * cell, yMargin + selRow * cell
        #draw border around the board: needed here so it covers the legal moves
        width = height = 640 
        canvas.create_rectangle(xMargin, yMargin,
                                xMargin + width, yMargin + height,
                                width = 4, outline = rgbString(120, 120, 120))
        # outline selected piece
        canvas.create_rectangle(left, top, left+cell, top+cell,
                                width = 4,  outline="blue")

def drawDisplay(canvas):
    # different words detailing state of game - currentplayer, check,
    # and last move made
    board = canvas.data.board
    if canvas.data.currentPlayer == "WHITE":
        currentPlayer = "White"
        currentKing = board[canvas.data.kingRowW][canvas.data.kingColW]
    elif canvas.data.currentPlayer == "BLACK":
        currentPlayer = "Black"
        currentKing = board[canvas.data.kingRowB][canvas.data.kingColB]
    currentMsg = "Current Player: %s" % (currentPlayer)
    canvas.create_text(10,10, text=currentMsg, anchor=NW, font=('Times',30))
    if currentKing != 0: currentKing.isKingInCheck(canvas)
    if currentKing != 0 and currentKing.inCheck:
        checkMsg = "%s King is in check." % currentPlayer
        canvas.create_text(10, 60, text=checkMsg, anchor=NW, font=('Times',30))
    if len(canvas.data.moveList) > 0:
        ((fromRow, fromCol), (toRow, toCol), piece,
        capPiece) = canvas.data.moveList[len(canvas.data.moveList)-1]
        last = 'Last Move Made'
        canvas.create_text(1030, 10, text=last, anchor=NE, font=('Times',30))
        capTxt = 'x' if capPiece != 0 else ' '
        lastMove = (piece.letter+chr(ord('a')+fromCol)+
                    str(8-fromRow)+capTxt+chr(ord('a')+toCol)+str(8-toRow))
        canvas.create_text(1030, 60, text=lastMove, anchor=NE, font=('Times',30))
    
    

def drawCapturedPieces(canvas):
    # draw captured white pieces on left side of board
    # and captured black pieces on the right
    margin = 10
    board = 640 # board width/height
    xMargin, yMargin, cell = 200, 150, 80
    for piece in xrange(len(canvas.data.capturedPiecesW)):
            capW = canvas.data.capturedPiecesW[piece]
            canvas.create_image(piece/8*cell+margin, yMargin+piece%8*cell,
                                image=capW.image, anchor=NW)
    for piece in xrange(len(canvas.data.capturedPiecesB)):
            capB = canvas.data.capturedPiecesB[piece]
            canvas.create_image(cell+margin+board+xMargin - piece/8*cell,
                                yMargin+piece%8*cell, image=capB.image, anchor=NW)
            
def drawGameOver(canvas):
    # taken from hw7.py - moreSnake
    spacing = 40
    cx = canvas.data.canvasWidth/2
    cy = canvas.data.canvasHeight/2
    if canvas.data.checkmate == True:
        if canvas.data.winner == "WHITE": winner = "White"
        elif canvas.data.winner == "BLACK": winner = "Black"
        canvas.create_text(cx, cy-spacing, text="Checkmate!",
                           font=("Helvetica", 64, "bold"))
        canvas.create_text(cx, cy+spacing, text="%s Player Wins!" % (winner),
                           font=("Helvetica", 64, "bold"))
    elif canvas.data.stalemate == True:
        canvas.create_text(cx, cy-spacing, text="Draw!",
                           font=("Helvetica", 64, "bold"))
        
def drawBackground(canvas):
    # background image taken from
    # http://www.pulsarmedia.eu/data/media/18/chess_image_pattern_1920x1200.jpg
    # used without permission 
    img = Image.open('game_background.png')
    canvas.data.backgroundImg = ImageTk.PhotoImage(img)
    canvas.create_image(0,0, image=canvas.data.backgroundImg, anchor=NW)
    
def redrawAll(canvas):
    canvas.delete(ALL)
    drawBackground(canvas)
    drawBoard(canvas)
    drawMoves(canvas)
    drawPieces(canvas)
    drawText(canvas)
    drawDisplay(canvas)
    drawCapturedPieces(canvas)
    if canvas.data.checkmate == True or canvas.data.stalemate == True:
        drawGameOver(canvas)
    
def showInstructions(canvas, event, root):
    # prints instructions for player when they click button
    top = Toplevel()
    top.title("Instructions")
    instructMsg = """
    'm' - Go to main menu \n
    's' - Save current game
    'o' - Open last saved game
    'u' - Undo last move
    'r' - Restart game
    """
    msg = Message(top, text=instructMsg)
    msg.pack()
    button = Button(top, text="Dismiss", command=top.destroy)
    button.pack()
    

def run():
    # general run function based on example in animation notes
    root = Tk()
    root.title("CHESS in Python")
    frame = Frame(root, width = 1040, height = 840)
    frame.pack()
    canvas = Canvas(frame, width = 1040, height = 840)
    canvas.pack()
    button = Button(frame,text='Instructions')
    button.bind("<Button-1>", lambda event: showInstructions(canvas, event, root))
    button.pack()
    button.place(x=1040,y=840, anchor=SE)
    root.resizable(width=0, height=0)
    root.canvas = canvas.canvas = canvas
    class Struct: pass
    canvas.data = Struct()
    canvas.data.canvasWidth = 1040
    canvas.data.canvasHeight = 840
    init(canvas)
    root.bind("<Button-1>", lambda event: mousePressed(canvas, event, root))
    root.bind("<Key>", lambda event: keyPressed(canvas, event, root))
    root.mainloop()

run()
