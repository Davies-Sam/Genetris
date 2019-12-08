#Our organisms and Evolutionary functions live here#

#AI FINAL PROJECT BRAINSTORMING
#need to store genes using a list of bitstrings
#https://pypi.org/project/bitstring/

import random
from tetris import TetrisApp
from agent import Agent




    ################################################################################
def init_pop():
    #init population with a seed
    random.seed(7)
    population = []
    organism = []

    #for each organism in the population
    for i in range(0, self._num_of_organisms):
        #create the 4 genes + attach them to list
        #the order is Height, Bumpiness, Holes, LinesCleared
        for j in range(0, 4):
            organism.append(BitArray(bin = random.randint(-128, 127)))
        #append the organism to the population
        population.append(organism)
        organism.clear()

    #returns a list of a list of 4 bitarrays
    return population

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
        self._selection = SelectionMethod.roulette
        self._crossover = CrossoverMethod.random_attributes
        self._mutation_rate = 20
        self._num_times_to_mutate = 3
        self._convergence_threshold = 85

        #initialize the population
        self.population = init_pop()
        #GA gets the application
        self.app = TetrisApp(self)
        #GA gets our agent
        self.ai = Agent(self.app)
        self.app.ai = self.ai
        #init the population of organisms
        self.population = 0

        #keep track of which organism in the population we are working on
        self.current_organism = 0
        #keeps track of what generation we are on
        self.current_generation = 0
        #set the ai heuristics to the first organism's heuristics
        self.ai.heuristics = self.population[self.current_organism].heuristics

    #start running the game
    def run(self):
        self.app.run()

    #This def 
    def next_AI(self):
        self.current_organism += 1
        #if we have worked on every organism in the current population, get the next
        #generation
        if self.current_organism >= self.population._num_of_organisms:
            self.current_organism = 0
            self.next_generation()

        #update the heuristics for the organism we are working on
        self.ai.heuristics = self.population[self.current_organism].heuristics

    #handles when a game we are testing the current organism on ends
    def game_over(self, current_score):
        chromo = self.population[self.current_organism]
        chromo.games += 1
        chromo.total_fitness += current_score
        
        #load the next organism into the algo
        self.next_AI()

        #restart the game
        self.app.start_game()

    #check if the population has converged
    def pop_convergenced(self):
        pop = self.population

        #check each organism in the population and see if the genes in the population
        #are close to each other (have similar values)
        return all(all(pop[0].heuristics[f]-self._convergence_threshold < weights < pop[0].heuristics[f] + self._convergence_threshold for f, weights in current_organism.heuristics.items()) for organism in pop)

    #this def takes the current population, removes the worst two organisms and 
    #re-produces two new ones to add to the population
    def next_gen(self):
        #if the population has converged, dont need another generation, print out
        #the genes and weights for each organism in the converged population
        if self.pop_convergenced():
            print("The Population has converged on generation %s\n", )


        #else the population has not converged, remove two worst organisms
        #create two new children to add to the next generation

        print("CURRENT GENERATION: %s" % self._current_generation)
        #to get average fitness, sum up the total_fitness for each organism/chromosome
        #then divide by _num_of_organisms
        print("AVERAGE FITNESS: %s", (sum([]) / self._num_of_organisms))

        #increment the generation
        self.current_generation += 1
        #create the new population with only the survivors
        new_pop = self.selection(self._survivors, self._selection)

        #create the new organisms to add to the new_pop
        for a in range(self._new_organisms):
            #select two parents
            parents = self._selection(2, self._selection)
            #create the new organisms and add them to the new_pop
            new_pop.append(self._crossover(parents[0], parents[1], self._crossover))

        #go through the new organism's bits and apply the chance to mutate
        #right now we do this three times per new organism
        for a  in range(self._num_times_to_mutate):
            for chomo in new_pop:
                self.mutation(chromo, self._mutation_rate / self._num_times_to_mutate)

        #check to make sure we have the correct number of organisms in the new
        #population
        assert len(new_pop) == len(self._population), "ERROR: new population doesnt have enough organisms"
        self.population = new_pop

    def selection():