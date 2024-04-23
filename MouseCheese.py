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
    def __init__(self, grid) -> None:
        self.cheeseEaten = 0
        self.totalCheese = grid.cheese
        self.dead = False
        self.grid = grid
        self.steps = 0 # how many steps the agent has taken
        self.trialTime = 0 # how many time steps (running a action/condition node is +1)
        
        self.x = self.grid.size // 2
        self.y = self.grid.size // 2
    
    def increment_steps(self):
        self.steps += 1
    
    def move(self, x, y): # move up, down, left, right randomly
        self.grid.grid[self.y][self.x] = None
        self.x = x
        self.y = y

        if isinstance(self.grid.grid[self.y][self.x], Fire):
            self.dead = True
        elif isinstance(self.grid.grid[self.y][self.x], Cheese):
            self.cheeseEaten += 1
        
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
        self.cheese = 0 # how many cheese in the grid at the start

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
