#Our organisms and Evolutionary functions live here#

#AI FINAL PROJECT BRAINSTORMING
#need to store genes using a list of bitstrings
#https://pypi.org/project/bitstring/

import random
from tetris import TetrisApp
from agent import Agent
#from bitstring import BitArray
from enum import Enum
import heuristics
import numpy

################################################################################
  #bitarray is annoying! we will represent the weights in decimal
    #when the crossover and mutation operations are done
    #we will convert into binary format "bin(num)", operate, and convert back!

def RandomOrganism():
    nums = []
    for j in range(0, 4):
        a = random.randint(0, 255)
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
    def __init__(self, heuristics): 
        self.heuristics = heuristics 
        self.fitness = 0

#population is a list of lists(the organisms) which contain the genes(bitarrays)
#
#population -> [organism0, organism1, .. , organism99]
#organism -> [BitArray0, BitArray1, BitArray2, BitArray3]
#

###################################################################################
class GA(object):
    def __init__(self):
        self.num_of_organisms = 100
        self.survivors = 98
        self.new_organisms = self.num_of_organisms - self.survivors
        self.mutation_rate = .2
        self.convergence_threshold = 85
        #initialize the population
        self.population = InitPop(self.num_of_organisms)   
        #keep track of which organism in the population we are working on
        self.current_organism = 0
        #keeps track of what generation we are on
        self.current_generation = 0
        #get the current organism
        self.currentOrganism = self.population[self.current_organism]
        #GA gets the application
        self.app = TetrisApp(self)
        #GA gets our agent, which needs the organism 
        #so it can access weights of the organism
        self.ai = Agent(self.app)
        self.app.ai = self.ai

    #start running the game
    def Run(self):
        
        """ mutation & crossover tests
        a = Organism([9,32,4,222])
        print("before mutation")
        print(a.heuristics)
        print("\n")
        self.mutate(a,20)
        print("after mutation: \n")
        print(a.heuristics)
        
        b = Organism([21,7,62,100])
        c = self.Crossover(a,b)
        print(c.heuristics)
        """
        """ pruning test
        self.SelectSurvivors()
        for i in self.population:
            print(i.heuristics)
        """
        
        self.app.run()

    #This def 
    def NextAI(self):
        self.current_organism += 1
        #if we have worked on every organism in the current population, get the next
        #generation
        if self.current_organism >= self.num_of_organisms:
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
    """
    def PopConvergenced(self):
        pop = self.population
        #check each organism in the population and see if the genes in the population
        #are close to each other (have similar values)
        return all(all(pop[0].heuristics[f]-self.convergence_threshold < weights < pop[0].heuristics[f] + self.convergence_threshold for f, weights in self.current_organism.heuristics.items()) for organism in pop)
    """
    #this def takes the current population, removes the worst two organisms and 
    #re-produces two new ones to add to the population
    def NextGeneration(self):
        #if the population has converged, dont need another generation, print out
        #the genes and weights for each organism in the converged population
        #if self.PopConvergenced():
        #    print("The Population has converged on generation %s\n", self.current_generation)
        #else the population has not converged, remove two worst organisms
        #create two new children to add to the next generation
        print("CURRENT GENERATION: %s" % self.current_generation)
        #to get average fitness, sum up the total_fitness for each organism/chromosome
        #then divide by _num_of_organisms
        print("AVERAGE FITNESS: %s", (sum([]) / self.num_of_organisms))
        #increment the generation
        self.current_generation += 1
        #create the new population with only the survivors
        self.SelectSurvivors()
        """
        #rethink this approach - we should create 2 new, evaluate them, and then check against the worst 2 organisms
        if they are better than the bottom 2, replace the bottom 2 with them """     
        print("after pruning:")
        print(len(self.population))
        #create the new organisms to add to the new_pop
        
        #select two parents
        parents = random.sample(self.population, 2)
        #create the new organisms and add them to the new_pop
        a = self.Crossover(parents[0],parents[1])
        b = self.Crossover(parents[0],parents[1])
        self.mutate(a, self.mutation_rate)
        self.mutate(b, self.mutation_rate)
        self.population.append(a)
        self.population.append(b)
        #go through the new organism's bits and apply the chance to mutate
        print("after reproduction:")
        print(len(self.population))
      

        #check to make sure we have the correct number of organisms in the new
        #population
       
        #assert 2 == len(self.population), "ERROR: new population doesnt have enough organisms"


    #Will return the survivors of a population, will return self.survivors number of organisms 
    def SelectSurvivors(self):
        #sort the population by Organism.fitness
        #make this more modular later by changing the 'magic number' 2 to a variable
        self.population.sort(key=lambda x: x.fitness)
        #remove the last 2 (least fit)
        self.population = self.population[:len(self.population)-2]
       
    #We need a crossover fucntion - given 2 parents produce a new orangism
    #make sure the binary representations are all the same length, pad with 0 at front
    #account for - in position [0]
    #account for "b" in the array aswell.

    #takes two parents and does uniform crossover
    #returns an Organism
    def Crossover(self, parent1, parent2):
        weights = []
        for i in range(0, len(parent1.heuristics)):
            if random.uniform(0,1) > .5:
                weights.append(parent1.heuristics[i])
            else:
                weights.append(parent2.heuristics[i])
        return Organism(weights)

    #We need a mutation function - will convert the numbers to binary then operate and convert back. "int(0b010101)" will go from binary to to decimal

    #after an organism is created, apply the mutation chance
    #chromosome is an array of 4 ints
    #returns the weights as a list of four ints
    def mutate(self, organism, mutation_chance):
        randomNew = RandomOrganism()
        for num, weight in enumerate(organism.heuristics):
            temp = list(numpy.binary_repr(weight, width=8))
            temp2 = list(numpy.binary_repr(randomNew.heuristics[num], width=8))
            for i in range(0,len(temp)):
                if random.uniform(0,1) > (1 - self.mutation_rate):
                    temp[i] = temp2[i]
            organism.heuristics[num] = int(''.join(str(i) for i in temp), 2)
                    
  
if __name__ == "__main__":
    GA().Run()
                
