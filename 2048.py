import random

def have_space():
    for i in range(4):
        for j in range(4):
            if game_area[i][j] == 0:
                return True
            
def addtile(r, c):
    if have_space():
        while game_area[r][c] != 0:
            c, r = random.randint(0, 3), random.randint(0, 3)
        if random.randint(1, 10) == 1:
            tilevalue = 4
        else:
            tilevalue = 2
        game_area[r][c] = tilevalue

def get_state():
    if have_space():
        return True
    for i in range(3):
        for j in range(3):
            if game_area[i][j] == game_area[i][j + 1] or game_area[i][j] == game_area[i + 1][j]:
                return True
            elif game_area[3][j] == game_area[3][j + 1] or game_area[i][3] == game_area[i + 1][3]:
                return True
    return False

def rotated_right(matrix: list[list]):
    rmatrix = [[], [], [], []]
    for i in range(4):
        for j in range(4):
            rmatrix[i].append(matrix[-1 - j][i])
    return rmatrix

def rotated_left(matrix: list[list]):
    rmatrix = [[], [], [], []]
    for i in range(4):
        for j in range(4):
            rmatrix[i].append(matrix[j][-1 - i])
    return rmatrix

def moved_left(matrix: list[list]):
    global score
    for i in range(4):
        l = 0
        r = 1
        while r != 4:
            if matrix[i][l] != 0:
                l += 1
                r += 1
            elif matrix[i][r] == 0:
                r += 1
            else:
                matrix[i][l] = matrix[i][r]
                matrix[i][r] = 0
                l += 1
                r += 1
        for j in range(3):
            if matrix[i][j] == matrix[i][j + 1] and matrix[i][j] != 0:
                matrix[i][j] *= 2
                score += matrix[i][j]
                matrix[i][j + 1] = 0
    for i in range(4):
        l = 0
        r = 1
        while r != 4:
            if matrix[i][l] != 0:
                l += 1
                r += 1
            elif matrix[i][r] == 0:
                r += 1
            else:
                matrix[i][l] = matrix[i][r]
                matrix[i][r] = 0
                l += 1
                r += 1
    return matrix

def moved_right(matrix: list[list]):
    return rotated_left(rotated_left(moved_left(rotated_right(rotated_right(matrix)))))

def moved_down(matrix: list[list]):
    return rotated_left(moved_left(rotated_right(matrix)))

def moved_up(matrix: list[list]):
    return rotated_right(moved_left(rotated_left(matrix)))

score = 0

game_area = [[0, 0, 0, 0],
             [0, 0, 0, 0],
             [0, 0, 0, 0],
             [0, 0, 0, 0]]

c, r = random.randint(0, 3), random.randint(0, 3)
addtile(r, c)
addtile(r, c)
while True:
    if get_state():
        for i in range(4):
            output_string = ''
            for j in range(4):
                output_string += '['+ str(game_area[i][j]) + '] '
            print(output_string)
        print(score)
        inp = input()
        match inp:
            case 'w':
                game_area = moved_up(game_area)
            case 'a':
                game_area = moved_left(game_area)
            case 's':
                game_area = moved_down(game_area)
            case 'd':
                game_area = moved_right(game_area)
            case 'q':
                break
            case _:
                pass
        addtile(r, c)
    else:
        print('Game Over')
        break