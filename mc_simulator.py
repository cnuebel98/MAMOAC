import random
import time
import copy
from renderer import Renderer
import plotly.graph_objects as go

class MCSimulator:
    def __init__(self, agent, grid, simu_depth=100, time_limit=1.0, max_rollouts=10000):
        """
        Monte Carlo Simulator class
        :param agent: Reference to the current agent (robot).
        :param grid: Reference to the current grid (playing field).
        :param iterations: Number of Monte Carlo simulations to run.
        :param time_limit: Maximum time limit for running the simulations in seconds.
        """
        self.agent = agent
        self.grid = grid # Use a method to get relevant data
        self.simu_depth = simu_depth
        self.time_limit = time_limit
        self.max_rollouts = max_rollouts

    def simulate(self):
        """
        Perform Monte Carlo simulations to determine the best move and obstacle shift.
        Returns:
            best_move (str): Best move direction ('up', 'down', 'top_left', etc.)
            best_shift (str): Best obstacle shift direction ('up', 'down', etc.)
        """
        best_move = None
        best_shift = None
        best_score = float('inf')  # Initialize with a large number, we want to minimize the score
        rollout_counter = 0
        start_time = time.time()
        print("---------------------------")
        print("Hi from simulation function")
        #print(f'Coords: ({self.agent.row}, {self.agent.col})')
        #print(temp_grid[self.agent.row][self.agent.col]['weight'])

        # simulations run for the time_limit but for a mximum of max_rollouts

        # list_of_first_actions = [('move_direction','shift_direction'),('',''),('',''), ...] max len: 6x6=36
        list_of_first_actions = []
        # list_of_fitness = [[(f1_value of first path, f2_value first path), (f1_value of next path, f2_value next path), ...],[(2,4), (4,9), ...],[(21,43), (45, 23)]]
        fitness_of_first_actions = []

        for _ in range(self.max_rollouts):
            rollout_counter += 1
            # For each rollout, the grid and agent must be reset
            temp_agent = copy.deepcopy(self.agent)
            temp_grid = copy.deepcopy(self.grid)
            
            # if time limit is reached, the for loop is broken
            if time.time() - start_time > self.time_limit:
                break
            
            # random simulations are done until goal is reached of until max simu depth is reached
            for _ in range(self.simu_depth):
                # we get possible movement directions
                move_directions = self.get_possible_directions((temp_agent.row, temp_agent.col), temp_grid=temp_grid)
                # choose index from possible move directions
                move_direction_index = random.randint(0, len(move_directions)-1)
                # get direction from the index
                move_direction = move_directions[move_direction_index]
                # move agent to new cell
                temp_agent.move(move_direction, temp_grid)
                
                # from the new position, get possible shift directions
                shift_directions = self.get_possible_directions((temp_agent.row, temp_agent.col), temp_grid=temp_grid)
                # randomly choose index from possible shift directions
                shift_direction_index = random.randint(0, len(shift_directions)-1)
                # get the actual direction to shift to
                shift_direction = shift_directions[shift_direction_index]
                # shift the weight to the chosen neighbor cell
                temp_agent.shift_obstacle(shift_direction, temp_grid)

                if ((temp_agent.row, temp_agent.col) == (temp_agent.goal_row, temp_agent.goal_col)):
                    print("simu ended before 5 moves! -----------------------------------")
                    break

            # now we need to see if the first action of the path 
            # that was simulated is already in the list of first actions
            # if not we append it
            # also we have to add an empty list to the fitness_of_first_actions
            #print(f"list of first actions before: {list_of_first_actions}")
            #print(f"list of fitness before: {fitness_of_first_actions}")
            
            search_tuple = (temp_agent.path_directions[0], temp_agent.shift_directions[0])
            #print(f'searching for: {search_tuple}')
            fitness_tuple = self.evaluate(temp_agent=temp_agent, temp_grid=temp_grid)
            if (search_tuple in list_of_first_actions):
                print(f'({temp_agent.path_directions[0], temp_agent.shift_directions[0]}) already in list')
                # Here we find the index of where the actions are in the list 
                found_at_index = list_of_first_actions.index(search_tuple)
                # then we need to add the fitness tuple to the fitness list at this index
                fitness_of_first_actions[found_at_index].append(fitness_tuple)
                
            else:
                #print(f'({search_tuple}) not in list yet')
                list_of_first_actions.append(search_tuple)
                fitness_of_first_actions.append([fitness_tuple])

            #print(f"list of first actions after {list_of_first_actions}")
            #print(f"list of fitness after {fitness_of_first_actions}")
            #print(f"a Path: {temp_agent.path_directions}")
            #print(f"tempAgent posititon: ({temp_agent.row, temp_agent.col})")
        #print(f'all fitness values: {fitness_of_first_actions}')
        # now we have a list of first actions and a list of fitness values
        # call a plotting function to look at the fitness values
        pareto_optimal_solutions = self.get_pareto_fronts(list_of_first_actions, fitness_of_first_actions)
        #print(f'Pareto Fronts: {x}')
        self.plot_fitness(list_of_first_actions, fitness_of_first_actions, title="All Fitness Values")
        self.plot_fitness(list_of_first_actions, pareto_optimal_solutions, title="Pareto Fronts")
        #print(f'max rollouts reached: {rollout_counter}')
        #print("1 sec later")

        return best_move, best_shift
    
    def get_pareto_fronts(self, list_of_first_actions, fitness_of_first_actions):
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
                name=str(label),  # Legend label for this sublist
                marker=dict(size=10),  # Customize marker size if needed
                line=dict(width=2),    # Customize line width
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

    def evaluate(self, temp_agent, temp_grid):
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

    def get_possible_directions(self, current_cell, temp_grid):
        '''This function returns a list of possible direction 
        for moving to or shifting to'''
        directions = []
        # even, even or odd, even: A2
        if ((current_cell[0] % 2 == 1 and current_cell[1] % 2 == 0)
            or (current_cell[0] % 2 == 0 and current_cell[1] % 2 == 0)):
            # check all 6 possible cells for validity
            if temp_grid.is_valid_position(current_cell[0], current_cell[1] + 1):
                directions.append("bottom_right")
            if temp_grid.is_valid_position(current_cell[0] - 1, current_cell[1]):
                directions.append("up")
            if temp_grid.is_valid_position(current_cell[0] + 1, current_cell[1]):
                directions.append("down")
            if temp_grid.is_valid_position(current_cell[0], current_cell[1] - 1):
                directions.append("bottom_left")
            if temp_grid.is_valid_position(current_cell[0] - 1, current_cell[1] + 1):
                directions.append("top_right")
            if temp_grid.is_valid_position(current_cell[0] - 1, current_cell[1] - 1):
                directions.append("top_left")

        # row even col odd or odd and odd: A1
        elif((current_cell[0] % 2 == 0 and current_cell[1] % 2 == 1)
            or (current_cell[0] % 2 == 1 and current_cell[1] % 2 == 1)):
            # check all 6 possible cells for validity
            if temp_grid.is_valid_position(current_cell[0] + 1, current_cell[1]):
                directions.append("down")
            if temp_grid.is_valid_position(current_cell[0] + 1, current_cell[1] + 1):
                directions.append("bottom_right")
            if temp_grid.is_valid_position(current_cell[0] + 1, current_cell[1] - 1):
                directions.append("bottom_left")
            if temp_grid.is_valid_position(current_cell[0], current_cell[1] - 1):
                directions.append("top_left")
            if temp_grid.is_valid_position(current_cell[0], current_cell[1] + 1):
                directions.append("top_right")
            if temp_grid.is_valid_position(current_cell[0] - 1, current_cell[1]):
                directions.append("up")
        return directions