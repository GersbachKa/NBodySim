import os
import csv
import numpy as np

from bokeh.io import push_notebook, show, output_notebook
from bokeh.plotting import figure

class Analyzer:
    """
    A class for analyzing a saved simulation.
    
    Create an instance of this to analyze a previously saved simulation
    
    Attributes:
        notebook (bool): A boolean on whether to output the resulting plots to a notebook.
        path (str): A string representing the folder where the .csv files are saved.
        colorOptions (list): A list of (r,g,b) color values which the plotting tool will use.
        objectData (Dict): An dictionary of name keys to get to the parameter data of that object name.
    """
    
    def __init__(self,path='',notebook=True):
        """
        A constructor for the analyzer.
        
        Use this constructor with the path of the saved simulation to allow for
        plotting of the various objects' parameters over time.
        
        Parameters:
            path (str): A string representing the folder where the .csv files are saved.
            notebook (bool): A boolean on whether to output the resulting plots to a notebook.
        """
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
        else:
            print("No path given.")
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
        """
        This method update the data stored within the objectData dictionary.
        
        If the data within the path variable changes, this upadteData method will refresh 
        the data in this object to reflect that change.
        """
        retData = {}
    
        for file in os.listdir(self.path):
            if file.endswith('.csv'):
                fullPath = self.path+file
                name = file[0:-4]
            
                data = []
                with open(fullPath,'r') as f:
                    fullData = list(csv.reader(f))
                    data = np.array(fullData[1:])
                    data = np.array(data[:,:12]).astype(np.float)
                
                retData.update({name:data})
        
        self.objectData = retData
        
    
    def plot(self,objectName,attribute,height=400,width=600):
        """
        A method to plot one or several time-varying attributes.
        
        This method takes in two lists representing the object names and parameters
        which can vary over time. The two lists must have the same number of elements
        and will be interpreted as plotting objectName[i]'s attribute[i]'s parameter over
        time.
        Valid options of attributes are: 'mass', 'radius', 'x', 'y', 'z', 'x-velocity' or
        'vx', 'y-velocity' or 'vy', 'z-velocity' or 'vz', 'x-acceleration' or 'ax', 
        'y-acceleration' or 'ay', 'z-acceleration' or 'az'
        
        Parameters:
            objectName (list): A list of objects to have their parameters plotted
            attribute (list): A list of object parameters to plot.
            height (int): the number of vertical pixels the plot will take up
            width (int): the number of horizontal pixels the plot will take up
        """
        
        if isinstance(objectName,str):
            objectName = [objectName]
            attribute = [attribute]
        
        if len(objectName) != len(attribute):
            print("Lists are of different sizes.")
            return
        
        time = []
        yvals = []
        
        for i in range(0,len(objectName)):
            n = objectName[i]
            a = attribute[i]
            time.append(self.objectData[n][:,0])
            
            if a.lower() == 'mass':
                yvals.append(self.objectData[n][:,1])
            elif a.lower() == 'radius':
                yvals.append(self.objectData[n][:,2])
            elif a.lower() == 'x':
                yvals.append(self.objectData[n][:,3])
            elif a.lower() == 'y':
                yvals.append(self.objectData[n][:,4])
            elif a.lower() == 'z':
                yvals.append(self.objectData[n][:,5])
                
            elif a.lower() == 'x-velocity' or a.lower() == 'vx':
                yvals.append(self.objectData[n][:,6])
            elif a.lower() == 'y-velocity' or a.lower() == 'vy':
                yvals.append(self.objectData[n][:,7])
            elif a.lower() == 'z-velocity' or a.lower() == 'vz':
                yvals.append(self.objectData[n][:,8])
                
            elif a.lower() == 'x-acceleration' or a.lower() == 'ax':
                yvals.append(self.objectData[n][:,9])
            elif a.lower() == 'y-acceleration' or a.lower() == 'ay':
                yvals.append(self.objectData[n][:,10])
            elif a.lower() == 'z-acceleration' or a.lower() == 'az':
                yvals.append(self.objectData[n][:,11])
                
            else:
                print("attribute \"{}\" not recognized for object \"{}\".".format(a,n))
                return
            
        xrange=(min([min(i) for i in time]),max([max(i) for i in time]))
        yrange=(min([min(i) for i in yvals]),max([max(i) for i in yvals]))
       
        TOOLS="hover,crosshair,pan,box_zoom,wheel_zoom,zoom_in,zoom_out,reset,save"
    
        fig = figure(plot_height=height,plot_width=width,x_range=xrange,y_range=yrange,tools=TOOLS)
        
        for i in range(0,len(yvals)):
            linecolor = self.colorOptions[i%7]
            
            fig.line(time[i],yvals[i],legend_label=objectName[i]+': '+attribute[i],
                     line_color=linecolor)
            
        show(fig)
        return fig    
                
    