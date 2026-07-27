import curses
import random
import time

WIDTH, HEIGHT, MINES = 9, 9, 10

def create_board():
    board = [[0 for _ in range(WIDTH)] for _ in range(HEIGHT)]
    mines_placed = 0
    while mines_placed < MINES:
        x, y = random.randint(0, WIDTH - 1), random.randint(0, HEIGHT - 1)
        if board[y][x] != -1:
            board[y][x] = -1
            mines_placed += 1
    for y in range(HEIGHT):
        for x in range(WIDTH):
            if board[y][x] == -1:
                continue
            count = 0
            for dy in [-1, 0, 1]:
                for dx in [-1, 0, 1]:
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < WIDTH and 0 <= ny < HEIGHT and board[ny][nx] == -1:
                        count += 1
            board[y][x] = count
    return board

def main(stdscr):
    curses.curs_set(0)
    stdscr.clear()
    curses.start_color()
    curses.init_pair(1, curses.COLOR_BLUE, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(4, curses.COLOR_CYAN, curses.COLOR_BLACK)
    curses.init_pair(5, curses.COLOR_WHITE, curses.COLOR_BLACK)
    
    stdscr.timeout(100)
    
    def reset_game():
        nonlocal board, revealed, flags, cx, cy, game_over, won, start_time, total_time
        board = create_board()
        revealed = [[False for _ in range(WIDTH)] for _ in range(HEIGHT)]
        flags = [[False for _ in range(WIDTH)] for _ in range(HEIGHT)]
        cx, cy = 0, 0
        game_over = False
        won = False
        start_time = time.time()
        total_time = 0

    board = revealed = flags = None
    cx = cy = 0
    game_over = won = False
    start_time = total_time = 0
    reset_game()

    while True:
        stdscr.erase()
        term_height, term_width = stdscr.getmaxyx()
        
        min_w = max(WIDTH * 2 + 4, 75)
        min_h = HEIGHT + 9
        if term_height < min_h or term_width < min_w:
            stdscr.addstr(0, 0, f"Пожалуйста, сделайте окно терминала больше (мин: {min_w}x{min_h})")
            stdscr.refresh()
            key = stdscr.getch()
            if key in [ord('q'), ord('Q')]:
                break
            continue

        
        if not game_over and not won:
            total_time = int(time.time() - start_time)

        start_y = (term_height - HEIGHT) // 2
        start_x = (term_width - (WIDTH * 2)) // 2

        title = "Termsweeper"
        controls = "Arrows: move | Space: open a check | F: flag | R: restart | Q: exit"
        stdscr.addstr(start_y - 4, (term_width - len(title)) // 2, title, curses.A_BOLD)
        stdscr.addstr(start_y - 3, (term_width - len(controls)) // 2, controls, curses.color_pair(4))
        
        # Рамка
        stdscr.addstr(start_y - 1, start_x - 2, "┌" + "─" * (WIDTH * 2 + 1) + "┐", curses.color_pair(5))
        for i in range(HEIGHT):
            stdscr.addstr(start_y + i, start_x - 2, "│", curses.color_pair(5))
            stdscr.addstr(start_y + i, start_x + (WIDTH * 2), "│", curses.color_pair(5))
        stdscr.addstr(start_y + HEIGHT, start_x - 2, "└" + "─" * (WIDTH * 2 + 1) + "┘", curses.color_pair(5))

        # Отрендерить поле
        for y in range(HEIGHT):
            for x in range(WIDTH):
                char = "."
                attr = curses.A_NORMAL
                if revealed[y][x]:
                    if board[y][x] == -1:
                        char = "*"
                        attr = curses.color_pair(3) | curses.A_BOLD
                    elif board[y][x] == 0:
                        char = " "
                    else:
                        char = str(board[y][x])
                        attr = curses.color_pair(min(board[y][x], 4)) | curses.A_BOLD
                elif flags[y][x]:
                    char = "F"
                    attr = curses.color_pair(3) | curses.A_BOLD
                if x == cx and y == cy:
                    attr |= curses.A_REVERSE
                stdscr.addstr(start_y + y, start_x + (x * 2), char, attr)

        # Вывод таймера под полем
        timer_str = f"Time: {total_time} sec."
        stdscr.addstr(start_y + HEIGHT + 1, (term_width - len(timer_str)) // 2, timer_str, curses.color_pair(1))

        if game_over:
            msg = "Game over! [R] Restart | [Q] Quit"
            stdscr.addstr(start_y + HEIGHT + 3, (term_width - len(msg)) // 2, msg, curses.color_pair(3) | curses.A_BOLD)
        elif won:
            msg = "Good work! [R] Restart | [Q] Quit"
            stdscr.addstr(start_y + HEIGHT + 3, (term_width - len(msg)) // 2, msg, curses.color_pair(2) | curses.A_BOLD)

        stdscr.refresh()
        key = stdscr.getch()

        
        if key == -1:
            continue

        if key in [ord('q'), ord('Q')]:
            break
        if key in [ord('r'), ord('R')]:
            reset_game()
            continue
        if game_over or won:
            continue

        if key == curses.KEY_UP and cy > 0: cy -= 1
        elif key == curses.KEY_DOWN and cy < HEIGHT - 1: cy += 1
        elif key == curses.KEY_LEFT and cx > 0: cx -= 1
        elif key == curses.KEY_RIGHT and cx < WIDTH - 1: cx += 1
        elif key == ord(' '):
            if not flags[cy][cx]:
                revealed[cy][cx] = True
                if board[cy][cx] == -1:
                    game_over = True
                    for r_y in range(HEIGHT):
                        for r_x in range(WIDTH):
                            if board[r_y][r_x] == -1: revealed[r_y][r_x] = True
                elif board[cy][cx] == 0:
                    queue = [(cx, cy)]
                    while queue:
                        curr_x, curr_y = queue.pop(0)
                        for dy in [-1, 0, 1]:
                            for dx in [-1, 0, 1]:
                                nx, ny = curr_x + dx, curr_y + dy
                                if 0 <= nx < WIDTH and 0 <= ny < HEIGHT and not revealed[ny][nx] and not flags[ny][nx]:
                                    revealed[ny][nx] = True
                                    if board[ny][nx] == 0:
                                        queue.append((nx, ny))
        elif key in [ord('f'), ord('F')]:
            if not revealed[cy][cx]:
                flags[cy][cx] = not flags[cy][cx]
        
        unrevealed_safe = sum(1 for y in range(HEIGHT) for x in range(WIDTH) if not revealed[y][x] and board[y][x] != -1)
        if unrevealed_safe == 0:
            won = True


def run():
	curses.wrapper(main)

if __name__ == "__main__":
	run()
