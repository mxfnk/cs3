"""
Show two targets. Record mouse when moving between them.

Run from the command line, from the /src directory. Example:

python fitts_law_exp.py

For more options type 

python basic_demo.py --help
"""

from typing import Tuple

import pandas as pd
import os
import itertools
from psychopy import prefs
from Experiment_helpers.experiment import Experiment, CloudExperiment, repeat_and_shuffle

# to avoid bug on windows (https://www.psychopy.org/troubleshooting.html#errors-with-getting-setting-the-gamma-ramp)
prefs.general["gammaErrorPolicy"] = "warn"

# load relevant stuff from psychopy
from psychopy import gui

# --------------------------------------
# Create writing folder/file
# --------------------------------------
# Before experiment starts
# id info dialog
dlg = gui.Dlg(title = "Introduce participant's ID")
dlg.addField('Participant ID', label ='Participant ID (*)',required = True)
dlg.addText('This will be the name of folder and output-files used for saving the data.')
dlg.addField('Screen', label ='Screen to use (int) (*)',initial = 0, required = True)
dlg.addText('Screen should be 0 if you only have one monitor (e.g. you laptop screen).\n'+\
            'If attaching an extra screen you might want to make this 0 or 1 to decide which monitor to show the stimulus on.\n'+\
            'Note that we did not yet fully test this option so this may lead to unexpected behaviour depending on your specific system.')
ok_data = dlg.show()
if dlg.OK:
  if ok_data['Participant ID'] == '':
    print('No participant alias was entered.\nPlease start again and fill in alias')
    quit()
  participantID = ok_data['Participant ID']
  screenID = ok_data['Screen']
else:
  quit()

## Does data folder exist? If not create it
os.makedirs(os.path.dirname(__file__)+"/data", exist_ok=True)
## Does participant's folder exist? If not create it
participant_folder = os.path.dirname(__file__)+"/data/"+ participantID
os.makedirs(participant_folder, exist_ok=True)

#-------------------------------------
# Create Conditions list
#-------------------------------------
Experiment_Type = 'targetCloud'
start_pos_X = [0]
start_pos_Y = [-240]
start_radius = [10]
target_X_List = [0] # initial dir should be set at random (not an actual thing that distinguishes trials)
target_Y_List = [240] # initial dir should be set at random (not an actual thing that distinguishes trials)
target_SDS = [(10,10)]
cursor_SDS = [(50,200),(100,100),(200,50)]
nDotsTarget = [1]
nDotsCursor = [200]
cursor_shift = [-240,0,240]
shift_threshold = [-240]
## Lifespan:
myLifeSpan = 5 # frames
lSpan = [myLifeSpan] # this should be 5 frames at 60Hz or the equivalent of that at higher frame rates

dfColumns = ['start_X','start_Y','startradius','target_X','target_Y','target_SX','target_SY','nDotsTarget',
             'cursor_SX','cursor_SY','nDotsCursor','cursor_shift','shift_threshold']

expConds = list(itertools.product(*[start_pos_X,start_pos_Y,start_radius,target_X_List,target_Y_List,
                                                 target_SDS,nDotsTarget,cursor_SDS,nDotsCursor,cursor_shift,shift_threshold]))
# flatten the rows removing the tuples
for row in range(0,len(expConds)):
    expConds[row] = list(itertools.chain(*(i if isinstance(i, tuple) else (i,) for i in expConds[row])))
# convert to pandas dataframe
expCondsDF = pd.DataFrame(expConds, columns = dfColumns).reset_index()
# add repetitions and shuffle the order of the trials
expCondsDF = repeat_and_shuffle(expCondsDF, 5, shuffle = True)


def main(windowed: bool, resolution: Tuple[int, int], screen: int, debug: bool,
         participant: str, participant_folder: str):
    """
    Starts the experiment
    """
    experiment: Experiment = CloudExperiment(
        windowed=windowed,
        resolution=resolution,
        screen=screen,
        trialList = expCondsDF,
        participantID = participant,
        dataDir = participant_folder,
        debug = debug,
    )
    experiment.run()

main(
    windowed = False,
    resolution = [1440,900],
    screen = screenID,
    debug = False,
    participant = participantID,
    participant_folder = participant_folder)

