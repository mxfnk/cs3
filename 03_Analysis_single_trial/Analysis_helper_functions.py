# HElper functions for the analysis of the Handeln experiment

from typing import List
import numpy as np
import pandas as pd


def velocity(trialData:pd.DataFrame, itemList:List[str], itemTime:str) -> np.array:
    """The output has the following format for the columns:
        [time, velocity in X, velocity in Y, absolute speed]

    Args:
        trialData (pd.DataFrame): the data for a particular condition
        itemList: list of column names that contains the data to compute speed of
        itemTime: column name for the column containing the timestamps

    Returns:
        np.array: numpy array with velocity data in it.
    """    
    # get the relevant data convert data to numpy
    npXY = np.array(trialData[itemList])
    
    # get the time interval between samples
    Dt = trialData[itemTime].diff()
    meanDt = Dt.mean()
    
    # apply the formula mentioned above to get velocity in X and Y
    # we can do this in one go on the complete array (no need for a for-loop)
    vXY = (npXY[4:,:]-npXY[0:-4,:]+npXY[3:-1,:]-npXY[1:-3,:])/(6*meanDt)
    # get the absolute speeds using Pythagoras
    if len(itemList) == 1:
        absSpeed = np.abs(vXY)
    else:
        absSpeed = np.sqrt(vXY[:,0]**2+vXY[:,1]**2)
    # get the time samples (note we have to shorten a bit to make it equal in lenght to vXY)
    time = np.array(trialData['time'])
    time = time[2:-2]
    
    # put the elements together
    rowlen = len(itemList)+2
    vXY = np.hstack((time[:,None],vXY,absSpeed[:,None]))
    # pad zeros for time-stamps for which velocity could not be computed
    vXY = np.vstack((np.zeros((2,rowlen)),vXY,np.zeros((2,rowlen))))
    
    return vXY


def normalize_time(data):
    """
    Normalize the time frame to go from 0 to 1.

    input:
    data: dataframe with trajectory data for one trial

    output:
    dataframe with normalized trajectory data after resampling to the normalized timeframe
    """
    data.loc[:,'datetime'] = pd.date_range('1/1/2001 00:00:00', '1/1/2001 00:00:01',len(data))
    normdata = data.set_index('datetime', drop = True).resample('10ms').mean().interpolate()
    normdata['normtime'] = np.arange(0,1.01,0.01)
    normdata = normdata.reset_index(drop=True)

    return normdata


def remove_outliers(data:pd.DataFrame, trial_var:str='trial', conditions=None) -> pd.DataFrame:
    """
    Will remove outliers based on the mean and the standard deviation of the movement time accross trials.
    A trial will be removed if the movement time is more than 3 std away from the mean in either direction.

    Input:
    data:   pandas DataFrame with all trajectory data. Note the algorithm assumes there is a column called 'trial' that keeps a trial index.
            The optional parameter trial_var can be used if this column has been named differently.

    trial_var (string, optional): column name in which the trial numbers for the samples are stored. Defaults to 'trial'.
    conditions (optional): dataframe that has the trial conditions in case you keep a separate dataframe for this.
            This should also have a similar trial column called 'trial' or trial_var as the trajectory dataframe.

    Deviating trials will be removed from data or both dataframes, if conditions is provided.
    """

    trial_nrs = data[[trial_var]].drop_duplicates().sort_values(by=[trial_var], axis = 0).reset_index(drop=True)
    for trial in trial_nrs[trial_var]:
        trial_data = data.loc[data[trial_var] == trial,:]
        mov_time = np.max(trial_data['time'])
        if trial == trial_nrs.loc[0,trial_var]:
            movtimelist = np.array([[trial,mov_time]])
        else:
            movtimelist = np.concatenate((movtimelist,[[trial,mov_time]]),axis = 0)

    mean_mt = np.mean(movtimelist[:,1])
    std_mt = np.std(movtimelist[:,1])

    movtimelist[:,1] = np.abs(movtimelist[:,1]-mean_mt)/std_mt

    flag4removal = movtimelist[movtimelist[:,1]>3,0]

    print('------------------\n')
    print('The following trials will be removed from the data base on outlier analysis:\n')
    print(flag4removal)
    print('------------------\n')

    new_data = data[~data[trial_var].isin(flag4removal)]
    if conditions is not None:
        new_cons = conditions[~conditions[trial_var].isin(flag4removal)]
        return new_data, new_cons
    
    return new_data