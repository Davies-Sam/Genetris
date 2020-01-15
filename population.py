import os
os.environ['SDL_AUDIODRIVER'] = 'dsp'
import sys
import random
from tetris import TetrisApp
from agent import Agent
import heuristics
import numpy
import names
import struct
import time
import datetime


RESULTS = "%s.txt" % names.get_full_name()

UPPERBOUND = 1
LOWERBOUND = -1


if len(sys.argv) == 1:
    POPSIZE = 1000
    ELITE = 100
    CROSSRATE = 1
    MUTRATE = .3
    SEQUENCE = "fixed"
    NUMGAMES = 10
    SELECTIONTYPE = "roulette"
    CROSSTYPE = "uniform"
else:
    POPSIZE = int(sys.argv[1])
    ELITE = int(sys.argv[2])
    CROSSRATE = float(sys.argv[3])
    MUTRATE = float(sys.argv[4])
    SEQUENCE = sys.argv[5] 
    if SEQUENCE == "fixed":
        NUMGAMES = 1
        SELECTIONTYPE = sys.argv[6]
        CROSSTYPE = sys.argv[7]
    elif SEQUENCE == "random":
        NUMGAMES = int(sys.argv[6])
        SELECTIONTYPE = sys.argv[7]
        CROSSTYPE = sys.argv[8]



#initialize the entire population



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
        self.population = self.InitPop(self.num_of_organisms)   
        #keep track of which organism in the population we are working on
        self.current_organism = 0
        #keeps track of what generation we are on
        self.current_generation = 0
        #GA gets the application
        self.sequenceType = SEQUENCE
        self.seed = numpy.random.random()
        self.app = TetrisApp(self)
        #GA gets our agent, which needs the organism 
        #so it can access weights of the organism
        self.ai = Agent(self.app)
        self.app.ai = self.ai
        self.cycleStart = 0
        self.cycleEnd = 0
        self.fitnessDictionary = {}
        self.lastBest = []

    def RandomOrganism(self):
        nums = []
        for j in range(0, 12):
            a = numpy.random.uniform(LOWERBOUND, UPPERBOUND)
            nums.append(a)
        organism = Organism(nums)
        self.normalize(organism)
        return organism

    def InitPop(self, populationSize):
        #init population with a seed
        #random.seed(7)
        population = []
        #for each organism in the population
        #population.append(Organism([-0.25835108880355967, -0.18873479853738032, -0.6081190254748627, -0.5281331622290867, -0.0936639080926526, -0.10826897335053938, 0.15010957868145391, -0.21161009827721672, -0.04113776799016001, 0.2957493369775496, -0.07093022881256028, -0.2586553756116776]))
        for i in range(0, populationSize):
            organism = self.RandomOrganism()
            population.append(organism)
        #returns a list of a list of 4 bitarrays
        return population

    #start running the game
    def Run(self):
        with open(RESULTS, 'w') as f:
            f.write("\n Cross Type: %s, Selection Type: %s, Crossover Rate: %s, Mutation Rate: %s , Replacement Per Cycle: %s\n" % (CROSSTYPE, SELECTIONTYPE, self.crossover_rate, self.mutation_rate, self.new_organisms))
            #all heuristics
            #f.write("Weights: Aggregate Height, Bumpiness, Holes, LinesCleared, Connected Holes, Blockades, Altitude Delta, Weighted Blocks, H-Roughness, V-Roughness, Wells, Biggest Well, Total Height.\n Mutation Rate: %s , Replacement Per Cycle: %s\n" % (self.mutation_rate, self.new_organisms))
        self.cycleStart = time.time()
        self.app.run()

    #This def 
    def NextAI(self):
        self.current_organism += 1
        #if we have worked on every organism in the current population, get the next
        #generation
        self.app.piecesPlayed = 0
        if self.current_organism >= self.num_of_organisms:
            self.current_organism = 0 
            self.NextGeneration()

        #this is for if we keep the same sequence for every generation and each organism only plays 1 game - we can use this to skip playing the elites
        if SEQUENCE == "fixed" and NUMGAMES == 1:
            while self.current_organism < self.num_of_organisms and tuple(self.population[self.current_organism].heuristics) in self.fitnessDictionary.keys():
                #print("ALREADY SEEN %s" % self.population[self.current_organism].heuristics)
                self.population[self.current_organism].fitness = self.fitnessDictionary[tuple(self.population[self.current_organism].heuristics)]
                self.current_organism += 1
        
        if self.current_organism >= self.num_of_organisms:
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
        if organism.played == NUMGAMES:
            self.fitnessDictionary[tuple(organism.heuristics)] = organism.fitness
            self.NextAI()
            if SEQUENCE == "fixed":
                self.app.start_game(self.seed)
            elif SEQUENCE == "random":
                self.app.start_game(numpy.random.random())
        else:       
            #restart the game
            self.app.piecesPlayed = 0
            if SEQUENCE == "fixed":
                self.app.start_game(self.seed)
            elif SEQUENCE == "random":
                self.app.start_game(numpy.random.random())

    #add normalization
    def normalize(self, org):
        squared = []
        for h in org.heuristics:
            squared.append(h*h)
        norm = numpy.sqrt(sum(squared))
        for i, weight in enumerate(org.heuristics):
            org.heuristics[i] /= norm

    #check if the population has converged -- TOD0 
    
    #tournament selection might be more valuable. add this 
    def tournament(self):
        indices = [ i for i in range(0,len(self.population))]
        #since the population is sorted, just select the two smallest indices from the pool.
        v1 = None 
        v2 = None

        x = int(self.num_of_organisms * .1 )
       
        for a in range(0, x):
            selected = numpy.random.choice(indices)
            if v1 == None or selected < v1 :
                v2 = v1
                v1 = selected
            elif v2 == None or selected < v2:
                v2 = selected
       
        return self.population[v1], self.population[v2]
    
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
            f.write("\nGeneration: %s,  Sequence Type: %s, Cycle Time: %s  Elite Average Lines Cleared in %s Games: %s\n" % (self.current_generation, SEQUENCE, str(datetime.timedelta(seconds = self.cycleEnd)), NUMGAMES, averageScore))
            
            for a in self.population:
                f.write("%s, Age: %s Weights: %s - Lines Cleared:%s\n" % (a.name, a.age, a.heuristics, a.fitness))
        
        for key in self.fitnessDictionary.keys():
            if key not in [tuple(org.heuristics) for org in self.population]:
                del self.fitnessDictionary[key]
       
        #increment the generation
        self.current_generation += 1
        #create the new population with only the survivors
        self.SelectSurvivors()

        eliteScores = [org.fitness for org in self.population[:self.survivors]]
        if eliteScores == self.lastBest:
            self.mutation_rate += .05
        #create the new organisms to add to the new_pop

      #roulette selction
        if SELECTIONTYPE == "roulette":
            for x in range (0, self.new_organisms):
                #select two parents
                parent1 = self.roulette()
                parent2 = self.roulette()
                while parent1 == parent2:
                    parent2 = self.roulette()
                #print("p1: %s , p2: %s" % (parent1.name, parent2.name))
                #create the new organism
                a = self.Crossover(parent1,parent2)
                #mutate the children
                if numpy.random.random() < MUTRATE:       
                    self.mutate(a)
                #add to population  
                self.population.append(a)
        elif SELECTIONTYPE == "tournament":
            #tounament selection
            for x in range (0, self.new_organisms):
                p1, p2 = self.tournament()
                while p1 == p2 or p1.fitness == 0 or p2.fitness == 0:
                    p1, p2 = self.tournament()
                new = self.Crossover(p1,p2)
                if numpy.random.random() < MUTRATE: 
                    self.mutate(new)
                self.population.append(new)
        
  
        #reset the fitness to 0
        for org in self.population:
                org.played = 0
                org.fitness = 0

        self.lastBest = eliteScores
        self.cycleStart = time.time()
        
        #check to make sure we have the correct number of organisms in the new
        #population
        assert self.num_of_organisms == len(self.population), "ERROR: new population doesnt the correct number of organisms have %s, want %s" % (len(self.population),self.num_of_organisms)

    #Will return the survivors of a population, will return self.survivors number of organisms 
    def SelectSurvivors(self):
        #sort the population by Organism.fitness    
        self.population.sort(key=lambda x: x.fitness, reverse=True)  
        #kill off amount needed to introduce specified amount of new organisms
        self.population = self.population[:self.survivors]
        for organism in self.population:
            organism.age += 1

    #takes two parents and does uniform crossover
    #returns an Organism
    def Crossover(self, parent1, parent2):
        child = []
        #two point 

        # add other crossover methods that can be specified at launch and crossover using the CROSSRATE

        #uniform crossover
        if CROSSTYPE == "uniform":
            for x in range(0, len(parent1.heuristics)):
                if numpy.random.random() < .5:
                    child.append(parent1.heuristics[x])
                else:
                    child.append(parent2.heuristics[x])

        elif CROSSTYPE == "average":
        #weighted average crossover 
            a = parent1.fitness
            b = parent2.fitness
            for x in range(0, len(parent1.heuristics)):
               child.append( (a * parent1.heuristics[x] ) + ( b * parent2.heuristics[x] ) )
        
        offspring = Organism(child)
        #print("CROSSOVER NORMALIZING %s" % offspring.heuristics)
        self.normalize(offspring)
        return offspring
            
    #mutates the weights of a chromosome
    def mutate(self, organism):
        #mutation range of -.2 to +.2
        mutation = numpy.random.random() * .4 - .2
        #choose a random weight to mutate
        x = numpy.random.randint(0,12)
        organism.heuristics[x] += mutation
        self.normalize(organism)
                
if __name__ == "__main__":
    GA().Run()

# Theoretical fitness limit = rounds * pieces * piece size / columns
#Theoretical fitness limit = 1 * 500 * 4 / 10 = 200 
