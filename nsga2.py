from grid_world import GridWorld
from agent import Agent
from copy import deepcopy
from helper_functions import HelperFunctions
from random import choice
class NSGA2():
    #Variables
    popSize = 100
    n_eval = 1000
    agents: list[Agent] = []
    mutProb = 0.1 #Mutation probability
    crossProb = 0.1 #Crossover probability
    evalCounter = 0

    def __init__(self) -> None:
        """Init method creates grid world and prepares agents for the algorithm."""
        #Create grid world
        self.grid = GridWorld() #standard size used

        #Create initial population (they are blank here)
        for x in range(self.popSize):
            tmpAgent = Agent(name=x)
            self.agents.append(deepcopy(tmpAgent))
            del tmpAgent #Memory management is comming to town (making sure that the agent is unique and has no pointers attached)
        
        #Sample path and evaluate directly afterwards
        for x in range(len(self.agents)):
            self.samplePath(self.agents[x], self.grid)
            #Evaluate directly after path sampling
            self.evaluate(self.agents[x])

        #Build fronts
        self.getFronts()
        


    def samplePath(self, agent: Agent, grid: GridWorld) -> None:
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
        agent.fullCells = tmpGrid.get_full_cells()


    def nothingCrossover(self, parent1: Agent, parent2: Agent) -> tuple[Agent, Agent]:
        """Just for testing purposes, does nothing."""
        return parent1, parent2
    
    def nothingMutation(self, baseAgent: Agent) -> Agent:
        """Just for testing purposes, does nothing."""
        return baseAgent

    def evaluate(self, agent: Agent) -> None:
        """Evaluate function for an agent."""
        self.evalCounter += 1
        #agent.print_results(agent.fullCells)

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
        
        print(fronts)
        print(len(self.agents))
                 

    def mainLoop(self):
        """Main loop of NSGA2 """
        pass