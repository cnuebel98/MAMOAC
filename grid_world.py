import pygame
import math

class GridWorld:
    def __init__(self, width=800, height=600, rows=10, cols=10, hex_radius=30):
        self.width = width
        self.height = height
        self.rows = rows
        self.cols = cols
        self.hex_radius = hex_radius
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Hexagonal Grid World")
        self.grid = self.create_grid()

    def create_grid(self):
        grid = []
        for row in range(self.rows):
            row_list = []
            for col in range(self.cols):
                x, y = self.get_hex_position(row, col)
                row_list.append((x, y))
            grid.append(row_list)
        return grid

    def get_hex_position(self, row, col):
        # Calculate hexagonal grid positions
        x_offset = (3/2) * self.hex_radius * col
        y_offset = math.sqrt(3) * self.hex_radius * (row + 0.5 * (col % 2))
        return (x_offset + self.hex_radius, y_offset + self.hex_radius)

    def draw(self):
        self.screen.fill((0, 0, 0))  # Clear screen
        for row in self.grid:
            for hex_pos in row:
                self.draw_hex(hex_pos)

    def draw_hex(self, position):
        x, y = position
        points = []
        for i in range(6):
            angle = math.pi / 3 * i
            px = x + self.hex_radius * math.cos(angle)
            py = y + self.hex_radius * math.sin(angle)
            points.append((px, py))
        pygame.draw.polygon(self.screen, (255, 255, 255), points, 2)

    def is_valid_position(self, row, col):
        print(f"row: {row} and col: {col}")
        return 0 <= row < self.rows and 0 <= col < self.cols
