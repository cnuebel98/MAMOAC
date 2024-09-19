import pygame
from agent import KeyboardAgent
from grid_world import GridWorld
from game_loop import GameLoop

# Example usage
def main():
    pygame.init()
    grid = GridWorld()
    agent1 = KeyboardAgent(name="1", row=4, col=8)
    agent2 = KeyboardAgent(name="2", row=6, col=7)
    GameLoop.run(grid, agent1, agent2)

if __name__ == "__main__":
    main()
