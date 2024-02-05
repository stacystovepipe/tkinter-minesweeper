import platform, random, os
from datetime import datetime
from tkinter import *
from tkinter import messagebox

root = Tk()
root.title("Minesweeper")

GRID_ROW_SIZE = 9
GRID_COLUMN_SIZE = 9
NUMBER_OF_MINES = 1
NUMBER_OF_NON_MINES = GRID_ROW_SIZE * GRID_COLUMN_SIZE - NUMBER_OF_MINES

DIRECTIONS = ((-1, 0), (0, -1), (1, 0), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1))

STATE_DEFAULT = 0
STATE_CLICKED = 1
STATE_FLAGGED = 2

BTN_CLICK = "<Button-1>"
BTN_FLAG = "<Button-2>" if platform.system() == 'Darwin' else "<Button-3>"

valid_index = lambda row, column: 0 <= row <= GRID_ROW_SIZE - 1 and 0 <= column <= GRID_COLUMN_SIZE - 1
print()
# Load all images into a dictionary.
images = {i: None for i in range(1, 9)}
images.update({'Empty': None, 'Exploded': None, 'Flag': None, 'FlagWrong': None, 'Mine': None, 'Unknown': None, 'Exploded': None, 'Smiley': None})
for i in images:
    images[i] = PhotoImage(file = str(os.path.dirname(os.path.realpath(__file__))) + rf'\assets\Tile{i}.png')

"""
This class is responsible for storing all the variables and functions required to run game.
"""
class Minesweeper():
    def __init__(self):
        self.board, self.mines_list = self.board_generation()
    
        self.starting_time = None
        self.timer = StringVar(value = "00:00:00")

        self.mines_left = NUMBER_OF_MINES
        self.score = StringVar(value = 'Mines: ' + str(self.mines_left))

        self.clicked_count = 0

        self.update_timer()

    """
    Generates the board, creating Tile objects for each tile on the board.
    """
    def board_generation(self):
        # tiles = [0, 1, 2, 3, 4, 5, 6, 7, 8, 'Mine']

        board = [[0 for i in range(GRID_COLUMN_SIZE)] for i in range(GRID_ROW_SIZE)]
        mines_list = []

        while len(mines_list) != NUMBER_OF_MINES:
            random_row_position = random.randint(0, GRID_ROW_SIZE - 1)
            random_column_position = random.randint(0, GRID_COLUMN_SIZE - 1)
            if (random_row_position, random_column_position) not in mines_list:
                mines_list.append((random_row_position, random_column_position))

        for row, column in mines_list:
            board[row][column] = 'Mine'
            for i, j in DIRECTIONS:
                if valid_index(row + i, column + j) and board[row + i][column + j] != 'Mine':
                    board[row + i][column + j] += 1

        for i in range(0, GRID_ROW_SIZE, 1):
            for j in range(0, GRID_COLUMN_SIZE, 1):
                board[i][j] = Tiles(i, j, board[i][j], images['Empty' if board[i][j] == 0 else board[i][j]]) # The ternary operator ensures the Empty sprite is used for cells containing 0.

        return board, mines_list
    
    def create_tiles(self):
        for row in self.board:
            for tile in row:
                tile.create_button()

    def clear_surrounding_tiles(self, tile):
        empty_tiles = [tile]
        while len(empty_tiles) != 0:
            empty_tile = empty_tiles.pop(0)
            for neighbour in self.get_neighbours(empty_tile):
                if neighbour.tile_id == 0:
                    neighbour.button.configure(image = neighbour.tile_image, command = 0, relief = 'sunken')
                    neighbour.state = STATE_CLICKED
                    self.clicked_count += 1
                    empty_tiles.append(neighbour)
                elif neighbour.tile_id != 'Mine':
                    neighbour.button.configure(image = neighbour.tile_image, command = 0, relief = 'sunken')
                    neighbour.state = STATE_CLICKED
                    self.clicked_count += 1

    def get_neighbours(self, tile):
        neighbours = []
        
        for i, j in DIRECTIONS:
            end_row = tile.row_number + i
            end_column = tile.column_number + j
            if valid_index(end_row, end_column):
                # print((i, j), (tile.row_number - 1, tile.column_number - 1), (end_row, end_column), valid_index(end_row, end_column), self.board[end_row][end_column].state)
                if self.board[end_row][end_column].state == STATE_DEFAULT:
                    neighbours.append(self.board[end_row][end_column])
        return neighbours
    
    def update_timer(self):
        timer = "00:00:00"
        if self.starting_time != None:
            delta = datetime.now() - self.starting_time
            timer = str(delta).split('.')[0] # Drop ms.
            if delta.total_seconds() < 36000:
                timer = "0" + timer
        self.timer.set(timer)
        self.timer_job_id = root.after(100, self.update_timer)

    def restart(self):
        self.board, self.mines_list = self.board_generation()
        self.create_tiles()

        self.starting_time = None
        self.timer.set("00:00:00")

        self.mines_left = NUMBER_OF_MINES
        self.score.set('Mines: ' + str(self.mines_left))
        
        self.clicked_count = 0

        self.update_timer()
    
    def game_over(self, has_won):
        # Stop the timer.
        root.after_cancel(self.timer_job_id)

        if has_won:
            for row, column in self.mines_list:
                tile = self.board[row][column]
                if tile.state != STATE_FLAGGED:
                    tile.button.configure(image = images['Flag'])
        else:
            for row, column in self.mines_list:
                tile = self.board[row][column]
                if tile.state == STATE_FLAGGED:
                    tile.button.configure(image = images['FlagWrong'])
                else:
                    tile.button.configure(image = tile.tile_image, relief = 'sunken')

        root.update()

        restart_prompt = messagebox.askyesno("Game Over", "You Win! Play again?" if has_won else "You Lose! Play again?")
        if restart_prompt:
            self.restart()
        else:
            root.quit()

"""
This class is responsible for storing all the information about the various tiles, along with creating the button.
"""
class Tiles:

    game = None

    def __init__(self, row_number, column_number, tile_id, tile_image):
        self.row_number = row_number
        self.column_number = column_number
        self.tile_id = tile_id
        self.tile_image = tile_image
        self.state = STATE_DEFAULT

    def create_button(self):
        self.button = Button(root, image = images['Unknown'], command = self.button_clicked, state = NORMAL)
        self.button.bind(BTN_FLAG, self.on_right_click_wrapper(self))
        self.button.grid(row = self.row_number + 1, column = self.column_number) # To account for information bar in the first row.
    
    def on_right_click_wrapper(self, tile):
        return lambda right_click: self.button_right_clicked(self)
    
    def button_clicked(self):
        if Tiles.game.starting_time == None:
            Tiles.game.starting_time = datetime.now()

        if self.state == STATE_DEFAULT:
            if self.tile_id == 'Mine':
                self.button.configure(image = images['Exploded'], command = 0, relief = 'sunken')
                Tiles.game.mines_list.remove((self.row_number, self.column_number))
                Tiles.game.game_over(False)
            else:
                self.button.configure(image = self.tile_image, command = 0, relief = 'sunken')
                if self.tile_id == 0:
                    self.state = STATE_CLICKED
                    Tiles.game.clear_surrounding_tiles(self)
                Tiles.game.clicked_count += 1
                if Tiles.game.clicked_count == NUMBER_OF_NON_MINES:
                    Tiles.game.game_over(True)
    
    def button_right_clicked(self, tile):
        if Tiles.game.starting_time == None:
            Tiles.game.starting_time = datetime.now()

        if tile.state == STATE_DEFAULT:
            tile.button.configure(image = images['Flag'])
            tile.state = STATE_FLAGGED
            Tiles.game.mines_left -= 1
        elif tile.state == STATE_FLAGGED:
            tile.button.configure(image = images['Unknown'])
            tile.state = STATE_DEFAULT
            Tiles.game.mines_left += 1

        Tiles.game.score.set('Mines: ' + str(Tiles.game.mines_left))

def main():
    # Create game instance.
    minesweeper = Minesweeper()

    # Set game instance required by Tiles as class variable.
    Tiles.game = minesweeper

    # Create information bar.
    Label(root, foreground = 'red', textvariable = minesweeper.score).grid(row = 0, column = 0, columnspan = 3)
    Button(root, image = images['Smiley'], state = NORMAL, height = 20, width = 20, command = minesweeper.restart).grid(row = 0, column = 2, columnspan = 5) # Restart button.
    Label(root, foreground = 'red', textvariable = minesweeper.timer).grid(row = 0, column = 6, columnspan = 3)

    # Create tiles.
    minesweeper.create_tiles()

    # Run event loop.
    root.mainloop()

if __name__ == "__main__":
    main()