import pygame
import random
import copy

class Agent:
    def __init__(self, name, row=0, col=0, color=(0, 0, 0)):
        self.name = name
        self.row = row  # Initial row position
        self.col = col  # Initial column position
        self.goal_row = row
        self.goal_col = col
        self.color = color
        self.radius = 15
        self.successful_shift = False
        self.successful_move = False
        self.max_weight_till_spill = 5
        self.next_weight_to_move = 0
        self.move_count_f1 = 0
        self.weight_shifted_f2 = 0
        self.path_directions = []
        self.shift_directions = []

    def move(self, direction, grid):
        self.move_count_f1 += 1
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
            print(f"Successful move to {direction}")
            self.append_to_path(direction)
            self.next_weigth_to_move = grid.grid[self.row][self.col]['weight']
            
            if self.next_weigth_to_move == 0:
                self.append_to_shift("no_weight_to_shift")

            if self.row == self.goal_row and self.col == self.goal_col:
                print("-----------------")
                print(f"Agent {self.name} reached the goal")
                print(f"Move count Agent {self.name}: {self.move_count_f1}")
                print(f"Weight shifted: {self.weight_shifted_f2}")
            #else:
                #print(f"Agent {self.name} moved to row: {self.row}, col: {self.col}")
                #print(f"Weight at this position: {grid.grid[self.row][self.col]['weight']}")
                #print(f"Move count Agent {self.name}: {self.move_count_f1}")

    def shift_obstacle(self, direction, grid):
        #print(f"Agent {self.name} is trying to shift the obstacle to {direction}")
        self.successful_shift = False
        target_cell = (0, 0)
        if direction == "up":
            if grid.is_valid_position(self.row - 1, self.col):
                grid.grid[self.row - 1][self.col]['weight'] = round(grid.grid[self.row - 1][self.col]['weight'] + grid.grid[self.row][self.col]['weight'], 2)
                grid.grid[self.row][self.col]['weight'] = 0.0
                self.successful_shift = True
                target_cell = (self.row - 1, self.col)
            else: print("shift direction not valid")

        elif direction == "down":
            if grid.is_valid_position(self.row + 1, self.col):
                grid.grid[self.row + 1][self.col]['weight'] = round(grid.grid[self.row + 1][self.col]['weight'] + grid.grid[self.row][self.col]['weight'], 2)
                grid.grid[self.row][self.col]['weight'] = 0.0
                self.successful_shift = True
                target_cell = (self.row + 1, self.col)
            else: print("shift direction not valid")
        
        elif direction == "top_left":
            if ((self.row % 2 == 1 and self.col % 2 == 1) 
                or (self.row % 2 == 0 and self.col % 2 == 1)):
                if (grid.is_valid_position(self.row, self.col - 1)):
                    grid.grid[self.row][self.col - 1]['weight'] = round(grid.grid[self.row][self.col - 1]['weight'] + grid.grid[self.row][self.col]['weight'], 2)
                    grid.grid[self.row][self.col]['weight'] = 0.0
                    self.successful_shift = True
                    target_cell = (self.row, self.col - 1)
                else: print("shift direction not valid")

            elif ((self.row % 2 == 0 and self.col % 2 == 0)
                  or (self.row % 2 == 1 and self.col % 2 == 0)):
                if (grid.is_valid_position(self.row - 1, self.col - 1)):
                    grid.grid[self.row - 1][self.col - 1]['weight'] = round(grid.grid[self.row - 1][self.col - 1]['weight'] + grid.grid[self.row][self.col]['weight'], 2)
                    grid.grid[self.row][self.col]['weight'] = 0.0
                    self.successful_shift = True
                    target_cell = (self.row - 1, self.col - 1)
                else: print("shift direction not valid")
        
        elif direction == "top_right":
            if ((self.row % 2 == 1 and self.col % 2 == 1) 
                or (self.row % 2 == 0 and self.col % 2 == 1)):
                if (grid.is_valid_position(self.row, self.col + 1)):
                    grid.grid[self.row][self.col + 1]['weight'] = round(grid.grid[self.row][self.col + 1]['weight'] + grid.grid[self.row][self.col]['weight'], 2)
                    grid.grid[self.row][self.col]['weight'] = 0.0
                    self.successful_shift = True
                    target_cell = (self.row, self.col + 1)
                else: print("shift direction not valid")

            elif ((self.row % 2 == 0 and self.col % 2 == 0)
                  or (self.row % 2 == 1 and self.col % 2 == 0)):
                if (grid.is_valid_position(self.row - 1, self.col + 1)):
                    grid.grid[self.row - 1][self.col + 1]['weight'] = round(grid.grid[self.row - 1][self.col + 1]['weight'] + grid.grid[self.row][self.col]['weight'], 2)
                    grid.grid[self.row][self.col]['weight'] = 0.0
                    self.successful_shift = True
                    target_cell = (self.row - 1, self.col + 1)
                else: print("shift direction not valid")
        
        elif direction == "bottom_left":
            if ((self.row % 2 == 1 and self.col % 2 == 1) 
                or (self.row % 2 == 0 and self.col % 2 == 1)):
                if (grid.is_valid_position(self.row + 1, self.col - 1)):
                    grid.grid[self.row + 1][self.col - 1]['weight'] = round(grid.grid[self.row + 1][self.col - 1]['weight'] + grid.grid[self.row][self.col]['weight'], 2)
                    grid.grid[self.row][self.col]['weight'] = 0.0
                    self.successful_shift = True
                    target_cell = (self.row + 1, self.col - 1)
                else: print("shift direction not valid")

            elif ((self.row % 2 == 0 and self.col % 2 == 0)
                  or (self.row % 2 == 1 and self.col % 2 == 0)):
                if (grid.is_valid_position(self.row, self.col-1)):
                    grid.grid[self.row][self.col - 1]['weight'] = round(grid.grid[self.row][self.col - 1]['weight'] + grid.grid[self.row][self.col]['weight'], 2)
                    grid.grid[self.row][self.col]['weight'] = 0.0
                    self.successful_shift = True
                    target_cell = (self.row, self.col - 1)
                else: print("shift direction not valid")

        elif direction == "bottom_right":
            if ((self.row % 2 == 1 and self.col % 2 == 1)
                or (self.row % 2 == 0 and self.col % 2 == 1)):
                if (grid.is_valid_position(self.row + 1, self.col + 1)):
                    grid.grid[self.row + 1][self.col + 1]['weight'] = round(grid.grid[self.row + 1][self.col + 1]['weight'] + grid.grid[self.row][self.col]['weight'], 2)
                    grid.grid[self.row][self.col]['weight'] = 0.0
                    self.successful_shift = True
                    target_cell = (self.row + 1, self.col + 1)
                else: print("shift direction not valid")

            elif ((self.row % 2 == 0 and self.col % 2 == 0)
                  or (self.row % 2 == 1 and self.col % 2 == 0)):
                if (grid.is_valid_position(self.row, self.col + 1)):
                    grid.grid[self.row][self.col + 1]['weight'] = round(grid.grid[self.row][self.col + 1]['weight'] + grid.grid[self.row][self.col]['weight'], 2)
                    grid.grid[self.row][self.col]['weight'] = 0.0
                    self.successful_shift = True
                    target_cell = (self.row, self.col + 1)
                else: print("shift direction not valid")

        # spill mechnics
        if self.successful_shift:
            print(f"Successful shift to: {direction}")
            self.weight_shifted_f2 = round(self.weight_shifted_f2 + self.next_weigth_to_move, 2)
            self.append_to_shift(direction)

            spill_probability = grid.grid[target_cell[0]][target_cell[1]]['weight']
            #print(f"spill probability: {spill_probability}")
            if self.max_weight_till_spill < spill_probability:
                print("Obstacle spill triggered")
                # how to access all neighbors of target cell
                weight_to_spill = spill_probability
                count_neighbors_to_spill_on = 0
                neighbors_to_spill_on = []
                # the neighbors are adressed differently depending on the row and col of the target cell
                # row odd, col even or even and even
                if ((target_cell[0] % 2 == 1 and target_cell[1] % 2 == 0)
                    or (target_cell[0] % 2 == 0 and target_cell[1] % 2 == 0)):
                    # check all 7 possible cells for validity
                    if grid.is_valid_position(target_cell[0], target_cell[1]):
                        count_neighbors_to_spill_on += 1
                        neighbors_to_spill_on.append((target_cell[0], target_cell[1]))
                    if grid.is_valid_position(target_cell[0], target_cell[1] + 1):
                        count_neighbors_to_spill_on += 1
                        neighbors_to_spill_on.append((target_cell[0], target_cell[1] + 1))
                    if grid.is_valid_position(target_cell[0] - 1, target_cell[1]):
                        count_neighbors_to_spill_on += 1
                        neighbors_to_spill_on.append((target_cell[0] - 1, target_cell[1]))
                    if grid.is_valid_position(target_cell[0] + 1, target_cell[1]):
                        count_neighbors_to_spill_on += 1
                        neighbors_to_spill_on.append((target_cell[0] + 1, target_cell[1]))
                    if grid.is_valid_position(target_cell[0], target_cell[1] - 1):
                        count_neighbors_to_spill_on += 1
                        neighbors_to_spill_on.append((target_cell[0], target_cell[1] - 1))
                    if grid.is_valid_position(target_cell[0] - 1, target_cell[1] + 1):
                        count_neighbors_to_spill_on += 1
                        neighbors_to_spill_on.append((target_cell[0] - 1, target_cell[1] + 1))
                    if grid.is_valid_position(target_cell[0] - 1, target_cell[1] - 1):
                        count_neighbors_to_spill_on += 1
                        neighbors_to_spill_on.append((target_cell[0] - 1, target_cell[1] - 1))

                # row even col odd or odd and odd
                elif((target_cell[0] % 2 == 0 and target_cell[1] % 2 == 1)
                    or (target_cell[0] % 2 == 1 and target_cell[1] % 2 == 1)):
                    # check all 7 possible cells for validity
                    if grid.is_valid_position(target_cell[0], target_cell[1]):
                        count_neighbors_to_spill_on += 1
                        neighbors_to_spill_on.append((target_cell[0], target_cell[1]))
                    if grid.is_valid_position(target_cell[0] + 1, target_cell[1]):
                        count_neighbors_to_spill_on += 1
                        neighbors_to_spill_on.append((target_cell[0] + 1, target_cell[1]))
                    if grid.is_valid_position(target_cell[0] + 1, target_cell[1] + 1):
                        count_neighbors_to_spill_on += 1
                        neighbors_to_spill_on.append((target_cell[0] + 1, target_cell[1] + 1))
                    if grid.is_valid_position(target_cell[0] + 1, target_cell[1] - 1):
                        count_neighbors_to_spill_on += 1
                        neighbors_to_spill_on.append((target_cell[0] + 1, target_cell[1] - 1))
                    if grid.is_valid_position(target_cell[0], target_cell[1] - 1):
                        count_neighbors_to_spill_on += 1
                        neighbors_to_spill_on.append((target_cell[0], target_cell[1] - 1))
                    if grid.is_valid_position(target_cell[0], target_cell[1] + 1):
                        count_neighbors_to_spill_on += 1
                        neighbors_to_spill_on.append((target_cell[0], target_cell[1] + 1))
                    if grid.is_valid_position(target_cell[0] - 1, target_cell[1]):
                        count_neighbors_to_spill_on += 1
                        neighbors_to_spill_on.append((target_cell[0] - 1, target_cell[1]))
                print(f"Neighbors to spill on: {count_neighbors_to_spill_on}")
                
                weight_per_neighbor = round(weight_to_spill / count_neighbors_to_spill_on, 2)
                for neighbor in neighbors_to_spill_on:
                    if neighbor == target_cell:
                        grid.grid[neighbor[0]][neighbor[1]]['weight'] = weight_per_neighbor
                    else:
                        grid.grid[neighbor[0]][neighbor[1]]['weight'] = round(grid.grid[neighbor[0]][neighbor[1]]['weight'] + weight_per_neighbor, 2)

    def draw(self, screen, grid):
        # Now access the position from the dictionary
        position = grid.grid[self.row][self.col]['position']
        x, y = position
        pygame.draw.circle(screen, self.color, (int(x), int(y)), self.radius)

    def append_to_path(self, direction):
        self.path_directions.append(direction)
        #print(f"Path list: {self.path_directions}")

    def append_to_shift(self, direction):
        self.shift_directions.append(direction)
        #print(f"Shift list: {self.shift_directions}")

    def copy_current_agent(self):
        return copy.deepcopy(self.agent)