import pygame
import random
import copy
import pandas as pd
from grid_world import GridWorld

class Agent:
    def __init__(self, name, row=0, col=0, color=(0, 0, 0)):
        self.name = name
        self.row = row  # Initial row position
        self.col = col  # Initial column position
        self.goal_row = 9
        self.goal_col = 16
        self.home_row = 0
        self.home_col = 0
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
        self.encoded_path = []
        self.results = []
        self.fullCells = 0
        self.dominationCount = 0 #Please ignore, this is just for NSGA2 to determine fronts
        self.crowdiDist = 0 #Same here (just pleasant to have it here)
        self.reachedHome = False
        self.reachedGoal = False

    def __eq__(self, agent) -> bool:
        #Pretty shitty statement
        return self.path_directions == agent.path_directions and self.shift_directions == agent.shift_directions and self.move_count_f1 == agent.move_count_f1 and self.weight_shifted_f2 == agent.weight_shifted_f2 and self.fullCells == agent.fullCells

    def move(self, direction, grid:GridWorld):
        self.move_count_f1 += 1
        # Movement logic for hexagonal grid with 6 directions
        self.successful_move = False
        if direction == "up":
            if grid.is_valid_position(self.row - 1, self.col):
                self.row -= 1
                self.successful_move = True
            #else: print("Movement direction not valid")

        elif direction == "down":
            if grid.is_valid_position(self.row + 1, self.col):
                self.row += 1

                self.successful_move = True
            #else: print("Movement direction not valid")

        elif direction == "top_left":
            if ((self.row % 2 == 1 and self.col % 2 == 1) 
                or (self.row % 2 == 0 and self.col % 2 == 1)):
                if (grid.is_valid_position(self.row, self.col - 1)):
                    self.col -= 1
                    self.successful_move = True
                #else: print("Movement direction not valid")

            elif ((self.row % 2 == 0 and self.col % 2 == 0)
                  or (self.row % 2 == 1 and self.col % 2 == 0)):
                if (grid.is_valid_position(self.row - 1, self.col - 1)):
                    self.row -= 1
                    self.col -= 1
                    self.successful_move = True
                #else: print("Movement direction not valid")

        elif direction == "top_right":
            if ((self.row % 2 == 1 and self.col % 2 == 1) 
                or (self.row % 2 == 0 and self.col % 2 == 1)):
                if (grid.is_valid_position(self.row, self.col + 1)):
                    self.col += 1
                    self.successful_move = True
                #else: print("Movement direction not valid")

            elif ((self.row % 2 == 0 and self.col % 2 == 0)
                  or (self.row % 2 == 1 and self.col % 2 == 0)):
                if (grid.is_valid_position(self.row - 1, self.col + 1)):
                    self.row -= 1
                    self.col += 1
                    self.successful_move = True
                #else: print("Movement direction not valid")

        elif direction == "bottom_right":
            if ((self.row % 2 == 1 and self.col % 2 == 1) 
                or (self.row % 2 == 0 and self.col % 2 == 1)):
                if (grid.is_valid_position(self.row + 1, self.col + 1)):
                    self.col += 1
                    self.row += 1
                    self.successful_move = True
                #else: print("Movement direction not valid")

            elif ((self.row % 2 == 0 and self.col % 2 == 0)
                  or (self.row % 2 == 1 and self.col % 2 == 0)):
                if (grid.is_valid_position(self.row, self.col + 1)):
                    self.col += 1
                    self.successful_move = True
                #else: print("Movement direction not valid")

        elif direction == "bottom_left":
            if ((self.row % 2 == 1 and self.col % 2 == 1) 
                or (self.row % 2 == 0 and self.col % 2 == 1)):
                if (grid.is_valid_position(self.row + 1, self.col - 1)):
                    self.row += 1
                    self.col -= 1
                #else: print("Movement direction not valid")

            elif ((self.row % 2 == 0 and self.col % 2 == 0)
                  or (self.row % 2 == 1 and self.col % 2 == 0)):
                if (grid.is_valid_position(self.row, self.col-1)):
                    self.col -= 1
                    self.successful_move = True
                #else: print("Movement direction not valid")
                
                
        if self.successful_move:
            #print(f"Successful move to {direction}")
            # Append move to encoded path
            self.encoded_path.append([(self.row, self.col)])
            self.append_to_path(direction)
            self.next_weigth_to_move = grid.grid[self.row][self.col]['weight']
            
            if self.next_weigth_to_move == 0:
                self.append_to_shift("no_weight_to_shift")

    def moveCoords(self, direction: tuple[int, int], grid:GridWorld):
        """Moves the agent using the coordinate encoding."""
        #print(f"Trying to move from {(self.row, self.col)} to {direction}")
        # Movement logic for hexagonal grid with 6 directions
        self.successful_move = False

        if (grid.is_valid_position(direction[0], direction[1])):
            self.row = direction[0]
            self.col = direction[1]
            self.next_weigth_to_move = grid.grid[self.row][self.col]['weight']
            self.successful_move = True
            #print(f"Move should have been executed, pos is now {(self.row, self.col)}")
        else:
            print("TRIED TO MAKE AN INVALID MOVE")
            exit()

    def shift_obstacle(self, direction, grid: GridWorld):
        #print(f"Agent {self.name} is trying to shift the obstacle to {direction}")
        self.successful_shift = False
        target_cell = (0, 0)
        if direction == "up":
            if grid.is_valid_position(self.row - 1, self.col):
                grid.grid[self.row - 1][self.col]['weight'] = round(grid.grid[self.row - 1][self.col]['weight'] + grid.grid[self.row][self.col]['weight'], 2)
                grid.grid[self.row][self.col]['weight'] = 0.0
                self.successful_shift = True
                target_cell = (self.row - 1, self.col)
            #else: print("shift direction not valid")

        elif direction == "down":
            if grid.is_valid_position(self.row + 1, self.col):
                grid.grid[self.row + 1][self.col]['weight'] = round(grid.grid[self.row + 1][self.col]['weight'] + grid.grid[self.row][self.col]['weight'], 2)
                grid.grid[self.row][self.col]['weight'] = 0.0
                self.successful_shift = True
                target_cell = (self.row + 1, self.col)
            #else: print("shift direction not valid")
        
        elif direction == "top_left":
            if ((self.row % 2 == 1 and self.col % 2 == 1) 
                or (self.row % 2 == 0 and self.col % 2 == 1)):
                if (grid.is_valid_position(self.row, self.col - 1)):
                    grid.grid[self.row][self.col - 1]['weight'] = round(grid.grid[self.row][self.col - 1]['weight'] + grid.grid[self.row][self.col]['weight'], 2)
                    grid.grid[self.row][self.col]['weight'] = 0.0
                    self.successful_shift = True
                    target_cell = (self.row, self.col - 1)
                #else: print("shift direction not valid")

            elif ((self.row % 2 == 0 and self.col % 2 == 0)
                  or (self.row % 2 == 1 and self.col % 2 == 0)):
                if (grid.is_valid_position(self.row - 1, self.col - 1)):
                    grid.grid[self.row - 1][self.col - 1]['weight'] = round(grid.grid[self.row - 1][self.col - 1]['weight'] + grid.grid[self.row][self.col]['weight'], 2)
                    grid.grid[self.row][self.col]['weight'] = 0.0
                    self.successful_shift = True
                    target_cell = (self.row - 1, self.col - 1)
                #else: print("shift direction not valid")
        
        elif direction == "top_right":
            if ((self.row % 2 == 1 and self.col % 2 == 1) 
                or (self.row % 2 == 0 and self.col % 2 == 1)):
                if (grid.is_valid_position(self.row, self.col + 1)):
                    grid.grid[self.row][self.col + 1]['weight'] = round(grid.grid[self.row][self.col + 1]['weight'] + grid.grid[self.row][self.col]['weight'], 2)
                    grid.grid[self.row][self.col]['weight'] = 0.0
                    self.successful_shift = True
                    target_cell = (self.row, self.col + 1)
                #else: print("shift direction not valid")

            elif ((self.row % 2 == 0 and self.col % 2 == 0)
                  or (self.row % 2 == 1 and self.col % 2 == 0)):
                if (grid.is_valid_position(self.row - 1, self.col + 1)):
                    grid.grid[self.row - 1][self.col + 1]['weight'] = round(grid.grid[self.row - 1][self.col + 1]['weight'] + grid.grid[self.row][self.col]['weight'], 2)
                    grid.grid[self.row][self.col]['weight'] = 0.0
                    self.successful_shift = True
                    target_cell = (self.row - 1, self.col + 1)
                #else: print("shift direction not valid")
        
        elif direction == "bottom_left":
            if ((self.row % 2 == 1 and self.col % 2 == 1) 
                or (self.row % 2 == 0 and self.col % 2 == 1)):
                if (grid.is_valid_position(self.row + 1, self.col - 1)):
                    grid.grid[self.row + 1][self.col - 1]['weight'] = round(grid.grid[self.row + 1][self.col - 1]['weight'] + grid.grid[self.row][self.col]['weight'], 2)
                    grid.grid[self.row][self.col]['weight'] = 0.0
                    self.successful_shift = True
                    target_cell = (self.row + 1, self.col - 1)
                #else: print("shift direction not valid")

            elif ((self.row % 2 == 0 and self.col % 2 == 0)
                  or (self.row % 2 == 1 and self.col % 2 == 0)):
                if (grid.is_valid_position(self.row, self.col-1)):
                    grid.grid[self.row][self.col - 1]['weight'] = round(grid.grid[self.row][self.col - 1]['weight'] + grid.grid[self.row][self.col]['weight'], 2)
                    grid.grid[self.row][self.col]['weight'] = 0.0
                    self.successful_shift = True
                    target_cell = (self.row, self.col - 1)
                #else: print("shift direction not valid")

        elif direction == "bottom_right":
            if ((self.row % 2 == 1 and self.col % 2 == 1)
                or (self.row % 2 == 0 and self.col % 2 == 1)):
                if (grid.is_valid_position(self.row + 1, self.col + 1)):
                    grid.grid[self.row + 1][self.col + 1]['weight'] = round(grid.grid[self.row + 1][self.col + 1]['weight'] + grid.grid[self.row][self.col]['weight'], 2)
                    grid.grid[self.row][self.col]['weight'] = 0.0
                    self.successful_shift = True
                    target_cell = (self.row + 1, self.col + 1)
                #else: print("shift direction not valid")

            elif ((self.row % 2 == 0 and self.col % 2 == 0)
                  or (self.row % 2 == 1 and self.col % 2 == 0)):
                if (grid.is_valid_position(self.row, self.col + 1)):
                    grid.grid[self.row][self.col + 1]['weight'] = round(grid.grid[self.row][self.col + 1]['weight'] + grid.grid[self.row][self.col]['weight'], 2)
                    grid.grid[self.row][self.col]['weight'] = 0.0
                    self.successful_shift = True
                    target_cell = (self.row, self.col + 1)
                #else: print("shift direction not valid")

        #TODO: Check if shift is necessary, if not make shifting coordinates null or (-1, -1)
        if self.successful_shift and len(self.encoded_path[-1]) == 1:
            if self.next_weigth_to_move == 0: #If there is nothing in the cell we do not have to shift
                self.encoded_path[-1].append((None, None))
            else:
                self.encoded_path[-1].append(target_cell)  


        # spill mechnics
        if self.successful_shift:
            self.weight_shifted_f2 = round(self.weight_shifted_f2 + self.next_weigth_to_move, 2)
            self.append_to_shift(direction)

            spill_probability = grid.grid[target_cell[0]][target_cell[1]]['weight']
            if self.max_weight_till_spill < spill_probability:
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
                
                weight_per_neighbor = round(weight_to_spill / count_neighbors_to_spill_on, 2)
                for neighbor in neighbors_to_spill_on:
                    if neighbor == target_cell:
                        grid.grid[neighbor[0]][neighbor[1]]['weight'] = weight_per_neighbor
                    else:
                        grid.grid[neighbor[0]][neighbor[1]]['weight'] = round(grid.grid[neighbor[0]][neighbor[1]]['weight'] + weight_per_neighbor, 2)

    def shiftCoords(self, targetCell: tuple[int, int], grid:GridWorld):
        self.successful_shift = False
        if grid.grid[self.row][self.col]['weight'] != 0:
            grid.grid[targetCell[0]][targetCell[1]]['weight'] = round(grid.grid[targetCell[0]][targetCell[1]]['weight'] + grid.grid[targetCell[0]][targetCell[1]]['weight'], 2)
            grid.grid[self.row][self.col]['weight'] = 0.0
            self.successful_shift = True

        # spill mechnics
        if self.successful_shift:
            self.weight_shifted_f2 = round(self.weight_shifted_f2 + self.next_weigth_to_move, 2)

            spill_probability = grid.grid[targetCell[0]][targetCell[1]]['weight']
            #print(f"Spill prob: {spill_probability}, max weight till spill: {self.max_weight_till_spill}")
            if self.max_weight_till_spill < spill_probability:
                # how to access all neighbors of target cell
                weight_to_spill = spill_probability
                count_neighbors_to_spill_on = 0
                neighbors_to_spill_on = []
                # the neighbors are adressed differently depending on the row and col of the target cell
                # row odd, col even or even and even
                if ((targetCell[0] % 2 == 1 and targetCell[1] % 2 == 0)
                    or (targetCell[0] % 2 == 0 and targetCell[1] % 2 == 0)):
                    # check all 7 possible cells for validity
                    if grid.is_valid_position(targetCell[0], targetCell[1]):
                        count_neighbors_to_spill_on += 1
                        neighbors_to_spill_on.append((targetCell[0], targetCell[1]))
                    if grid.is_valid_position(targetCell[0], targetCell[1] + 1):
                        count_neighbors_to_spill_on += 1
                        neighbors_to_spill_on.append((targetCell[0], targetCell[1] + 1))
                    if grid.is_valid_position(targetCell[0] - 1, targetCell[1]):
                        count_neighbors_to_spill_on += 1
                        neighbors_to_spill_on.append((targetCell[0] - 1, targetCell[1]))
                    if grid.is_valid_position(targetCell[0] + 1, targetCell[1]):
                        count_neighbors_to_spill_on += 1
                        neighbors_to_spill_on.append((targetCell[0] + 1, targetCell[1]))
                    if grid.is_valid_position(targetCell[0], targetCell[1] - 1):
                        count_neighbors_to_spill_on += 1
                        neighbors_to_spill_on.append((targetCell[0], targetCell[1] - 1))
                    if grid.is_valid_position(targetCell[0] - 1, targetCell[1] + 1):
                        count_neighbors_to_spill_on += 1
                        neighbors_to_spill_on.append((targetCell[0] - 1, targetCell[1] + 1))
                    if grid.is_valid_position(targetCell[0] - 1, targetCell[1] - 1):
                        count_neighbors_to_spill_on += 1
                        neighbors_to_spill_on.append((targetCell[0] - 1, targetCell[1] - 1))

                # row even col odd or odd and odd
                elif((targetCell[0] % 2 == 0 and targetCell[1] % 2 == 1)
                    or (targetCell[0] % 2 == 1 and targetCell[1] % 2 == 1)):
                    # check all 7 possible cells for validity
                    if grid.is_valid_position(targetCell[0], targetCell[1]):
                        count_neighbors_to_spill_on += 1
                        neighbors_to_spill_on.append((targetCell[0], targetCell[1]))
                    if grid.is_valid_position(targetCell[0] + 1, targetCell[1]):
                        count_neighbors_to_spill_on += 1
                        neighbors_to_spill_on.append((targetCell[0] + 1, targetCell[1]))
                    if grid.is_valid_position(targetCell[0] + 1, targetCell[1] + 1):
                        count_neighbors_to_spill_on += 1
                        neighbors_to_spill_on.append((targetCell[0] + 1, targetCell[1] + 1))
                    if grid.is_valid_position(targetCell[0] + 1, targetCell[1] - 1):
                        count_neighbors_to_spill_on += 1
                        neighbors_to_spill_on.append((targetCell[0] + 1, targetCell[1] - 1))
                    if grid.is_valid_position(targetCell[0], targetCell[1] - 1):
                        count_neighbors_to_spill_on += 1
                        neighbors_to_spill_on.append((targetCell[0], targetCell[1] - 1))
                    if grid.is_valid_position(targetCell[0], targetCell[1] + 1):
                        count_neighbors_to_spill_on += 1
                        neighbors_to_spill_on.append((targetCell[0], targetCell[1] + 1))
                    if grid.is_valid_position(targetCell[0] - 1, targetCell[1]):
                        count_neighbors_to_spill_on += 1
                        neighbors_to_spill_on.append((targetCell[0] - 1, targetCell[1]))
                
                weight_per_neighbor = round(weight_to_spill / count_neighbors_to_spill_on, 2)
                for neighbor in neighbors_to_spill_on:
                    if neighbor == targetCell:
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
    
    def print_results(self, full_cells):
        #print(f"Path: {self.path_directions}")
        #print(f"Shift: {self.shift_directions}")
        print("-----------------")
        print(f"Agent {self.name} reached the goal")
        print(f"Path Length: {self.move_count_f1}")
        print(f"Weight Shifted: {self.weight_shifted_f2}")
        print(f"Full Cells: {full_cells}")

    def save_results(self):
        # Create a DataFrame from the results
        df = pd.DataFrame(self.results, columns=['steps', 'weight_shifted', 'full_cells', 'move_dirs', 'shift_dirs'])
        df.to_csv(f"results/{self.name}_results.csv", index=False)

    def record_result(self, full_cells):
        self.results.append([self.move_count_f1, self.weight_shifted_f2, full_cells, self.path_directions, self.shift_directions])