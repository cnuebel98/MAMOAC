import random
import time
import copy
from renderer import Renderer
import plotly.graph_objects as go
from helper_functions import HelperFunctions

class MO_MCSimulator:
    def __init__(self, agent, grid, simu_depth=100, time_limit=1.0, max_rollouts=10000):
        """
        Monte Carlo Simulator class
        :param agent: Reference to the current agent (robot).
        :param grid: Reference to the current grid (playing field).
        :param iterations: Number of Monte Carlo simulations to run.
        :param time_limit: Maximum time limit for running the simulations in seconds.
        """
        self.agent = agent
        self.grid = grid
        self.simu_depth = simu_depth
        # simulations run for the time_limit but for a mximum of max_rollouts
        self.time_limit = time_limit
        self.max_rollouts = max_rollouts
        
        # list_of_first_actions = [('move_direction','shift_direction'),('',''),('',''), ...] max len: 6x6=36
        # list_of_fitness = [[(f1_value of first path, f2_value first path), (f1_value of next path, f2_value next path), ...],[(2,4), (4,9), ...],[(21,43), (45, 23)]]
        self.list_of_first_actions = []
        self.fitness_of_first_actions = []

    def simulate(self):
        """
        Perform Monte Carlo simulations to determine the best move and obstacle shift.
        Returns:
            best_move (str): Best move direction
            best_shift (str): Best obstacle shift direction
        """
        rollout_counter=0
        start_time = time.time()

        for _ in range(self.max_rollouts):
            # For each rollout, the grid and agent must be reset
            temp_agent = copy.deepcopy(self.agent)
            temp_grid = copy.deepcopy(self.grid)

            goal_reached = False
            returned_to_start = False

            # Reset path and shift directions for the temporary agent
            temp_agent.path_directions = []
            temp_agent.shift_directions = []
            
            # if time limit is reached, the for loop is broken
            if time.time() - start_time > self.time_limit:
                break
            
            # random simulations are done until goal is reached of until max simu depth is reached
            for _ in range(self.simu_depth):
                # we get possible movement directions
                move_directions = HelperFunctions.get_possible_directions((temp_agent.row, temp_agent.col), temp_grid=temp_grid)
                # choose index from possible move directions
                move_direction_index = random.randint(0, len(move_directions)-1)
                # get direction from the index
                move_direction = move_directions[move_direction_index]
                # move agent to new cell
                temp_agent.move(move_direction, temp_grid)
                
                # from the new position, get possible shift directions
                shift_directions = HelperFunctions.get_possible_directions((temp_agent.row, temp_agent.col), temp_grid=temp_grid)
                # randomly choose index from possible shift directions
                shift_direction_index = random.randint(0, len(shift_directions)-1)
                # get the actual direction to shift to
                shift_direction = shift_directions[shift_direction_index]
                # shift the weight to the chosen neighbor cell
                temp_agent.shift_obstacle(shift_direction, temp_grid)

                if ((temp_agent.row, temp_agent.col) == (temp_agent.goal_row, temp_agent.goal_col)) and goal_reached == False:
                    temp_agent.goal_row, temp_agent.goal_col = temp_agent.home_row, temp_agent.home_col
                    goal_reached = True
                if ((temp_agent.row, temp_agent.col) == (temp_agent.goal_row, temp_agent.goal_col)) and goal_reached == True:
                    returned_to_start = True
                    
            rollout_counter += 1
            # now we need to see if the first action of the path 
            # that was simulated is already in the list of first actions
            # if not we append it
            # search tuple is the first action of the path
            search_tuple = (temp_agent.path_directions[0], temp_agent.shift_directions[0])
            # evaluate the agent by full cells and weight shifted
            fitness_tuple = self.evaluate_full_cells_WSUM_weight_shifted_steps_taken(temp_agent=temp_agent, temp_grid=temp_grid)
            fitness_tuple = (fitness_tuple[0], fitness_tuple[1])

            if (goal_reached == True) and (returned_to_start == False):
                fitness_tuple = (fitness_tuple[0]*0.5, fitness_tuple[1]*0.5)
            elif returned_to_start == True:
                fitness_tuple = (fitness_tuple[0]*0.1, fitness_tuple[1]*0.1)

            if (search_tuple in self.list_of_first_actions):
                # Here we find the index of where the actions are in the list 
                found_at_index = self.list_of_first_actions.index(search_tuple)
                # then we need to add the fitness tuple to the fitness list at this index
                self.fitness_of_first_actions[found_at_index].append(fitness_tuple)
            else:
                # new first action found and appended to the list
                self.list_of_first_actions.append(search_tuple)
                self.fitness_of_first_actions.append([fitness_tuple])
        #print(rollout_counter)
        # now we have a list of first actions and a list of fitness values
        # get the pareto fronts of this data
        pareto_optimal_solutions = self.get_pareto_fronts(self.fitness_of_first_actions)
        
        # call a plotting function to look at the fitness values
        #self.plot_fitness(list_of_first_actions, fitness_of_first_actions, title="All Fitness Values")
        #self.plot_fitness(list_of_first_actions, pareto_optimal_solutions, title="Pareto Fronts")

        # now we need to find the best move and shift based on the hypervolume
        list_hv_values = self.get_hypervolume(pareto_optimal_solutions)
        # get index of the hv list where the value is highest
        best_hv_index = list_hv_values.index(max(list_hv_values))
        #print(self.list_of_first_actions)
        #print(f'Best Hypervolume Index: {best_hv_index} in list {list_hv_values}')
        
        best_move = self.list_of_first_actions[best_hv_index][0]
        best_shift = self.list_of_first_actions[best_hv_index][1]
        
        return best_move, best_shift

    ######################## ACTION SELECTION FUNCTIONS ########################

    def get_hypervolume(self, pareto_fronts):
        # Get the reference point (f1, f2)
        ref_point = self.get_ref_point(pareto_fronts)
        # Initialize a list to store hypervolumes per front
        hypervolumes = []
        # Iterate over each Pareto front
        for front in pareto_fronts:
            # Sort the points on the Pareto front by the first objective (f1) in descending order
            sorted_front = sorted(front, key=lambda x: x[0], reverse=True)
            # Initialize the hypervolume for the current Pareto front
            hypervolume = 0
            # Initialize the previous point's x (f1) as the reference point's x-coordinate
            prev_x = ref_point[0]
            # Calculate the hypervolume for this Pareto front
            for p in sorted_front:
                # Get the current point (x, y)
                x, y = p
                # Width of the rectangle is the difference between the current x and the previous x
                width = prev_x - x
                # Height of the rectangle is the difference between the reference point's y and the current y
                height = ref_point[1] - y
                # Add the rectangle's area to the hypervolume
                if width > 0 and height > 0:  # Make sure both width and height are positive
                    hypervolume += width * height
                # Update the previous x-coordinate to the current x-coordinate
                prev_x = x
            # Append the hypervolume for this front to the result list
            hypervolumes.append(hypervolume)
        return hypervolumes

    def get_ref_point(self, pareto_fronts):
        # Implement the calculation of ref point
        worst_f1_free_cells = 0
        worst_f2_weight_shifted = 0
        for front in pareto_fronts:
            for f1, f2 in front:
                if f1 > worst_f1_free_cells:
                    worst_f1_free_cells = f1
                if f2 > worst_f2_weight_shifted:
                    worst_f2_weight_shifted = f2
        return (round(worst_f1_free_cells*1.1), round(worst_f2_weight_shifted*1.1, 2))

    def get_pareto_fronts(self, fitness_of_first_actions):
        list_of_pareto_fronts = []
        # Loop over each sublist of fitness data
        for i, fitness_sublist in enumerate(fitness_of_first_actions):
            pareto_front = []
            # Check each point in the sublist
            for j, (x1, y1) in enumerate(fitness_sublist):
                is_pareto = True
                for k, (x2, y2) in enumerate(fitness_sublist):
                    if k == j:
                        continue
                    # Check for strict Pareto dominance
                    if (x2 <= x1 and y2 <= y1) and (x2 < x1 or y2 < y1):
                        is_pareto = False
                        break
                # If no other point dominates (x1, y1), it's Pareto optimal
                if is_pareto:
                    pareto_front.append((x1, y1))
            list_of_pareto_fronts.append(pareto_front)
        return list_of_pareto_fronts

    def plot_fitness(self, list_of_first_actions, fitness_of_first_actions, title="Objective Values"):
        fig = go.Figure()
        
        # Loop over each sublist of fitness data
        for i, fitness_sublist in enumerate(fitness_of_first_actions):
            # Unpack the tuples in the sublist for plotting
            x_values = [x for (x, _) in fitness_sublist]
            y_values = [y for (_, y) in fitness_sublist]
            
            # Get the corresponding label for the current sublist
            label = list_of_first_actions[i]

            # Add a scatter plot trace for each sublist
            fig.add_trace(go.Scatter(
                x=x_values,
                y=y_values,
                mode='markers',
                name=str(label),        # Legend label for this sublist
                marker=dict(size=10),   # Customize marker size if needed
                line=dict(width=2),     # Customize line width
            ))
        
        # Customize layout
        fig.update_layout(
            title=title,
            xaxis_title="Full cells",
            yaxis_title="Weight Shifted",
            legend_title="First Actions",
            showlegend=True
        )
        
        # Show the plot
        fig.show()

    ######################## EVALUATION FUNCTIONS ########################

    def evaluate_full_cells_weight_shifted(self, temp_agent, temp_grid):
        """ This function evaluates the agent in terms of how much area was cleared 
        and how much obstacle weight needed to be shifted for that. 
        Returns a tuple (full_cells, weight_shifted)"""
        full_cells = 0
        weight_shifted = temp_agent.weight_shifted_f2
        # Loop through the grid and count the number of cells with weight >= threshold
        for row in temp_grid.grid:
            for cell in row:
                if cell['weight'] > 0:
                    full_cells += 1
        return (full_cells, weight_shifted)
    
    def evaluate_full_cells_WSUM_weight_shifted_steps_taken(self, temp_agent, temp_grid):
        '''This function evaluates the agents in terms of how much area was cleared,
        how many steps they took and how much obstacle weight needed to be shifted for that.'''
        full_cells = 0
        steps_taken = len(temp_agent.path_directions)
        WSUM_Steps_and_weight = 1/2*temp_agent.weight_shifted_f2 + 1/2*steps_taken
        # Loop through the grid and count the number of cells with weight >= threshold
        for row in temp_grid.grid:
            for cell in row:
                if cell['weight'] > 0:
                    full_cells += 1
        return full_cells, WSUM_Steps_and_weight

    def evaluate_full_cells_weight_shifted_steps_taken(self, temp_agent, temp_grid):
        '''This function evaluates the agents in terms of how much area was cleared,
        how many steps they took and how much obstacle weight needed to be shifted for that.'''
        full_cells = 0
        steps_taken = len(temp_agent.path_directions)
        weight_shifted = temp_agent.weight_shifted_f2
        # Loop through the grid and count the number of cells with weight >= threshold
        for row in temp_grid.grid:
            for cell in row:
                if cell['weight'] > 0:
                    full_cells += 1
        return (full_cells, weight_shifted, steps_taken)
