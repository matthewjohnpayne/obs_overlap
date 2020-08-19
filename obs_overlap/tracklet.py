'''
MJP 2020_08_14

The classes in "tracklet" focus on the functions needed to
operate on a tracklet of (new) observations to decide on
the overlap status of the constituent observations.

It will assume that constituent observations will have already
had their "ObsGroup" status calculated / set

'''

# -------------------------------------------------------------
# Third Party Imports
# -------------------------------------------------------------
import sys, os

# -------------------------------------------------------------
# Local Imports
# -------------------------------------------------------------
from db import TrackletID
#from group_observations import Obs , assign_groupID


# -------------------------------------------------------------
# Tracklett Class <==> Accepted Observations Table
# -------------------------------------------------------------
class Tracklet():
    '''
    Real tracklets will probably need more attributes than this
    This is just the subset I needed to get my code working
    '''
    def __init__(self, observations):
        self.TrackletID = TrackletID.get_next_from_db()
    
        self.observations = { o.ObsID:o for o in observations}
        
    # -------------------------------------------------------------
    # Functions to understand overlap between new tracklet &
    # previously submitted tracklets
    # -------------------------------------------------------------
    """
    def categorize_overlap(self, new_tracklet_observations , DB ):
        
        assert np.all( [_.desig for _ in new_tracklet_observations]), 'Not all new_tracklet_observations have the same  desig '
        
        for obs in tracklet_observations:
            print(obs.ObsGroupID)
        
        # Count the number of ObsGroupID members for each new_tracklet_observation
        # NB: At this point, the known_obs *DOES* contain tracklet_observations
        # ***   THIS WOULD BE FAR BETTER DONE AS AN SQL QUERY !!!  ***
        n_members = [ np.len( [known for known in known_obs if known.ObsGroup == _.ObsGroup] ) for _ in new_tracklet_observations ]

        # If all ==1 , then there is no overlap (disjoint) [which we hope is standard / common]
        if np.all( np.asarray(n_members) == 1 ) :
            tracklet_processing_blackbox( new_tracklet_observations , {'OVERLAP':'DISJOINT', 'MODE':'BACKFILL' } , destination_dict)

        sys.exit()
        

    def tracklet_processing_blackbox( new_tracklet_observations , param_dict , destination_dict)
        '''
        For *new* tracklets, I imagine a lengthy process that
        (i) checks whether this is any known designated object
         - this may involve a number of steps, including performing orbit fits
        (ii) checks whether this can be joined with any ITF tracklets
        (iii)
        
        For tracklets that we are back-filling from the obs-table / flat-files, ...
        I think that we will have to grandfather them in (perhaps only performing
        a subset of the checks?) and only flag-up a subset of egregious errors
        
        '''
        if param_dict['MODE'] != 'BACKFILL':
            print('Standard Processing Mode for New Observations')
        else:
            print('BACKFILL Mode: Lengthy checks will be SUPPRESSED')
            

        
"""
