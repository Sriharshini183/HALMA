neighbor = [(i, j) for i in [-1, 0, 1] for j in [-1, 0, 1] if i or j]

class Board:
    def __init__(self):
        self.mode = None
        self.player = None
        self.rem_time = None
        self.state = []
        self.proponent = None
        self.opponent = None

class Player:
    def __init__(self, name):
        if name == 'BLACK':
            self.name = 'BLACK'
            self.ID = 'B'
            # self.oppID = 'W'
            self.mycamp = [(0,0),(0,1),(0,2),(0,3),(0,4),(1,0),(1,1),(1,2),(1,3),(1,4),(2,0),(2,1),(2,2),(2,3),(3,0),\
                           (3,1),(3,2),(4,0),(4,1)]
            self.oppcamp = [(11,14),(11,15),(12,13),(12,14),(12,15),(13,12),(13,13),(13,14),(13,15), \
                            (14,11),(14,12),(14,13),(14,14),(14,15),(15,11),(15,12),(15,13),(15,14),(15,15)]
            self.mycorner = (0, 0)
            self.mygoal = (15, 15)
        elif name == 'WHITE':
            self.name = 'WHITE'
            self.ID = 'W'
            # self.oppID = 'B'
            self.mycamp = [(11,14),(11,15),(12,13),(12,14),(12,15),(13,12),(13,13),(13,14),(13,15), \
                            (14,11),(14,12),(14,13),(14,14),(14,15),(15,11),(15,12),(15,13),(15,14),(15,15)]
            self.oppcamp = [(0,0),(0,1),(0,2),(0,3),(0,4),(1,0),(1,1),(1,2),(1,3),(1,4),(2,0),(2,1),(2,2),(2,3),(3,0),\
                           (3,1),(3,2),(4,0),(4,1)]
            self.mycorner = (15, 15)
            self.mygoal = (0, 0)
class Move:
    def __init__(self):
        self.type = None
        self.from_x = None
        self.from_y = None
        self.to_x = None
        self.to_y = None
    def __str__(self):
        return self.type + ' ' + str(self.from_x) + ',' + str(self.from_y) + ' ' + str(self.to_x) + ',' + str(self.to_y)


infinity = float('inf')

def processed(data_lines):
    return [line.strip() for line in data_lines]


def store(data):
    input = Board()
    input.mode = str(data[0])
    input.player = str(data[1])
    input.rem_time = float(data[2])

    grid = []
    for row in range(16):
        grid.append([(x) for x in data[3 + row]])
    input.state = list(map(list, zip(*grid)))

    if input.player == 'BLACK':
        input.proponent = Player('BLACK')
        input.opponent = Player('WHITE')
    elif input.player == 'WHITE':
        input.proponent = Player('WHITE')
        input.opponent = Player('BLACK')
    count = 0
    for (x,y) in input.proponent.oppcamp:
            if input.state[x][y] == input.proponent.ID:
                count += 1
    print(count)
    if count > 14:
        input.heuristic = 2
    else:
        input.heuristic = 1

    return input

def roll(board,x,y):
    rolls = []
    for (dx,dy) in neighbor:
        tx,ty = x + dx, y + dy
        if 0 <= tx < 16 and 0 <= ty < 16 and board.state[tx][ty] == '.':
            t = board.state[tx][ty]
            new = Move()
            new.type = 'E'
            new.from_x = x
            new.from_y = y
            new.to_x = tx
            new.to_y = ty
            rolls.append([new])
    return rolls

def hops(board, x, y):
    queue = []
    jump = []
    explored = []
    for (dx, dy) in neighbor:
        mx, my = x + dx, y + dy
        tx, ty = mx + dx, my + dy
        if 0 <= tx < 16 and 0 <= ty < 16:
            if board.state[mx][my] != '.' and board.state[tx][ty] == '.':
                start = Move()
                start.type = 'J'
                start.from_x = x
                start.from_y = y
                start.to_x = tx
                start.to_y = ty
                queue.append([start])
    explored.append((x,y))
    while len(queue) > 0:
        path = queue.pop(0)
        current = path[-1]
        jump.append(path)
        fx = current.to_x
        fy = current.to_y
        for (dx, dy) in neighbor:
            mx, my = fx + dx, fy + dy
            tx, ty = mx + dx, my + dy
            if 0 <= tx < 16 and 0 <= ty < 16 and (tx,ty) not in explored:
                if board.state[mx][my] != '.' and board.state[tx][ty] == '.':
                    new = Move()
                    new.type = 'J'
                    new.from_x = fx
                    new.from_y = fy
                    new.to_x = tx
                    new.to_y = ty
                    queue.append(path + [new])
        explored.append((fx, fy))
    return jump

def listOfMoves(board, player):
    moves = []
    count = 19
    for x in range(16):
        for y in range(16):
            if count <= 0:
                return moves
            else:
                if board.state[x][y] == player.ID:
                    moves.extend(hops(board,x,y))
                    moves.extend(roll(board,x,y))
                    count -= 1
    return moves

def euclidean(x, y, corner):
    dx = x - corner[0]
    dy = y - corner[1]
    distance = (dx * dx + dy * dy)
    return distance


def moving_away(fx,fy,tx,ty,mycorner):
    dx1 = abs(fx - mycorner[0])
    dx2 = abs(tx - mycorner[1])
    dy1 = abs(fy - mycorner[0])
    dy2 = abs(ty - mycorner[1])
    return not(dx1 > dx2 or dy1 > dy2)

def legal(board,turn = None):
    if turn == 0:
        player = board.proponent
    else:
        player = board.opponent
    in_out_dict = {}
    not_going_out_dict = {}
    out_camp_dict = {}
    for move in listOfMoves(board, player):
        fx = move[0].from_x
        fy = move[0].from_y
        tx = move[-1].to_x
        ty = move[-1].to_y
        currentgoald = euclidean(tx,ty,player.mygoal)
        prevd = euclidean(fx, fy, player.mycorner)
        currentd = euclidean(tx, ty, player.mycorner)
        if (fx,fy) in player.mycamp:
            if (tx,ty) not in player.mycamp:
                in_out_dict.update({tuple(move) : currentgoald})
            else:
                if prevd < currentd and moving_away(fx,fy,tx,ty, player.mycorner):
                    not_going_out_dict.update({tuple(move) : currentgoald})
        elif ((tx,ty) not in player.mycamp) and  not((fx,fy) in player.oppcamp and (tx,ty) not in player.oppcamp):
            out_camp_dict.update({tuple(move): currentgoald})

    if in_out_dict:
        sortedq = sorted(in_out_dict.items(), key=lambda item: item[1], reverse = True)
        legal_queue = []
        for j in sortedq:
            legal_queue.append(list(j[0]))
        return legal_queue
    elif not_going_out_dict:
        sortedq = sorted(not_going_out_dict.items(), key=lambda item: item[1], reverse = True)
        legal_queue = []
        for j in sortedq:
            legal_queue.append(list(j[0]))
        return legal_queue
    else:
        sortedq = sorted(out_camp_dict.items(), key=lambda item: item[1], reverse = True)
        legal_queue = []
        for j in sortedq:
            legal_queue.append(list(j[0]))
        return legal_queue

def checkifWin(board, player):
    wait = False
    for (x,y) in player.oppcamp:
        if board.state[x][y] == '.':
            return False
        elif board.state[x][y] == player.ID:
            wait = True
    if wait == True:
        return True

def terminal_state(board):
    if checkifWin(board, board.proponent):
        return True, 10000
    elif checkifWin(board, board.opponent):
        return True, -10000
    else:
        return False, 0

def distancefeature(board):
    mygoal = board.proponent.mygoal
    mydist = 0
    count = 19
    for x in range(16):
        for y in range(16):
            if count < 0:
                return -1 * mydist
            elif board.state[x][y] == board.proponent.ID:
                mydist += euclidean(x, y, mygoal)
                count -= 1
    return -1 * mydist

def misplaced(board):
    empty_goal = []
    for (x,y) in board.proponent.oppcamp:
        if board.state[x][y] == ".":
            empty_goal.append((x,y))
    out_camp = []
    for x in range(16):
        for y in range(16):
            if board.state[x][y] == board.proponent.ID:
                out_camp.append((x,y))
    ans = 0
    for (x1,y1) in empty_goal:
        for p in out_camp:
            ans = ans + euclidean(x1,y1,p)
    return -1 * ans

def eval(board):
    if board.heuristic == 1:
        f1 = distancefeature(board)
    else:
        f1 = misplaced(board)
    return f1

def maxValue(game_board, alpha, beta, turn, depth):
    truth, val = terminal_state(game_board)
    if truth:
        return val
    elif depth == 0:
        return eval(game_board)
    value = - infinity
    for node in legal(game_board,turn):
        fx = node[0].from_x
        fy = node[0].from_y
        tx = node[-1].to_x
        ty = node[-1].to_y
        game_board.state[fx][fy], game_board.state[tx][ty] = game_board.state[tx][ty], game_board.state[fx][fy]
        turn = int(not turn)
        value = max(value, minValue(game_board, alpha, beta, turn, depth - 1))
        if value >= beta:
            return value
        alpha = max(alpha, value)
        game_board.state[tx][ty], game_board.state[fx][fy] = game_board.state[fx][fy], game_board.state[tx][ty]
    return value

def minValue(game_board, alpha, beta, turn, depth):
    truth, val = terminal_state(game_board)
    if truth:
        return val
    elif depth == 0:
        return eval(game_board)
    value = infinity
    for node in legal(game_board, turn):
        fx = node[0].from_x
        fy = node[0].from_y
        tx = node[-1].to_x
        ty = node[-1].to_y
        game_board.state[fx][fy], game_board.state[tx][ty] = game_board.state[tx][ty], game_board.state[fx][fy]
        turn = int(not turn)
        value = min(value, maxValue(game_board, alpha, beta, turn, depth - 1))
        if value <= alpha:
            return alpha
        beta = min(beta, value)
        game_board.state[tx][ty], game_board.state[fx][fy] = game_board.state[fx][fy], game_board.state[tx][ty]
    return value

def alpha_beta(board, depth):
    game_board = board
    alpha = - infinity
    beta = infinity
    best_value = - infinity
    best_move = None
    turn = 0
    for node in legal(game_board, turn):
        fx = node[0].from_x
        fy = node[0].from_y
        tx = node[-1].to_x
        ty = node[-1].to_y
        game_board.state[fx][fy], game_board.state[tx][ty] = game_board.state[tx][ty], game_board.state[fx][fy]
        turn = int(not turn)
        value = minValue(game_board, alpha, beta, turn, depth - 1)
        if value > best_value:
            best_move = node
            best_value = value
        game_board.state[tx][ty], game_board.state[fx][fy] = game_board.state[fx][fy], game_board.state[tx][ty]
    return best_move

def game():
    with open("input.txt") as file:
        data = file.readlines()
        input = store(processed(data))
    best_move = alpha_beta(input, 1)

    opfile = open('output.txt', 'w')
    result = ''
    for i in best_move:
        result += i.type + ' ' + str(i.from_x) + ',' + str(i.from_y) + ' ' + str(i.to_x) + ',' + str(i.to_y) + '\n'
    opfile.write(result)

if __name__ == '__main__':
        game()