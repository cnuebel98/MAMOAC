from grid_world import GridWorld
from agent import Agent
from copy import deepcopy
from helper_functions import HelperFunctions
import random
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
class NSGA2():
    #Variables
    popSize = 100
    n_eval = 1000
    agents: list[Agent] = []
    mutProb = 0.1 #Mutation probability
    crossProb = 0.1 #Crossover probability
    evalCounter = 0
    numberOfParents = 50

    def __init__(self) -> None:
        """Init method creates grid world and prepares agents for the algorithm."""
        #Create grid world
        self.grid = GridWorld() #standard size used

        #Create initial population (they are blank here)
        for x in range(self.popSize):
            tmpAgent = Agent(name=x)
            self.agents.append(deepcopy(tmpAgent))
            del tmpAgent #Memory management is comming to town (making sure that the agent is unique and has no pointers attached)
        
        #Sample path
        for x in range(len(self.agents)):
            self.samplePath(self.agents[x], self.grid)
            #While sampling we already evaluate so we manually change the counter
            self.evalCounter += 1
        
        self.mainLoop()
            
    def samplePath(self, agent: Agent, grid: GridWorld) -> None:
        """Samples a path for a newly created agent randomly if needed."""
        #Both those variables should be in the agent class TODO: Change later

        #Make copy of grid
        tmpGrid = deepcopy(grid)

        while not agent.reachedGoal and not agent.reachedHome:
            #While we did not visit the goal AND the home
            #Get walking direction
            walkingDirection = random.choice(HelperFunctions.get_possible_directions((agent.row, agent.col), temp_grid=tmpGrid))
            agent.append_to_path(walkingDirection)
            agent.move(walkingDirection, tmpGrid)

            #Get shift
            shiftingDirection = random.choice(HelperFunctions.get_possible_directions((agent.row, agent.col), temp_grid=tmpGrid))
            agent.append_to_shift(shiftingDirection)
            agent.shift_obstacle(shiftingDirection, tmpGrid)

            #Checks if goal or home was visited
            if agent.reachedGoal:
                if agent.row == agent.home_row and agent.col == agent.home_col:
                    agent.reachedHome = True
            else:
                if agent.row == agent.goal_row and agent.col == agent.goal_col:
                    agent.reachedGoal = True
        agent.fullCells = tmpGrid.get_full_cells()

    def nothingCrossover(self, parent1: Agent, parent2: Agent) -> Agent:
        """Just for testing purposes, does nothing."""
        #Deepcopy here makes this slow I suppose
        return deepcopy(parent1)
    
    def nothingMutation(self, baseAgent: Agent) -> Agent:
        """Just for testing purposes, does nothing."""
        return baseAgent #we use deepcopy here since we dont want to have a pointer to the original instead of a new object

    def evaluate(self, agent: Agent, gird:GridWorld) -> None:
        """Evaluate function for an agent."""
        #Deepcopying for every agent is slow (multiprocessing might be way to go)
        tmpGrid = deepcopy(gird)
        for x in range(len(agent.path_directions)):
            agent.move(agent.path_directions[x], tmpGrid)
            agent.shift_obstacle(agent.shift_directions[x], tmpGrid)

        self.evalCounter += 1

    def getFronts(self):
        """Gives back lists corresponding to the fronts of the population."""
        fronts = []

        for i in range(len(self.agents)):
            dominationCounter = 0
            for j in range(len(self.agents)):
                if i != j:
                    #Prepare value lists
                    valueList1 = [self.agents[i].move_count_f1, self.agents[i].weight_shifted_f2, self.agents[i].fullCells]
                    valueList2 = [self.agents[j].move_count_f1, self.agents[j].weight_shifted_f2, self.agents[j].fullCells]
                    if HelperFunctions.getParetoDominance(valueList2, valueList1): #we check if the point we test against gets dominated (in this case i)
                        dominationCounter+=1
            self.agents[i].dominationCount = dominationCounter
        
        self.agents.sort(key=lambda agent: agent.dominationCount)

        for agent in self.agents:
            if len(fronts) != 0:
                if fronts[-1][0].dominationCount == agent.dominationCount:
                    fronts[-1].append(agent)
                else: 
                    fronts.append([agent])

            else:
                fronts.append([agent])
        if False:
            self.showFront(fronts)
        
        return fronts

    def showFront(self, fronts: list) -> None:
        """Creates a plot of the found fronts (has to be list with nested list which holds tuples of 3)."""
        data = [[(x.move_count_f1, x.weight_shifted_f2, x.fullCells) for x in front] for front in fronts]
        # Generate a list of colors for each sublist
        colors = plt.cm.viridis(np.linspace(0, 1, len(data)))

        # Create a 3D plot
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')

        # Iterate over each sublist in 'data' and assign a different color
        for i, sublist in enumerate(data):
            x_vals = [point[0] for point in sublist]
            y_vals = [point[1] for point in sublist]
            z_vals = [point[2] for point in sublist]
    
            # Scatter plot the points in the current sublist with a specific color
            ax.scatter(x_vals, y_vals, z_vals, color=colors[i], marker='o', label=f'List {i+1}')

        # Label the axes
        ax.set_xlabel('Move count')
        ax.set_ylabel('Weight Shifted')
        ax.set_zlabel('Full Cells')

        # Set plot title
        ax.set_title('Fronts for NSGA2')

        # Add a legend to identify each sublist
        legend = [f"Front {x}" for x in range(len(data))]
        ax.legend(labels=legend)

        # Show the plot
        plt.show()

    def calcCrowdingDistance(self, front: list[Agent]):
        """Calculates the crowding distances for a given front."""
        #Sort for each objective and identify the nearest neighbors per objective
        #TODO: Look for better alternatives, worst case here is O(n)
        for agent in front:
            nearestNeighf1 = []
            nearestNeighf2 = []
            nearestNeighf3 = []
            for x in range(len(front)):
                front.sort(key= lambda x: x.move_count_f1)
                if front[x] == agent:
                    if x > 0 and x < len(front)-1:
                        nearestNeighf1.append(front[x-1])
                        nearestNeighf1.append(front[x+1])
            for x in range(len(front)):
                front.sort(key= lambda x: x.weight_shifted_f2)
                if front[x] == agent:
                    if x > 0 and x < len(front)-1:
                        nearestNeighf2.append(front[x-1])
                        nearestNeighf2.append(front[x+1])
            for x in range(len(front)):
                front.sort(key= lambda x: x.fullCells)
                if front[x] == agent:
                    if x > 0 and x < len(front)-1:
                        nearestNeighf3.append(front[x-1])
                        nearestNeighf3.append(front[x+1])

            #If one of these is empty, we set the CD to infinity
            if len(nearestNeighf1) != 2 or len(nearestNeighf2) != 2 or len(nearestNeighf3) != 2:
                agent.crowdiDist = np.inf #-1 is here a replacement for infinity since the CD can never be negative
            else:
                #This looks a bit messy but here we calc the CD for each objective and sum it up
                #agent.crowdiDist = ((f1Sorted[nearestNeighf1[1]].move_count_f1 - f1Sorted[nearestNeighf1[0]].move_count_f1)/(f1Sorted[-1].move_count_f1 - (f1Sorted[0].move_count_f1))+
                #                    (f2Sorted[nearestNeighf1[1]].weight_shifted_f2 - f2Sorted[nearestNeighf1[0]].weight_shifted_f2)/(f2Sorted[-1].weight_shifted_f2 - (f2Sorted[0].weight_shifted_f2))+
                #                    (f3Sorted[nearestNeighf1[1]].fullCells - f3Sorted[nearestNeighf1[0]].fullCells)/(f3Sorted[-1].fullCells - (f3Sorted[0].fullCells)))
                agent.crowdiDist = ((nearestNeighf1[-1].move_count_f1 - nearestNeighf1[0].move_count_f1)+
                                    (nearestNeighf2[-1].weight_shifted_f2 - nearestNeighf2[0].weight_shifted_f2)+
                                    (nearestNeighf3[-1].fullCells - nearestNeighf3[0].fullCells))
    
    def selection(self) -> list[Agent]:
        """Binary tournament selection for NSGA2."""
        selectedInd = []
        #We want to select as many parents as we defined
        for x in range(self.numberOfParents):
            #Randomly choose 2 individuals from the population (we do remove them from the pop since we do not want to use deepcopy)
            agent1 = random.choice(self.agents)
            agent2 = random.choice(self.agents)

            #Quick check if the same one got selected:
            if agent1 == agent2:
                selectedInd.append(agent1)
                self.agents.remove(agent1)
                continue

            if agent1.dominationCount != agent2.dominationCount:
                if agent1.dominationCount < agent2.dominationCount:
                    selectedInd.append(agent1)
                    self.agents.remove(agent1)
                else:
                    selectedInd.append(agent2)
                    self.agents.remove(agent2)
            else:
                if agent1.crowdiDist != agent2.crowdiDist:
                    if agent1.crowdiDist > agent2.crowdiDist:
                        selectedInd.append(agent1)
                        self.agents.remove(agent1)
                    else:
                        selectedInd.append(agent2)
                        self.agents.remove(agent2)
                else:
                    selectedInd.append(agent1)
                    self.agents.remove(agent1)
        
        return selectedInd

    def mainLoop(self):
        """Main loop of NSGA2 """
        #Innit -> Crossover Mutation Updating the population
        while self.evalCounter < self.n_eval:
            #Build fronts
            fronts = self.getFronts()
            if self.evalCounter == 500 or self.evalCounter == 950 :
                self.showFront(fronts)
            
        
            #Get CD for fronts
            for front in fronts:
                self.calcCrowdingDistance(front)

            #Select parents
            parents = self.selection()
        
            #Select random parents for crossover
            children = [] #to keep pop size we have to produce as much children as we do have parents
            while len(children) < len(parents):
                selectedParents = random.sample(parents, 2)
                children.append(self.nothingCrossover(selectedParents[0], selectedParents[1]))
        
            #Now do mutation for the children and evaluate them
            for child in children:
                if random.random() < self.mutProb:
                    child = self.nothingMutation(child)
                self.evaluate(child, self.grid)
                #We now check that the individual reached the goal, if not we sample a new one
                if not child.reachedHome: #Home can only be reached if we visited goal first so no need for 2 checks
                    child = self.samplePath(Agent(name=self.evalCounter), self.grid)
            
            #Now merge children and parents lists
            parents.extend(children)

            #Only keep selected parents as pop
            self.agents = parents

            print(f"Evaluations: {self.evalCounter}")