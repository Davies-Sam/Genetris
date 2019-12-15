#Our organisms and Evolutionary functions live here#

#AI FINAL PROJECT BRAINSTORMING
#need to store genes using a list of bitstrings
#https://pypi.org/project/bitstring/
import sys
import random
from tetris import TetrisApp
from agent import Agent
#from bitstring import BitArray
from enum import Enum
import heuristics
import numpy
import names
import struct
import time
import datetime

results = "%s-%s-%s-%s" % (sys.argv[1],sys.argv[2],sys.argv[3],sys.argv[4])
RESULTS = "%s.txt" % results
PLAYLIMIT = 1

POPSIZE = int(sys.argv[1])
ELITE = int(sys.argv[2])
CROSSRATE = float(sys.argv[3])
MUTRATE = float(sys.argv[4])

################################################################################
#binary format not used. gaussian mutation added.
################################################################################
def float_to_bin(num):
    return format(struct.unpack('!I', struct.pack('!f', num))[0], '032b')

def bin_to_float(binary):
    return struct.unpack('!f',struct.pack('!I', int(binary, 2)))[0]
#################################################################################
    
def RandomOrganism():
    nums = []
    for j in range(0, 12):
        a = round(numpy.random.uniform(-1.0,1.0),4)
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
        self.name = names.get_full_name()
        self.age = 0
        self.played = 0


###################################################################################
class GA(object):
    def __init__(self):
        self.num_of_organisms = POPSIZE
        self.survivors = ELITE
        self.new_organisms = self.num_of_organisms - self.survivors
        self.mutation_rate = MUTRATE
        self.crossover_rate = CROSSRATE
        #initialize the population
        self.population = InitPop(self.num_of_organisms)   
        #keep track of which organism in the population we are working on
        self.current_organism = 0
        #keeps track of what generation we are on
        self.current_generation = 0
        #GA gets the application
        self.app = TetrisApp(self)
        #GA gets our agent, which needs the organism 
        #so it can access weights of the organism
        self.ai = Agent(self.app)
        self.app.ai = self.ai
        self.cycleStart = 0
        self.cycleEnd = 0
        self.fitnessDictionary = {}

    #start running the game
    def Run(self):
        with open(RESULTS, 'w') as f:
            f.write("Weights: TotalHeight, Bumpiness, Holes, LinesCleared, Connected Holes, Blockades, Altitude Delta, Weighted Blocks, H-Roughness, V-Roughness.\n Mutation Rate: %s , Replacement Per Cycle: %s\n" % (self.mutation_rate, self.new_organisms))
        self.cycleStart = time.time()
        self.app.run()

    #This def 
    def NextAI(self):
        self.current_organism += 1
        #if we have worked on every organism in the current population, get the next
        #generation
        
        if self.current_organism >= self.num_of_organisms:
            self.current_organism = 0 
            self.NextGeneration()

        while self.current_organism < self.num_of_organisms and tuple(self.population[self.current_organism].heuristics) in self.fitnessDictionary.keys():
            #print("ALREADY SEEN %s" % self.population[self.current_organism].heuristics)
            self.population[self.current_organism].fitness = self.fitnessDictionary[tuple(self.population[self.current_organism].heuristics)]
            self.current_organism += 1

        if self.current_organism > self.num_of_organisms:
            self.current_organism = 0 
            self.NextGeneration()
        
        #update the heuristics for the organism we are working on
        self.ai.heuristics = self.population[self.current_organism].heuristics

    #handles when a game we are testing the current organism on ends
    def GameOver(self, lines_cleared):
        organism = self.population[self.current_organism]     
        organism.fitness += lines_cleared   
        #load the next organism into the algo
        organism.played +=1
        if organism.played == PLAYLIMIT:
            self.fitnessDictionary[tuple(organism.heuristics)] = organism.fitness
            self.NextAI()
            self.app.start_game(numpy.random.random())
        else:       
            #restart the game
            self.app.start_game(numpy.random.random())

    #check if the population has converged -- TOD0 
    
    #roulette selection 
    def roulette(self):
        fSum = float(sum([org.fitness for org in self.population]))
        relativeFitness = []
        for x in range(0, len(self.population)):
            relativeFitness.append(self.population[x].fitness/fSum)
        #worse organisms are more likey to miss in roulette
        probs = [sum(relativeFitness[:i+1]) for i in range(len(relativeFitness))]
        r = random.random()
        for i, organism in enumerate(self.population):
            if r <= probs[i]:              
                return organism
        
    #this def takes the current population, removes the worst two organisms and 
    #re-produces two new ones to add to the population
    def NextGeneration(self):
        self.population.sort(key=lambda x: x.fitness, reverse=True)
        averageScore = 0 
        elite = self.population[:self.survivors]
        for a in elite:
            averageScore += a.fitness
        averageScore = averageScore/len(elite)

        self.cycleEnd = time.time() - self.cycleStart

        #print the last generation out
        with open(RESULTS, 'a') as f:
            f.write("\nGeneration: %s, Cycle Time: %s  Elite Average Lines Cleared in %s Games: %s\n" % (self.current_generation, str(datetime.timedelta(seconds = self.cycleEnd)), PLAYLIMIT, averageScore))
            
            for a in self.population:
                f.write("%s, Age: %s Weights: %s - Lines Cleared:%s\n" % (a.name, a.age, a.heuristics, a.fitness))

        for key in self.fitnessDictionary.keys():
            if key not in [tuple(org.heuristics) for org in self.population]:
                del self.fitnessDictionary[key]

        #increment the generation
        self.current_generation += 1
        #create the new population with only the survivors
        self.SelectSurvivors()

        #create the new organisms to add to the new_pop
      
        for x in range (0, int(self.new_organisms/2)):
            #select two parents
            parent1 = self.roulette()
            parent2 = self.roulette()
            while parent1 == parent2:
                parent2 = self.roulette()
            #print("p1: %s , p2: %s" % (parent1.name, parent2.name))
            #create the new organism
            a, b = self.Crossover(parent1,parent2)
            #mutate the children       
            self.mutate(a)
            self.mutate(b)  
            #add to population  
            self.population.append(a)
            self.population.append(b)
        #add last one
        if self.new_organisms % 2 == 1:
            parent1 = self.roulette()
            parent2 = self.roulette()
            while parent1 == parent2:
                parent2 = self.roulette()
            #print("p1: %s , p2: %s" % (parent1.name, parent2.name))
            #create the new organism
            a, b = self.Crossover(parent1,parent2)
            #mutate the children       
            self.mutate(a)
            self.population.append(a)
  
        #reset the fitness to 0
        for org in self.population:
                org.played = 0
                org.fitness = 0

        self.cycleStart = time.time()
        
        #check to make sure we have the correct number of organisms in the new
        #population
        assert self.num_of_organisms == len(self.population), "ERROR: new population doesnt the correct number of organisms have %s, want %s" % (len(self.population),self.num_of_organisms)

    #Will return the survivors of a population, will return self.survivors number of organisms 
    def SelectSurvivors(self):
        #sort the population by Organism.fitness    
        self.population.sort(key=lambda x: x.fitness, reverse=True)  
        #kill off amount needed to introduce specified amount of new organisms
        self.population = self.population[:len(self.population)-(self.new_organisms)]
        for organism in self.population:
            organism.age += 1

    #takes two parents and does uniform crossover
    #returns an Organism
    def Crossover(self, parent1, parent2):
        child1 = []
        child2 = []
        #two point 
        """
        if numpy.random.random() < .5:
        #first otion is two point at alleles 3, 7 resulting in the regeion 4 - 7 (middle genes)
            for x in range(0, len(parent1.heuristics)):
                if x > 3 and x < 8:
                    child2.append(parent1.heuristics[x])
                    child1.append(parent2.heuristics[x])
                else:
                    child1.append(parent1.heuristics[x])
                    child2.append(parent2.heuristics[x])
        else:
            """
       #crossover based on the crossover rate 
        for x in range(0, len(parent1.heuristics)):
            if numpy.random.random() < self.crossover_rate:
                child2.append(parent1.heuristics[x])
                child1.append(parent2.heuristics[x])
            else:
                child1.append(parent1.heuristics[x])
                child2.append(parent2.heuristics[x])        
        return Organism(child1), Organism(child2)
            
    #mutates the weights of a chromosome
    def mutate(self, organism):
        for num, weight in enumerate(organism.heuristics):
            if numpy.random.random() < self.mutation_rate:
                rVal = numpy.random.uniform(-1.0,1.0, 1)
                organism.heuristics[num] = round(weight + rVal, 4)
                
if __name__ == "__main__":
    GA().Run()
                
