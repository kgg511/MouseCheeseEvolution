import time
# Objects used in the game
class Cheese():
    def __init__(self, x, y):
        self.x = x
        self.y = y
        
    def __str__(self):
        return "C"
    
class Fire(): # Kills mouse
    def __init__(self, x, y):
        self.x = x
        self.y = y
    def __str__(self):
        return "F"


class Agent():
    def __init__(self, dead, grid) -> None:
        self.cheeseEaten = 0
        self.dead = False
        self.grid = grid
        
        self.x = self.grid.size // 2
        self.y = self.grid.size // 2
        self.timeStartEnd = time.time()
    
    def move(self, x, y): # move up, down, left, right randomly
        self.grid.grid[self.y][self.x] = None
        self.x = x
        self.y = y

        if isinstance(self.grid.grid[self.y][self.x], Fire):
            self.dead = True
            self.timeStartEnd = time.time() - self.timeStartEnd
        elif isinstance(self.grid.grid[self.y][self.x], Cheese):
            self.cheeseEaten += 1
            print("yum")
        
        self.grid.grid[self.y][self.x] = self
        # put self in the grid
    
    def __str__(self) -> str:
        if self.dead:
            return "X"
        else:
            return "A"


class Grid():
    def __init__(self, size) -> None:
        self.grid = []
        self.size = size

    
    def printGrid(self):
        for i in range(self.size):
            row = ""
            for j in range(self.size):
                if self.grid[i][j] == None:
                    row += "0 "
                else:
                    row += str(self.grid[i][j]) + " "
            row += "\n"
            print(row)
        print("-----------------")
