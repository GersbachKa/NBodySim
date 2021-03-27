import numpy as np
import multiprocessing as mp

#from nbodysim.Simulator import Simulator as sim
from nbodysim.MassObject import MassObject

def eulerStepFunction(simulator, dt, collisions=True):
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
    if collisions:
    
        toCombine = []
        for i in range(simulator.objectCount-1):
            for j in range(i+1,simulator.objectCount):
                if checkCollision(simulator.allObjects[i],simulator.allObjects[j]):
                    #collision occured!
                    n1 = simulator.allObjects[i].name
                    n2 = simulator.allObjects[j].name
                    if not ((n1,n2) in toCombine or (n2,n1) in toCombine):
                        toCombine.append((n1,n2))
        
        toCombine = np.array(toCombine)
        for n1,n2 in toCombine:
            m1 = simulator.getObject(n1)
            m2 = simulator.getObject(n2)
            
            #Ensure they aren't the same object
            if m1!=m2:
            
                dom, sub = None, None
            
                #Assign dominance
                if m1.mass>m2.mass:
                    dom = m1
                    sub = m2
                else:
                    dom = m2
                    sub = m1
        
                #Conservation of linear momentum
                dom.velocity = (dom.mass*dom.velocity + sub.mass*sub.velocity)/(dom.mass+sub.mass)
        
                #Have dom get proportionally bigger (same density as before)
                dom.radius = ((dom.mass+sub.mass)/dom.mass * dom.radius**3)**(1/3)
        
                #Add mass
                dom.mass += sub.mass
        
                #Replace all instances of sub name with the dom name in subsiquent collisions
                toCombine[toCombine==sub.name] = dom.name
        
                #Remove sub
                simulator.removeObject(sub.name)
            
            
            
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
    difference = m2.position[0] - m1.position[0] #m1 is origin
    
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
    m1.position[0]+=m1.velocity*dt
    m1.velocity+=m1.acceleration*dt

def checkCollision(m1,m2):
    """
    A function used to check if there is a collision.
    
    This function is used to check if there are any collisions between
    the two mass objects provided. If so, this will return True
    
    Parameters:
        m1 (MassObject): The first mass used to calculate
        m2 (MassObject): The second mass used to calculate
        
    Returns:
        (bool): Whether there is a collision between m1 and m2
    """
    dif = m1.position[0] - m2.position[0]
    return (m1.radius+m2.radius)**2 > (dif.dot(dif)) and (m1.mass> 0 and m2.mass>0)
    
        
        
        