from grid_world import GridWorld
from agent import Agent
from copy import deepcopy, copy
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

    def greedyPathFinding(self, start:list[tuple, tuple], end:list[tuple, tuple]):
        """Finds a greedy path between start and goal using the euclidean distance."""
        #We dont need to simulate it on the grid since we can just use random shifts for this purpose
        #We will not include the start and end point in the path
        #print(f"Start: {start}, End: {end}")
        path = []
        if start != end:
            currentPos = start
            while currentPos != end:
                possibleMoves = HelperFunctions.getPossibleDirectionCoords((currentPos[0], currentPos[1]), self.grid) #We dont need to use a copy of the grid since the direction method makes no changes
                possibleMoves.sort(key = lambda x: HelperFunctions.getDistance(x, end)) #Sorts the list by using the euclidean distance to the goal
                move = possibleMoves[0]
                shift = random.choice(HelperFunctions.getPossibleDirectionCoords((move[0], move[1]), self.grid)) #Get random shifting direction
                path.append([move, shift])
                currentPos = move
            path.pop(-1)
        return path    

    def checkPath(self, path:list[list[tuple, tuple]]):
        """This method checks if a path is fully connected and it repairs it if not."""
        #First check: Path ends with home
        home = (self.agents[0].home_row, self.agents[0].home_col)
        goal = (self.agents[0].goal_row, self.agents[0].goal_col)
        if path[-1][0] != home:
            print("Did not end with home.")
            validShift = random.choice(HelperFunctions.getPossibleDirectionCoords(home, self.grid))
            path.append([home, validShift])
            return self.checkPath(path)

        #Second check goal was reached in the path
        onlyCoordPath = [x[0] for x in path]
        if goal not in onlyCoordPath:
            print("Goal was not reached in path")
            #This is not elegant but ok I guess
            smallestDistance = np.inf
            index = None
            for x in range(len(path)):
                currentPos = path[x][0]
                if smallestDistance > HelperFunctions.getDistance(currentPos, goal) or index == None:
                    smallestDistance = HelperFunctions.getDistance(currentPos, goal)
                    index = x
            #Now we have the index of the coord with the smallest distance to the goal
            #Insert the goal after it with random valid shift
            path.insert(index+1, [goal, random.choice(HelperFunctions.getPossibleDirectionCoords(goal, self.grid))])
            return self.checkPath(path)

        #Third check if all cells are connected
        for x in range(len(path)-1):
            currentPos = path[x]
            nextPos = path[x+1]
            #print(f"CurrentPos: {currentPos}, nextPos: {nextPos}")
            validMoves = HelperFunctions.getPossibleDirectionCoords(currentPos[0], self.grid)
            #print(f"validMoves: {validMoves}")
            #If same pos repeats
            if currentPos[0] == nextPos[0]:
                path.pop(x+1)
                return self.checkPath(path)
            #If not connected
            if nextPos[0] not in validMoves:
                return self.checkPath(path[:x+1] + self.greedyPathFinding(currentPos[0], nextPos[0]) + path[x+1:])
        
        return path

    def samplePath(self, agent: Agent, grid: GridWorld) -> None:
        """Samples a path for a newly created agent randomly if needed."""
        #Make copy of grid
        tmpGrid = deepcopy(grid)

        while True:
            #While will be broken by reaching home after reaching the goal
            #Get walking direction
            walkingDirection = random.choice(HelperFunctions.getPossibleDirectionCoords((agent.row, agent.col), temp_grid=tmpGrid))
            agent.moveCoords(walkingDirection, tmpGrid)

            #Get shift
            shiftingDirection = random.choice(HelperFunctions.getPossibleDirectionCoords((agent.row, agent.col), temp_grid=tmpGrid))
            agent.shiftCoords(shiftingDirection, tmpGrid)
            
            #Append walking direction and shifting direction to agents encoded path
            agent.encoded_path.append([walkingDirection, shiftingDirection])

            #Checks if goal or home was visited
            if agent.reachedGoal:
                if agent.row == agent.home_row and agent.col == agent.home_col:
                    agent.reachedHome = True
                    break
            else:
                if agent.row == agent.goal_row and agent.col == agent.goal_col:
                    agent.reachedGoal = True

        agent.move_count_f1 = len(agent.encoded_path)
        agent.fullCells = tmpGrid.get_full_cells()

    def nothingCrossover(self, parent1: Agent, parent2: Agent) -> Agent:
        """Just for testing purposes, does nothing."""
        #Deepcopy here makes this slow I suppose
        return deepcopy(parent1)
    
    def onePointCrossover(self, parent1: Agent, parent2: Agent):
        """Implementation of one point crossover for 2 agents, using greedy pathfinding to connect the parts."""
        path1 = deepcopy(parent1.encoded_path)
        path2 = deepcopy(parent2.encoded_path)
        maxPathLength = min(len(parent1.encoded_path), len(parent2.encoded_path))
        cuttingPoint = random.randint(1, maxPathLength-2) #1 to maxPath length -1 since we do not want to be the end/start point to be different

        #print(f"maxPathLength: {maxPathLength}")
        #input()

        #Split the paths to recombine
        path1fh = path1[:cuttingPoint+1]
        path1sh = path1[cuttingPoint+1:]
        path2fh = path2[:cuttingPoint+1]
        path2sh = path2[cuttingPoint+1:]
        
        #print(path2fh)
        #Create new paths
        newPath1 = path1fh + self.greedyPathFinding(path1fh[-1][0], path2sh[0][0]) + path2sh
        newPath2 = path2fh + self.greedyPathFinding(path2fh[-1][0], path1sh[0][0]) + path1sh

        #Check if paths are connected (can be omitted when we are sure that the crossover works correctly)
        newPath1 = self.checkPath(newPath1)
        newPath2 = self.checkPath(newPath2)

        #Create new agents and add them to the population
        nAgent1 = Agent.__new__(Agent)
        nAgent1.__init__("child")
        nAgent1.encoded_path = newPath1
        nAgent2 = Agent.__new__(Agent)
        nAgent2.__init__("child")
        nAgent2.encoded_path = newPath1

        return [nAgent1, nAgent2]

    def nothingMutation(self, baseAgent: Agent) -> Agent:
        """Just for testing purposes, does nothing."""
        return baseAgent #we use deepcopy here since we dont want to have a pointer to the original instead of a new object

    def evaluate(self, agent: Agent, grid:GridWorld) -> None:
        """Evaluate function for an agent."""
        #Deepcopying for every agent is slow (multiprocessing might be way to go)
        tmpGrid = deepcopy(grid)
        for x in range(len(agent.encoded_path)):
            agent.moveCoords(agent.encoded_path[x][0], tmpGrid)
            agent.shiftCoords(agent.encoded_path[x][1], tmpGrid)

        agent.move_count_f1 = len(agent.encoded_path)
        agent.fullCells = tmpGrid.get_full_cells()
        #print(f"F1: {agent.move_count_f1}, F2: {agent.weight_shifted_f2}, F3: {agent.fullCells}")
        self.evalCounter += 1

    def getFronts_old(self):
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

    def getFronts(self):
        """Get fronts by removing already found fronts."""
        fronts = []
        tmpAgents = copy(self.agents)

        while len(tmpAgents) != 0:
            #Here we get the domination count (we make it faster by breaking the loop as soon as the count is bigger than 0)
            for i in range(len(tmpAgents)):
                dominationCounter = 0
                for j in range(len(tmpAgents)):
                    if i != j:
                        #Prepare value lists
                        valueList1 = [tmpAgents[i].move_count_f1, tmpAgents[i].weight_shifted_f2, tmpAgents[i].fullCells]
                        valueList2 = [tmpAgents[j].move_count_f1, tmpAgents[j].weight_shifted_f2, tmpAgents[j].fullCells]
                        if HelperFunctions.getParetoDominance(valueList2, valueList1): #we check if the point we test against gets dominated (in this case i)
                            dominationCounter+=1
                            break #Break the loop since dom count is bigger than 1
                tmpAgents[i].dominationCount = dominationCounter
    
            fronts.append([agent for agent in tmpAgents if agent.dominationCount == 0]) #We append a list of all non dom individuals to the fronts
            tmpAgents = [agent for agent in tmpAgents if agent.dominationCount != 0] #We keep only dominated agents in the tmpAgents list

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
    
    def selection(self, parents: list[Agent]) -> list[Agent]:
        """Binary tournament selection for NSGA2."""
        tmpParents = copy(parents)
        selectedInd = []
        #We want to select as many parents as we defined
        for x in range(int(self.popSize/4)): #Popsize / 4 since we get 2 children from each pair of parents and we keep half of the pop 
            #Randomly choose 2 individuals from the population (we do remove them from the pop since we do not want to use deepcopy)
            agent1 = random.choice(tmpParents)
            agent2 = random.choice(tmpParents)

            #Quick check if the same one got selected:
            if agent1 == agent2:
                selectedInd.append(agent1)
                tmpParents.remove(agent1)
                continue

            if agent1.dominationCount != agent2.dominationCount:
                if agent1.dominationCount < agent2.dominationCount:
                    selectedInd.append(agent1)
                    tmpParents.remove(agent1)
                else:
                    selectedInd.append(agent2)
                    tmpParents.remove(agent2)
            else:
                if agent1.crowdiDist != agent2.crowdiDist:
                    if agent1.crowdiDist > agent2.crowdiDist:
                        selectedInd.append(agent1)
                        tmpParents.remove(agent1)
                    else:
                        selectedInd.append(agent2)
                        tmpParents.remove(agent2)
                else:
                    selectedInd.append(agent1)
                    tmpParents.remove(agent1)
        
        return selectedInd

    def mainLoop(self):
        """Main loop of NSGA2 """
        #Innit -> Crossover Mutation Updating the population
        while self.evalCounter < self.n_eval:
            #Build fronts
            fronts = self.getFronts()
            if self.evalCounter == 500 or self.evalCounter == 950 :
                self.showFront(fronts)
        
            #Get CD for fronts and sort them
            for front in fronts:
                self.calcCrowdingDistance(front)
                front.sort(key=lambda x: x.crowdiDist, reverse=True)

            #Environmental selection
            #When all fronts are sorted, we can join them all together in a list and pick the number of individuals we want more easily
            joinedFronts = []
            for front in fronts:
                joinedFronts += front
            
            #Select surviving individuals and append them to new pop
            newPop = []
            for x in range(int(self.popSize/2)):
                newPop.append(joinedFronts[x])
        
            #Select random parents for crossover
            children = [] #to keep pop size we have to produce as much children as we do have parents
            while len(children) < (self.popSize/2):
                selectedParents = self.selection(newPop) #Select parents from new pop
                children += self.onePointCrossover(selectedParents[0], selectedParents[1])
        
            #Now do mutation for the children and evaluate them
            #print(children)
            #print(newPop)
            for child in children:
                if random.random() < self.mutProb:
                    child = self.nothingMutation(child)
                self.evaluate(child, self.grid)
                #We now check that the individual reached the goal, if not we sample a new one
                if not child.reachedHome: #Home can only be reached if we visited goal first so no need for 2 check
                    #print(child.encoded_path)
                    print(child.encoded_path)
                    print(f"SOMETHING WENT HORRIBLY WRONG, CHILD DID NOT REACH HOME: {child.reachedHome}, {child.reachedGoal}")
                    exit()
            
            #Now merge children and parents lists
            newPop += children

            #Update pop
            self.agents = newPop
            print(f"PopSize: {len(self.agents)}")
            print(f"Evaluations: {self.evalCounter}")