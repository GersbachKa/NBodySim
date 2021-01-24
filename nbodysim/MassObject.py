import numpy as np
import os
import csv
import copy

class MassObject:
    """
    A class which describes all attributes of the objects within the system.
    
    The values in the attributes will change over time as the simulator evolves.
    
    Attributes:
        name (str): Name of the mass
        mass (double): Mass of the object
        radius (double): Radius of the spherical object
        position (Numpy Array): A 3D vector representing the position in meters
        velocity (Numpy Array): A 3D vector representing the velocity in meters/s
        acceleration (Numpy Array): A 3D vector representing the acceleration in m/(s^2)
        color (str): A binary representation of the color in RGB
    """
    
    def __init__(self,name="Object",mass=1,radius=1,position=[0,0,0],
                 velocity=[0,0,0],color=(0,0,0)):
        """
        The constructor for the MassObject class.
        
        It is not recommended to make your own MassObjects, as the Simulator will do this for you.
    
        Parameters:
            name (str): Name of the mass
            mass (double): Mass of the object
            radius (double): Radius of the spherical object
            position (Numpy Array): A 3D vector representing the position in meters
            velocity (Numpy Array): A 3D vector representing the velocity in meters/s
            acceleration (Numpy Array): A 3D vector representing the acceleration in m/(s^2)
            color (str): A binary representation of the color in RGB
        """
        self.name=name
        self.mass=mass
        self.radius=radius
        self.position = np.array(position,dtype=np.float32)
        self.velocity = np.array(velocity,dtype=np.float32)
        self.color = "#%02x%02x%02x" % color
        self.acceleration = np.zeros(3,dtype=np.float32)
    
    def _copy(self,other):
        """
        A method which copies all elements from another mass object to this one.
        
        It is not recommended that you use this method, as the Simulator will do this for you.
        
        Parameters:
            other (MassObject): Another MassObject from which data will be copied.
        """
        self.name = other.name
        self.mass = other.mass
        self.position = other.position
        self.velocity = other.velocity
        self.color = other.color
        self.acceleration = other.acceleration
        
    def _saveState(self,folder,time):
        """
        A method to save attributes of the MassObject to a .csv file
        
        This method will either make a new file with the name of the
        MassObject as the filename or append to the file with it's current
        status.
        It is not recommended that you use this method, as the Simulator will do this for you.
        
        Parameters:
            folder (str): The folder to save the file
            time (double): number of seconds since the start of the sim
        """
        fileDirectory = folder+'/'+self.name+".csv"
        
        #If the file doesn't exist or the time is 0
        if not (os.path.exists(fileDirectory) and time>0):
            with open(fileDirectory,'w',newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['time','mass','radius','x','y','z',
                                 'x-velocity','y-velocity','z-velocity',
                                 'x-acceleration','y-acceleration','z-acceleration',
                                 'color'
                                ])
        #End if
        
        with open(fileDirectory,'a',newline='') as f:
            writer = csv.writer(f)
            toWrite = [time, self.mass, self.radius,
                       self.position[0], self.position[1], self.position[2],
                       self.velocity[0], self.velocity[1], self.velocity[2],
                       self.acceleration[0], self.acceleration[1], self.acceleration[2],
                       self.color
                      ]
            writer.writerow(toWrite)
            
    
    def resetAcceleration(self):
        """
        A method to set the acceleration of the MassObject back to 0.
        
        This method will set all values of the acceleration vector to 0 so
        the simulator can recalculate during the next time step.
        It is not recommended that you use this method, as the Simulator will do this for you.
        """
        self.acceleration[0]=0
        self.acceleration[1]=0
        self.acceleration[2]=0
        
        
    def __str__(self):
        """
        A method to output the name and common variables of a MassObject.
        
        The method will be called if you call print() on a MassObject. It includes
        the name, position vector, and velocity vector in the string.
        
        """
        return "{0}: (Position:{1}, Velocity:{2})".format(self.name,self.position,self.velocity)
         