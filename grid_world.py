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

'''import pygame
import math
import random
import copy

class GridWorld:
    def __init__(self, width=800, height=600, rows=10, cols=17, hex_radius=30):
        self.width = width
        self.height = height
        self.rows = rows
        self.cols = cols
        self.hex_radius = hex_radius
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("MAMOAC")
        self.grid = self.create_grid()

        # Initialize Pygame's font module
        pygame.font.init()
        self.font = pygame.font.SysFont(None, 24)  # Use a default system font with size 24

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
        total_weight = sum(cell['weight'] for row in self.grid for cell in row)
        return total_weight
    
    def calculate_current_max_weight(self):
        curr_max_weight = 0
        for row in self.grid:
            for cell in row:
                if cell['weight'] > curr_max_weight:
                    curr_max_weight = cell['weight']
        return curr_max_weight

    def normalize_weight(self, weight, total_weight):
        # Normalize the weight to be between 0 and 1 based on the total weight
        return min(weight / total_weight, 1) if total_weight > 0 else 0

    def get_color_from_weight(self, weight):
        # Weight is a value between 0 and 1 (normalized)
        if weight == 0:
            r = 128
            g = 128
            b = 128
        
        elif weight < 0.5:
            # Interpolate between green (0, 255, 0) and yellow (255, 255, 0)
            r = int(255 * (weight * 2))  # Goes from 0 to 255
            g = 255  # Stays 255
            b = 0    # Stays 0
        else:
            # Interpolate between yellow (255, 255, 0) and red (255, 0, 0)
            r = 255  # Stays 255
            g = int(255 * ((1 - weight) * 2))  # Goes from 255 to 0
            b = 0    # Stays 0
        return (r, g, b)

    def draw(self):
        self.screen.fill((60, 60, 60))
        max_weight = self.calculate_current_max_weight()

        for row in self.grid:
            for cell in row:
                normalized_weight = self.normalize_weight(cell['weight'], max_weight)
                self.draw_hex(cell['position'], normalized_weight, cell['weight'])  # Pass both the normalized weight and raw weight

    def draw_hex(self, position, normalized_weight, raw_weight):
        x, y = position
        points = []
        for i in range(6):
            angle = math.pi / 3 * i
            px = x + self.hex_radius * math.cos(angle)
            py = y + self.hex_radius * math.sin(angle)
            points.append((px, py))

        # Get color based on the normalized weight
        color = self.get_color_from_weight(normalized_weight)

        # Draw the hexagon with the computed color
        pygame.draw.polygon(self.screen, color, points)  # Fill the hexagon with the color

        # Draw the outline of the hexagon
        pygame.draw.polygon(self.screen, (255, 255, 255), points, 2)

        # Draw the raw weight in the center of the hexagon
        weight_text = self.font.render(str(raw_weight), True, (255, 255, 255))  # White color text
        text_rect = weight_text.get_rect(center=(x, y))
        self.screen.blit(weight_text, text_rect)

    def is_valid_position(self, row, col):
        return 0 <= row < self.rows and 0 <= col < self.cols
    
    def copy_current_grid(self):
        return copy.deepcopy(self.grid)
'''