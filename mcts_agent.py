import time
import copy
from helper_functions import HelperFunctions
import random
import numpy as np
import matplotlib.pyplot as plt

class Node:
    def __init__(self, state, parent=None, action=None):
        self.state = state
        self.parent = parent
        self.children = []
        self.visits = 0
        self.pareto_fitness = []
        self.action = action
        self.hypervolume = 0
        self.ucb = 0

    def get_legal_actions(self):
        '''Get all legal actions from node as a list of tuples of (move, shift)'''
        possible_actions = []
        temp_agent = self.state[0]
        temp_grid = self.state[1]
        possible_moves = HelperFunctions.get_possible_directions(
            (temp_agent.row, temp_agent.col), 
            temp_grid)
        for move in possible_moves:
            temp_agent_copy = copy.copy(temp_agent)
            temp_agent_copy.move(move, temp_grid)
            possible_shifts = HelperFunctions.get_possible_directions(
                (temp_agent_copy.row, temp_agent_copy.col), 
                temp_grid)
            for shift in possible_shifts:
                possible_actions.append((move, shift))

        return possible_actions
    
    def is_fully_expanded(self):
        '''Check if all children have been visited'''
        return len(self.children) == len(self.get_legal_actions())
    
    def add_child(self, child_state, action):
        child_node = Node(child_state, parent=self, action=action)
        self.children.append(child_node)
        return child_node

class MCTS_Agent:
    def __init__(self, agent, grid, simu_depth=100, num_simus=100, time_limit=0.5):
        self.agent = agent
        self.grid = grid
        self.simu_depth = simu_depth
        self.num_simus = num_simus
        self.time_limit = time_limit

    def simulate(self):
        start_time = time.time()
        budget_left = True
        best_move, best_shift = None, None

        root = Node(state=(self.agent, self.grid))
        root.visits = 0
        root.hypervolume = 0
        root.pareto_fitness.clear()
        
        node = root

        
        while budget_left:
            # reset node to root node after each iteration
            node = root

            if time.time() - start_time > self.time_limit:
                budget_left = False
            
            possible_actions = node.get_legal_actions()

            # 1. Selection Phase: Traverse the Tree to a leaf 
            # node using the tree policy
            while node.is_fully_expanded() and node.children:
                #print("1. Selection phase")
                for child in node.children:
                    child.ucb = self.ucb_value(node, child)
                i = np.argmax([child.ucb for child in node.children])
                # i = random.randint(0, len(node.children)-1)
                #print(i)
                node = node.children[i]

            # 2. Expansion phase: add a new child node to the tree
            if (not node.is_fully_expanded()) or not node.children:
                #print("2. Expanding one node")

                expansion_agent = copy.deepcopy(node.state[0])
                expansion_grid = copy.deepcopy(node.state[1])

                expansion_node = None
                random_action = ()
                # Choose random unvisited action to expand
                possible_actions = node.get_legal_actions()
                list_of_unexplored_actions = list(set(possible_actions) - set([child.action for child in node.children]))
                i = random.randint(0, len(list_of_unexplored_actions)-1)
                random_action = list_of_unexplored_actions[i]
                
                # apply action to reach new state
                expansion_agent.move(random_action[0], expansion_grid)
                expansion_agent.shift_obstacle(random_action[1], expansion_grid)

                # add new state to the node
                child_state = (expansion_agent, expansion_grid)
                expansion_node = node.add_child(child_state, random_action)
                
            # 3. Simulation phase: Simulate the game from the new node
            fitness = self.simulation_phase(expansion_node)

            # 4. Backpropagation phase: Update visit count and fitness
            self.backpropagate(expansion_node, fitness)

        best_move, best_shift = self.select_best_action(root)

        return best_move, best_shift
    
    def ucb_value(self, parent, child):
        '''Calculate the UCB value for a child node'''
        # UCB = Q + C * sqrt(ln(N) / n)
        # Q = average reward of child node
        # C = exploration factor
        # N = number of visits of parent node
        # n = number of visits of child node
        C = 1.41
        Q = child.hypervolume
        N = parent.visits
        n = child.visits
        ucb = Q + C * np.sqrt(np.log(N) / n)
        return ucb

    def simulation_phase(self, expansion_node):
        #print("3. Simulation phase")
        fitness_values = []
        # Simulate the game for a fixed number of steps or until 
        # goal is reachend and then returned to home
        temp_agent = copy.deepcopy(expansion_node.state[0])
        temp_grid = copy.deepcopy(expansion_node.state[1])
        node = expansion_node

        for _ in range(self.num_simus):
            # Before each rollout, reset the temp_agent 
            # and grid to the expansion node state
            goal_reached = False
            returned_to_home = False
            temp_agent_copy = copy.copy(temp_agent)
            temp_grid_copy = copy.copy(temp_grid)
            #print(f"Goal: {temp_agent_copy.goal_row, temp_agent_copy.goal_col}")

            for _ in range(self.simu_depth):
                # Get all legal actions
                possible_actions = node.get_legal_actions()
                # Choose a random action
                i = random.randint(0, len(possible_actions)-1)
                random_action = possible_actions[i]

                # Apply action to reach new state
                temp_agent_copy.move(random_action[0], temp_grid_copy)
                temp_agent_copy.shift_obstacle(random_action[1], temp_grid_copy)

                # Check if goal is reached and returned to home
                # Set a variable to true if goal is reached
                if ((temp_agent_copy.row, temp_agent_copy.col) 
                    == (temp_agent_copy.goal_row, temp_agent_copy.goal_col) 
                    and goal_reached == False):
                    #print("Goal Reached in a rollout, still have to return to home!")
                    goal_reached = True
                    
                if ((temp_agent_copy.row, temp_agent_copy.col) 
                    == (temp_agent_copy.home_row, temp_agent_copy.home_row) 
                    and goal_reached == True
                    and returned_to_home == False):
                    #print("Returned to home in a rollout after collecting the goal!")
                    returned_to_home = True
                    
                
            # Calculate fitness values
            # If Goal Reached is True, then substract from the fitness
            full_cells = temp_grid_copy.get_full_cells()
            steps_taken = temp_agent_copy.move_count_f1
            weight_shifted = temp_agent_copy.weight_shifted_f2

            if ((goal_reached == False) and (returned_to_home == False)):
                #print("Goal not reached and not returned to home")
                full_cells = full_cells * 1.5
                steps_taken = steps_taken * 1.5
                weight_shifted = weight_shifted * 1.5

            if ((goal_reached == True) and (returned_to_home == False)):
                #print("Goal Reached but not returned to home")
                full_cells = full_cells * 0.5
                steps_taken = steps_taken * 0.5
                weight_shifted = weight_shifted * 0.5
            if ((goal_reached == True) and (returned_to_home == True)):
                #print("Goal Reached and returned to home")
                full_cells = full_cells * 0.1
                steps_taken = steps_taken * 0.1
                weight_shifted = weight_shifted * 0.1
            goal_reached = False
            returned_to_home = False
            fitness_values.append((full_cells, steps_taken, weight_shifted))
            
        return fitness_values
    
    def backpropagate(self, node, fitness):
        """Update the node's statistics based on the result."""
        while node is not None:
            node.visits += 1
            # only append fitness value to childs 
            # pareto_fitness if the new value is not dominated
            
            # TODO if self.is_non_dominated(fitness, node.pareto_fitness):
            node.pareto_fitness.append(fitness)

            #print(f"node pareto fitness: {node.pareto_fitness}")
            node = node.parent

    def is_non_dominated(self, fitness, front):
        '''Check if the new fitness triple is non-dominated in the front'''
        for solution in front:
        # Check if 'solution' dominates the 'fitness' triple
            if (all(s <= f for s, f in zip(solution, fitness)) 
                and any(s < f for s, f in zip(solution, fitness))):
                #print("Fitness is dominated by solution")
                return False  # A solution dominates 'fitness'
        #print("Fitness is non-dominated")
        return True

    def select_best_action(self, root):
        #print("5. Selecting best action")
        best_move, best_shift = None, None

        # get reference point
        ref_point = self.get_ref_point(root.children)

        # assign hypervolume to all children
        for child in root.children:
            self.assign_hypervolume(child, ref_point)
        
        # select the child with the highest hypervolume
        best_child = max(root.children, key=lambda x: x.hypervolume)
        best_move, best_shift = best_child.action[0], best_child.action[1]
        return best_move, best_shift

    def assign_hypervolume(self, node, ref_point):
        '''Assign the hypervolume of the node based on the reference point'''
        # Get the pareto front of the node
        pareto_front = []
        for front in node.pareto_fitness:
            for fitness_triple in front:
                pareto_front.append(fitness_triple)
        # Calculate the hypervolume of the pareto front
        #self.plot_pareto_front(pareto_front, ref_point)
        hypervolume = HelperFunctions.calculate_hypervolume(pareto_front, ref_point)
        node.hypervolume = hypervolume


    def get_ref_point(self, solutions):
        '''Returns the reference point of a number of solutions'''
        ref_point = (float('inf'), float('inf'), float('inf'))
        all_fitness_triples = []
        for sol in solutions:
            all_fitness_triples.append(sol.pareto_fitness)

        # Flatten the list of lists into a single list of triples
        all_triples = [triple for sublist in all_fitness_triples for inner_list in sublist for triple in inner_list]
        
        max_x = max(x for x, y, z in all_triples)
        max_y = max(y for x, y, z in all_triples)
        max_z = max(z for x, y, z in all_triples)

        # Nadir Point is worst value of each objective
        nadir_point = [max_x, max_y, max_z]
        # Reference point is 10% more than the nadir point in each objective
        ref_point = (nadir_point[0]*1.1, nadir_point[1]*1.1, nadir_point[2]*1.1)
        
        return ref_point

    def plot_pareto_front(self, pareto_front, ref_point):

        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')

        # Extract objectives
        pareto_front = np.array(pareto_front)
        obj1 = pareto_front[:, 0]
        obj2 = pareto_front[:, 1]
        obj3 = pareto_front[:, 2]

        # Plot Pareto front points
        ax.scatter(obj1, obj2, obj3, color='b', label='Pareto Front')

        # Plot reference point
        ax.scatter(ref_point[0], ref_point[1], ref_point[2], color='r', label='Reference Point', marker='x')

        # Set axis labels
        ax.set_xlabel('Objective 1')
        ax.set_ylabel('Objective 2')
        ax.set_zlabel('Objective 3')

        # Display plot
        ax.legend()
        plt.show()