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
import names
import struct 
################################################################################
#currently unused - ran into issue with floating point mutations
################################################################################
def float_to_bin(num):
    return format(struct.unpack('!I', struct.pack('!f', num))[0], '032b')

def bin_to_float(binary):
    return struct.unpack('!f',struct.pack('!I', int(binary, 2)))[0]
#################################################################################
    
def RandomOrganism():
    nums = []
    for j in range(0, 10):
        #a = random.randint(-128, 127)
        a = round(random.uniform(-1, 1),4)
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

#population is a list of lists(the organisms) which contain the genes(bitarrays)
#
#population -> [organism0, organism1, .. , organism99]
#organism -> [BitArray0, BitArray1, BitArray2, BitArray3]
#

###################################################################################
class GA(object):
    def __init__(self):
        self.num_of_organisms = 20
        self.survivors = 4
        self.new_organisms = self.num_of_organisms - self.survivors
        self.mutation_rate = .05
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

    #start running the game
    def Run(self):
        with open('resultsFixed.txt', 'w') as f:
            f.write("Weights: TotalHeight, Bumpiness, Holes, LinesCleared, Connected Holes, Blockades, Altitude Delta, Weighted Blocks, H-Roughness, V-Roughness.\n Mutation Rate: %s , Replacement Per Cycle: %s\n" % (self.mutation_rate, self.new_organisms))
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
    def GameOver(self, lines_cleared):
        organism = self.population[self.current_organism]     
        organism.fitness = lines_cleared
       
        #load the next organism into the algo
        self.NextAI()
        #restart the game
        self.app.start_game(1)

    #check if the population has converged
    

    # roulette selection 
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
        averageScore = 0 
        for a in self.population:
            averageScore += a.fitness
        averageScore = averageScore/len(self.population)
        self.population.sort(key=lambda x: x.fitness, reverse=True)
        #print the last generation out
        with open('resultsFixed.txt', 'a') as f:
            f.write("\nGeneration: %s , Average Lines Cleared: %s\n" % (self.current_generation, averageScore))
            for a in self.population:
                f.write("%s, Age: %s Weights: %s - Lines Cleared:%s\n" % (a.name, a.age, a.heuristics, a.fitness))
                
        #increment the generation
        self.current_generation += 1
        #create the new population with only the survivors
        self.SelectSurvivors()
  
        #create the new organisms to add to the new_pop
        for x in range (0, self.new_organisms):
            #select two parents
            parent1 = self.roulette()
            parent2 = self.roulette()
            while parent1 == parent2:
                parent2 = self.roulette()
            print("p1: %s , p2: %s" % (parent1.name, parent2.name))
            #print("SELECTED PARENTS %s %s" % (parents[0].name, parents[1].name))
            #create the new organism
            a = self.Crossover(parent1,parent2)
            #mutate the child
            #print("child: %s\n" % a.heuristics)
            self.mutate(a,self.mutation_rate)
            #print("mutated: %s\n" % a.heuristics)
            #add to population  
            self.population.append(a)
        
        #check to make sure we have the correct number of organisms in the new
        #population
       
        assert self.num_of_organisms == len(self.population), "ERROR: new population doesnt have enough organisms"


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
        weights = []
    
        for x in range(0, len(parent1.heuristics)):
            p1 = list(float_to_bin(parent1.heuristics[x]))
            p2 = list(float_to_bin(parent1.heuristics[x]))
            temp = p1
            m = 16
            for i in range(0, 16):
                if random.random() < .5:
                    temp[m] = p1[m]
                else:
                    temp[m] = p2[m]
            x = round(bin_to_float(''.join(str(i) for i in temp)), 2)
            weights.append(x)

        return Organism(weights)


    #mutates the weights of a chromosome
    def mutate(self, organism, mutation_chance):
        for num, weight in enumerate(organism.heuristics):    
            binWeight = float_to_bin(weight)
            temp = list(binWeight)     
            #we want to lower the frequency of mutating the signed bit (too large a change)
            if random.random() < self.mutation_rate/2:
                if temp[0] == '0':
                        temp[0] = '1'
                else:
                        temp[0] = '0'
            x = 16
            for i in range(0,16):
                if random.random() < self.mutation_rate:
                    if temp[x] == '0':
                        temp[x] = '1'
                    else:
                        temp[x] = '0'
                x += 1          
            x = round(bin_to_float(''.join(str(i) for i in temp)),4)
            organism.heuristics[num] = x

                    
  
if __name__ == "__main__":
    GA().Run()
                
