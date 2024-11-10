from enum import Enum

class CellState(Enum):
    UNLIT = 0
    LIT = 1
    LIGHT = 2
    CROSSED_OFF = 3

state_char = {
    CellState.UNLIT: " ",
    CellState.LIT: "~",
    CellState.LIGHT: "*",
    CellState.CROSSED_OFF: "X"
}

class Cell:
    def __init__(self, row, col):
        self.row = row
        self.col = col

class EmptyCell(Cell):
    def __init__(self, row, col):
        super().__init__(row, col)
        self.state = CellState.UNLIT

    def char(self):
        return state_char[self.state]

def is_empty_cell(cell):
    return isinstance(cell, EmptyCell)

class WallCell(Cell):
    def __init__(self, row, col, number = None):
        super().__init__(row, col)
        self.number = number
    def char(self):

        return "W" if self.number is None else str(self.number)

class Grid:
    def __init__(self, width, height, values):
        self.width = width
        self.height = height
        self.values = values

    def print(self):
        for row in range(self.height):
            for col in range(self.width):
                value = next((c for c in self.values if c.row == row and c.col == col), None)
                char = value.char() if value is not None else " "
                print(char, end="")
            print()
        print()

    def direction(self, cell, direction):
        diff = lambda cell, adjacent: (cell.row - adjacent.row, cell.col - adjacent.col)
        match direction:
            case "left":
                return next((c for c in self.values if diff(c, cell) == (0, -1)), None)
            case "right":
                return next((c for c in self.values if diff(c, cell) == (0, 1)), None)
            case "up":
                return next((c for c in self.values if diff(c, cell) == (-1, 0)), None)
            case "down":
                return next((c for c in self.values if diff(c, cell) == (1, 0)), None)

    def direction_while(self, cell, direction, predicate):
        cell = self.direction(cell, direction)
        while predicate(cell):
            yield cell
            cell = self.direction(cell, direction)

    def adjacent_cells(self, cell):
        return [self.direction(cell, direction) for direction in ["left", "right", "up", "down"] if self.direction(cell, direction) is not None]
    
    def numbers(self):
        return [cell for cell in self.values if isinstance(cell, WallCell) and cell.number is not None]
    
    def lights(self):
        return [cell for cell in self.values if cell.state == CellState.LIGHT]

    def is_valid(self):
        valid = True
        for number in self.numbers():
            adjacent = self.adjacent_cells(number)
            if len([c for c in adjacent if c.state == CellState.LIGHT]) > number.number:
                valid = False
            if len([c for c in adjacent if not c.state == CellState.LIT]) < number.number:
                valid = False
        for light in self.lights():
            if any([c for c in self.lights() if c.col == light.col or c.row == light.row]):
                valid = False
        return valid

    def is_complete(self):
        return all([cell.state in [CellState.LIT, CellState.LIGHT] for cell in self.values if isinstance(cell, EmptyCell)])

    def place_light(self, cell):
        cell.state = CellState.LIGHT
        for direction in ["left", "right", "up", "down"]:
            for visible in self.direction_while(cell, direction, is_empty_cell):
                visible.state = CellState.LIT

    def cross_off_around_numbers(self):
        for number in self.numbers():
            lights = [c for c in self.adjacent_cells(number) if c.state == CellState.LIGHT]
            if len(lights) == number.number:
                for cell in self.adjacent_cells(number):
                    if cell.state == CellState.UNLIT:
                        cell.state = CellState.CROSSED_OFF

    def fill_obvious_numbers(self):
        for number in self.numbers():
            open = [c for c in self.adjacent_cells(number) if not c.state in [CellState.LIT, CellState.CROSSED_OFF]]
            if len(open) == number.number:
                for cell in open:
                    self.place_light(cell)
    
    def fill_isolated_cells(self):
        blanks = [c for c in self.values if isinstance(c, EmptyCell) and c.state == CellState.UNLIT]
        for blank in blanks:
            isolated = True
            for direction in ["left", "right", "up", "down"]:
                for cell in self.direction_while(blank, direction, is_empty_cell):
                    if cell.state == CellState.UNLIT:
                        isolated = False
                        break
            if isolated:
                self.place_light(blank)

grid = """  1 W  
2     2
 1   W 
       
 0   2 
W     3
  0 W  """

def parse_grid(grid):
    result = []
    for row, row_str in enumerate(grid.split("\n")):
        for col, cell in enumerate(row_str):
            match cell:
                case " ":
                    result.append(EmptyCell(row, col))
                case "W":
                    result.append(WallCell(row, col))
                case _:
                    result.append(WallCell(row, col, int(cell)))
    return Grid(row + 1, col + 1, result)


grid = parse_grid(grid)
grid.print()
grid.cross_off_around_numbers()
grid.print()
grid.fill_obvious_numbers()
grid.print()
grid.fill_obvious_numbers()
grid.print()
grid.fill_obvious_numbers()
grid.print()
grid.fill_obvious_numbers()
grid.print()
grid.cross_off_around_numbers()
grid.print()
grid.fill_isolated_cells()
grid.print()

# grid = parse_grid(grid)
# grid.print()
# grid.place_light(grid.values[10])
# grid.print()