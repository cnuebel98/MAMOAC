import time
import copy
from helper_functions import HelperFunctions


class MO_RHEA:
    def __init__(self, agent, grid, simu_depth, time_limit, max_rollouts, pop_size=20):
        '''Rolling Horizon EA strategy for MOAC'''
        self.agent = agent
        self.grid = grid
        self.pop_size = pop_size
        self.simu_depth = simu_depth
        self.time_limit = time_limit
        self.max_rollouts = max_rollouts

    def simulate(self):
        '''Simulate the agent's actions using RHEA'''
        start_time = time.time()

        best_move, best_shift = None, None

        temp_agent = copy.deepcopy(self.agent)
        temp_grid = copy.deepcopy(self.grid)
        
        pop = self.get_initial_population()

        for i in range(self.max_rollouts):
            # For each rollout, the grid and agent must be reset
            temp_agent = copy.deepcopy(self.agent)
            temp_grid = copy.deepcopy(self.grid)
            

            if time.time() - start_time > self.time_limit:
                break
            


        return best_move, best_shift
    
    def get_initial_population(self, agent, grid):
        '''Generate the initial population for the RHEA algorithm'''
        pop = []

        for i in range(self.pop_size):
            

            pop.append()

        return pop