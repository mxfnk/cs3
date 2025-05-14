"""
Class to create limited life time dot cloud
"""

import numpy as np
import psychopy.visual
#import psychopy.core
#import psychopy.event
#from psychopy import prefs

class lltDotCloud:
    def __init__(self, pos, n_dots, spawn_sigma,
            win, colors= (255,255,255),lifeSpan = 5):
        """
        From input:
        cloud_pos: [x,y] 1d array. Mean position of the cloud
        n_dots: int. Number of dots
        spawn_sigma: [x,y,rho] 1d array. Initial spawn distance sigma in pix in x and y and correlation rho. Size of the dot patch in stds
        lifeSpan: int. Max. lifetime of an individual dot in frames.
        """
        self.pos = pos
        self.n_dots = n_dots
        self.spawn_Sigma = np.diag(spawn_sigma[:2])**2 # create diag matrix with sigma_X and sigma_Y
        self.spawn_Sigma[1,0] = spawn_sigma[2]*spawn_sigma[0]*spawn_sigma[1] # rho * sigma_X * sigma_Y
        self.spawn_Sigma[0,1] = spawn_sigma[2]*spawn_sigma[0]*spawn_sigma[1]
        self.lifeSpan = lifeSpan
        self.colors = colors
        """
        Set in the class itself:
        xys: [n_dots, 2] 2D array. Dots positions in pixels
        dot_L: [n_dots,1] vertical int array. Individual dot-lifetime
        died: [n_dots,1] vertical bool array. Individual dot-lifetime
        """
        self.xys = np.zeros([n_dots,2])
        self.dot_L = np.zeros([n_dots,1])
        self.died =  np.argwhere(self.dot_L == self.lifeSpan)
        """
        max_distance: float. Max distance from center.
        move: bool. Has the stimulus been initilized?
        thisMIPS: Wrap for ElementArrayStim from Psychopy
        """
        self.move = False # set state to not be initialized
        self.thisCloud = psychopy.visual.ElementArrayStim(win=win,
                                                        fieldPos = self.pos,
                                                        units="pix",
                                                        nElements=self.n_dots,
                                                        elementTex=None,
                                                        elementMask="circle",
                                                        xys=self.xys,
                                                        colorSpace = 'rgb255',
                                                        colors= self.colors,
                                                        sizes=3)


    def main_update(self):
        # First iteration initilize dots
        if self.move == False:
            self.initiate_dots()
        # Then... Update
        else:
            # Dots
            self.update_dots()
            
            # If any dot should die...
            if len(self.died) != 0:
                # Check dead dots and create new ones
                self.check_dots()
                            
            self.thisCloud.fieldPos = self.pos
            #self.thisCloud.draw()
                
            # Set dots pos
            self.thisCloud.xys = self.xys
            
    def initiate_dots(self):
        # Set the life-timers for the dots (frames)
        self.dot_L = np.random.randint(0,self.lifeSpan, size = [self.n_dots,1])
        self.move = True

        # Initiate dots at a random position mu = 0, SD = spawn_sigma
        ## If debug do not correct for lifespan (to check how dots behave under long lifespans)
        self.xys = np.random.multivariate_normal(mean = (0,0), cov = self.spawn_Sigma, size = [self.n_dots])

    def update_dots(self):
        # Dots grow older
        self.dot_L +=  1

        # Find dead dots
        self.died =  np.argwhere(self.dot_L >= self.lifeSpan)


    def check_dots(self):
        # Relocate a new dot
        self.xys[self.died[:,0],:] = np.random.multivariate_normal(mean = (0,0), cov=self.spawn_Sigma, size = [self.died.shape[0]])

        # Rebirth the dots with age 0
        self.dot_L[self.died[:,0]] = 0
    
    def draw(self):
        self.thisCloud.draw()
