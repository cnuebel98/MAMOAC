import pygame
import pygame_menu
from agent import Agent
from grid_world import GridWorld
from game_loop import GameLoop

# Variables for grid size and number of agents
grid_size = [10, 17]  # Default grid size (rows, cols)
num_agents = 1  # Default number of agents

# This function will be called when you press the "Play" button
def start_game():
    pygame.init()

    # Create the grid with the selected size
    grid = GridWorld(rows=grid_size[0], cols=grid_size[1])

    # Create agents dynamically based on user input
    agents = []
    for i in range(num_agents):
        row = 0  # Assign initial row position
        col = i * 2  # Spread agents across the grid horizontally (just an example)
        agents.append(Agent(name=f"Agent {i+1}", row=row, col=col))

    # Start the game loop with the created grid and agents
    if num_agents == 1:
        GameLoop.run(grid, agents[0], None)  # Single player scenario
    elif num_agents >= 2:
        GameLoop.run(grid, agents[0], agents[1])  # Two-player scenario

def set_grid_size(value, size):
    print(size)
    grid_size[0] = size[0]  # Set rows
    grid_size[1] = size[1]  # Set cols

def set_num_agents(value, agents):
    global num_agents
    num_agents = agents  # Update the number of agents

def main():
    pygame.init()
    surface = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("MAMOAC Menu")

    # Create the menu
    menu = pygame_menu.Menu('Welcome to MAMOAC', 800, 600,
                            theme=pygame_menu.themes.THEME_DARK)
    
    # Grid size selector (rows x cols)
    menu.add.selector('Grid Size: ', 
                      [('10x17', (10, 17)), ('15x15', (15, 15)), ('20x20', (20, 20))],
                      onchange=set_grid_size)

    # Number of agents selector
    menu.add.selector('Number of Agents: ', 
                      [('1 Agents', 1), ('2 Agents', 2)],
                      onchange=set_num_agents)
    
    # Play button to start the game
    menu.add.button('Play', start_game)

    # Quit button to exit the menu
    menu.add.button('Quit', pygame_menu.events.EXIT)

    # Main loop for the menu
    while True:
        surface.fill((0, 0, 0))  # Black background

        # Handle menu events
        events = pygame.event.get()
        menu.update(events)

        # Draw the menu
        menu.draw(surface)

        # Update display
        pygame.display.flip()

if __name__ == "__main__":
    main()
