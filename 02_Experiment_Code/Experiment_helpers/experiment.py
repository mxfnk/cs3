from typing import Tuple, List

import numpy as np
import pandas as pd
import psychopy
from psychopy.event import Mouse
from psychopy.visual import Window
from psychopy.clock import Clock
from psychopy.visual.circle import Circle
from psychopy.visual import TextStim
#from psychopy import event
#from psychopy import visual
#from Experiment_helpers.dots_class import lltDotCloud
from .dots_class import lltDotCloud

import os
import csv

def repeat_and_shuffle(df, reps = 5, shuffle = True, grouping = "None"):
    df = pd.concat([df]*reps,ignore_index=True)
    if shuffle:
        if grouping == "None":
            df = df.sample(frac = 1).reset_index(drop = True)
        else:
            df = df.groupby(grouping).sample(frac=1).reset_index(drop=True)
    else:
        df = df.sort_values(by=grouping,kind='stable').reset_index(drop=True)
        
    return df


class Experiment:
    window: Window
    mouse: Mouse

    framerate: int
    debug: bool

    running: bool

    def __init__(self, windowed: bool, resolution: Tuple[int, int], screen: int, debug: bool = False):
        self.debug = debug

        # self.window = Window(
        #     size=resolution,
        #     units="pix",
        #     screen=screen,
        #     checkTiming=True,
        #     fullscr=not windowed,
        #     allowGUI=True,
        # )
        self.window = Window(
            screen=screen,
            size=resolution,
            units="pix",
            colorSpace = "rgb255",
            color = (128,128,128),
            fullscr=not windowed
        )

        self.mouse = Mouse(
            win=self.window,
            visible=debug
        )

        self.running = True

        psychopy.core.wait(0.1)

    def handle_keys(self):
        keys = psychopy.event.getKeys()

        for key in keys:
            if key == "q" or key == "escape":
                self.running = False
                self.exit()

            self.key(key)

    def run(self):
        while self.running:
            self.handle_keys()

            self.update()
            self.draw()

            self.window.flip()

        self.exit()

    def exit(self):
        self.on_exit()

        self.window.close()
        psychopy.core.quit()

    def update(self):
        pass

    def draw(self):
        pass

    def key(self, key: str):
        pass

    def on_exit(self):
        pass

    def text(self, message: str):
        pass
    
# -----------------------------------------------
# Target is dot Cloud experiment
# -----------------------------------------------


class FeedbackText:

    #isInTrial: bool

    def __init__(self,win):
        """
        little class for score updates
        """
        self.textElem = TextStim(
            win,
            units="norm",
            text=(""),
            wrapWidth=0.9,
            height=0.05,
        )
        self.isInTrial = False

    def update(self,score,totalScore,inTrial,addText):
        # create text elements for showing score
        if inTrial:
            if score < 0:
                self.textElem.color = "red"
            else:
                self.textElem.color = "white"
            if not self.isInTrial:
                self.isInTrial = True
                self.textElem.pos=(0,0.9)
                self.textElem.height = 0.2
                self.textElem.anchorHoriz = 'center'
                self.textElem.anchorVert = 'top'
            scoretext=("Score: " + str(score))
        else:
            self.isInTrial = False
            self.textElem.color = "white"
            self.textElem.pos=(0,0)
            self.textElem.height = 0.1
            self.textElem.anchorHoriz = 'center'
            self.textElem.anchorVert = 'center'
            scoretext = "Score this trial: " + str(score) + "\n\nTotal Score: " + str(totalScore)
        self.textElem.text = scoretext + addText
        self.textElem.draw()



class CloudExperiment(Experiment):
    participantID: str
    dataDir: str

    # dependent on cloud item if cloudItem = 'cursor' the following two are swapped
    target: None
    cursor: None
    presursor: Circle # cursor before trial really starts (non-cloud per definition)
    startpoint: Circle
    timer: Clock
    shift: int
    shift_threshold: int
    shift_applied: int

    conditions: pd.DataFrame

    trial: int
    trialPhase: int
    frameCount: int
    trialScore: int
    totalScore: int
    trialStartTime: int

    trialHistory: List[
        list[
            int, int, int, int, int]]  # List[List[int, int, int, int]] "time", "cursor_x", "actual_cursor_x"  "snake/buttons_x"


    #text_between_trials: visual.TextStim
    text_between_trials: TextStim
    scoreText: TextStim

    # def __init__(self, windowed: bool, resolution: Tuple[int, int], screen: int, trialList: pd.DataFrame, participantID: str, dataDir: str,
    #              cursor_size: Tuple[int, int] = (5,5), target_size: Tuple[int, int] = (50,100), debug: bool = False ):
    def __init__(self, windowed: bool, resolution: Tuple[int, int], screen: int,
                 trialList: pd.DataFrame, participantID: str, dataDir: str,
                 debug: bool = False ):
        super().__init__(windowed, resolution, screen, debug)

        self.text_startExperiment = TextStim(self.window,
            text='----- Hit the target -----\n\n\n\n'
            'In the following trials you will be making reaching movements, where you should try to hit the '
            'CENTRE of targets with the CENTRE of the cursor.\n\n'
            'This means you should try to click as close to the CENTRE of each targets as you can get.\n'
            'Simply clicking anywhere on the target, with any part of the cursor won\'t give you as many points\n'
            'as clicking on the centre of the target with the centre of cursor.\n'
            '\n'
            'To continue press space'
            , pos=(0,0), color="white")
        self.text_startExperiment.draw()
        self.window.setMouseVisible(False)
        self.window.flip()
        psychopy.event.waitKeys(keyList = ['space'])

        self.text_between_trials = TextStim(self.window,
                                        text='----- Hit the target -----\n\n\n\n'
                                        'Start the trial: click on the start position. A pointing target will appear. '
                                        'The target and or cursor may be represented by a normally distributed cloud of dots.\n\n'
                                        'Using the CENTRE of the cursor, move to and click on the CENTRE of the target '
                                        'as fast and accurately as you can.'
                                        , pos=(0,0), color="white")
        
        self.scoreText = TextStim(
            self.window,
            text="Total Score: 0",
            color = "white",
            pos = (0,200)
        )

        self.participantID = participantID
        self.dataDir = dataDir

        self.precursor = Circle(
                win=self.window,
                radius=5,
                fillColor="black",
                colorSpace='rgb',
                pos=(0,0)
            )

        self.conditions = trialList
        # initialize handlers
        self.trial = 0
        self.trialPhase = 0
        self.frameCount = 0
        self.trialScore = 0
        self.totalScore = 0

        self.timer = Clock()
        self.start_trial()


    def start_trial(self):

        # Draw the text stimulus
        # self.text_between_trials.draw()
        # self.window.flip()

        mousepos = self.mouse.getPos()

        if self.conditions.loc[self.trial,'nDotsCursor'] == 1:
            self.cursor = Circle(
                win=self.window,
                radius=(self.conditions.loc[self.trial,'cursor_SX'],self.conditions.loc[self.trial,'cursor_SY']),
                fillColor="black",
                colorSpace='rgb',
                pos=mousepos
            )
        else:
            self.cursor = lltDotCloud(
                pos = mousepos,
                n_dots = self.conditions.loc[self.trial,'nDotsCursor'],
                spawn_sigma = (self.conditions.loc[self.trial,'cursor_SX'],self.conditions.loc[self.trial,'cursor_SY'],0),
                win = self.window,
                colors = (0,0,0),
                lifeSpan = 5)

        if self.conditions.loc[self.trial,'nDotsTarget'] == 1:
            self.target = Circle(
                win=self.window,
                radius= (self.conditions.loc[self.trial,'target_SX'],self.conditions.loc[self.trial,'target_SY']),
                fillColor="white",
                colorSpace='rgb',
                pos=(self.conditions.loc[self.trial,'target_X'],self.conditions.loc[self.trial,'target_Y'])
            )
        else:
            self.target = lltDotCloud(
                pos = (self.conditions.loc[self.trial,'target_X'],self.conditions.loc[self.trial,'target_Y']),
                n_dots = self.conditions.loc[self.trial,'nDotsTarget'],
                spawn_sigma = (self.conditions.loc[self.trial,'target_SX'],self.conditions.loc[self.trial,'target_SY'],0),
                win = self.window,
                lifeSpan = 5)

        self.startpoint = Circle(
            win=self.window,
            radius=self.conditions.loc[self.trial,'startradius'],
            fillColor="green",
            colorSpace='rgb',
            pos=(self.conditions.loc[self.trial,'start_X'],self.conditions.loc[self.trial,'start_Y'])
        )
        self.window.setMouseVisible(False)

        # update score text
        self.scoreText.text = "Trial Score = " +str(self.trialScore) +"\nTotal Score: " + str(self.totalScore)

        self.trialHistory = []
        self.trialPhase = 0
        self.frameCount = 0
        self.trialScore = 0
        self.shift = self.conditions.loc[self.trial,'cursor_shift']
        self.shift_threshold = self.conditions.loc[self.trial,'shift_threshold']
        self.shift_applied = 0

        self.timer.reset()
        

    def update(self):
        # get mouse position
        self.cursor.pos = self.mouse.getPos()
        self.precursor.pos = self.cursor.pos
        checkclick = (self.mouse.getPressed()[0]==1)
        startErr = np.sqrt((self.cursor.pos[0]-self.startpoint.pos[0])**2 + (self.cursor.pos[1]-self.startpoint.pos[1])**2)
        # match self.trialPhase:
        #     case 0:
        if self.trialPhase == 0:
            # check if click on start happened
            self.text_between_trials.draw()
            self.scoreText.draw()
            if checkclick and startErr < self.startpoint.radius:
                self.trialPhase += 1
                self.frameCount = 0
                self.timer.reset()
        if self.trialPhase == 1:
            # case 1:
            self.frameCount +=1
            if self.cursor.pos[1] > self.shift_threshold:
                self.cursor.pos[0] = self.cursor.pos[0]+self.shift
                self.shift_applied = 1
            # in pointing phase of the trial
            if isinstance(self.target, lltDotCloud ):
                self.target.main_update()
            if isinstance(self.cursor, lltDotCloud ):
                self.cursor.main_update()

            # append the current history to the trialHistory
            self.trialHistory.append(
                [self.timer.getTime(), self.frameCount, self.cursor.pos[0], self.cursor.pos[1], self.shift_applied])
            
            # check if click and significantly away from starting point
            # this is the condition to end a trial
            if checkclick and startErr > 2*self.startpoint.radius:
                # write trial and setup next trial
                # create a new CSV file for each trial and put it in the folder
                file_name = f"participant_{self.participantID}_trial_{self.trial}_trajectory.csv"
                file_path = os.path.join(self.dataDir, file_name)

                # update trial score based on whether hit or not
                self.compute_EndScore(self.conditions.loc[self.trial,'target_SX':'target_SY'],
                                self.conditions.loc[self.trial,'cursor_SX':'cursor_SY'])
                #self.trialHistory[-1][-1] = self.trialScore
                self.totalScore += self.trialScore

                # write out trial_results
                with open(file_path, "a", newline="") as f:
                    writer = csv.writer(f)
                    # TODO : add as first line the 0th line of the input csv file:
                    #writer.writerow(self.conditions.columns)
                    # TODO : add corresponding to trial row from input file
                    temprow  = self.conditions.iloc[[self.trial],:]
                    temprow['trial_score'] = self.trialScore
                    writer.writerow(temprow.columns)
                    writer.writerow(temprow.iloc[0,:])
                    #writer.writerow(self.conditions.iloc[self.trial,:])
                    # write for trajectory data
                    writer.writerow(["time", "frame_nr", "cursor_x", "cursor_y", "shift_applied"])
                    writer.writerows(self.trialHistory)
                
                self.trial += 1
                if self.trial >= len(self.conditions):
                    self.exit()

                #self.start_trial(self.trial)
                self.start_trial()

    def draw(self):
        # match self.trialPhase:
        #     case 0:
        if self.trialPhase == 0:
                self.startpoint.draw()
                self.precursor.draw()
            # case 1:
        if self.trialPhase == 1:
                self.target.draw()
                self.cursor.draw()

    # def update_InTrialScore(self,targetSize,cursorSize):
    #     error = (self.cursor.pos[0]-self.target.pos[0])**2/2*(targetSize[0]+cursorSize[0])**2 + \
    #             (self.cursor.pos[1]-self.target.pos[1])**2/2*(targetSize[1]+cursorSize[1])**2
    #     if error > 1:
    #         # add penalty if penalty experiment
    #         self.trialScore += 0

    def compute_EndScore(self,targetSize,cursorSize):
        # compute distance taking sizes into account
        # since participants need to aim for centre of the target we here only take size of cursor into account
        # note this can be changed if the task of the experiment changes
        error = np.sum( (self.cursor.pos-self.target.pos)**2/(2*targetSize**2) ) 
        if error < 1:
            score = 100
        else:
            slope = 1/5
            score = int(np.round(100* np.exp(-(error-1)*slope) ))
        self.trialScore += score


    # def text(self, message: str):
    #     instructions = TextStim(
    #         self.window, text=message, wrapWidth=700, height=32,
    #     )

    #     instructions.draw()
    #     self.window.flip()

    #     event.waitKeys()