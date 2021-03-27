import numpy as np
import time
import csv
import os

import threading

from nbodysim.MassObject import MassObject
from nbodysim.EulerStep import eulerStepFunction

from bokeh.models import ColumnDataSource
from bokeh.io import push_notebook, show, output_notebook
from bokeh.plotting import figure

class Simulator:
    """
    The main class for the project.
    
    Create an instance of this class to use the N-Body Simulator.
    
    Attributes:
        name (str): The name of the Simulation
        path (str): A string representation of the path where the simulator will store data
        time (float): A representation of the time in seconds since the start of a simulation
        stepFunction (function): The step function for time evolution of the system
        G (float): The force constant defaulting to the value of the gravitational constant G
        allObjects (numpy Array): An array of all mass objects in the system
        objectCount (int): The number of objects in the system currently
        notebookOutput (bool): A boolean that determines whether plots will be output to a Jupyter notebook
        fig (figure): A bokeh figure of the simulator plot output
    """
    
    def __init__(self,name='Simulation',path='',notebook=True,importSystem=None,load=False):
        """
        A constructor for a simulator.
        
        Use this constructor to create a simulation with a given name, with
        the option of using a jupyter notebook and an option to import a
        pre-programmed system in the software. By setting a name and path,
        you can use the "load" boolean to extract data from a previously saved
        simulator. (The name should be set to the folder name of the previous simulation)
        
        Parameters:
            name (str): Name of the simulation
            path (str): A path to put the output in, if desired
            notebook (bool): Whether to output to a jupyter notebook or HTML
            importSystem (str): Set this to a string of one of the pre-programmed
                                 simulation to skip adding masses.
            load (bool): Whether to load an existing simulation.
        """
        if importSystem!=None:
            self._importSystem(importSystem)
        elif load:
            self._loadSystem(name,path)
        else:
            self.name = name
        
            #Path edits
            if path != '':
                if os.path.exists(path):
                    if path[-1] == '/':
                        path=path[:-1]

                    self.path = path

                else:
                    raise IOError("Simulation Path does not exist!")
            else:
                self.path = os.getcwd()

            self.time=0
            self.G = 6.67259 * (10**-11)

            self.allObjects = np.empty((10),dtype=MassObject)
            self.objectCount = 0
        #End else
        self.stepFunction = None
        self.notebookOutput=notebook
        if notebook:
            output_notebook()
        
    
    def _importSystem(self,systemName):
        """
        A method used to import a pre-programmed system.
        
        This method is used by the Simulation class to automatically generate
        a pre-programmed system for the user. (Note: it is not recommended that
        you use this method directly.)
        
        Parameters:
            name (str): Name of the system to import.
        """
        pass
    
    
    def _loadSystem(self,systemName,path):
        """
        A method used to load a previous simulator.
        
        This method takes in a system name and path, then, if the previous simulation
        was saved, this method will load that system in the state it was last saved in.
        (Note: it is not reccomended that you use this method directly.)
        
        Parameters:
            systemName (str): The name of the system to load.
            path (str): The path where the system was saved.
        """
        importPath = None
        if path=='':
            path = os.getcwd()
            
        if not path.endswith(systemName):
            if path.endswith('/'):
                importPath = path+systemName
                self.path=path[:-1]
            else:
                importPath = path+'/'+systemName
                self.path=path
        else:
            importPath = path
            self.path = path[:-len(systemName)+1]
        
        if not importPath.endswith('/'):
            importPath+='/'
        
        if not os.path.exists(importPath):
            raise FileNotFoundError("The file path, \"{}\" does not exist!".format(importPath))
        
        fileList = [i for i in os.listdir(importPath) if i.endswith('.csv')]
        
        if len(fileList)<1:
            print("No objects found within \"{}\", creating empty simulation.")
            self.__init__(name='systemName',path=path)
            return
        
        self.name=systemName
        self.G = 6.67259 * (10**-11)
        
        #Set time
        timeList = []
        for f in fileList:
            with open(importPath+f,'r') as d:
                data = list(csv.reader(d))
                time = np.array(data[-1][0]).astype(np.float)
                timeList.append(time)
        
        self.time=max(timeList)
        
        #Add Objects
        self.objectCount = 0
        self.allObjects = np.empty((len(fileList)),dtype=MassObject)
        
        for f in fileList:
            with open(importPath+f,'r') as d:
                data = list(csv.reader(d))
                color = str(data[-1][-1])
                data = np.array(data[-1][:-1]).astype(np.float)
                if data[0] == self.time:
                    self.addObject(f[:-4],data[1],data[2],data[3:6],data[6:9])
                    self.allObjects[self.objectCount-1].color = color
                
    
    def addObject(self,name="Object",mass=1,radius=1,position=[0,0,0],
                  velocity=[0,0,0],color=(0,0,0)):
        """
        A method to add a new MassObject to the simulation
        
        This method is to add a new object with specified parameters to the
        system. Every parameter has a default value and does not need to be
        changed if it isn't necessary. Masses named the same thing will be
        given a '(1)' or '(2)' depending on the amount of similar names. For
        example, if three masses are added all with name 'm' , one will be
        labeled, 'm' the second, 'm(1)' and third, 'm(2)'.
        NOTE: Masses in the same location will be discarded.
        
        Parameters:
            name (str): Name of the object
            mass (double): Mass of the object in kg
            radius (double): Radius of the spherical object in m
            position (Numpy Array): A vector of the position in m
            velocity (Numpy Array): A vector of the velocity in m
            color (3 tuple): The RGB values for the Color of the object
        """
        
        #Make sure name doesn't already exist
        if self.getObject(name) != None:
            i=1
            newName = name + "({})".format(i)
            while self.getObject(newName) != None:
                i+=1
                newName = name + "({})".format(i)
            
            name = newName
        
        #Check if the position is duplicated
        for i in range(self.objectCount):
            o = self.allObjects[i]
            for i in range(3):
                if o.position[0,i] != position[i]:
                    break
                if i==2:
                    print("Object: {} already occupies the position. Cannot add {} object!".format(o.name,name))
                    return
        
        #Check if need to expand numpy array
        if(self.allObjects.size == self.objectCount):
            nextSize = min(self.objectCount*10, self.objectCount+100)
            nextObjects = np.empty((nextSize),dtype=MassObject)
            nextObjects[:self.objectCount] = self.allObjects[:]
            self.allObjects = nextObjects
            
        #Add the object
        self.allObjects[self.objectCount] = MassObject(name,mass,radius,position,velocity,color)
        self.objectCount+=1
        
        
    def removeObject(self,nameOrIndex):
        """
        A method used to remove a MassObject.
        
        This method easily removes mass object from a system based on index or name.
        
        Parameters:
            nameOrIndex (str / int): The index or name of a mass to be removed.
        """
        index = 0
        if isinstance(nameOrIndex,str):
            for i in range(self.objectCount):
                if self.allObjects[i].name == nameOrIndex:
                    index = i
                    break
                    
        if isinstance(nameOrIndex,int):
            while nameOrIndex<0:
                nameOrIndex = self.objectCount+nameOrIndex
                
            if nameOrIndex<self.objectCount:
                index = nameOrIndex
            else:
                return None
        
        returnElement = MassObject
        postElements = self.allObjects[index+1:]
        self.allObjects[index:-1] = postElements
        self.allObjects[-1] = None
        self.objectCount-=1
        
        
    def getObject(self,nameOrIndex):
        """
        A method for retrieving MassObjects.
        
        This method gets an object from the simulator that fits the index or
        the name of the mass. If a negative value is given, or the name isn't
        found, returns None.
        
        Parameters:
            nameOrIndex (str / int): The index or name of a mass you want.
            
        Returns:
            MassObject: The mass object you want.
        """
        if isinstance(nameOrIndex, str):
            for i in range(self.objectCount):
                if self.allObjects[i].name == nameOrIndex:
                    return self.allObjects[i]
                
            return None
                
        elif isinstance(nameOrIndex, int):
            while nameOrIndex<0:
                nameOrIndex = self.objectCount+nameOrIndex
                
            if nameOrIndex<self.objectCount:
                return self.allObjects[nameOrIndex]
            else:
                return None
        
        else:
            raise ValueError("{} is not an integer or string".format(nameOrIndex))
            
       
    def getTotalEnergy(self,nameOrIndex):
        """
        Gets total energy of one object in our system.
        
        This will find the kinetic energy given by the velocity and the potential energy
        between all objects given by the position and mass. This will give to scalar values
        which the functions adds to give the total energy. The nameOrIndex variable allows
        the user to input either the name or index of a specific object.
        
         Parameters:
            nameOrIndex (str / int): The index or name of a mass you want.
            
         Returns: 
             Total energy of one particular object in Joules.
        
        
        """
        z = self.getObject(nameOrIndex)
        kineticEnergy = (1/2)*(z.mass)*(z.velocity.dot(z.velocity))
        
        potentialEnergy = 0
        
        for i in range(self.objectCount):
            
            y = self.allObjects[i]
            
            if y != z:
                dif = ((z.position[0]-y.position[0]))
                pE = (-self.G*z.mass*y.mass)/np.sqrt(dif.dot(dif))
                potentialEnergy += pE 
                
        return(kineticEnergy + potentialEnergy)
            
    
    
    def setStepFunction(self,stepType="Euler"):
        """
        A method for setting the type of step function the simulator uses.
        
        This method allows you to change the step function to time evolve the
        simulator. In order to add a different step function, you must create a
        new .py file and import in this file. The functions must take in a 
        simulator object and a dt and must evolve the simulation by that dt value.
        
        Parameters:
            stepType (str): A string of the step type to time evolve the simulator.
        """
        if stepType=="Euler":
            self.stepFunction = eulerStepFunction
            
    
    def step(self,dt=1,numberOfSteps=60,save=False,collisions=True):
        """
        A method to step the simulation forward in time.
        
        To use this method, you must first assign a stepFunction.
        This method allows the user to step the simulation forward in time.
        The total time elapsed is t=dt*numberOfSteps, where dt is the step size and
        numSteps is the number of times to calculate this movement. dt should be
        small for the simulation to be accurate. The save boolean will save the
        state of the simulation AFTER the whole calculation. (i.e after you step
        forward numSteps times using dt as the step size).
        
        Parameters:
            dt (double): The distance forward in time for each step
            numSteps (int): The number of times to step forward by dt
            save (bool): Whether to save to a file after completing the the full step
            collisions (bool): Whether to allow collisions or skip them
        
        """
        if self.stepFunction == None:
            print("No step function specified, defaulting to Euler.")
            self.setStepFunction("Euler")
        
        if save:
            self._saveState()
        
        for i in range(numberOfSteps):
            self.stepFunction(self,dt,collisions)
            self.time+=dt
        
        
    def plot(self,axes=('x','y'),plotRange=None,plotSize=(400,400),trails=True):
        """
        Plot the current state of the system using the axes specified.
        
        This method will plot the current state of the system, either in a
        notebook or HTML, using the axis specified in the tuple labeled "axes".
        The optional parameter "plotRange" can be used to change the range of the plot.
        The optional parameter "plotSize" can be used to change the size of the plot.
        
        Parameters:
            axes (2 tuple): A pair of chars (either 'x', 'y', or 'z') corresponding
                          to the axis in which to plot.
            plotRange (2 tuple): A pair of doubles that describes the range of the
                               plots. This will correspond to every axis range.
            plotSize (2 tuple): A pair of integers that represents the size in pixels
                                of the created plot.
            trails (boolean): Whether to show object trails
        
        """
        #Check for same axes
        if axes[0] == axes[1]:
            raise ValueError("Axes cannot be the same dimension")
        
        x = []
        y = []
        z = []
        xt = []
        yt = []
        zt = []
        rad = []
        colors = []
        labels = []
        
        for i in range(self.objectCount):
            o = self.allObjects[i]
            x.append(o.position[0,0])
            y.append(o.position[0,1])
            z.append(o.position[0,2])
            xt.append(o.position[:,0])
            yt.append(o.position[:,1])
            zt.append(o.position[:,2])
            rad.append(o.radius)
            colors.append(o.color)
            labels.append(o.name)
            
        TOOLS="hover,pan,wheel_zoom,zoom_in,zoom_out,reset,save"
        
        timedTitle = self.name+'\t \t'+self.getTime()
        
        if plotRange==None:
            inp = [None,None]
            for i in [0,1]:
                if axes[i] == 'x':
                    inp[i] = x
                elif axes[i] == 'y':
                    inp[i] = y
                else:
                    inp[i] = z
            
            plotRange = self._findBestRange(inp[0],inp[1])
        
        self.fig = figure(title=timedTitle,plot_height=plotSize[0],plot_width=plotSize[1],
                          x_axis_label = axes[0]+" (m)", y_axis_label = axes[1]+" (m)",
                          x_range=plotRange[0], y_range=plotRange[1], tools=TOOLS)
        
        self.plotSource = ColumnDataSource(dict(x=x,y=y,z=z,xt=xt,yt=yt,zt=zt,radius=rad,color=colors,label=labels))
        
        self.fig.scatter(x=axes[0],y=axes[1],radius='radius',fill_color='color',line_color=None,
                                  source=self.plotSource)
        
        if trails:
            self.fig.multi_line(xs=axes[0]+'t',ys=axes[1]+'t',color='color',source=self.plotSource)
            
        self.fig.hover.tooltips=[("Name","@label"),("Location","@x, @y, @z")]
        show(self.fig,notebook_handle=self.notebookOutput)
    
    
    def play(self,dt=1,numberOfSteps=100,save=False,pause=0,plotFirst=True,axes=('x','y'),
             plotRange=None,plotSize=(400,400),trails=True,collisions=True):
        """
        A method to show the simulation evolve over time.
        
        Similar to the step() method, this method will move the simulation
        forward in time. To stop this, simply use a keyboard interrupt
        (ctrl+c) or press the stop button in jupyter notebooks. The total time
        elapsed per frame is t=dt*numSteps, where dt is the step size and
        numSteps is the number of times to calculate this movement. Pause is the
        number of seconds between frames. Setting save to True will save the
        state of the system after each set of numSteps. plotFirst is for either
        creating a new plot or updating an old one. axes correspond to the axes
        to show the system, plotRange is for setting the square range of the
        plot on both axes, plotSize is the size in pixels of the output plot size.
        
        Parameters:
            dt (double): The distance forward in time for each step
            numSteps (int): The number of times to step forward by dt
            save (boolean): Whether to save to a file after completing each number of steps
            pause (double): Time in seconds to pause between frames
            plotFirst (boolean): Whether to generate a new plot before playing
            axes (2 tuple): A pair of chars (either 'x', 'y', or 'z') corresponding
                          to the axis in which to plot
            plotRange (2 tuple): A pair of doubles that describes the range of the
                               plots. This will correspond to every axis range.
            plotSize (2 tuple): A pair of integers that represents the size in pixels
                                of the created plot.
            trails (boolean): Whether to show object trails
            collisions (boolean): Whether to allow collisions or skip them
        """
        
        if plotFirst:
            self.plot(axes,plotRange,plotSize,trails)
        
        keepPlay=True
        try:
            while keepPlay:
                self.step(dt,numberOfSteps,save,collisions)
                self.updatePlot()
                time.sleep(pause)
        except KeyboardInterrupt:
            print("Stopped")
            self.updatePlot()
        
    
    def getTime(self):
        """
        A method that returns the current simulation time.
        
        This method has no parameters, but returns the current time of the
        system if a form: Years, Days, hh:mm:ss.
        
        Returns:
            str: A string representing the time.     
        """
        y, rem = divmod(self.time,31536000)
        d, rem = divmod(rem, 86400)
        h, rem = divmod(rem, 3600)
        m, s = divmod(rem, 60)
        return '+ {}y, {}d, {}:{}:{}'.format(int(y),int(d),int(h),int(m),s)
    
    
    def updatePlot(self):
        """
        A method to update the Bokeh plots.
        
        This method used internally to update the plots as they progress
        using the play() method. Axes is specified as a tuple for the axes
        being plotted.
        """
        x = []
        y = []
        z = []
        xt = []
        yt = []
        zt = []
        rad = []
        colors = []
        labels = []
        
        for i in range(self.objectCount):
            o = self.allObjects[i]
            x.append(o.position[0,0])
            y.append(o.position[0,1])
            z.append(o.position[0,2])
            xt.append(o.position[:,0])
            yt.append(o.position[:,1])
            zt.append(o.position[:,2])
            rad.append(o.radius)
            colors.append(o.color)
            labels.append(o.name)
        
        self.plotSource.data = dict(x=x,y=y,z=z,xt=xt,yt=yt,zt=zt,radius=rad,color=colors,label=labels)
        
        self.fig.title.text = self.name+'\t \t'+self.getTime()
        
        if self.notebookOutput:
            push_notebook()
    
    def _findBestRange(self,x,y):
        """
        A method used to find the best plot ranges.
        
        This method uses the current state of the simulator and attempts to
        find a decent initial "zoom level" for the simulator. This assumes a square
        area.
        
        Parameters:
            x (list): A list of all object x-axis values
            y (list): A list of all object y-axis values
            
        Returns:
            (2 tuple): a tuple of the best guesses for x and y ranges
        
        """
        if len(x)<1:
            return ((-1,1),(-1,1))
        
        mins = (min(x),min(y))
        maxs = (max(x),max(y))
        difs = ((maxs[0]-mins[0])/2,(maxs[1]-mins[1])/2)
        center = (mins[0]+difs[0],mins[1]+difs[1])
        
        if len(x)==1:
            return ((x[0]-1,x[0]+1),(y[0]-1,y[0]+1))
        
        if (max(difs)==difs[0]):
            #X is the larger axis
            return (((center[0]-difs[0])*1.1,(center[0]+difs[0])*1.1),
                    ((center[1]-difs[0])*1.1,(center[1]+difs[0])*1.1))
        else:
            return (((center[0]-difs[1])*1.1,(center[0]+difs[1])*1.1),
                    ((center[1]-difs[1])*1.1,(center[1]+difs[1])*1.1))
        
    
    def _saveState(self):
        """
        A method used to save the current state of the system to a file.
        
        This method takes the current state of the system and saves it to a
        file.
        (Note: it is not recommended that you use this method directly.)
        """
        directory = self.path+'/'+self.name
        
        if not os.path.exists(directory):
            os.mkdir(directory)
            
        for i in range(self.objectCount):
            self.allObjects[i]._saveState(directory,self.time)
