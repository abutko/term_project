# Andrew Butko, abutko, Section A
# 15-112 Spring 2013 Term Project - due 5/1/13 at 9 PM

# chess piece classes for term project
# images taken from http://ixian.com/chess/jin-piece-sets/ - they are lincensed
# under a Creative Commons Attribution-Share Alike 3.0 Unported License

# some of the functions here are quite obnoxious because are how specific
# the movement and special 'powers' of certain pieces are (castling, promotion).
# 'checking for check' has to be done separately because I wanted to do it from
# the king's perspective - this means that I could not store some 'repeated'
# lines in separate functions because they are tweaked just slightly in the
# middle of lines that can't be separated
# I apologize for subjecting anyone to reading this

from Tkinter import *
from PIL import Image, ImageTk


class Piece(object):
    def __init__(self, player, row, col, hasMoved=False):
        self.player = player
        if (player == "WHITE"): self.color = "w"
        elif (player == "BLACK"): self.color = "b"
        self.row = row
        self.col = col
        self.initPos = (row, col)
        self.hasMoved = hasMoved
        self.captured = False

    def __getstate__(self):
        return (type(self), self.player, self.row, self.col, self.hasMoved)

    
    
# values of pieces taken from wikipedia entry on relative values

class Pawn(Piece):
    def __init__(self, player, row, col, hasMoved=False):
        Piece.__init__(self, player, row, col, hasMoved)
        img = Image.open("%sp.png" % (self.color))
        self.image = ImageTk.PhotoImage(img)
        self.value = 1
        self.letter = ''
        
    def getLegalMoves(self, canvas):
        board = canvas.data.board
        rows = cols = 8
        legalMoveList = [ ]
        if (self.player == "WHITE"): drow = -1
        elif (self.player == "BLACK"): drow = +1
        if onBoard(self.row+drow, self.col) and board[self.row+drow][self.col] == 0:
            legalMoveList.append((self.row+drow, self.col))  # normal move one
            if (self.hasMoved == False and onBoard(self.row+(2*drow),self.col) and
                board[self.row+(2*drow)][self.col] == 0):
                legalMoveList.append((self.row+(2*drow), self.col)) # move two
        if (onBoard(self.row+drow,self.col+1) and
            board[self.row+drow][self.col+1] != 0):
            if board[self.row+drow][self.col+1].player != self.player: #diag capture
                legalMoveList.append((self.row+drow,self.col+1))
        if (onBoard(self.row+drow,self.col-1) and
            board[self.row+drow][self.col-1] != 0):
            if board[self.row+drow][self.col-1].player != self.player: # diag capture
                legalMoveList.append((self.row+drow,self.col-1))
        if (canvas.data.kingRowW, canvas.data.kingColW) in legalMoveList:
            legalMoveList.remove((canvas.data.kingRowW, canvas.data.kingColW))
        elif (canvas.data.kingRowB, canvas.data.kingColB) in legalMoveList:
            legalMoveList.remove((canvas.data.kingRowB, canvas.data.kingColB))
        return legalMoveList
    def __repr__(self):
        return "Pawn(%r, %r, %r)" % (self.player, self.row, self.col)

    
class Bishop(Piece):
    def __init__(self, player, row, col, hasMoved=False):
        Piece.__init__(self, player, row, col, hasMoved)
        img = Image.open("%sb.png" % (self.color))
        self.image = ImageTk.PhotoImage(img)
        self.value = 3
        self.letter = 'B'
    
    def getLegalMoves(self, canvas):
        board = canvas.data.board
        rows = cols = 8
        legalMoveList = [ ]
        dirs = [(-1,-1),(-1,+1),(+1,-1),(+1,+1)]
        for dir in dirs:
            drow, dcol = dir
            currentRow,currentCol = self.row + drow, self.col + dcol
            while onBoard(currentRow, currentCol):
                if board[currentRow][currentCol] == 0: # empty
                    legalMoveList.append((currentRow, currentCol))
                elif board[currentRow][currentCol].player == self.player:
                    break
                else: # other player's piece
                    legalMoveList.append((currentRow, currentCol))
                    break
                currentRow += drow
                currentCol += dcol
        if (canvas.data.kingRowW, canvas.data.kingColW) in legalMoveList:
            legalMoveList.remove((canvas.data.kingRowW, canvas.data.kingColW))
        elif (canvas.data.kingRowB, canvas.data.kingColB) in legalMoveList:
            legalMoveList.remove((canvas.data.kingRowB, canvas.data.kingColB))
        return legalMoveList
    def __repr__(self):
        return "Bishop(%r, %r, %r)" % (self.player, self.row, self.col)


class Knight(Piece):
    def __init__(self, player, row, col, hasMoved=False):
        Piece.__init__(self, player, row, col, hasMoved)
        img = Image.open("%sn.png" % (self.color))
        self.image = ImageTk.PhotoImage(img)
        self.value = 3
        self.letter = 'N'
    def getLegalMoves(self, canvas):
        board = canvas.data.board
        rows = cols = 8
        legalMoveList = [ ]
        dirs = [(-1,-2),(-2,-1),(-2,+1),(-1,+2),
                (+1,-2),(+2,-1),(+2,+1),(+1,+2)]
        for dir in dirs:
            drow, dcol = dir
            currentRow,currentCol = self.row + drow, self.col + dcol
            if onBoard(currentRow, currentCol):
                if board[currentRow][currentCol] == 0: # empty
                    legalMoveList.append((currentRow, currentCol))
                elif board[currentRow][currentCol].player != self.player:
                    legalMoveList.append((currentRow, currentCol))
                else: pass # piece that is the same player
        # can't capture kings3
        if (canvas.data.kingRowW, canvas.data.kingColW) in legalMoveList:
            legalMoveList.remove((canvas.data.kingRowW, canvas.data.kingColW))
        elif (canvas.data.kingRowB, canvas.data.kingColB) in legalMoveList:
            legalMoveList.remove((canvas.data.kingRowB, canvas.data.kingColB))
        return legalMoveList
    def __repr__(self):
        return "Knight(%r, %r, %r)" % (self.player, self.row, self.col)

    
class Rook(Piece):
    def __init__(self, player, row, col, hasMoved=False):
        Piece.__init__(self, player, row, col, hasMoved)
        img = Image.open("%sr.png" % (self.color))
        self.image = ImageTk.PhotoImage(img)
        self.value = 5
        self.letter = 'R'
    def getLegalMoves(self, canvas):
        board = canvas.data.board
        rows = cols = 8
        legalMoveList = [ ]
        dirs = [(-1,0),(+1,0),(0,-1),(0,+1)]
        for dir in dirs:
            drow, dcol = dir
            currentRow,currentCol = self.row + drow, self.col + dcol
            while onBoard(currentRow, currentCol):
                if board[currentRow][currentCol] == 0: # empty
                    legalMoveList.append((currentRow, currentCol))
                elif board[currentRow][currentCol].player == self.player:
                    break
                else: # other player's piece
                    legalMoveList.append((currentRow, currentCol))
                    break
                currentRow += drow
                currentCol += dcol
        if (canvas.data.kingRowW, canvas.data.kingColW) in legalMoveList:
            legalMoveList.remove((canvas.data.kingRowW, canvas.data.kingColW))
        elif (canvas.data.kingRowB, canvas.data.kingColB) in legalMoveList:
            legalMoveList.remove((canvas.data.kingRowB, canvas.data.kingColB))
        return legalMoveList
    def __repr__(self):
        return "Rook(%r, %r, %r)" % (self.player, self.row, self.col)

class Queen(Piece):
    def __init__(self, player, row, col, hasMoved=False):
        Piece.__init__(self, player, row, col, hasMoved)
        img = Image.open("%sq.png" % (self.color))
        self.image = ImageTk.PhotoImage(img)
        self.value = 9
        self.letter = 'Q'
    def getLegalMoves(self, canvas):
        board = canvas.data.board
        rows = cols = 8
        legalMoveList = [ ]
        dirs = [ (-1, -1), (-1, 0), (-1, +1),
                 ( 0, -1),          ( 0, +1),
                 (+1, -1), (+1, 0), (+1, +1) ]
        for dir in dirs:
            drow, dcol = dir
            currentRow,currentCol = self.row + drow, self.col + dcol
            while onBoard(currentRow, currentCol):
                if board[currentRow][currentCol] == 0: # empty
                    legalMoveList.append((currentRow, currentCol))
                elif board[currentRow][currentCol].player == self.player:
                    break
                else: # other player's piece
                    legalMoveList.append((currentRow, currentCol))
                    break
                currentRow += drow
                currentCol += dcol
        if (canvas.data.kingRowW, canvas.data.kingColW) in legalMoveList:
            legalMoveList.remove((canvas.data.kingRowW, canvas.data.kingColW))
        elif (canvas.data.kingRowB, canvas.data.kingColB) in legalMoveList:
            legalMoveList.remove((canvas.data.kingRowB, canvas.data.kingColB))
        return legalMoveList
    def __repr__(self):
        return "Queen(%r, %r, %r)" % (self.player, self.row, self.col)


class King(Piece):
    def __init__(self, player, row, col, hasMoved=False):
        Piece.__init__(self, player, row, col, hasMoved)
        img = Image.open("%sk.png" % (self.color))
        self.image = ImageTk.PhotoImage(img)
        self.inCheck = False
        initRow, initCol = self.initPos
        self.castlePos = [(initRow, initCol-2), (initRow, initCol+2)]
        self.canCastle = False
        self.nextToKing = False
        self.value = 200
        self.letter = 'K'

    def getLegalMoves(self, canvas):
        board = canvas.data.board
        rows = cols = 8
        legalMoveList = [ ]
        dirs = [ (-1, -1), (-1, 0), (-1, +1),
                 ( 0, -1),          ( 0, +1),
                 (+1, -1), (+1, 0), (+1, +1) ]
        for dir in dirs:
            drow, dcol = dir
            currentRow,currentCol = self.row + drow, self.col + dcol
            if onBoard(currentRow, currentCol):
                if board[currentRow][currentCol] == 0: # empty
                    legalMoveList.append((currentRow, currentCol))
                elif board[currentRow][currentCol].player != self.player:
                    legalMoveList.append((currentRow, currentCol))
        lrDirs = [-1,1]
        if self.hasMoved == False:
            for dir in lrDirs: # castling
                row, col = self.row, self.col+dir
                while col > 0 and col < 7:
                    if board[row][col] != 0: break
                    col += dir
                if (col == 0) or (col == 7):
                    piece = board[row][col]
                    if (piece != 0 and type(piece) == Rook and
                        piece.hasMoved == False):
                        legalMoveList.append((row,self.col+2*dir))
                        self.canCastle = True
                        #self.castlePos.append((row,self.col+2*dir))
        else:
            self.canCastle == False
            #self.castlePos = [ ]
        return legalMoveList
    
    def isKingInCheck(self, canvas):
        board = canvas.data.board
        diagDirs = [(-1,-1),(-1,+1),(+1,-1),(+1,+1)]
        crossDirs = [(-1,0),(+1,0),(0,-1),(0,+1)]
        knightDirs = [(-1,-2),(-2,-1),(-2,+1),(-1,+2),
                      (+1,-2),(+2,-1),(+2,+1),(+1,+2)]
        kingDirs = [ (-1, -1), (-1, 0), (-1, +1),
                     ( 0, -1),          ( 0, +1),
                     (+1, -1), (+1, 0), (+1, +1) ]
        
        for dir in diagDirs: # queen and bishop check
            drow, dcol = dir
            currentRow,currentCol = self.row + drow, self.col + dcol
            while onBoard(currentRow, currentCol):
                space = board[currentRow][currentCol]
                if space != 0:
                    if space.player == self.player: break
                    else:
                        if (type(space) == Queen or type(space) == Bishop or
                            type(space) == PromotedQueen or
                            type(space) == PromotedBishop):
                            self.inCheck = True
                            return
                        else: break
                currentRow += drow
                currentCol += dcol
        
        for dir in crossDirs: # rook and queen check
            drow, dcol = dir
            currentRow,currentCol = self.row + drow, self.col + dcol
            while onBoard(currentRow, currentCol):
                space = board[currentRow][currentCol]
                if space != 0:
                    if space.player == self.player: break
                    else:
                        if (type(space) == Rook or type(space) == Queen or
                            type(space) == PromotedQueen or
                            type(space) == PromotedRook):
                            self.inCheck = True
                            return
                        else: break
                currentRow += drow
                currentCol += dcol
        
        for dir in knightDirs: # knight check
            drow, dcol = dir
            currentRow,currentCol = self.row + drow, self.col + dcol
            if onBoard(currentRow, currentCol):
                space = board[currentRow][currentCol]
                if space != 0:
                    if space.player != self.player:
                        if type(space)==Knight or type(space)==PromotedKnight:
                            self.inCheck = True
                            return
                        
        for dir in kingDirs:
            drow, dcol = dir
            currentRow,currentCol = self.row + drow, self.col + dcol
            if onBoard(currentRow, currentCol):
                space = board[currentRow][currentCol]
                if space != 0:
                    if space.player != self.player:
                        if type(space) == King:
                            self.inCheck = True
                            self.nextToKing = True
                            return
                    
        if (self.player == "WHITE"): # white - pawn check
            if (onBoard(self.row-1,self.col+1) and
                board[self.row-1][self.col+1] != 0):
                if board[self.row-1][self.col+1].player != "WHITE": #diag capture
                    if type(board[self.row-1][self.col+1]) == Pawn:
                        self.inCheck = True
                        return
            if (onBoard(self.row-1,self.col-1) and
                board[self.row-1][self.col-1] != 0):
                if board[self.row-1][self.col-1].player != "WHITE": # diag capture
                    if type(board[self.row-1][self.col-1]) == Pawn:
                        self.inCheck = True
                        return
        
        elif (self.player == "BLACK"): # black - rows increasing instead of decreasing
            if (onBoard(self.row+1,self.col+1) and
                board[self.row+1][self.col+1] != 0):
                if board[self.row+1][self.col+1].player != "BLACK": #diag capture
                    if type(board[self.row+1][self.col+1]) == Pawn:
                        self.inCheck = True
                        return
            if (onBoard(self.row+1,self.col-1) and
                board[self.row+1][self.col-1] != 0):
                if board[self.row+1][self.col-1].player != "BLACK": # diag capture
                    if type(board[self.row+1][self.col-1]) == Pawn:
                        self.inCheck = True
                        return
        self.inCheck = False # all checks failed, function has not returned yet
        return
    def __repr__(self):
        return "King(%r, %r, %r)" % (self.player, self.row, self.col)

def onBoard(row, col):
        rows = cols = 8
        if row >= 0 and row < rows and col >= 0 and col < cols: return True
        return False

class PromotedQueen(Queen):
    def __init__(self, player, oldRow, oldCol, moveRow, moveCol, hasMoved):
        Queen.__init__(self, player, moveRow, moveCol, hasMoved)
        self.oldPos = (oldRow, oldCol)
        self.promotedPos = (moveRow, moveCol)

class PromotedBishop(Bishop):
    def __init__(self, player, oldRow, oldCol, moveRow, moveCol, hasMoved):
        Bishop.__init__(self, player, moveRow, moveCol, hasMoved)
        self.oldPos = (oldRow, oldCol)
        self.promotedPos = (moveRow, moveCol)
        
class PromotedRook(Rook):
    def __init__(self, player, oldRow, oldCol, moveRow, moveCol, hasMoved):
        Rook.__init__(self, player, moveRow, moveCol, hasMoved)
        self.oldPos = (oldRow, oldCol)
        self.promotedPos = (moveRow, moveCol)

class PromotedKnight(Knight):
    def __init__(self, player, oldRow, oldCol, moveRow, moveCol, hasMoved):
        Knight.__init__(self, player, moveRow, moveCol, hasMoved)
        self.oldPos = (oldRow, oldCol)
        self.promotedPos = (moveRow, moveCol)

def createPiece(piece, player, row, col, hasMoved):
    if piece == Pawn: return Pawn(player, row, col, hasMoved)
    elif piece == Bishop: return Bishop(player, row, col, hasMoved)
    elif piece == Knight: return Knight(player, row, col, hasMoved)
    elif piece == Rook: return Rook(player, row, col, hasMoved)
    elif piece == Queen: return Queen(player, row, col, hasMoved)
    elif piece == King: return King(player, row, col, hasMoved)

