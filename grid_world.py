import math
import random

class GridWorld:
    def __init__(self, rows=10, cols=17, hex_radius=30):
        self.rows = rows
        self.cols = cols
        self.hex_radius = hex_radius
        self.grid = self.create_grid()

    def create_grid(self):
        grid = []
        for row in range(self.rows):
            row_list = []
            for col in range(self.cols):
                x, y = self.get_hex_position(row, col)
                # Assign a random weight for each cell initially
                weight = round(random.uniform(0, 1), 2)
                row_list.append({'position': (x, y), 'weight': weight})
            grid.append(row_list)
        return grid

    def get_hex_position(self, row, col):
        # Calculate hexagonal grid positions
        x_offset = (3/2) * self.hex_radius * col
        y_offset = math.sqrt(3) * self.hex_radius * (row + 0.5 * (col % 2))
        return (x_offset + self.hex_radius, y_offset + self.hex_radius)

    def calculate_total_weight(self):
        # Calculate the total weight of all cells
        return sum(cell['weight'] for row in self.grid for cell in row)

    def calculate_current_max_weight(self):
        # Find the maximum weight in the grid
        return max(cell['weight'] for row in self.grid for cell in row)

    def normalize_weight(self, weight, total_weight):
        # Normalize the weight to be between 0 and 1 based on the total weight
        return min(weight / total_weight, 1) if total_weight > 0 else 0
    
    def is_valid_position(self, row, col):
        return 0 <= row < self.rows and 0 <= col < self.cols

    def get_empty_cells(self):
        # Loop through the grid and count the number of cells with weight == 0
        empty_cells = 0
        for row in self.grid:
            for cell in row:
                if cell['weight'] == 0:
                    empty_cells += 1
        return empty_cells
    
    def get_full_cells(self):
        # Loop through the grid and count the number of cells with weight > 0
        full_cells = 0
        for row in self.grid:
            for cell in row:
                if cell['weight'] > 0:
                    full_cells += 1
        return full_cells