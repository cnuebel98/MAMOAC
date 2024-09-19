import pygame

class KeyboardAgent:
    def __init__(self, name, row=0, col=0):
        self.name = name
        self.row = row  # Initial row position
        self.col = col  # Initial column position
        self.color = (0, 0, 0) if name == "1" else (0, 0, 255)  # Different color for agents
        self.radius = 15
        self.successful_shift = False
        self.successful_move = False

    def move(self, direction, grid):
        # Movement logic for hexagonal grid with 6 directions
        self.successful_move = False
        if direction == "up":
            if grid.is_valid_position(self.row - 1, self.col):
                self.row -= 1
                self.successful_move = True
            else: print("Movement direction not valid")

        elif direction == "down":
            if grid.is_valid_position(self.row + 1, self.col):
                self.row += 1
                self.successful_move = True
            else: print("Movement direction not valid")

        elif direction == "top_left":
            if ((self.row % 2 == 1 and self.col % 2 == 1) 
                or (self.row % 2 == 0 and self.col % 2 == 1)):
                if (grid.is_valid_position(self.row, self.col - 1)):
                    self.col -= 1
                    self.successful_move = True
                else: print("Movement direction not valid")

            elif ((self.row % 2 == 0 and self.col % 2 == 0)
                  or (self.row % 2 == 1 and self.col % 2 == 0)):
                if (grid.is_valid_position(self.row - 1, self.col - 1)):
                    self.row -= 1
                    self.col -= 1
                    self.successful_move = True
                else: print("Movement direction not valid")

        elif direction == "top_right":
            if ((self.row % 2 == 1 and self.col % 2 == 1) 
                or (self.row % 2 == 0 and self.col % 2 == 1)):
                if (grid.is_valid_position(self.row, self.col + 1)):
                    self.col += 1
                    self.successful_move = True
                else: print("Movement direction not valid")

            elif ((self.row % 2 == 0 and self.col % 2 == 0)
                  or (self.row % 2 == 1 and self.col % 2 == 0)):
                if (grid.is_valid_position(self.row - 1, self.col + 1)):
                    self.row -= 1
                    self.col += 1
                    self.successful_move = True
                else: print("Movement direction not valid")

        elif direction == "bottom_right":
            if ((self.row % 2 == 1 and self.col % 2 == 1) 
                or (self.row % 2 == 0 and self.col % 2 == 1)):
                if (grid.is_valid_position(self.row + 1, self.col + 1)):
                    self.col += 1
                    self.row += 1
                    self.successful_move = True
                else: print("Movement direction not valid")

            elif ((self.row % 2 == 0 and self.col % 2 == 0)
                  or (self.row % 2 == 1 and self.col % 2 == 0)):
                if (grid.is_valid_position(self.row, self.col + 1)):
                    self.col += 1
                    self.successful_move = True
                else: print("Movement direction not valid")

        elif direction == "bottom_left":
            if ((self.row % 2 == 1 and self.col % 2 == 1) 
                or (self.row % 2 == 0 and self.col % 2 == 1)):
                if (grid.is_valid_position(self.row + 1, self.col - 1)):
                    self.row += 1
                    self.col -= 1
                else: print("Movement direction not valid")

            elif ((self.row % 2 == 0 and self.col % 2 == 0)
                  or (self.row % 2 == 1 and self.col % 2 == 0)):
                if (grid.is_valid_position(self.row, self.col-1)):
                    self.col -= 1
                    self.successful_move = True
                else: print("Movement direction not valid")
        if self.successful_move:
            print(f"Agent {self.name} moved to row: {self.row}, col: {self.col}")
            print(f"Weight at this position: {grid.grid[self.row][self.col]['weight']}")

    def shift_obstacle(self, direction, grid):
        print(f"Agent {self.name} is trying to shift the obstacle to {direction}")
        self.successful_shift = False

        if direction == "up":
            if grid.is_valid_position(self.row - 1, self.col):
                grid.grid[self.row - 1][self.col]['weight'] = round(grid.grid[self.row - 1][self.col]['weight'] + grid.grid[self.row][self.col]['weight'], 2)
                grid.grid[self.row][self.col]['weight'] = 0.0
                self.successful_shift = True
            else: print("shift direction not valid")

        elif direction == "down":
            if grid.is_valid_position(self.row + 1, self.col):
                grid.grid[self.row + 1][self.col]['weight'] = round(grid.grid[self.row + 1][self.col]['weight'] + grid.grid[self.row][self.col]['weight'], 2)
                grid.grid[self.row][self.col]['weight'] = 0.0
                self.successful_shift = True
            else: print("shift direction not valid")
        
        elif direction == "top_left":
            if ((self.row % 2 == 1 and self.col % 2 == 1) 
                or (self.row % 2 == 0 and self.col % 2 == 1)):
                if (grid.is_valid_position(self.row, self.col - 1)):
                    grid.grid[self.row][self.col - 1]['weight'] = round(grid.grid[self.row][self.col - 1]['weight'] + grid.grid[self.row][self.col]['weight'], 2)
                    grid.grid[self.row][self.col]['weight'] = 0.0
                    self.successful_shift = True
                else: print("shift direction not valid")

            elif ((self.row % 2 == 0 and self.col % 2 == 0)
                  or (self.row % 2 == 1 and self.col % 2 == 0)):
                if (grid.is_valid_position(self.row - 1, self.col - 1)):
                    grid.grid[self.row - 1][self.col - 1]['weight'] = round(grid.grid[self.row - 1][self.col - 1]['weight'] + grid.grid[self.row][self.col]['weight'], 2)
                    grid.grid[self.row][self.col]['weight'] = 0.0
                    self.successful_shift = True
                else: print("shift direction not valid")
        
        elif direction == "top_right":
            if ((self.row % 2 == 1 and self.col % 2 == 1) 
                or (self.row % 2 == 0 and self.col % 2 == 1)):
                if (grid.is_valid_position(self.row, self.col + 1)):
                    grid.grid[self.row][self.col + 1]['weight'] = round(grid.grid[self.row][self.col + 1]['weight'] + grid.grid[self.row][self.col]['weight'], 2)
                    grid.grid[self.row][self.col]['weight'] = 0.0
                    self.successful_shift = True
                else: print("shift direction not valid")
            elif ((self.row % 2 == 0 and self.col % 2 == 0)
                  or (self.row % 2 == 1 and self.col % 2 == 0)):
                if (grid.is_valid_position(self.row - 1, self.col + 1)):
                    grid.grid[self.row - 1][self.col + 1]['weight'] = round(grid.grid[self.row - 1][self.col + 1]['weight'] + grid.grid[self.row][self.col]['weight'], 2)
                    grid.grid[self.row][self.col]['weight'] = 0.0
                    self.successful_shift = True
                else: print("shift direction not valid")
        
        elif direction == "bottom_left":
            if ((self.row % 2 == 1 and self.col % 2 == 1) 
                or (self.row % 2 == 0 and self.col % 2 == 1)):
                if (grid.is_valid_position(self.row + 1, self.col - 1)):
                    grid.grid[self.row + 1][self.col - 1]['weight'] = round(grid.grid[self.row + 1][self.col - 1]['weight'] + grid.grid[self.row][self.col]['weight'], 2)
                    grid.grid[self.row][self.col]['weight'] = 0.0
                    self.successful_shift = True
                    print("(ungerade, ungerade) oder row gerade, col ungerade, Agent bottom left pushing attemt successful")
                else: print("shift direction not valid")

            elif ((self.row % 2 == 0 and self.col % 2 == 0)
                  or (self.row % 2 == 1 and self.col % 2 == 0)):
                if (grid.is_valid_position(self.row, self.col-1)):
                    grid.grid[self.row][self.col - 1]['weight'] = round(grid.grid[self.row][self.col - 1]['weight'] + grid.grid[self.row][self.col]['weight'], 2)
                    grid.grid[self.row][self.col]['weight'] = 0.0
                    self.successful_shift = True
                else: print("shift direction not valid")

        elif direction == "bottom_right":
            if ((self.row % 2 == 1 and self.col % 2 == 1) 
                or (self.row % 2 == 0 and self.col % 2 == 1)):
                if (grid.is_valid_position(self.row + 1, self.col + 1)):
                    grid.grid[self.row + 1][self.col + 1]['weight'] = round(grid.grid[self.row + 1][self.col + 1]['weight'] + grid.grid[self.row][self.col]['weight'], 2)
                    grid.grid[self.row][self.col]['weight'] = 0.0
                    self.successful_shift = True
                else: print("shift direction not valid")

            elif ((self.row % 2 == 0 and self.col % 2 == 0)
                  or (self.row % 2 == 1 and self.col % 2 == 0)):
                if (grid.is_valid_position(self.row, self.col + 1)):
                    grid.grid[self.row][self.col + 1]['weight'] = round(grid.grid[self.row][self.col + 1]['weight'] + grid.grid[self.row][self.col]['weight'], 2)
                    grid.grid[self.row][self.col]['weight'] = 0.0
                    self.successful_shift = True
                else: print("shift direction not valid")

    def draw(self, screen, grid):
        # Now access the position from the dictionary
        position = grid.grid[self.row][self.col]['position']
        x, y = position
        pygame.draw.circle(screen, self.color, (int(x), int(y)), self.radius)
