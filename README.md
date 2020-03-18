# NBodySim
A basic N-Body simulation.

This project uses basic Newtonian mechanics to simulate numerous bodies interacting via gravity. 

Required software packages for the simulator to work:

  1. Numpy
  2. Bokeh - a plotting software that allows for interactive graphs
  3. Jupyter - The current iteration of this software relies on plots being output to a jupyter notebook. This requirement should go away as development progresses, but is currently a low priority.
  
To use the simulator, simply make an instance of the Simulator object and add masses using the addMass() function to create and either step() or play() function to progress the simulation.

The Analyser object can be used to view attribute vs time data from the simulation if the "save" flag was set to True when using play() or step(). 
