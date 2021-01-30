import numpy as np
import multiprocessing as mp

#from nbodysim.Simulator import Simulator as sim
from nbodysim.MassObject import MassObject

def eulerStepFunction(simulator, dt):
    """
    A function that steps a simulator object forward in a dt time step. 
    
    This function steps the simulation forward in time by an amount dt using
    a single calculation. For the simulator to be accurate, dt should be small.
    
    Parameters:
        simulator (Simulator): The simulator to step forward in time
        dt (double): The distance forward in time to step
    """
    #Reset all forces to 0
    for i in range(simulator.objectCount):
        simulator.allObjects[i].resetAcceleration()
    
    #Calculate forces
    for i in range(simulator.objectCount-1):
        for j in range(i+1,simulator.objectCount):
            calcAcceleration(simulator.G,simulator.allObjects[i],simulator.allObjects[j])
            
    #Calculate movement
    for i in range(simulator.objectCount):
        calculateMovement(simulator.allObjects[i],dt)
        
    #Check for collisions
    toRemove = []
    for i in range(simulator.objectCount-1):
        for j in range(i+1,simulator.objectCount):
            r = checkCollision(simulator.allObjects[i],simulator.allObjects[j])
            if r==1:
                #Don't duplicate deletes
                print(simulator.allObjects[i].mass , simulator.allObjects[j].mass)
                if not (i in toRemove):
                    toRemove.append(i)
            elif r==2:
                #Don't duplicate deletes
                print(simulator.allObjects[i].mass , simulator.allObjects[j].mass)
                if not (j in toRemove):
                    toRemove.append(j)
    
    toRemove = np.flip(np.sort(toRemove))
    for i in toRemove:
        simulator.removeObject(i)
            
            
def calcAcceleration(G,m1,m2):
    """
    A function used to calculate the force between two masses.

    This function takes in two masses and calculates the forces between them.
    
    Parameters:
        G (double): The mass constant to use in the calculation
        m1 (MassObject): The first mass used to calculate
        m2 (MassObject): The second mass used to calculate
    """
    #Find the vector difference...
    difference = m2.position - m1.position #m1 is origin
    
    #...magnitude of that difference squared...
    magnitudeSquare = difference.dot(difference) #Faster than np.sum(np.square(difference))
    
    if magnitudeSquare == 0:
        raise ZeroDivisionError("Objects occupy the same space!")
    
    #...and the unit vector difference
    positionHat = difference/np.sqrt(magnitudeSquare)
    
    #Calculate the massless force vector (acceleration/mass)
    fVector = (G/magnitudeSquare)*positionHat
    
    #Now multiply fVector by mass to get acceleration. Use Newton's 3rd law to equate the two
    m1.acceleration+=m2.mass*fVector
    m2.acceleration-=m1.mass*fVector
    

def calculateMovement(m1,dt):
    """
    A function used to calculate a MassObject's movement.
    
    This function takes in a MassObject and a dt and calculates the motion
    based on the acceleration calculated in _calcAcceleration().
        
    Parameters:
        m1 (MassObject): The MassObject to calculate it's movement.
        dt (double): The timestep to move it forward.
    """
    m1.position+=m1.velocity*dt
    m1.velocity+=m1.acceleration*dt

def checkCollision(m1,m2):
    """
    A function used to check if there is a collision.
    
    This function is used to check if there are any collisions between
    the two mass objects provided. If so, it will combine the masses
    in a way that preserves the name of the larger mass, and removes
    a smaller one.
    
    Parameters:
        m1 (MassObject): The first mass used to calculate
        m2 (MassObject): The second mass used to calculate
    """
    
    if m1 == None or m2 == None:
        return 0
    
    #Find the vector difference
    difference = m2.position - m1.position
    
    #To get the magnitude of that difference
    magnitude = np.sqrt(difference.dot(difference)) #Faster than np.sum(np.square(difference))
    
    retVal = 0
    if (m1.radius+m2.radius>=magnitude) and m1.mass>0 and m2.mass>0:
        #Collision occured!
        
        #Determine larger mass
        dom, sub = None, None
        if m1.mass>m2.mass:
            retVal = 2
            dom = m1
            sub = m2
        else:
            retVal = 1
            dom = m2
            sub = m1
        
        #Inelastic collision properties (Conserve linear momentum)
        dom.velocity = (dom.mass*dom.velocity + sub.mass*sub.velocity)/(dom.mass+sub.mass)
        
        #Have dom get proportionally bigger (same density as before)
        dom.radius = ((dom.mass+sub.mass)/dom.mass * dom.radius**3)**(1/3)
        
        #Add mass
        dom.mass += sub.mass
        
        #Remove sub
        sub = None
        
    #return so the sim knows to delete masses, if needed (0 is no delete, 1 is m1, 2 is m2)
    return retVal
        
        
        