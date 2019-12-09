#Our organisms and Evolutionary functions live here#

#AI FINAL PROJECT BRAINSTORMING
#need to store genes using a list of bitstrings
#https://pypi.org/project/bitstring/

import random
from tetris import TetrisApp
from agent import Agent
from bitstring import BitArray
from enum import Enum
import heuristics


################################################################################
  #bitarray is annoying! we will represent the weights in decimal
    #when the crossover and mutation operations are done
    #we will convert into binary format "bin(num)", operate, and convert back!

def RandomOrganism():
    nums = []
    for j in range(0, 4):
        a = random.randint(-128,127)
        nums.append(a)
    organism = Organism(nums)
    return organism

#initialize the entire population

def InitPop(populationSize):
    #init population with a seed
    #random.seed(7)
    population = []

    #for each organism in the population
    for i in range(0, populationSize):
        organism = RandomOrganism()
        population.append(organism)
    #returns a list of a list of 4 bitarrays
    return population

class Organism(object):
    def __init__(self, heurisitcs): 
        self.heuristics = heurisitcs 
        self.fitness = 0

#population is a list of lists(the organisms) which contain the genes(bitarrays)
#
#population -> [organism0, organism1, .. , organism99]
#organism -> [BitArray0, BitArray1, BitArray2, BitArray3]
#

###################################################################################
class GA(object):
    def __init__(self):
        self._num_of_organisms = 100
        self._survivors = 98
        self._new_organisms = self._num_of_organisms - self._survivors
        self._mutation_rate = 20
        self._convergence_threshold = 85

        #initialize the population
        self.population = InitPop(self._num_of_organisms)
      
        #keep track of which organism in the population we are working on
        self.current_organism = 0
        #keeps track of what generation we are on
        self.current_generation = 0

        #get the current organism
        self.currentOrganism = self.population[self.current_organism]

        #GA gets the application
        self.app = TetrisApp(self, True)

        #GA gets our agent, which needs the organism 
        #so it can access weights of the organism
        self.ai = Agent(self.app)
        self.app.ai = self.ai

    #start running the game
    def Run(self):
        self.app.run()

    #This def 
    def NextAI(self):
        self.current_organism += 1
        #if we have worked on every organism in the current population, get the next
        #generation
        if self.current_organism >= self.population._num_of_organisms:
            self.current_organism = 0
            self.NextGeneration()

        #update the heuristics for the organism we are working on
        self.ai.heuristics = self.population[self.current_organism].heuristics

    #handles when a game we are testing the current organism on ends
    def GameOver(self, current_score):
        organism = self.population[self.current_organism]
        organism.fitness = current_score

        #load the next organism into the algo
        self.NextAI()

        #restart the game
        self.app.start_game()

    #check if the population has converged
    def PopConvergenced(self):
        pop = self.population
        #check each organism in the population and see if the genes in the population
        #are close to each other (have similar values)
        return all(all(pop[0].heuristics[f]-self._convergence_threshold < weights < pop[0].heuristics[f] + self._convergence_threshold for f, weights in current_organism.heuristics.items()) for organism in pop)

    #this def takes the current population, removes the worst two organisms and 
    #re-produces two new ones to add to the population
    def NextGeneration(self):
        #if the population has converged, dont need another generation, print out
        #the genes and weights for each organism in the converged population
        if self.PopConvergenced():
            print("The Population has converged on generation %s\n", self.current_generation)
        #else the population has not converged, remove two worst organisms
        #create two new children to add to the next generation
        print("CURRENT GENERATION: %s" % self._current_generation)
        #to get average fitness, sum up the total_fitness for each organism/chromosome
        #then divide by _num_of_organisms
        print("AVERAGE FITNESS: %s", (sum([]) / self._num_of_organisms))
        #increment the generation
        self.current_generation += 1
        #create the new population with only the survivors
        new_pop = self.SelectSurvivors(self._survivors, self._selection)
        """
        #rethink this approach - we should create 2 new, evaluate them, and then check against the worst 2 organisms
        if they are better than the bottom 2, replace the bottom 2 with them """     
        
        #create the new organisms to add to the new_pop
        for a in range(self._new_organisms):
            #select two parents
            parents = self._selection(2, self._selection)
            #create the new organisms and add them to the new_pop
            new_pop.append(self._crossover(parents[0], parents[1], self._crossover))
        #go through the new organism's bits and apply the chance to mutate
        #right now we do this once
        for organism in new_pop:
            self.mutation(organism, self._mutation_rate)
        #check to make sure we have the correct number of organisms in the new
        #population
        assert len(new_pop) == len(self._population), "ERROR: new population doesnt have enough organisms"
        self.population = new_pop


    #Will return the survivors of a population, will return self.survivors number of organisms 
    def SelectSurvivors(self):
        #sort the population by Organism.fitness
        #chop off the bottom 2
        return
       
    
    #We need a crossover fucntion - given 2 parents produce a new orangism


    #We need a mutation function - will convert the numbers to binary then operate and convert back. "int(0b010101)" will go from binary to to decimal


  
if __name__ == "__main__":
    GA().Run()
                
