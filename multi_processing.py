from mc_simulator import MO_MCSimulator
from rhea import MO_RHEA
from agent import Agent
from grid_world import GridWorld
import multiprocessing

def run_one_agent(agent_id):
    agent1_mode = 'move'  # Options: 'move', 'shift'
    agent1 = Agent(name=f"Agent {agent_id}", row=0, col=0)
    grid = GridWorld(rows=10, cols=17)
    # Trigger Monte Carlo Simulation when space bar is pressed
    # repeat the steps below x times
    running = True

    while running:
        mc_simulator = MO_MCSimulator(agent1, grid, simu_depth=100, time_limit=0.1, max_rollouts=4000000)
        best_move, best_shift = mc_simulator.simulate()
        
        if agent1_mode == 'move':
            agent1.move(best_move, grid)
            agent1_mode = 'shift_obstacle'
        if agent1_mode == 'shift_obstacle':
            agent1.shift_obstacle(best_shift, grid)
            agent1_mode = 'move'
        best_move, best_shift = None, None 

        if (agent1.row == agent1.goal_row and agent1.goal_col == agent1.col):
            agent1.goal_row, agent1.goal_col = agent1.home_row, agent1.home_col
            if ((agent1.row, agent1.col) == (agent1.home_row, agent1.home_col)):
                print("Goal Reached and Returned to Home.")
                empty_cells = grid.get_empty_cells()
                agent1.print_results(empty_cells)
                running = False

# now run the function in parallel using mulitprocessing
def run_parallel_agents(num_agents):
    with multiprocessing.Pool(processes=multiprocessing.cpu_count()) as pool:
        pool.map(run_one_agent, range(num_agents))

if __name__ == '__main__':
    print("Hi")
    num_agents = 10  # Adjust the number of parallel agents
    run_parallel_agents(num_agents)
