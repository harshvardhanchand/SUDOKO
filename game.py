# main.py

import pygame
from solvers import SudokuSolver, backTrackingSolver  # Ensure these solvers are correctly implemented
import time

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 600, 600
GRID_SIZE = 9
CELL_SIZE = WIDTH // GRID_SIZE
FONT = pygame.font.SysFont('Arial', 40)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
LIGHT_BLUE = (173, 216, 230)
GRAY = (128, 128, 128)

# Screen setup
screen = pygame.display.set_mode((WIDTH, HEIGHT + 50))  # Extra space for messages
pygame.display.set_caption('Sudoku Solver')

# Example initial grid with some fixed cells (0 represents empty cells)
initial_grid = [
    [5, 3, 0, 0, 7, 0, 0, 0, 0],
    [6, 0, 0, 1, 9, 5, 0, 0, 0],
    [0, 9, 8, 0, 0, 0, 0, 6, 0],
    [8, 0, 0, 0, 6, 0, 0, 0, 3],
    [4, 0, 0, 8, 0, 3, 0, 0, 1],
    [7, 0, 0, 0, 2, 0, 0, 0, 6],
    [0, 6, 0, 0, 0, 0, 2, 8, 0],
    [0, 0, 0, 4, 1, 9, 0, 0, 5],
    [0, 0, 0, 0, 8, 0, 0, 7, 9]
]

# Initialize grids
grid = [row[:] for row in initial_grid]
fixed_grid = [row[:] for row in initial_grid]
error_grid = [[0 for _ in range(9)] for _ in range(9)]

# Message display
message = ""
message_color = BLACK

# Draw grid function
def draw_grid():
    # Fill background
    screen.fill(WHITE)

    # Highlight selected cell
    if selected_cell:
        row, col = selected_cell
        rect = pygame.Rect(col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE)
        pygame.draw.rect(screen, LIGHT_BLUE, rect)

    # Draw grid lines
    for x in range(0, WIDTH + 1, CELL_SIZE):
        line_width = 4 if x % (3 * CELL_SIZE) == 0 else 1
        pygame.draw.line(screen, BLACK, (x, 0), (x, HEIGHT), line_width)
    for y in range(0, HEIGHT + 1, CELL_SIZE):
        line_width = 4 if y % (3 * CELL_SIZE) == 0 else 1
        pygame.draw.line(screen, BLACK, (0, y), (WIDTH, y), line_width)

    # Draw numbers
    draw_numbers()

    # Draw message area
    pygame.draw.rect(screen, GRAY, (0, HEIGHT, WIDTH, 50))
    msg_text = FONT.render(message, True, message_color)
    screen.blit(msg_text, (10, HEIGHT + 10))

# Display numbers in grid
def draw_numbers():
    for i in range(GRID_SIZE):
        for j in range(GRID_SIZE):
            value = grid[i][j]
            if value != 0:
                if fixed_grid[i][j]:
                    color = BLACK
                elif error_grid[i][j]:
                    color = RED
                else:
                    color = BLUE
                text = FONT.render(str(value), True, color)
                text_rect = text.get_rect(center=(j * CELL_SIZE + CELL_SIZE//2, i * CELL_SIZE + CELL_SIZE//2))
                screen.blit(text, text_rect)

# Reset the grid to initial state
def reset_grid():
    global grid, error_grid, message, message_color
    grid = [row[:] for row in initial_grid]
    error_grid = [[0 for _ in range(9)] for _ in range(9)]
    message = "Grid Reset"
    message_color = BLACK

# Handle user input for a cell
def handle_input(row, col, value):
    global message, message_color
    if fixed_grid[row][col]:
        message = "Cannot change a fixed cell!"
        message_color = RED
        return
    if value in range(1, 10):
        grid[row][col] = value
        error_grid[row][col] = 0
        message = ""
    else:
        grid[row][col] = 0
        message = ""

# Check for errors in the grid (rows, columns, and subgrids)
def check_grid():
    global error_grid
    # Reset error grid
    error_grid = [[0 for _ in range(9)] for _ in range(9)]

    # Check rows for duplicates
    for row in range(GRID_SIZE):
        seen = {}
        for col in range(GRID_SIZE):
            val = grid[row][col]
            if val != 0:
                if val in seen:
                    error_grid[row][col] = 1
                    error_grid[row][seen[val]] = 1
                else:
                    seen[val] = col

    # Check columns for duplicates
    for col in range(GRID_SIZE):
        seen = {}
        for row in range(GRID_SIZE):
            val = grid[row][col]
            if val != 0:
                if val in seen:
                    error_grid[row][col] = 1
                    error_grid[seen[val]][col] = 1
                else:
                    seen[val] = row

    # Check subgrids for duplicates
    for box_row in range(3):
        for box_col in range(3):
            seen = {}
            for i in range(3):
                for j in range(3):
                    row = box_row * 3 + i
                    col = box_col * 3 + j
                    val = grid[row][col]
                    if val != 0:
                        if val in seen:
                            error_grid[row][col] = 1
                            error_grid[seen[val][0]][seen[val][1]] = 1
                        else:
                            seen[val] = (row, col)

# Solve the grid using the specified solver
def solve_puzzle(solver_type='backtracking'):
    global grid, message, message_color
    if solver_type == 'backtracking':
        solved_grid, elapsed_time = backTrackingSolver(grid)
        if solved_grid:
            grid = solved_grid
            message = f"Puzzle Solved! Time: {elapsed_time:.5f} seconds"
            message_color = BLUE
        else:
            message = "No solution exists!"
            message_color = RED
    else:
        solver = SudokuSolver()
        result = solver.solve(grid)
        if result["found_solutions"]:
            # Assuming we take the first solution
            grid = result["found_solutions"][0]
            message = f"Puzzle Solved! Time: {result['time_elapsed']}"
            message_color = BLUE
        else:
            message = "No solution exists!"
            message_color = RED

# Main game loop
running = True
selected_cell = None
solve_triggered = False
reset_triggered = False

while running:
    draw_grid()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Select cell with mouse click
        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = pygame.mouse.get_pos()
            if pos[1] < HEIGHT:  # Ignore clicks on message area
                selected_cell = (pos[1] // CELL_SIZE, pos[0] // CELL_SIZE)
                message = ""
            else:
                selected_cell = None

        # Handle key input
        if event.type == pygame.KEYDOWN:
            if selected_cell:
                row, col = selected_cell
                if event.key == pygame.K_1:
                    handle_input(row, col, 1)
                elif event.key == pygame.K_2:
                    handle_input(row, col, 2)
                elif event.key == pygame.K_3:
                    handle_input(row, col, 3)
                elif event.key == pygame.K_4:
                    handle_input(row, col, 4)
                elif event.key == pygame.K_5:
                    handle_input(row, col, 5)
                elif event.key == pygame.K_6:
                    handle_input(row, col, 6)
                elif event.key == pygame.K_7:
                    handle_input(row, col, 7)
                elif event.key == pygame.K_8:
                    handle_input(row, col, 8)
                elif event.key == pygame.K_9:
                    handle_input(row, col, 9)
                elif event.key in [pygame.K_BACKSPACE, pygame.K_DELETE, pygame.K_0]:
                    handle_input(row, col, 0)

        # Debounced key presses for solving and resetting
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r and not reset_triggered:
                reset_grid()
                reset_triggered = True
            if event.key == pygame.K_b and not solve_triggered:
                solve_puzzle('backtracking')
                solve_triggered = True
            if event.key == pygame.K_d and not solve_triggered:
                solve_puzzle('dlx')
                solve_triggered = True

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_r:
                reset_triggered = False
            if event.key in [pygame.K_b, pygame.K_d]:
                solve_triggered = False

    # Optional: Display real-time feedback or additional features here

    check_grid()
    pygame.display.update()

pygame.quit()

