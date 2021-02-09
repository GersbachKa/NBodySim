import numpy as np
import multiprocessing as mp
import numpy as np


from nbodysim.MassObject import MassObject
MPENABLED = True

def fastEuler(simulator,dt):
    
    if MPENABLED:
        oCount = simulator.objectCount
        args = np.array([[simulator]*oCount,list(range(oCount)),[dt]*oCount])
        args = np.swapaxes(args,0,1)
        with mp.Pool() as p:
            simulator.allObjects[0:simulator.objectCount]= p.map(calculateMovement,args)
            
    else:
        simulator.allObjects[0:simulator.objectCount]=[calculateMovement((simulator,i,dt)) for i in range(simulator.objectCount)]
    
    toRemove = []
    for i in range(simulator.objectCount-1):
        for j in range(i+1,simulator.objectCount):
            m1 = simulator.allObjects[i]
            m2 = simulator.allObjects[j]
            r = checkCollision(m1,m2)
            if r==1:
                if not i in toRemove:
                    toRemove.append(i)
            elif r==2:
                if not j in toRemove:
                    toRemove.append(j)
    
    toRemove = np.flip(np.sort(toRemove))
    for i in toRemove:
        simulator.removeObject(i)
                    
def calculateMovement(args):
    simulator=args[0]
    i=args[1]
    dt=args[2]
        
    m1 = simulator.allObjects[i]
    m1.resetAcceleration()
        
    #Calculate acceleration
    for j in range(simulator.objectCount):
        if j!=i:
            m2 = simulator.allObjects[j]
                
            #Find the vector difference...
            diff = m2.position[0] - m1.position[0]
                
            #...magnitude of that difference squared...
            magSquare = diff.dot(diff)
                
            if magSquare==0:
                raise ZeroDivisionError("Objects occupy the same space!")
                
            #...and the unit vector difference
            posHat = diff/np.sqrt(magSquare)
                
            #Calculate the massless force vector (acceleration/mass)
            fVector = (simulator.G/magSquare)*posHat
                
            #Now multiply fVector by mass to get acceleration. Use Newton's 3rd law to equate the two
            m1.acceleration+=m2.mass*fVector
        
    #Calculate movment
    m1.position[0]+=m1.velocity*dt
    m1.velocity+=m1.acceleration*dt
    return m1
    
    
def checkCollision(m1,m2):
    if m1==None or m2 == None:
        return 0
        
    #Find the difference
    diff = m1.position[0] - m2.position[0]
        
    #Take the magnitude square
    magSquare = diff.dot(diff)
        
    retVal = 0
    if m1.mass>0 and m2.mass>0 and ((m1.radius+m2.radius)**2>=magSquare):
        #Collision has occured
            
        #Determine the larger of the masses
        if m1.mass>=m2.mass:
            retVal = 2
            dom = m1
            sub = m2
        else:
            retVal = 1
            dom = m2
            sub = m1
            
        #Inelastic collision: Conservation of linear momentum
        dom.velocity = (dom.mass*dom.velocity + sub.mass*sub.velocity)/(dom.mass+sub.mass)
            
        #Have dom get proportionally bigger (Same density)
        dom.radius = ((dom.mass+sub.mass)/dom.mass * dom.radius**3)**(1/3)
            
        #Add masses together
        dom.mass += sub.mass
            
        #Remove sub
        sub.mass = 0
        
    return retVal
    
    
    
