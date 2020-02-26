

import numpy as np
import time

#from ipywidgets import interact
from bokeh.io import push_notebook, show, output_notebook
from bokeh.plotting import figure

class Simulator:
    """
    The main class for the project.

    Create an instance of this class to use the N-Body Simulator.

    Attributes:
        massList (list): a list of MassObjects used in the simulation
        G (double): Newton's gravitational constant
        fig (figure): the object used in Bokeh's plotting functions

    """

    class MassObject:
        """
        An inner-class used by the simulator

        Main use is for the simulator. Some small functions are available.

        Parameters:
            name (str): Name of the mass
            mass (double): Mass of the object
            radius (double): Radius of the spherical object
            color (???): Color used on the plots #TODO: What is this?
            x (double): The current x position of the object
            y (double): The current y position of the object
            z (double): The current z position of the object
            xVel (double): The current x velocity of the object
            yVel (double): The current y velocity of the object
            zVel (double): The current z velocity of the object
            xForce (double): The current force in the x direction
            yForce (double): The current force in the y direction
            zForce (double): The current force in the z direction
            xAccel (double): The current acceleration in the x direction
            yAccel (double): The current acceleration in the y direction
            zAccel (double): The current acceleration in the z direction
        """

        def __init__(self,name,mass,radius,
                     xPos,yPos,zPos,xVel,yVel,zVel,
                     color):
            """
            A constructor for a MassObject

            There are no default values here, everything needs to be set if you
            directly use this function. (Note: it is not recommended that you
            use this function directly.)

            Parameters:
                name (str): Name of the mass
                mass (double): Mass of the object
                radius (double): Radius of the spherical object
                color (???): Color used on the plots #TODO: What is this?
                xPos (double): The current x position of the object
                yPos (double): The current y position of the object
                zPos (double): The current z position of the object
                xVel (double): The current x velocity of the object
                yVel (double): The current y velocity of the object
                zVel (double): The current z velocity of the object
            """
            self.name=name
            self.mass=mass
            self.radius=radius
            self.color=color
            
            self.x=xPos
            self.y=yPos
            self.z=zPos
            
            self.xVel=xVel
            self.yVel=yVel
            self.zVel=zVel
            
            self.xForce=0
            self.yForce=0
            self.zForce=0
            
            self.xAccel=0
            self.yAccel=0
            self.zAccel=0
            
            
        def getCoordinates(self):
            """
            A simple command to get an objects current coordinates.

            This function will return the current location of the object in
            the form of a tuple.

            Returns:
                Tuple: Returned in the form of: (x,y,z)
            """
            return (self.x,self.y,self.z)
        
        def getVelocities(self):
            """
            A simple command to get an objects current velocities.

            This function will return the current velocities of the object in
            the form of a tuple.

            Returns:
                Tuple: Returned in the form of: (x-velocity,y-velocity,z-velocity)
            """
            return (self.xVel,self.yVel,self.zVel)
        
    #End Subclass
    
    def __init__(self,notebook=True,importSystem=None):
        """
        A constructor for a simulator.

        Use this constructor to create a simulation, with the option of using a
        jupyter notebook and an option to import a pre-programmed system in the
        software.

        Parameters:
            notebook (bool): Whether to output to a jupyter notebook or HTML
            importSystem (str): Set this to a string of one of the pre-programmed
                                 simulation to skip adding masses.
        """

        self.time=0
        self.G = 6.67259 * (10**-11)
        self.setPlot()
        if notebook:
            output_notebook()
        
        if importSystem!=None:
            self._importSystem(importSystem)
        else:
            self.massList=[]
    
    
    def _importSystem(self,name):
        """
        A function used to import a pre-programmed system.

        This function is used by the Simulation class to automatically generate
        a pre-programmed system for the user. (Note: it is not recommended that
        you use this function directly.)

        Parameters:
            name (str): Name of the system to import.
        """

        pass


    def addMass(self, name='mass', mass=1, radius=1,
                xPos=0, yPos=0, zPos=0, xVel=0, yVel=0, zVel=0,
                color='Blue'):
        """
        A function to add a new mass to the simulation

        This function is to add a new mass with specified parameters to the
        system. Every parameter has a default value and does not need to be
        changed if it isn't necessary. Masses named the same thing will be
        given a '(1)' or '(2)' depending on the amount of similar names. For
        example, if three masses are added all with name 'm' , one will be
        labeled, 'm' the second, 'm(1)' and third, 'm(2)'.
        NOTE: Masses in the same location will be discarded.

        Parameters:
            name (str): Name of the mass
            mass (double): Mass of the object
            radius (double): Radius of the spherical object
            xPos (double): The current x position of the object
            yPos (double): The current y position of the object
            zPos (double): The current z position of the object
            xVel (double): The current x velocity of the object
            yVel (double): The current y velocity of the object
            zVel (double): The current z velocity of the object
            color (???): Color used on the plots #TODO: What is this?
        """

        # Default mass names + same mass names
        if self.getMass(name) != None:
            i = 1
            newName = name + '(' + str(i) + ')'
            while self.getMass(newName) != None:
                i += 1
                newName = name + '(' + str(i) + ')'
            name = newName
        # end names

        for o1 in self.massList:
            if o1.getCoordinates() == (xPos, yPos, zPos):
                print('Mass: {} not added (Same position as mass {})'.format(name, o1.name))

        m = self.MassObject(name, mass, radius, xPos, yPos, zPos, xVel, yVel, zVel, color)
        self.massList.append(m)


    def removeMass(self, nameOrIndex):
        """
        A function used to remove a mass.

        This function easily removes masses from a system based on index or name.

        Parameters:
            nameOrIndex (str / int): The index or name of a mass to be removed.
        """

        self.massList.remove(self.getMass(nameOrIndex))


    def getMass(self, nameOrIndex):
        """
        A function for retrieving MassObjects.

        This function gets a MassObject from the massList that fits the index or
        the name of the mass. If a negative value is given, or the name isn't
        found, returns None.

        Parameters:
            nameOrIndex (str / int): The index or name of a mass you want.

        Returns:
            MassObject: The mass object you want.
        """

        if isinstance(nameOrIndex, str):
            for m1 in self.massList:
                if m1.name == nameOrIndex:
                    return m1

        elif isinstance(nameOrIndex, int):
            try:
                return self.massList[nameOrIndex]
            except:
                return None
        else:
            return None

    
    def _singleStep(self,dt):
        """
        A function used to step the simulation forward in time.

        This function steps the simulation forward in time by an amount dt using
        a single calculation. For the simulator to be accurate, dt should be small.
        (Note: it is not recommended that you use this function directly.)

        Parameters:
            dt (double): The distance forward in time to step
        """

        N=len(self.massList)
        #Zero net forces
        for o1 in self.massList:
            o1.xForce=0
            o1.yForce=0
            o1.zForce=0
        
        
        for i in range(0,N-1):
            o1 = self.massList[i]
            for j in range(i+1,N):
                o2=self.massList[j]
                self._calcForces(o1,o2)
        
        for i in range(0,N):
            o1 = self.massList[i]
            self._calcAcceleration(o1)
            self._calcMovement(o1,dt)
            for j in range(0,i):
                o2 = self.massList[j]
                self._checkCollision(o1,o2)
        
        self.time+=dt
                
    
    def step(self,dt=1,numSteps=10,save=False):
        """
        A function to step the simulation forward in time.

        This function allows the user to step the simulation forward in time.
        The total time elapsed is t=dt*numSteps, where dt is the step size and
        numSteps is the number of times to calculate this movement. dt should be
        small for the simulation to be accurate. The save boolean will save the
        state of the simulation AFTER the whole calculation. (i.e after you step
        forward numSteps times using dt as the step size).

        Parameters:
            dt (double): The distance forward in time for each step
            numSteps (int): The number of times to step forward by dt
            save (bool): Whether to save to a file after completing the function
        """

        for i in range(0,numSteps):
            self._singleStep(dt)
        if save:
            self._saveState()


    def _calcForces(self, o1, o2):
        """
        A function used to calculate the force between two masses.

        This function takes in two masses and calculates the forces between them.
        (Note: it is not recommended that you use this function directly.)

        Parameters:
            o1 (MassObject): The first mass used to calculate
            o2 (MassObject): The second mass used to calculate
        """

        r = np.sqrt((o1.x - o2.x) ** 2 + (o1.y - o2.y) ** 2 + (o1.z - o2.z) ** 2)
        forceMag = (self.G * (o1.mass) * (o2.mass)) / (r ** 2)

        xhat = (o2.x - o1.x) / r
        yhat = (o2.y - o1.y) / r
        zhat = (o2.z - o1.z) / r

        fx = forceMag * xhat
        fy = forceMag * yhat
        fz = forceMag * zhat

        o1.xForce += fx
        o1.yForce += fy
        o1.zForce += fz

        o2.xForce -= fx
        o2.yForce -= fy
        o2.zForce -= fz


    def _calcAcceleration(self, o1):
        """
        A function to calculate the total acceleration on a MassObject

        This function takes in a MassObject and calculates the total acceleration
        on that object based on the net forces calculated using _calcForces().
        (Note: it is not recommended that you use this function directly.)

        Parameters:
            o1 (MassObject): The MassObject to calculate
        """

        o1.xAccel = o1.xForce / o1.mass
        o1.yAccel = o1.yForce / o1.mass
        o1.zAccel = o1.zForce / o1.mass


    def _calcMovement(self, o1, dt):
        """
        A function used to calculate a MassObject's movement.

        This function takes in a MassObject and a dt and calculates the motion
        based on the acceleration calculated in _calcAcceleration().
        (Note: it is not recommended that you use this function directly.)

        Parameters:
            o1 (MassObject): The MassObject to calculate it's movement.
            dt (double): The timestep to move it forward.
        """

        o1.x += o1.xVel * dt
        o1.y += o1.yVel * dt
        o1.z += o1.zVel * dt

        o1.xVel += o1.xAccel * dt
        o1.yVel += o1.yAccel * dt
        o1.zVel += o1.zAccel * dt


    def _checkCollision(self, o1, o2):
        """
        A function used to check if there is a collision.

        This function is used to check if there are any collisions between
        the two mass objects provided. If so, this function will call
        _combineMasses().
        (Note: it is not recommended that you use this function directly.)

        Parameters:
            o1 (MassObject): The first mass used to calculate
            o2 (MassObject): The second mass used to calculate
        """

        distance = np.sqrt((o1.x - o2.x) ** 2 + (o1.y - o2.y) ** 2 + (o1.z - o2.z) ** 2)
        interactionR = o1.radius + o2.radius

        if (interactionR >= distance):
            self._combineMasses(o1, o2)


    def _combineMasses(self, o1, o2):
        """
        A constructor for a MassObject

        This function takes two MassObjects and adds them together in an
        inelastic collision. The resulting mass will have the name of the larger
        mass, a radius proportional to the addition two volumes, and velocities
        calculated based on conservation of momentum. The smaller mass is then
        removed from the system.
        (Note: it is not recommended that you use this function directly.)

        Parameters:
            o1 (MassObject): The first mass used to combine
            o2 (MassObject): The second mass used to combine
        """

        # Dominate mass
        if (o1.mass >= o2.mass):
            dom = o1
            sub = o2
        else:
            dom = o2
            sub = o1

        # combine masses
        newM = dom.mass + sub.mass

        # combine radii
        dom.radius = (dom.radius ** 3 + sub.radius ** 3) ** (1 / 3)

        # combine velocities
        dom.xVel = (dom.mass * dom.xVel + sub.mass * sub.xVel) / newM
        dom.yVel = (dom.mass * dom.yVel + sub.mass * sub.yVel) / newM
        dom.zVel = (dom.mass * dom.zVel + sub.mass * sub.zVel) / newM

        dom.mass = newM  # setting this value after its final use

        self.massList.remove(sub)
    
    
    def _saveState(self):
        """
        A function used to save the current state of the system to a file

        This function takes the current state of the system and saves it to a
        file.
        (Note: it is not recommended that you use this function directly.)
        """

        pass

    
    def setPlot(self,plotTitle='N-Body Sim',plotRange=(-5,5),plotSize=600):
        """
        A function used to set the basic parameters of the Bokeh plots.

        This small function is used to customize different parameters of the
        Bokeh plots. Due to limitations, plotRange corresponds to all axes
        being plotted as the plots must be square. plotSize is represented in
        pixels.

        Parameters:
            plotTitle (str): The title to be added to the plots
            plotRange (tuple): A pair of doubles that describes the range of the
                               plots. This will correspond to every axis range.
            plotSize (int): The number of pixels for the width and height of
                            the plots
        """

        self.plotTitle=plotTitle
        self.plotRange=plotRange
        self.plotSize=plotSize


    def plot(self,axes=('x','y'),plotRange=None):
        """
        Plot the current state of the system using the axes specified.

        This function will plot the current state of the system, either in a
        notebook or HTML, using the axis specified in the tuple labeled "axes".
        The optional parameter "plotRange" can be used in place of setPlot().

        Parameters:
            axes (tuple): A pair of chars (either 'x', 'y', or 'z') corresponding
                          to the axis in which to plot
            plotRange (tuple): A pair of doubles that describes the range of the
                               plots. This will correspond to every axis range.
        """

        if plotRange!=None:
            self.plotRange=plotRange
        
        xp=[]
        yp=[]
        rad=[]
        colors=[]
        
        for o1 in self.massList:
            if axes[0]=='x':
                xp.append(o1.x)
            elif axes[0]=='y':
                xp.append(o1.y)
            else:
                xp.append(o1.z)
                
            if axes[1]=='x':
                yp.append(o1.x)
            elif axes[1]=='y':
                yp.append(o1.y)
            else:
                yp.append(o1.z)
                
            rad.append(o1.radius)
            colors.append(o1.color)
        
        timedTitle = self.plotTitle+'\t \t'+self.getTime()
        
        self.fig= figure(title=timedTitle,plot_height=self.plotSize,
                         plot_width=self.plotSize,
                         x_range=self.plotRange,
                         y_range=self.plotRange,
                         x_axis_label = axes[0]+' (m)',
                         y_axis_label = axes[1]+' (m)')
        self.sca= self.fig.scatter(xp,yp,radius=rad)
        show(self.fig,notebook_handle=True)


    def play(self,dt=.1,numSteps=10,save=False,pause=0,
             plotFirst=True,axes=('x','y'),plotRange=None):
        """
        A function to show the simulation evolve over time.

        Similar to the step() function, this method will move the simulation
        forward in time. To stop this funcion, simply use a keyboard interrupt
        (ctrl+c) or press the stop button in jupyter notebooks. The total time
        elapsed per frame is t=dt*numSteps, where dt is the step size and
        numSteps is the number of times to calculate this movement. Pause is the
        numebr of seconds between frames. Setting save to True will save the
        state of the system after each set of numSteps. plotFirst is for either
        creating a new plot or updating an old one. axes correspond to the axes
        to show the system and plotRange is for setting the square range of the
        plot on both axes.

        Parameters:
            dt (double): The distance forward in time for each step
            numSteps (int): The number of times to step forward by dt
            save (boolean): Whether to save to a file after completing the function
            pause (double): Time in seconds to pause between frames
            plotFirst (boolean): Whether to generate a new plot before playing
            axes (tuple): A pair of chars (either 'x', 'y', or 'z') corresponding
                          to the axis in which to plot
            plotRange (tuple): A pair of doubles that describes the range of the
                               plots. This will correspond to every axis range.

        """

        if plotFirst:
            self.plot(axes,plotRange)
        
        try:
            while True:
                self.step(dt,numSteps,save)
                time.sleep(pause)
                self._updatePlot(axes)
            
        except KeyboardInterrupt:
            print("Halted")


    def _updatePlot(self, axes):
        """
        A function used to update the Bokeh plots.

        This function is used internally to update the plots as they progress
        using the play() function. Axes is specified as a tuple for the axes
        being plotted.
        (Note: it is not recommended that you use this function directly.)

        Parameters:
            axes (tuple): A pair of chars (either 'x', 'y', or 'z') corresponding
                          to the axis in which to plot
        """

        xp = []
        yp = []
        rad = []
        for o1 in self.massList:
            if axes[0] == 'x':
                xp.append(o1.x)
            elif axes[0] == 'y':
                xp.append(o1.y)
            else:
                xp.append(o1.z)

            if axes[1] == 'x':
                yp.append(o1.x)
            elif axes[1] == 'y':
                yp.append(o1.y)
            else:
                yp.append(o1.z)

            rad.append(o1.radius)

        self.sca.data_source.data['x'] = xp
        self.sca.data_source.data['y'] = yp
        self.sca.data_source.data['radius'] = rad
        self.fig.title.text = self.plotTitle + '\t \t' + self.getTime()
        push_notebook()


    def getTime(self):
        """
        A function that returns the current simulation time.

        This function has no parameters, but returns the current time of the
        system if a form: Years, Days, hh:mm:ss.

        Returns:
            str: A string representing the time.
        """

        y, rem = divmod(self.time,31536000)
        d, rem = divmod(rem, 86400)
        h, rem = divmod(rem, 3600)
        m, s = divmod(rem, 60)
        return '+ {}y, {}d, {}:{}:{}'.format(int(y),int(d),int(h),int(m),s)
