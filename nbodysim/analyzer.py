from .simulator import Simulator
import os
import csv
import numpy as np

from bokeh.io import push_notebook, show, output_notebook
from bokeh.plotting import figure

class Analyzer:
    
    def __init__(self,path='',simulator=None,notebook=True):
        currentPath = ''
    
        if path != '':
            if os.path.exists(path):
                if path[-1] !='/':
                    currentPath=path+'/'
                else:
                    currentPath = path
            else:
                print("Path to files does not exist.")
                return
        elif simulator != None:
            currentPath = simulator.path+'/'+simulator.name+'/'
            if not os.path.exists(currentPath):
                print("Path to files does not exist.")
                return
        else:
            print("No path or simulator given.")
            return
        
        if notebook:
            output_notebook()
            self.notebook = True
        else:
            self.notebook = False
        
        self.path=currentPath
        
        self.colorOptions = [(255,0,0),(0,255,0),(0,0,255),(255,255,0),(255,0,255),(0,255,255),(255,255,255)]
        
        self.updateData()
    
    def updateData(self):
        retData = {}
    
        for file in os.listdir(self.path):
            if file.endswith('.csv'):
                fullPath = self.path+file
                name = file[0:-4]
            
                data = []
                with open(fullPath,'r') as f:
                    fullData = list(csv.reader(f))
                    data = np.array(fullData[1:]).astype(np.float)
                
                retData.update({name:data})
        
        self.massData = retData
        
    
    def plot(self,massName,attribute,height=600,width=600):
        
        if isinstance(massName,str):
            massName = [massName]
            attribute = [attribute]
        
        if len(massName) != len(attribute):
            print("Lists are of different sizes.")
            return
        
        time = []
        yvals = []
        
        for i in range(0,len(massName)):
            n = massName[i]
            a = attribute[i]
            time.append(self.massData[n][:,0])
            
            if a.lower() == 'mass':
                yvals.append(self.massData[n][:,1])
            elif a.lower() == 'radius':
                yvals.append(self.massData[n][:,2])
            elif a.lower() == 'x':
                yvals.append(self.massData[n][:,3])
            elif a.lower() == 'y':
                yvals.append(self.massData[n][:,4])
            elif a.lower() == 'z':
                yvals.append(self.massData[n][:,5])
                
            elif a.lower() == 'x-velocity':
                yvals.append(self.massData[n][:,6])
            elif a.lower() == 'y-velocity':
                yvals.append(self.massData[n][:,7])
            elif a.lower() == 'z-velocity':
                yvals.append(self.massData[n][:,8])
                
            elif a.lower() == 'x-acceleration':
                yvals.append(self.massData[n][:,9])
            elif a.lower() == 'y-acceleration':
                yvals.append(self.massData[n][:,10])
            elif a.lower() == 'z-acceleration':
                yvals.append(self.massData[n][:,11])
                
            elif a.lower() == 'x-force':
                yvals.append(self.massData[n][:,12])
            elif a.lower() == 'y-force':
                yvals.append(self.massData[n][:,13])
            elif a.lower() == 'z-force':
                yvals.append(self.massData[n][:,14])
                
            else:
                print("attribute \"{}\" not recognized for mass \"{}\".".format(a,n))
                return
            
        xrange=(min([min(i) for i in time]),max([max(i) for i in time]))
        yrange=(min([min(i) for i in yvals]),max([max(i) for i in yvals]))
       
        fig = figure(plot_height=height,plot_width=width,x_range=xrange,y_range=yrange)
        
        for i in range(0,len(yvals)):
            linecolor = self.colorOptions[i%7]
            
            fig.line(time[i],yvals[i],legend_label=massName[i]+': '+attribute[i],
                     line_color=linecolor)
            
        show(fig,notebook_handle=self.notebook)
        return fig    
                
    