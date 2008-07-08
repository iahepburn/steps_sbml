from libsbml import *
import cPickle
import sys
import io
import control as c
import sbmlImporter

#####
# Usage script to run one simulation
def usage():
    print "Give me three args: the number of sec to simulate and the dt" 


#####
# Grabbing the argument

if (len(sys.argv) != 3): # Two arguments + the name of the script
    print usage()
    exit() # For ipython
    sys.exit()

nSec = int(sys.argv[1]) #sec
dt_exp = int(sys.argv[2]) 

#############
# STEP Setup
############

# Setting the kinetic simulation
import steps.model as smodel
mdl = smodel.Model()

############ 
#### STEPS geometry


# setting the geometry
import steps.geom.wm as swm
mesh = swm.Geom()
comp = swm.Comp('comp', mesh)
comp.addVolsys('vsys')
# Setting the Volume
volsys = smodel.Volsys('vsys', mdl)


#Importing things from the SBML
#
sbmlFile = "BIOMD0000000152.xml"
iSbml = sbmlImporter.Interface(sbmlFile)

volComp = iSbml.getVolume()

# Convert the volume to METER (Native unit of STEPS
# 1 l = 10^-3 m
volComp = volComp * pow(10,-3)
comp.vol = volComp

# Getting the variuos species
species = iSbml.getSpecies() #Dict specie --> concentration

mols = iSbml.setMols(smodel, mdl, species) # Name Specie --> Mols in STEPS

reactions = iSbml.getReactions(mols)

print "reactions : %d " %len(reactions)
for r in reactions:
    
    # Adding the reactions
    kreac = smodel.Reac(r.getName(), volsys, lhs = r.getLhs(), rhs = r.getRhs())
    
    # Setting the value for The Calcium
#    if ( len (r.getReacts()) == 0 and
#    len(r.getProds()) == 1 and 
#    'Ca' in r.getProds() ):
#        r.setKReact(15)
#        print "Reaction %s reacts: %s prods %s k: %e" % (r.getName(), r.getReacts(), 
#                                                         r.getProds(), r.getKReact()) 
    kreac.kcst = r.getKValue()
    print r.getName(), r.getReacts(), r.getProds(), r.getKName(), r.getKValue()
# Destroy the reactions to free memory
del(reactions)

import steps.rng as srng
r = srng.create('mt19937', 512)
r.initialize(23412)

import steps.wmdirect as swmdirect

sim = swmdirect.Solver(mdl, mesh, r)

###########
## Simulation

iterations = 1
simMan = c.SimulationManager(nSec, dt_exp, species, iterations)
#simMan.baseLine(sim)

### Creating the input
#inputTimePoint = inputTime * pow(10, abs(sel.dt_exp)) # Inpute time

input1 = c.Input(250001, 'Ca', 2300)
input2 = c.Input(300001, 'Ca', 2300)
input3 = c.Input(350001, 'Ca', 2300)
input4 = c.Input(400001, 'Ca', 2300)
input5 = c.Input(450001, 'Ca', 2300)
input6 = c.Input(400001, 'cAMP', 4000)

#inputs = [] # Steady State
#inputs = [input1, input2, input3, input4, input5]
#inputs = [input1, input2, input3, input4, input5, input6]
inputs = [input6]

simMan.inputsIn(sim, inputs)


### Write some interesting value for the simulation
dir = simMan.currentDir
fInfo = open(dir + "/info.txt", 'w')
fInfo.write('Simulation:\n nSec: %d\n iterations: %d\n'  %(nSec, iterations))
for inp in inputs:
    inputInfo = "time: %d\tmol: %s\tquantity:%d\n" % (inp.getInputTimePoint(), 
                                                      inp.getMol(),
                                                      inp.getQuantity())
    fInfo.write(inputInfo)
fInfo.close()

print "Cookies ready."
