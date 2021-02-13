import numpy as np

#Wow~!

#This file is intended to contain a variety of different utility functions that can be useful
G = 6.6743e-11

def periapsisFinder(orbitMass, semiMajorAxis, eccentricity, inclination):
    """
    This function will calculate the position and velocity of an object at a periapsis of
    an orbit given some mass, semiMajorAxis, eccentricity and inclination.
    
    This function will return a position vector of an object in orbit around another planet 
    at [0,0,0]. The position will always return in the -x direction and a positive inclination
    will push the plane of the orbit into the -z axis. So an i of 5 degrees will shift the
    orbit into the -z direction at the periapsis. The initial velocity will always be in the
    -y direction. 
    
    Parameters:
        orbitMass (double): The mass of the object being orbited in kg.
        semiMajorAxis (double): The semi-major axis of the orbit in m.
        eccentricity (double): The eccentricity of the orbit. This must be between 0 and 1.
        inclination (double): The inclination in degrees of the orbit.
    
    Returns:
        posVector (Numpy Array): The position of the object at the periapsis.
        velVector (Numpy Array): The velocity of the object at the periapsis.
    """
    
    #Velocity----------------
    periSpeed = ((G*orbitMass*(1+eccentricity))/(semiMajorAxis*(1-eccentricity)))**(1/2)
    velVector = np.array([0,-periSpeed,0])
    
    #Position---------------
    deg2Rad = np.pi/180
    posVector = np.array([-(semiMajorAxis*(1-eccentricity)*np.cos(inclination*deg2Rad)),0,
                          -(semiMajorAxis*(1-eccentricity)*np.sin(inclination*deg2Rad))])
    
    return posVector, velVector