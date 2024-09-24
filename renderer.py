import pygame
import math

class Renderer:
    def __init__(self, grid_world, width=800, height=600):
        self.grid_world = grid_world
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("MAMOAC")

        # Initialize Pygame's font module
        pygame.font.init()
        self.font = pygame.font.SysFont(None, 24)  # Use a default system font with size 24

    def get_color_from_weight(self, weight):
        # Color mapping based on weight
        if weight == 0:
            return (128, 128, 128)
        elif weight < 0.5:
            r = int(255 * (weight * 2))  # From green to yellow
            g = 255
            b = 0
        else:
            r = 255  # From yellow to red
            g = int(255 * ((1 - weight) * 2))
            b = 0
        return (r, g, b)

    def draw(self):
        self.screen.fill((60, 60, 60))
        max_weight = self.grid_world.calculate_current_max_weight()

        for row in self.grid_world.grid:
            for cell in row:
                normalized_weight = self.grid_world.normalize_weight(cell['weight'], max_weight)
                self.draw_hex(cell['position'], normalized_weight, cell['weight'])

    def draw_hex(self, position, normalized_weight, raw_weight):
        x, y = position
        points = []
        for i in range(6):
            angle = math.pi / 3 * i
            px = x + self.grid_world.hex_radius * math.cos(angle)
            py = y + self.grid_world.hex_radius * math.sin(angle)
            points.append((px, py))

        # Get color based on the normalized weight
        color = self.get_color_from_weight(normalized_weight)

        # Draw the hexagon with the computed color
        pygame.draw.polygon(self.screen, color, points)

        # Draw the outline of the hexagon
        pygame.draw.polygon(self.screen, (255, 255, 255), points, 2)

        # Draw the raw weight in the center of the hexagon
        weight_text = self.font.render(str(raw_weight), True, (255, 255, 255))  # White color text
        text_rect = weight_text.get_rect(center=(x, y))
        self.screen.blit(weight_text, text_rect)

    def update_display(self):
        pygame.display.flip()
