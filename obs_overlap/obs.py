'''
MJP 2020_08_14

The Obs class in "obs.py" focuses on the functions needed to
work out whether an individual "new" observation is
similar to any other observations already known.

If so, the group of similar observations will be
assigned to an "ObsGroup"

'''

# -------------------------------------------------------------
# Third Party Imports
# -------------------------------------------------------------
import sys, os
import numpy as np
from collections import namedtuple
import healpy as hp
from datetime import date, timedelta
import dateutil.parser

# -------------------------------------------------------------
# Local Imports
# -------------------------------------------------------------
from db import AcceptedObsID
#from obs_group import ObsGroup



# -------------------------------------------------------------
# Obs Class <==> Accepted Observations Table
# -------------------------------------------------------------
class Obs():
    '''
    Real obs will obviously need more attributes than this
    This is just the subset I needed to get my code working
    '''
    def __init__(self,RA,Dec,ObsTime,ObsCode, Replaces, desig, Deleted, db):

        # Generate a unique ID (as if from db)
        self.ObsID      = AcceptedObsID.get_next_from_db()
        
        # Observation-level data
        # Supplied at point of submissions
        self.RA         = RA
        self.Dec        = Dec
        self.ObsTime    = dateutil.parser.isoparse(ObsTime)
        self.ObsCode    = ObsCode
        self.Replaces   = Replaces
        self.desig      = desig
        self.Deleted    = Deleted

        # Calculated by us as/after we insert
        self.SimilarityGroupID      = None
        self.Healpix                = None
        self.PROCESSING_COMPLETE    = False

        # Allow the parent TrackletID to be stored in the observation
        #(this will be set by the parent)
        self.TrackletID = None
        self.BatchID    = None

        # Store self in db
        #db.ACCEPTED.append(self)
        
        
    def __str__(self,):
        return str(self.ObsID)
        
    # -------------------------------------------------------------
    # Core Functions: assign observations to groups
    # -------------------------------------------------------------

    def find_similar(self,target_obs, previous_obs):
        ''' find observations that are related/near-duplicate to the supplied target observation
        
        A wrapper around an updated version of check-near-dups
        
        No need to iterate: observations that are already in the accepted
        table will already have an assigned SimilarityGroupID
        
        '''
        
        # (1) Check for near duplicates using a version of the cnd.py algorithm
        similar_observations = self.upgraded_check_near_dups(target_obs, previous_obs)
        
        # (2) Check explicit remeasurement / similarity indicator(s)
        # N.B.
        # - Only need to check the *new* observation: all the ones in the db
        #   have already been checked.
        #
        # (2a) Here I check whether the incoming observation has been explicitly
        #      labelled as replacing a previously known observation
        #      (presumably labelled by submitting observer in some manner)
        if target_obs.Replaces is not None :
            similar_observations.extend( [_ for _ in previous_obs if _.ObsID == target_obs.Replaces] )
        
        # Ensure returned set contains target_obs
        similar_observations.append(target_obs)
        return list(set(similar_observations))


                
    # -------------------------------------------------------------
    # Upgraded check-near-dups logic ...
    # -------------------------------------------------------------
    def upgraded_check_near_dups(self,target_obs, previous_obs):
        ''' check for near duplicates
        
        *** THIS SHOULD PROBABLY BE IMPLEMENTED DIRECTLY IN SQL ***
        ***      (NOT JUST AS AN IMPORTED PYTHON FUNC)          ***
        
        This is rough-and-ready
         - Refer to the original cnd.py for more details ...

         # N.B. (1)
         # - The critical times and separations assumed in cnd.py  become
         #   look-up functions that are functions of ObsCode, and perhaps ObsTime
         # N.B. (2)
         # - The obscode check in cnd.py check for
         #   similarly located / equivalent obscodes (from a pre-defined dict)
         
        '''
        
        # Calc healpix for new object (saved as object attribute)
        self.set_observation_healpix(target_obs)
        
        # Get shortlist of similar observations based on healpix
        shortlist_prev_obs = self.get_similar_observations_based_on_healpix(target_obs,previous_obs)
        # Refine shortlist based on ...
        # (i) Angular separation
        if shortlist_prev_obs:
            shortlist_prev_obs = self.get_close_angular_sepn(target_obs , shortlist_prev_obs)
        # (ii) Difference in time
        if shortlist_prev_obs:
            shortlist_prev_obs = self.get_close_in_time(target_obs , shortlist_prev_obs)
        # (iii) Similarity in obsCode
        if shortlist_prev_obs:
            shortlist_prev_obs = self.get_close_observatory_location(target_obs , shortlist_prev_obs)

        return shortlist_prev_obs

    def set_observation_healpix(self,obs, sideHP=32768, nestedHP=True):
        '''
        Set healpix for observations using standard parameters
        See original cnd.py for more details
        '''
        obs.Healpix = hp.ang2pix(sideHP , np.radians(obs.RA) , np.radians(90.-obs.Dec), nest=nestedHP)

    def get_similar_observations_based_on_healpix(self,target_obs,previous_obs):
        '''
        Get any known observations that are in healpix near to the target_obs
        See original cnd.py for more details
        ***         OBVIOUSLY THIS SHOULD BE A TRIVIAL SQL QUERY        ***
        '''
        return [obs for obs in previous_obs if obs.Healpix in self.get_nearby_healpix_list(target_obs) ]

    def get_nearby_healpix_list(self,obs, sideHP=32768, nestedHP=True):
        ''' See original cnd.py for more details '''
        
        # If arcsecRadius < hp.nside2resol(32768, arcmin = True)*60 [ which is ~ 6.4 arc-sec ], ...
        # ... then only need to search adjacent HP
        listHP = list(hp.get_all_neighbours(sideHP, obs.Healpix, nest=nestedHP ))
        listHP.append(obs.Healpix)

        # If arcsecRadius > hp.nside2resol(32768, arcmin = True)*60, then need to search neighbors of neighbours ...
        arcsecRadius = self.get_arcsecRadius(obs)
        if arcsecRadius > hp.nside2resol(sideHP, arcmin = True)*60 :
            for i in range(int( arcsecRadius // (hp.nside2resol(sideHP, arcmin = True)*60) )):
                tmpHP = [h for h in listHP]
                for h in tmpHP:
                    listHP.extend(list(hp.get_all_neighbours(sideHP, h, nest=nestedHP )))
                listHP=list(set(listHP))
        return listHP
       
        
    def get_close_angular_sepn(self,target_obs , shortlist_prev_obs):
        '''
        Select any observations that are within arcsecRadius of the target observation
        See original cnd.py for more details
        '''
        dotProducts         = np.clip([
                                hp.ang2vec(np.radians(90 - target_obs.Dec), np.radians(target_obs.RA)).dot(uv) for uv in \
                                        [ hp.ang2vec(np.radians(90 - o.Dec), np.radians(o.RA)) for o in shortlist_prev_obs ] ], -1,1)
        
        angles              = np.degrees(np.arccos(dotProducts))*3600.
        
        allowed_radii_for_shortlist = [ np.max( [self.get_arcsecRadius(_) ,self.get_arcsecRadius(target_obs)]) for _ in shortlist_prev_obs ]
        return [ obs for i,obs in enumerate(shortlist_prev_obs) if angles[i] < allowed_radii_for_shortlist[i] ]
        
    def get_close_in_time(self,target_obs , shortlist_prev_obs ):
        '''
        Select any observations that are taken within timeDeltaSeconds of the target observation
        See original cnd.py for more details
        ***         OBVIOUSLY THIS SHOULD BE A TRIVIAL SQL QUERY                        ***
        *** (PRESUMABLY COMBINED WITH get_similar_observations_based_on_healpix ABOVE ) ***
        '''
        # The allowed time-range is the time of the observation +/- the time-delta (in days)
        deltaMins = self.get_timeDeltaSeconds(target_obs) / (60.)

        # Now search the shortlist
        return [obs for obs in shortlist_prev_obs if np.abs( obs.ObsTime - target_obs.ObsTime) <= timedelta(minutes=deltaMins) ]

    def get_close_observatory_location(self,target_obs , shortlist_prev_obs ):
        '''
        Select any observations that are taken from co-located ObsCodes
        ***         OBVIOUSLY THIS SHOULD BE A TRIVIAL SQL QUERY                        ***
        *** (PRESUMABLY COMBINED WITH get_similar_observations_based_on_healpix ABOVE ) ***
        '''
        return [obs for obs in shortlist_prev_obs if obs.ObsCode in self.get_ObsCodeList(target_obs) ]

    # This dictionary would become a table of values
    # in the main database
    arcsecRadius_DICT = {
    'C51' : 10.0,
    'C57' : 20.0,
    }
    def get_arcsecRadius(self,obs, arcsecRadius=5.0):
        ''' return allowed search-radius [arc-sec] : note that arcsecRadius_DICT is NOT complete'''
        return arcsecRadius if obs.ObsCode not in self.arcsecRadius_DICT else self.arcsecRadius_DICT[obs.ObsCode]
        
    # This dictionary would become a table of values
    # in the main database
    timeDeltaSeconds_DICT = {
    '704' : 8
    }
    def get_timeDeltaSeconds(self,obs, timeDeltaSeconds=30.0):
        ''' return allowed search-radius [time]: note that timeDeltaSeconds_DICT is NOT complete'''
        return timeDeltaSeconds if obs.ObsCode not in self.timeDeltaSeconds_DICT else self.timeDeltaSeconds_DICT[obs.ObsCode]

    # This dictionary would become a table of values
    # in the main database
    obsCode_DICT = {
        '568' : ['568','T09','T10','T12','T14'],
        'T09' : ['568','T09'],
        'T10' : ['568','T10'],
        'T12' : ['568','T12'],
        'T14' : ['568','T14'],
    }
    def get_ObsCodeList(self, obs):
        ''' return allowed equivalent obs-codes : note that obsCode_DICT is NOT complete'''
        return [obs.ObsCode] if obs.ObsCode not in self.obsCode_DICT else self.obsCode_DICT[obs.ObsCode]




