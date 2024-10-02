from itertools import combinations
import time
import copy
from helper_functions import HelperFunctions
import random

class Node:
    def __init__(self, state, parent=None):
        self.state = state
        self.parent = parent
        self.children = []
        self.visits = 0
        self.pareto_fitness = []

    def get_legal_actions(self):
        '''Get all legal actions from node as a list of tuples of (move, shift)'''
        possible_actions = []
        temp_agent = self.state[0]
        temp_grid = self.state[1]
        possible_moves = HelperFunctions.get_possible_directions(
            (temp_agent.row, temp_agent.col), 
            temp_grid)
        for move in possible_moves:
            temp_agent_copy = copy.deepcopy(temp_agent)
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
    
    def add_child(self, child_state):
        child_node = Node(child_state, parent=self)
        self.children.append(child_node)
        return child_node

class MCTS_Agent:
    def __init__(self, agent, grid, simu_depth=100, num_simus=100, time_limit=5):
        self.agent = agent
        self.grid = grid
        self.simu_depth = simu_depth
        self.num_simus = num_simus
        self.time_limit = time_limit

    def mcts_loop(self):
        start_time = time.time()
        running = True
        best_move, best_shift = None, None

        root = Node(state=(self.agent, self.grid))
        node = root
        
        while running:

            if time.time() - start_time > self.time_limit:
                running = False
            
            possible_actions = node.get_legal_actions()

            # 1. Selection Phase: Traverse the Tree to a leaf 
            # node using the tree policy
            while node.is_fully_expanded() and node.children:
                #print("1. Selection phase")
                # TODO make this dependent on a 3 objective UCT Value
                i = random.randint(0, len(node.children)-1)
                node = node.children[i]

            # 2. Expansion phase: add a new child node to the tree
            if (not node.is_fully_expanded()) or not node.children:
                #print("2. Expanding one node")

                expansion_agent = copy.deepcopy(node.state[0])
                expansion_grid = copy.deepcopy(node.state[1])

                expansion_node = None
                random_action = ()
                # Choose action to expand
                possible_actions = node.get_legal_actions()
                list_of_unexplored_actions = list(set(possible_actions) - set(node.children))
                i = random.randint(0, len(list_of_unexplored_actions)-1)
                random_action = list_of_unexplored_actions[i]
                
                # apply action to reach new state
                expansion_agent.move(random_action[0], expansion_grid)
                expansion_agent.shift_obstacle(random_action[1], expansion_grid)

                # add new state to the node
                child_state = (expansion_agent, expansion_grid)
                expansion_node = node.add_child(child_state)
                
            # 3. Simulation phase: Simulate the game from the new node
            fitness = self.simulation_phase(expansion_node)

            # 4. Backpropagation phase: Update visit count and fitness
            self.backpropagate(expansion_node, fitness)

        print(f"len of root pareto fitness: {len(root.pareto_fitness)}")
        print(f"n visits of root: {root.visits}")
        print(f"num children of root: {len(root.children)}")
        #print(f"best_shift: {best_shift}, best_move: {best_move}")
        return best_move, best_shift
    
    def simulation_phase(self, expansion_node):
        #print("3. Simulation phase")
        fitness_values = []
        # Simulate the game for a fixed number of steps or until goal is reachend and then returned to home
        temp_agent = copy.deepcopy(expansion_node.state[0])
        temp_grid = copy.deepcopy(expansion_node.state[1])
        node = expansion_node

        for _ in range(self.num_simus):
            # Before each rollout, reset the temp_agent 
            # and grid to the expansion node state
            goal_reached = False
            returned_to_home = False
            temp_agent_copy = copy.deepcopy(temp_agent)
            temp_grid_copy = copy.deepcopy(temp_grid)

            for _ in range(self.simu_depth):
                # Get all legal actions
                possible_actions = node.get_legal_actions()
                # Choose a random action
                i = random.randint(0, len(possible_actions)-1)
                random_action = possible_actions[i]
                # Apply action to reach new state
                
                temp_agent_copy.move(random_action[0], temp_grid_copy)
                temp_agent_copy.shift_obstacle(random_action[1], temp_grid_copy)

                # TODO Check if goal is reached and returned to home
                # TODO Set a variable to true if goal is reached
                if ((temp_agent_copy.row, temp_agent_copy.col) 
                    == (self.agent.goal_row, self.agent.goal_col) 
                    and goal_reached == False):
                    print("Goal Reached in a rollout, still have to return to home!")
                    goal_reached = True
                    
                elif ((temp_agent_copy.row, temp_agent_copy.col) 
                    == (self.agent.goal_row, self.agent.goal_col) 
                    and goal_reached == True
                    and returned_to_home == False):
                    returned_to_home = True
                
                node = node.add_child((temp_agent_copy, temp_grid_copy))

            # Calculate fitness values
            # If Goal Reached is True, then substract from the fitness
            full_cells = temp_grid_copy.get_full_cells()
            steps_taken = temp_agent_copy.move_count_f1
            weight_shifted = temp_agent_copy.weight_shifted_f2
            fitness_values.append((full_cells, steps_taken, weight_shifted))
            #print(f"Len: Fitness values: {len(fitness_values[0])}")
        return fitness_values
    
    def backpropagate(self, node, fitness):
        """Update the node's statistics based on the result."""
        #print("4. Backpropagation Phase")
        while node is not None:
            node.visits += 1
            node.pareto_fitness.append(fitness)
            node = node.parent

