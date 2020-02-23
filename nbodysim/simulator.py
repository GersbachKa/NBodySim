import numpy as np
import time

from ipywidgets import interact
from bokeh.io import push_notebook, show, output_notebook
from bokeh.plotting import figure

class Simulator:
    
    class MassObject:
        def __init__(self,name,mass,radius,xPos,yPos,zPos,xVel,yVel,zVel,color):
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
            return (self.x,self.y,self.z)
        
        def getVelocities(self):
            return (self.xVel,self.yVel,self.zVel)
        
    #End Subclass
    
    def __init__(self,notebook=True,defaultSystem=None):
        self.time=0
        self.G = 6.67259 * (10**-11)
        self.setPlot()
        if notebook:
            output_notebook()
        
        if defaultSystem!=None:
            self._importDefaultSystem(defaultSystem)
        else:
            self.massList=[]
    
    
    def _importDefaultSystem(self,name):
        pass
    
    
    def _singleStep(self,dt):
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
        for i in range(0,numSteps):
            self._singleStep(dt)
        if save:
            self._saveState()
    
    
    def _saveState(self):
        pass
    
    
    def plot(self,axes=('x','y'),plotRange=None):
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
                         x_range=self.plotRange,y_range=self.plotRange,
                         x_axis_label = axes[0]+' (m)',y_axis_label = axes[1]+' (m)')
        self.sca= self.fig.scatter(xp,yp,radius=rad)
        show(self.fig,notebook_handle=True)
    
    def _updatePlot(self,axes):
        xp=[]
        yp=[]
        rad=[]
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
        
        self.sca.data_source.data['x']=xp
        self.sca.data_source.data['y']=yp
        self.sca.data_source.data['radius']=rad
        self.fig.title.text = self.plotTitle+'\t \t'+self.getTime()
        push_notebook()
    
    def setPlot(self,plotTitle='N-Body Sim',plotRange=(-5,5),plotSize=600):
        self.plotTitle=plotTitle
        self.plotRange=plotRange
        self.plotSize=plotSize
        
    
    def play(self,dt=.1,numSteps=10,save=False,pause=0,plotFirst=True,axes=('x','y'),plotRange=None):
        if plotFirst:
            self.plot(axes,plotRange)
        
        try:
            while True:
                self.step(dt,numSteps,save)
                time.sleep(pause)
                self._updatePlot(axes)
            
        except KeyboardInterrupt:
            print("Halted")
        
    
    def addMass(self,name='mass',mass=1,radius=1,
                xPos=0,yPos=0,zPos=0,xVel=0,yVel=0,zVel=0,color='Blue'):
        #Default mass names + same mass names
        if self.getMass(name) != None:
            i=1
            newName = name + '('+str(i)+')'
            while self.getMass(newName) != None:
                i+=1
                newName = name + '('+str(i)+')'
            name=newName
        #end names
        
        for o1 in self.massList:
            if o1.getCoordinates() == (xPos,yPos,zPos):
                print('Mass: {} not added (Same position as mass {})'.format(name,o1.name))
        
        m = self.MassObject(name,mass,radius,xPos,yPos,zPos,xVel,yVel,zVel,color)
        self.massList.append(m)
        
    def removeMass(self,nameOrIndex):
        self.massList.remove(self.getMass(nameOrIndex))
    
    def getMass(self,nameOrIndex):
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
        
    
    def _calcForces(self,o1,o2):
        r = np.sqrt((o1.x-o2.x)**2+(o1.y-o2.y)**2+(o1.z-o2.z)**2)
        forceMag =(self.G*(o1.mass)*(o2.mass))/(r**2)
        
        xhat=(o2.x-o1.x)/r
        yhat=(o2.y-o1.y)/r
        zhat=(o2.z-o1.z)/r
                
        fx = forceMag*xhat
        fy = forceMag*yhat
        fz = forceMag*zhat
        
        o1.xForce+=fx
        o1.yForce+=fy
        o1.zForce+=fz
        
        o2.xForce-=fx
        o2.yForce-=fy
        o2.zForce-=fz
    
    
    def _calcAcceleration(self,o1):
        o1.xAccel=o1.xForce/o1.mass
        o1.yAccel=o1.yForce/o1.mass
        o1.zAccel=o1.zForce/o1.mass
    
    
    def _calcMovement(self,o1,dt):
        o1.x += o1.xVel*dt
        o1.y += o1.yVel*dt
        o1.z += o1.zVel*dt
            
        o1.xVel += o1.xAccel*dt
        o1.yVel += o1.yAccel*dt
        o1.zVel += o1.zAccel*dt
    
    
    def _checkCollision(self,o1,o2):
        distance = np.sqrt((o1.x-o2.x)**2+(o1.y-o2.y)**2+(o1.z-o2.z)**2)
        interactionR = o1.radius + o2.radius
                    
        if(interactionR>=distance):
            self._combineMasses(o1,o2)
    
    
    def _combineMasses(self,o1,o2):
        #Dominate mass
        if(o1.mass>=o2.mass):
            dom=o1
            sub=o2
        else:
            dom=o2
            sub=o1
            
        #combine masses
        newM=dom.mass+sub.mass
        
        #combine radii
        dom.radius=(dom.radius**3 + sub.radius**3 )**(1/3)
        
        #combine velocities
        dom.xVel= (dom.mass*dom.xVel+sub.mass*sub.xVel)/newM
        dom.yVel= (dom.mass*dom.yVel+sub.mass*sub.yVel)/newM
        dom.zVel= (dom.mass*dom.zVel+sub.mass*sub.zVel)/newM
        
        dom.mass=newM #setting this value after its final use
        
        
        self.massList.remove(sub)
        
    def getTime(self):
        y, rem = divmod(self.time,31536000)
        d, rem = divmod(rem, 86400)
        h, rem = divmod(rem, 3600)
        m, s = divmod(rem, 60)
        return '+ {}y, {}d, {}:{}:{}'.format(int(y),int(d),int(h),int(m),s)
    