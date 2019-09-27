import random
import numpy as np
import pygame
import sys

pygame.init()

SQUARESIZE = 28
WIDTH = 1
BORDER = SQUARESIZE * 2
DARK_GRAY = (60, 60, 60)
HIDDEN_GRAY = (100, 100, 100)
REVEALED_GRAY = (160, 160, 160)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
GRAY = (100, 100, 100)
PURPLE = (150, 0, 200)
MAROON = (130, 0, 0)
TURQUOISE = (0, 200,200)

colors = {0: REVEALED_GRAY,
          1: BLUE,
          2: GREEN,
          3: RED,
          4: PURPLE,
          5: MAROON,
          6: TURQUOISE,
          7: BLACK,
          8: GRAY}


def is_mine(x, y):
    if x < 0 or x >= rows or y < 0 or y >= columns:
        return False
    elif field[x][y] == "M":
        return True
    else:
        return False


def place_hints():
    for r in range(rows):
        for c in range(columns):
            if field[r][c] != "M":
                bombs = 0
                for i in range(3):
                    if is_mine(r + 1, c + i - 1):
                        bombs += 1
                    if is_mine(r - 1, c + i - 1):
                        bombs += 1
                if is_mine(r, c + 1):
                    bombs += 1
                if is_mine(r, c - 1):
                    bombs += 1
                field[r][c] = bombs


def draw_board():
    pygame.draw.rect(game_screen, HIDDEN_GRAY, (BORDER,BORDER, -2 * BORDER + game_screen_width, -2 * BORDER + game_screen_height))
    for r in range(rows):
        for c in range(columns):
            pygame.draw.rect(game_screen, BLACK, (c * SQUARESIZE + BORDER, r * SQUARESIZE + BORDER, SQUARESIZE, SQUARESIZE), WIDTH)
    pygame.display.update()


def get_cell(x, y):
    if BORDER < x < columns * SQUARESIZE + BORDER and BORDER < y < rows * SQUARESIZE + BORDER:
        return int((y - BORDER) / SQUARESIZE), int((x - BORDER) / SQUARESIZE)
    else:
        return -1, -1


def message(size, word, color, bold=True):
    # sets font with hard coded font type and passed in size 
    set_font = pygame.font.SysFont("Courier New", size, bold)

    # creates text block with passed in message and color
    set_color = set_font.render(word, True, color)

    # gets dimension of text block in form [left,top,game_screen_width,game_screen_height]
    get_dimension = set_color.get_rect()

    return set_color, get_dimension[2], get_dimension[3]


def flag_cell(cellx, celly):
    cell_value = display_field[cellx][celly]
    if cell_value == "H":
        pygame.draw.rect(game_screen, DARK_GRAY, (celly * SQUARESIZE + BORDER + WIDTH, cellx * SQUARESIZE + BORDER + WIDTH, -2 * WIDTH + SQUARESIZE, -2 * WIDTH + SQUARESIZE))
        pygame.draw.polygon(game_screen, RED, ((celly * SQUARESIZE + BORDER + WIDTH + (SQUARESIZE / 5), cellx * SQUARESIZE + BORDER + WIDTH + (SQUARESIZE / 5)), (celly * SQUARESIZE + BORDER + WIDTH + (SQUARESIZE / 5), cellx * SQUARESIZE + BORDER + (4 * SQUARESIZE / 5)), (celly * SQUARESIZE + BORDER + (4 * SQUARESIZE / 5), cellx * SQUARESIZE + BORDER + (WIDTH / 2) + (SQUARESIZE / 2))))

        display_field[cellx][celly] = "F"
    elif cell_value == "F":
        pygame.draw.rect(game_screen, HIDDEN_GRAY, (celly * SQUARESIZE + BORDER + WIDTH, cellx * SQUARESIZE + BORDER + WIDTH, -2 * WIDTH + SQUARESIZE, -2 * WIDTH + SQUARESIZE))
        display_field[cellx][celly] = "H"
    pygame.display.update()


def reveal_cell(cellx, celly):
    cell_value = field[cellx][celly]
    pygame.draw.rect(game_screen, REVEALED_GRAY, (celly * SQUARESIZE + BORDER + WIDTH, cellx * SQUARESIZE + BORDER + WIDTH, -2 * WIDTH + SQUARESIZE, -2 * WIDTH + SQUARESIZE))
    text, x1, y1 = message(22, cell_value, colors[int(cell_value)])
    x = (SQUARESIZE - x1) / 2
    y = (SQUARESIZE - y1) / 2
    game_screen.blit(text, (celly * SQUARESIZE + BORDER + x, cellx * SQUARESIZE + BORDER + y, SQUARESIZE, SQUARESIZE))
    display_field[cellx][celly] = ""  
    pygame.display.update()      


def check_win():
    opened_cells = 0
    hidden_cells = 0
    for r in range(rows):
        hidden_cells += np.count_nonzero(display_field[r] == "H")
        if hidden_cells > mines:
            return False
        opened_cells += np.count_nonzero(display_field[r] == "")
    if opened_cells == rows * columns - mines:
        return True
    else:
        return False


def check_flags(x, y, required_flags):
    found_flags = 0
    for i in range(3):
        for j in range(3):
            if 0 <= x + i - 1 < rows and 0 <= y + j - 1 < columns:
                if display_field[x + i - 1][y + j - 1] == "F": # and field[x + i - 1][y + j - 1] == "M":
                    found_flags += 1
    if found_flags == required_flags:
        return True
    return False


def check_hit_mine(x, y):
    hit_mine = False
    cell_value = field[x][y]
    if cell_value != "M" and display_field[x][y] != "F":
        if cell_value != "0":
            if display_field[x][y] == "H":
                reveal_cell(x, y)
            elif check_flags(x, y, int(cell_value)):
                for i in range(3):
                    for j in range(3):
                        if 0 <= x + i - 1 < rows and 0 <= y + j - 1 < columns and field[x + i - 1][y + j - 1] != "M": 
                            if display_field[x + i - 1][y + j - 1] == "F":
                                return True
                            else:
                                reveal_cell(x + i - 1, y + j - 1)
            else:
                reveal_cell(x, y)
        else:
            for i in range(3):
                for j in range(3):
                    if 0 <= x + i - 1 < rows and 0 <= y + j - 1 < columns:
                        reveal_cell(x + i - 1, y + j - 1)
        
    elif display_field[x][y] != "F":
        hit_mine = True
    return hit_mine


def reveal_mines():
    for r in range(rows):
        for c in range(columns):
            if field[r][c] == "M" or display_field[r][c] == "F":
                if display_field[r][c] == "F":
                    pygame.draw.lines(game_screen, BLACK, True, ((c * SQUARESIZE + BORDER + WIDTH, r * SQUARESIZE + BORDER + WIDTH), ((c * SQUARESIZE + BORDER + WIDTH -2 * WIDTH + SQUARESIZE, r * SQUARESIZE + BORDER + WIDTH -2 * WIDTH + SQUARESIZE))), WIDTH * 4)
                    pygame.draw.lines(game_screen, BLACK, True, ((c * SQUARESIZE + BORDER + WIDTH, r * SQUARESIZE + BORDER + WIDTH -2 * WIDTH + SQUARESIZE), ((c * SQUARESIZE + BORDER + WIDTH -2 * WIDTH + SQUARESIZE, r * SQUARESIZE + BORDER + WIDTH))), WIDTH * 4)

                else:
                    pygame.draw.rect(game_screen, RED, (c * SQUARESIZE + BORDER + WIDTH, r * SQUARESIZE + BORDER + WIDTH, -2 * WIDTH + SQUARESIZE, -2 * WIDTH + SQUARESIZE))
    
    pygame.display.update()


def start_menu():
    start_screen_side = 9 * SQUARESIZE + (2 * BORDER)
    start_screen = create_screen(start_screen_side, start_screen_side)
    pygame.draw.rect(start_screen, DARK_GRAY, (BORDER, BORDER, SQUARESIZE * 9, SQUARESIZE * 9))
    
    novice = pygame.draw.rect(start_screen, BLACK, (SQUARESIZE + BORDER, SQUARESIZE * 3 + BORDER, SQUARESIZE * 7, SQUARESIZE))
    intermediate = pygame.draw.rect(start_screen, BLACK, (SQUARESIZE + BORDER, SQUARESIZE * 5 + BORDER, SQUARESIZE * 7, SQUARESIZE))
    expert = pygame.draw.rect(start_screen, BLACK, (SQUARESIZE + BORDER, SQUARESIZE * 7 + BORDER, SQUARESIZE * 7, SQUARESIZE))
    
    text, x2, y2 = message(24, "CHOOSE DIFFICULTY", RED)
    x1 = (SQUARESIZE * 7 - x2) / 2
    y1 = (SQUARESIZE - y2) / 2
    start_screen.blit(text, (SQUARESIZE + BORDER + x1, SQUARESIZE + BORDER + y1, SQUARESIZE * 7, SQUARESIZE))
    text, x2, y2 = message(24, "NOVICE", RED)
    x1 = (SQUARESIZE * 7 - x2) / 2
    y1 = (SQUARESIZE - y2) / 2
    start_screen.blit(text, (SQUARESIZE + BORDER + x1, SQUARESIZE * 3 + BORDER + y1, SQUARESIZE * 7, SQUARESIZE))
    text, x2, y2 = message(24, "INTERMEDIATE", RED)
    x1 = (SQUARESIZE * 7 - x2) / 2
    y1 = (SQUARESIZE - y2) / 2
    start_screen.blit(text, (SQUARESIZE + BORDER + x1, SQUARESIZE * 5 + BORDER + y1, SQUARESIZE * 7, SQUARESIZE))
    text, x2, y2 = message(24, "EXPERT", RED)
    x1 = (SQUARESIZE * 7 - x2) / 2
    y1 = (SQUARESIZE - y2) / 2
    start_screen.blit(text, (SQUARESIZE + BORDER + x1, SQUARESIZE * 7 + BORDER + y1, SQUARESIZE * 7, SQUARESIZE))
    
    pygame.display.update()

    difficulty = 0
    while difficulty == 0:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                difficulty_choice = event.pos
                if novice.collidepoint(difficulty_choice):
                    difficulty = 1
                if intermediate.collidepoint(difficulty_choice):
                    difficulty = 2
                if expert.collidepoint(difficulty_choice):
                    difficulty = 3
    if difficulty == 1:
        return 9, 9, 10
    elif difficulty == 2:
        return 16, 16, 40
    else:
        return 16, 30, 99


def create_screen(width, height):
    temp_screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("Minesweeper")
    return temp_screen


def first_click():
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                pixelx = event.pos[0]
                pixely = event.pos[1]
                firstx, firsty = get_cell(pixelx, pixely)
                if firstx != -1:
                    return firstx, firsty


def end_game():
    text, x2, y2 = message(28, "PLAY AGAIN?", WHITE)
    x1 = (game_screen_width - x2) / 2
    y1 = (BORDER - y2) / 2
    game_screen.blit(text, (x1, SQUARESIZE * rows + BORDER + y1, game_screen_width, BORDER))

    text, x2, y2 = message(28, "YES", BLACK)
    x1 = (game_screen_width / 3 - x2) / 2
    y1 = (BORDER - y2) / 2

    yes_block = pygame.draw.rect(game_screen, GREEN, (x1, SQUARESIZE * rows + BORDER + y1, x2, -2 * y1 + BORDER))
    no_block = pygame.draw.rect(game_screen, RED, (2 / 3 * game_screen_width + x1, SQUARESIZE * rows + BORDER + y1, x2, -2 * y1 + BORDER))

    game_screen.blit(text, (x1, SQUARESIZE * rows + BORDER + y1, game_screen_width, BORDER))

    text, x2, y2 = message(28, "NO", BLACK)
    x1 = (game_screen_width / 3 - x2) / 2
    y1 = (BORDER - y2) / 2

    game_screen.blit(text, (2 / 3 * game_screen_width + x1, SQUARESIZE * rows + BORDER + y1, game_screen_width, BORDER))

    pygame.display.update()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                choice = event.pos
                if yes_block.collidepoint(choice):
                    return True
                if no_block.collidepoint(choice):
                    return False


def set_mines(x, y):
    skip_spaces = []
    cell_num = x * columns + y + 1
    for i in range(3):
        for j in range(3):
            skip_spaces.append(cell_num + ((i - 1) * columns) + j - 1)
    forbidden = [i for i in skip_spaces if i > 0]

    mine_locations = []
    while len(mine_locations) < mines:
        m = random.randint(1, rows * columns - len(forbidden))
        if m not in mine_locations and m not in forbidden:
            mine_locations.append(m)

    mine_locations = sorted(mine_locations)
    space = 1
    mines_placed = 0
    for r in range(rows):
        for c in range(columns):
            if space == mine_locations[mines_placed]:
                field[r][c] = "M"
                mines_placed += 1
            space += 1
            if mines_placed >= mines:
                break
        if mines_placed >= mines:
            break


play_again = True
while play_again:
    game = True
    rows, columns, mines = start_menu()

    game_screen_width = columns * SQUARESIZE + (2 * BORDER)
    game_screen_height = rows * SQUARESIZE + (2 * BORDER)
    game_screen = create_screen(game_screen_width, game_screen_height)

    field = np.full((rows, columns), "")
    display_field = np.full((rows, columns), "H")

    draw_board()
    startx, starty = first_click()

    set_mines(startx, starty)
    place_hints()
    check_hit_mine(startx, starty)
    
    start_time = pygame.time.get_ticks()

    clock = pygame.time.Clock()

    clock.tick(60)

    while game:
        pygame.draw.rect(game_screen, BLACK, (0, 0, game_screen_width, BORDER))
        minutes = int((pygame.time.get_ticks() - start_time) / 1000 / 60)
        seconds = round(round((pygame.time.get_ticks() - start_time) / 1000, 1) % 60, 1)
        display_clock = "{}:{}".format(minutes, seconds)
        if minutes == 0:
            display_clock = "{}".format(seconds)
        elif seconds < 10:
            display_clock = "{}:0{}".format(minutes, seconds)
        text, x2, y2 = message(32, display_clock, RED)
        x1 = (game_screen_width - x2) / 2
        y1 = (BORDER - y2) / 2
        
        game_screen.blit(text, (x1, y1, game_screen_width, BORDER))
        pygame.display.update()
        for event in pygame.event.get():
            
            if event.type == pygame.QUIT:
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                posx = event.pos[0]
                posy = event.pos[1]
                selectedx, selectedy = get_cell(posx, posy)
                if selectedx != -1:
                    if event.button == 1:
                        if not check_hit_mine(selectedx, selectedy):
                            if check_win():
                                game = False
                        else:
                            game = False
                            reveal_mines()
                    elif event.button == 3:
                        flag_cell(selectedx, selectedy)
    play_again = end_game()
                    