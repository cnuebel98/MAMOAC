import pygame
import pygame_menu
from agent import Agent
from grid_world import GridWorld
from game_loop import GameLoop
from renderer import Renderer
from nsga2 import NSGA2
from copy import deepcopy
from time import sleep

# Variables for grid size and number of agents
grid_size = [10, 17]  # Default grid size (rows, cols)
num_agents = 1  # Default number of agents

def showPath(encodedPath: list[list[tuple, tuple]]):
    """This method accepts and encoded path and shows it in the grid world render engine."""
    algo = NSGA2.__new__(NSGA2) #This samples multiple paths
    algo.__init__()
    path = algo.agents[0].encoded_path
    grid = deepcopy(algo.grid)
    grid_renderer = Renderer(grid)
    agent = Agent.__new__(Agent)
    agent.__init__(name="Damn thats too bad")
    pygame.init()
    #update the screen with grid and agent
    for pair in path:
        agent.moveCoords(pair[0], grid)
        grid_renderer.draw()
        agent.draw(grid_renderer.screen, grid)
        pygame.display.flip()
        agent.shiftCoords(pair[1], grid)
        grid_renderer.draw()
        agent.draw(grid_renderer.screen, grid)
        pygame.display.flip()
        sleep(0.1)

    #print(f"Encoded path: {path}")

def start_game():
    pygame.init()

    # Create the grid with the selected size
    grid = GridWorld(rows=grid_size[0], cols=grid_size[1])

    # Create the renderer with the grid
    grid_renderer = Renderer(grid)

    # Create agents dynamically based on user input
    agents = []
    for i in range(num_agents):
        row = 0  # Assign initial row position
        col = i * 2  # Spread agents across the grid horizontally
        agents.append(Agent(name=f"Agent {i+1}", row=row, col=col))

    # Start the game loop with the created grid, agents, and renderer
    if num_agents == 1:
        GameLoop.run(grid, grid_renderer, agents[0], None)  # Single player scenario
    elif num_agents >= 2:
        GameLoop.run(grid, grid_renderer, agents[0], agents[1])  # Two-player scenario

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
    
    #Button to run NSGA2
    menu.add.button('NSGA2', startNSGA2)

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

def startNSGA2():
    nsga2 = NSGA2.__new__(NSGA2)
    nsga2.__init__()
    nsga2.mainLoop()

if __name__ == "__main__":
    main()
    #nsga2 = NSGA2.__new__(NSGA2).__init__()
    #showPath(None)
