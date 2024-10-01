from mc_simulator import MO_MCSimulator
from rhea import MO_RHEA
from agent import Agent
from grid_world import GridWorld
import multiprocessing
import pandas as pd
import os

def run_one_agent(agent_id):
    agent1_mode = 'move'  # Options: 'move', 'shift'
    agent1 = Agent(name=f"agent_{agent_id}", row=0, col=0)
    grid = GridWorld(rows=10, cols=17)
    running = True

    while running:
        mc_simulator = MO_MCSimulator(agent1, grid, simu_depth=100, time_limit=0.1, max_rollouts=100000)
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
                full_cells = grid.get_full_cells()
                agent1.print_results(full_cells=full_cells)
                #agent1.record_result(full_cells)  # Record the results
                running = False
        
    # Record results at each step if needed
    full_cells = grid.get_full_cells()
    agent1.record_result(full_cells)
    agent1.save_results()  # Save the results to a CSV file

def run_parallel_agents(num_agents):
    with multiprocessing.Pool(processes=multiprocessing.cpu_count()) as pool:
        pool.map(run_one_agent, range(num_agents))

if __name__ == '__main__':
    num_agents = 10
    run_parallel_agents(num_agents)

    all_results = []
    for agent_id in range(num_agents):
        agent_name = f"agent_{agent_id}"
        df = pd.read_csv(f"results/{agent_name}_results.csv")
        all_results.append(df)
        os.remove(f"results/{agent_name}_results.csv")


    # Combine all results into a single DataFrame
    combined_results = pd.concat(all_results, ignore_index=True)
    combined_results.to_csv("results/combined_results.csv", index=False)
