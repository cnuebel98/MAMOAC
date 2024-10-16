from grid_world import GridWorld
from agent import Agent
from copy import deepcopy
from helper_functions import HelperFunctions
from random import choice
class NSGA2():
    #Variables
    helperFunc = HelperFunctions()
    popSize = 100
    n_eval = 1000
    agents = []

    def __init__(self) -> None:
        """Init method creates grid world and prepares agents for the algorithm."""
        #Create grid world
        self.grid = GridWorld() #standard size used

        #Create initial population (they are blank here)
        for x in range(self.popSize):
            tmpAgent = Agent(name=x)
            self.agents.append(deepcopy(tmpAgent))
            del tmpAgent #Memory management is comming to town (making sure that the agent is unique and has no pointers attached)
        
        self.samplePath(self.agents[0], self.grid)

    def samplePath(self, agent: Agent, grid):
        """Samples a path for a newly created agent randomly if needed."""
        #Both those variables should be in the agent class TODO: Change later
        goalReached = False
        homeReached = False

        #Make copy of grid
        tmpGrid = deepcopy(grid)

        while not goalReached and not homeReached:
            #While we did not visit the goal AND the home
            #Get walking direction
            walkingDirection = choice(HelperFunctions.get_possible_directions((agent.row, agent.col), temp_grid=tmpGrid))
            agent.append_to_path(walkingDirection)
            agent.move(walkingDirection, tmpGrid)

            #Get shift
            shiftingDirection = choice(HelperFunctions.get_possible_directions((agent.row, agent.col), temp_grid=tmpGrid))
            agent.append_to_shift(shiftingDirection)
            agent.shift_obstacle(shiftingDirection, tmpGrid)

            #Checks if goal or home was visited
            if goalReached:
                if agent.row == agent.home_row and agent.col == agent.home_col:
                    homeReached = True
            else:
                if agent.row == agent.goal_row and agent.col == agent.goal_col:
                    goalReached = True
        print(agent.path_directions)

    
