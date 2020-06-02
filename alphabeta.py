import pygame
import pygame.locals
import numpy
from itertools import cycle, permutations
import time
import os
import random

pygame.init()
board = 600
sideNav = 300
gameDisplay = pygame.display.set_mode((board, board))
clock = pygame.time.Clock()

def buttons():
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            quit()

def setUp():
    gameDisplay.fill((255, 255, 255))
    def squareGen():
        x = cycle([(115, 50, 30), (255, 255, 255)])
        for i in x:
            yield i

    colour = squareGen()
    for j in range(8):
        for i in range(8):
            pygame.draw.rect(gameDisplay, next(colour), [i*board/8, j*board/8, board/8, board/8])
        next(colour)

def text(text, x, y, fontSize=board/8):
    font = pygame.font.SysFont(None, round(fontSize))
    text = font.render(text, True, (0, 0, 0))
    gameDisplay.blit(text,(x, y))

def checkMovement():
    botter = False
    mouse = pygame.mouse.get_pos()
    coords = (mouse[0], mouse[1])
    scale = board / 8
    if pygame.mouse.get_pressed()[0]:
        f = lambda x: scale * round(x/scale)
        xshow = f(mouse[0]) if f(mouse[0]) < mouse[0] else f(mouse[0]-scale)
        yshow = f(mouse[1]) if f(mouse[1]) < mouse[1] else f(mouse[1]-scale)
        x = int(xshow/scale)
        y = int(yshow/scale)
        movingPiece = grid[y][x]
        if movingPiece:
            if not movingPiece.ai:
                old = movingPiece.coords
                while pygame.mouse.get_pressed()[0]:
                    mouse = pygame.mouse.get_pos()
                    buttons()
                    grid[y][x] = ''
                    setUp()
                    showPieces(grid)
                    gameDisplay.blit(movingPiece.image, (mouse[0]-board/20, mouse[1]-board/20))
                    pygame.display.update()

                x = int(f(mouse[0])/scale) if f(mouse[0]) < mouse[0] else int(f(mouse[0]-scale)/scale)
                y = int(f(mouse[1])/scale) if f(mouse[1]) < mouse[1] else int(f(mouse[1]-scale)/scale)
                if [x, y] in movingPiece.getMoves():
                    oldPiece = grid[y][x]
                    grid[y][x] = movingPiece
                    movingPiece.coords = [x, y]
                    if old != [x, y]: botter = True
                    if check():
                        grid[old[1]][old[0]] = movingPiece
                        movingPiece.coords = old
                        grid[y][x] = oldPiece
                        botter = False

                else: grid[old[1]][old[0]] = movingPiece
                if botter:
                    bot()
                    for row in grid:
                        for piece in row:
                            if piece:
                                if piece.pieceName == 'king' and not piece.ai:
                                    return bool(checkmate(piece))
    return False

def check():
    for row in grid:
        for piece in row:
            if piece:
                if not piece.ai and piece.pieceName == 'king':
                    king = piece
    for row in grid:
        for piece in row:
            if piece:
                if piece.ai:
                    if king.coords in piece.getMoves():
                        return True
    return False


def checkmate(king):
    moves = king.getMoves()
    moves.append(king.coords)
    moves = set(map(tuple, moves))
    for row in grid:
        for piece in row:
            if piece:
                if piece.ai:
                    moves = moves - set(map(tuple, piece.getMoves()))
    if not moves:
        killers = []
        for row in grid:
            for piece in row:
                if piece:
                    if piece.ai and king.coords in piece.getMoves():
                        killers.append(piece)
        if len(killers) == 1:
            for row in grid:
                for piece in row:
                    if piece:
                        if killers[0].coords in piece.getMoves() and not piece.ai:
                            return 0
        return 10000
    return 0
    

def showPieces(grid):
    x = board / 64
    y = board / 64
    for i in grid:
        for j in i:
            if j:
                gameDisplay.blit(j.image, (x-board / 64, y))
            x += board / 8
        x = board / 64
        y += board / 8

def thinking():
    pygame.draw.rect(gameDisplay, (176, 99, 11), [board * 0.3, board * 0.3, board * 0.4, board * 0.27])
    border = pygame.image.load(os.path.join(os.getcwd(), 'frame.png'))
    border = pygame.transform.scale(border, (int(board * 0.4), int(board * 0.27)))
    gameDisplay.blit(border, (board * 0.3, board * 0.3))

    font = pygame.font.SysFont(None, 30)
    text = font.render('Thinking...', True, (0, 0, 0))
    gameDisplay.blit(text,(board * 0.4, board * 0.42))
    pygame.display.update()


def scorer(minimax, depth, alpha=-9999, beta=9999):
    if depth == 0:
        return scoreBoard()
    if minimax:
        for row in grid:
            for piece in row:
                if piece:
                    if piece.ai:
                        oldPossible = piece.getMoves()
                        oldCoords = piece.coords

                        if piece.pieceName == 'king':
                            score = checkmate(piece)
                            if score: return -score

                        for move in oldPossible:
                            old = grid[move[1]][move[0]]
                            grid[move[1]][move[0]] = piece
                            grid[piece.coords[1]][piece.coords[0]] = ''
                            score = scorer(False, depth - 1, alpha, beta)
                            grid[move[1]][move[0]] = old
                            grid[piece.coords[1]][piece.coords[0]] = piece
                            if score > alpha:
                                alpha = score
                                if alpha >= beta:
                                    return alpha   
        return alpha                       
    else:
        for row in grid:
            for piece in row:
                if piece:
                    if not piece.ai:
                        oldPossible = piece.getMoves()
                        oldCoords = piece.coords

                        if piece.pieceName == 'king':
                            score = checkmate(piece)
                            if score: return score

                        for move in oldPossible:
                            old = grid[move[1]][move[0]]
                            grid[move[1]][move[0]] = piece
                            grid[piece.coords[1]][piece.coords[0]] = ''
                            piece.coords = move
                            score = scorer(True, depth - 1, alpha, beta)
                            grid[move[1]][move[0]] = old
                            piece.coords = oldCoords
                            grid[piece.coords[1]][piece.coords[0]] = piece
                            if score < beta:
                                beta = score
                                if alpha >= beta:
                                    return beta
        return beta

def bot():
    bestScore = -9999

    thinking()

    for row in grid:
        for piece in row:
            if piece:
                if piece.ai:
                    oldPossible = piece.getMoves()
                    oldCoords = piece.coords
                    for move in oldPossible:
                        old = grid[move[1]][move[0]]
                        grid[move[1]][move[0]] = piece
                        grid[piece.coords[1]][piece.coords[0]] = ''
                        piece.coords = move
                        score = scorer(False, 4)
                        grid[move[1]][move[0]] = old
                        piece.coords = oldCoords
                        grid[piece.coords[1]][piece.coords[0]] = piece
                        piece.possibleMoves = oldPossible
                        if score > bestScore or score == bestScore and not random.randint(0, 2):
                            bestScore = score
                            bestMove = move
                            obj = piece
    grid[obj.coords[1]][obj.coords[0]] = ''
    grid[bestMove[1]][bestMove[0]] = obj
    obj.coords = bestMove


def scoreBoard():
    lstOfPieces = {'P':10, 'B':30, 'Kn':30, 'R':50, 'Q':90, 'K':900}
    points = 0
    for i in grid:
        for j in i:
            if j:
                if j.ai:
                    points += lstOfPieces[j.basicPiece]
                else:
                    points -= lstOfPieces[j.basicPiece] * 0.99
    return points

class Piece:
    def __init__(self, pieceName, coords, ai):
        self.pieceName = pieceName
        self.coords = list(coords)
        self.ai = ai
        self.basicPiece = pieceName[0].upper() if pieceName != 'knight' else 'Kn'
        if self.basicPiece == 'Kn': imageName = 'n'
        else: imageName = pieceName[0]
        f = lambda x, y: f'Chess_{x}{y}t60.png'
        lightDark = 'd' if self.ai else 'l'
        self.image = pygame.image.load(os.path.join(os.getcwd() + '\\pieces', f(imageName, lightDark)))
    
    def getMoves(self):
        if self.basicPiece == 'P':
            moves = self.pawnPossible()
        elif self.basicPiece == 'K':
            moves = self.kingPossible()
        elif self.basicPiece == 'Q':
            moves = self.queenPossible()
        elif self.basicPiece == 'B':
            moves = self.bishopPossible()
        elif self.basicPiece == 'Kn':
            moves = self.knightPossible()
        elif self.basicPiece == 'R':
            moves = self.rookPossible()
        random.shuffle(moves)
        return moves
    
    def pawnPossible(self):
        change = 1 if self.ai else -1
        lst = []
        try:
            if not grid[self.coords[1]+change][self.coords[0]]:
                lst.append([self.coords[0], self.coords[1]+change])
        except IndexError: pass
        try:
            if ((self.coords[1] == 1 and self.ai) or (self.coords[1] == 6 and not self.ai)) and lst and (not grid[self.coords[1]+(change*2)][self.coords[0]]):
                lst.append([self.coords[0], self.coords[1]+change*2])
        except IndexError: pass
        for i in [[self.coords[1]+change, self.coords[0]+1], [self.coords[1]+change, self.coords[0]-1]]:
            try:
                if grid[i[0]][i[1]].ai != self.ai:
                    lst.append([i[1], i[0]])
            except (AttributeError, IndexError): pass
        return [i for i in lst if i[0] in range(8) and i[1] in range(8)]
    
    def kingPossible(self):
        lstOfPositions = [(0, 1), (-1, 1), (-1, 0), (-1, -1), (0, -1), (1, 0), (1, -1), (1, 1)]
        lstOfPositions = [[self.coords[0]+i[0], self.coords[1]+i[1]] for i in lstOfPositions]
        lstOfPositions = [i for i in lstOfPositions if i[0] in range(8) and i[1] in range(8)]
        return self._aiCheck(lstOfPositions)
    
    def queenPossible(self):
        return self.rookPossible() + self.bishopPossible()

    def bishopPossible(self):
        possible = []
        additions = [[1, 1], [1, -1], [-1, 1], [-1, -1]]
        for i in additions:
            changeable = list(self.coords[:])
            while True:
                changeable[0] += i[0]
                changeable[1] += i[1]
                if not (changeable[0] in range(8) and changeable[1] in range(8)): break
                try:
                    if grid[changeable[1]][changeable[0]].ai == self.ai: break
                except AttributeError: pass
                possible.append(changeable[:])
                if grid[changeable[1]][changeable[0]]: break
        return possible
    
    def knightPossible(self):
        lstOfPositions = [(1, 2), (-2, 1), (-1, 1), (-1, -2), (2, -2), (2, -1), (-2, 2), (2, 1), (-1, 2), (1, -1), (-2, -1), (1, -2)]
        lstOfPositions = [i for i in lstOfPositions if i[0]*-1 != i[1]]
        lstOfPositions = [[self.coords[0]+i[0], self.coords[1]+i[1]] for i in lstOfPositions]
        lstOfPositions = [i for i in lstOfPositions if i[0] in range(8) and i[1] in range(8)]
        return self._aiCheck(lstOfPositions)

    def rookPossible(self):
        possible = []
        additions = {i[:2] for i in list(permutations((1, -1, 0)))}
        additions = [i for i in additions if i[0]*-1 != i [1]]
        for i in additions:
            changeable = self.coords[:]
            while True:
                changeable[0] += i[0]
                changeable[1] += i[1]
                if not (changeable[0] in range(8) and changeable[1] in range(8)): break
                try:
                    if grid[changeable[1]][changeable[0]].ai == self.ai: break
                except AttributeError: pass
                possible.append(changeable[:])
                if grid[changeable[1]][changeable[0]]: break
        return possible
    
    def _aiCheck(self, lst):
        newLst = []
        for i in lst:
            try:
                if grid[i[1]][i[0]].ai != self.ai:
                    newLst.append(i)
            except AttributeError: newLst.append(i)
        return newLst

def lose():

    font = pygame.font.SysFont(None, 60)
    text = font.render('You Lose', True, (0, 0, 0))
    gameDisplay.blit(text,(board * 0.4, board * 0.42))
    pygame.display.update()


grid = [['' for i in range(8)] for j in range(4)]
grid.insert(0, [Piece('rook', (0, 0), True), Piece('knight', (1, 0), True), Piece('bishop', (2, 0), True), Piece('queen', (3, 0), True), Piece('king', (4, 0), True), Piece('bishop', (5, 0), True), Piece('knight', (6, 0), True), Piece('rook', (7, 0), True)])
grid.insert(1, [Piece('pawn', (i, 1), True) for i in range(8)])
grid.append([Piece('pawn', (i, 6), False) for i in range(8)])
grid.append([Piece('rook', (0, 7), False), Piece('knight', (1, 7), False), Piece('bishop', (2, 7), False), Piece('king', (3, 7), False), Piece('queen', (4, 7), False), Piece('bishop', (5, 7), False), Piece('knight', (6, 7), False), Piece('rook', (7, 7), False)])

def main():
    while True:
        global grid
        buttons()
        setUp()
        showPieces(grid)
        if checkMovement():
            break


        pygame.display.update()
        clock.tick(60)

    while True:
        buttons()
        setUp()
        showPieces(grid)
        lose()
        pygame.display.update()

if __name__ == '__main__':
    main()