#Our organisms and Evolutionary functions live here#

#AI FINAL PROJECT BRAINSTORMING
#need to store genes using a list of bitstrings
#https://pypi.org/project/bitstring/

import random

#
#population is a list of lists(the organisms) which contain the genes(bitarrays)
#
#population -> [organism0, organism1, .. , organism99]
#organism -> [BitArray0, BitArray1, BitArray2, BitArray3]
#
#global to keep track of the number of organisms
_num_of_organisms = 100

def init_pop():

    #init population with a seed
    random.seed(7)
    population = []
    organism = []

    #for each organism in the population
    for i in range(0, num_of_organisms):
        #create the 4 genes + attach them to list
        for j in range(0, 4):
            organism.append(BitArray(bin = random.randint(-128, 127)))
        #append the organism to the population
        population.append(organism)
        organism.clear()

    #returns a list of a list of 4 bitarrays
    return population
