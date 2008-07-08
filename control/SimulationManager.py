import numpy
import io
from Input import *

class SimulationManager(object):
	"""
		Define a set of ready to use Simulations
	"""
	

	
	def __init__(self, nSec, dt_exp, species, iterations):
			
		self.nSec = nSec
		self.dt = pow(10, dt_exp)
		self.dt_exp = dt_exp
		self.lastTPoint = nSec + self.dt #Extreme of the array
		self.tpnt = numpy.arange(0.0, self.lastTPoint, self.dt) # Numpy array, with start, end and increment
		self.nTPoints = nSec * pow(10, abs(dt_exp)) + 1 # Number of Time Points
		self.__species = species
		self.numMol = len(species)
		self.__iterations = iterations # Number iterations
		self.res = numpy.zeros([self.__iterations, self.nTPoints, self.numMol])
		self.legendDict = {} # Map the Id of the specie with the number

		
	def instantSec(self, t, it):
		if (t % (pow(10, abs(self.dt_exp))) == 0):
			   	instantSec = t / pow(10, abs(self.dt_exp))
				print "iteration %d sec %f" %(it, instantSec)
				
	
	def run(self, sim, tp1, tp2, inputToApply, it):
		"""
			Function to run the simulation from one point to another one
			:params:
				sim
					The simulator variable of STEPS
				tp1
					Time point where to start the simulation (ex.: 0)
				tp2
					Time where to stop the simulation (ex.: 3001)
		"""
#		print inputToApply
		for t in xrange(tp1, tp2):
 			if (inputToApply is not None and t in inputToApply):
 				inputList = inputToApply.pop(t)
 				for inp in inputList:
	 				print inp, t
	 				mol = inp.getMol()
	 				q = inp.getQuantity()
 					sim.setCompCount('comp', mol, 
			  						sim.getCompCount('comp', mol) + q)
			i = 0
			for specie in self.__species:
				self.res[it,t,i] = sim.getCompCount('comp', specie)
				self.legendDict[specie] = i
				i = i + 1
			sim.run(self.tpnt[t])
			self.instantSec(t, it)

	def baseLine(self, sim):
		"""
			Simulate a Base Line
			:params:
				sim 
					The simulation object of STEPS
				lastTPoints
					The end time Point
				tpnt
					The array with all the time points
				species
					The species involved in the simulation
				legendDict
					The Dictionary to map the number with the Mol
		"""
		
		self.run(sim, 0, self.nTPoints, None) ## No input To Apply
			  
	def iteration(self, sim, tStart, tStop, inputs, it):
		# We need to reset the simulator
		sim.reset()		
		
		# Setting the conc
		speciesWithInitialConc = []
		for specie in self.__species:
		    conc = self.__species[specie]
		    if (conc > 0):
#		        print "\t %s %e" %(specie, conc)
		        speciesWithInitialConc.append(specie)
#		    else:
#		        print specie
		    sim.setCompConc('comp', specie, self.__species[specie])
		
		# Ordering the input
		inputToApply = self.orderInput(inputs)
		self.run(sim, tStart, tStop, inputToApply, it)
	
	def orderInput(self, inputs):
				# Ordering the input
		inputToApply = {}
		
		for input in (inputs):
			timePoint = input.getInputTimePoint()
			if (timePoint in inputToApply):
				list = inputToApply[timePoint] # Grabbing all the present Inputs
				list.append(input) # adding the inputs
				inputToApply[timePoint] = list # Update
			else:
				inputToApply[timePoint] = [input]
#		
#		for k, v in inputToApply.iteritems():
#
#			for inp in v:
#			     print inp.getInputTimePoint(), inp.getMol(),inp.getQuantity()
		
		return inputToApply
	
	def inputsIn(self, sim, inputs):
		"""
			Simulate a Base Line
			:params:
				sim 
					The simulation object of STEPS
				inputs
					List of Inputs to give during the simulation
		"""
		
		# Taking the inputs
#		# Ordering the input
		
		for it in xrange(self.__iterations):
			self.iteration(sim, 0, self.nTPoints, inputs, it)
		
				## Save the result
		self.currentDir = io.loader.createDir()
		io.loader.saveAll(self.currentDir, self.res, self.tpnt, self.legendDict, 
						   self.__species)
		print "Simulation Ended. Path to Simulation Files %s" %self.currentDir