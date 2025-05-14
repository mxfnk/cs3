# Handeln Summer Semester Experiment component

## target shape experiment 

This experiment is coded with PsychoPy. It requires the participant to move to and click on a target - ideally with a graphics tablet or mouse. Note that the target and/or cursor can vary in shape, which is one of the things we will be looking at. The scoring of points may also vary depending on the exact task.

For the report:
Pay close attention to what separate conditions you recognise in the experiment. You will have to separate these in your analysis later on. So write down anything you notice from the experiment once you have gone through the experiment.

## Running the experiment

#### Starting from the command line
You can run the experiment from the command by navigating to the correct folder. Make sure you have activated the handeln conda environment. If not already done so you can activate it by typing:

`conda activate handeln2025` 

Then, to start the experiment type:  
`python main.py`

#### Starting from within VS code
When starting the experiment from within VS code you have to make sure VS code is using the right kernel and that it knows the right working directory.

### Entering Participant Alias
With either way of starting the experiment a window will pop up in which you can specify an alias for the current participant. This alias will also be used to store the data. That is, a `data` folder will be created in the case it does not already exist and within this `data` another subfolder will be created with the participant alias you entered in the pop-up window. In this folder the data for the current participant will be stored.


## During the experiment

###  Trial procedure

At the start of the trial you will see some instruction text and a green circle in the bottom half of your screen, centered with respect to the horizontal midline. This green circle will be your trial-starting point. To start a pointing trial you have to move your cursor onto the green circle and click on it. Then a target appears either to the top-left or top-right of the screen. Note that the target can either be a solid object (circular or elongated) or consist of a number of dots that are roughly Gaussian distributed.

***Your task*** is to click with the ***centre*** of the cursor on the ***centre*** of the target as fast and as accurately as you can. 

When you click on the target it will disappear and you will be shown the starting screen for the next trial.

It is best to use a computer mouse, or if you have one, even better would be to use a graphics tablet, for this task. As a last resort a trackpad can be used, but in this case you should expect that the movements are likely to consist of multiple sub-movements, which may interfere with the research question somewhat. If necessary you can also ask us for a default dataset for the current experiment.

## After the experiment

Of course after the experiment we will want to have a look at the data so here are a few pointers so how the data-files resulting from the experiment will look like.

As indicated above the data is stored in a folder `data` with the alias you entered at the start of the experiment as a subfolder. Within that specific subfolder there is a separate file for each trial in the experiment. Each file therefore constitutes one movement to a given target.

The file structure for the data of each trial is as follows. The file consists of two parts. The first part is a single row of values accompanied with an appropriate header to indicate the condition for a given trial. This lists:

| input         | description    |
|---------------|------|
| `start_X`     | X-location of starting point for the trial   |
| `start_Y`     | Y-location of starting point for the trial |
| `startradius` | the radius of the starting position dot in which to click to start the trial   |
| `target_X`    | X-location of the target to point to |
| `target_Y`    | Y-location of the target to point to  |
| `target_SX`   | target horizontal size (if dot cloud its horizontal standard deviation)   |
| `target_SY`   | target vertical size (if dot cloud its vertical standard deviation)  |
| `nDotsTarget` | nr of dots included for displaying the target (if 1: single oval with size indicated above; if > 1 dot cloud distributed with SD indicated above)  |
| `cursor_SX`   | cursor horizontal size    |
| `cursor_SY`   | cursor vertical size    |
| `nDotsCursor` | nr of dots included for displaying the cursor (see target above)    |
| `cursor_shift`| shift size for the cursor (sign indicating the direction left (-) or right (+) ) |
| `shift_threshold` | threshold in y-direction when to apply to shift|
| `trial_score` |  the score the participant received for this trial |

The second part of the file contains the actual data for the trial. That is this contains the trajectory the cursor made in the trial. This is listed as a time series containing the following elements:

| column label | description |
|---|---|
| `time`        | the time stamp of the sample |
| `frame_nr`    | the frame number of the sample (this might be easier to work with than the actual time stamp) |
| `cursor_x`    | the cursor X position in pixels |
| `cursor_y`    | the cursor Y position in pixels |
| `shift_applied` | whether the shift was already applied (1) or not (0) within the trail. |

Note that spatial data is stored as pixel values. Best practice is to convert these to SI units using the screen dimension and screen resolution of your setup for your report.

