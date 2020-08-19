'''
MJP 2020_08_14

The classes in "obs_group" focus on the functions needed to
operate on an ObsGroup to decide which of the constituent
observations will be assigned "credit" and "selected" status.

'''
# -------------------------------------------------------------
# Third Party Imports
# -------------------------------------------------------------
import sys, os
from collections import defaultdict
import numpy as np

# -------------------------------------------------------------
# Local Imports
# -------------------------------------------------------------
from db import SimilarityGroupID

# -------------------------------------------------------------
# Apply labels to a group of similar observations
# -------------------------------------------------------------



# -------------------------------------------------------------
# Set the ObsGroupID for the set of input observations
# -------------------------------------------------------------
def get_SimilarityGroupID(  grouped_observations ):
    '''
    If SimilarityGroupID previously assigned, use minimum
    Otherwise, generate a new one
    '''
    extant_SimilarityGroupIDs = check_extant_SimilarityGroupIDs( grouped_observations)
    return SimilarityGroupID.get_next_from_db() if extant_SimilarityGroupIDs is None else np.min(extant_SimilarityGroupIDs)
    
def check_extant_SimilarityGroupIDs( grouped_observations):
    ''' if we have a group, we want to assign the lowest extant SimilarityGroupID to all associated obs'''
    #for _ in grouped_observations:
    #    print(_.__dict__)
    extant_SimilarityGroupIDs = [obs.SimilarityGroupID for obs in grouped_observations if obs.SimilarityGroupID is not None]
    return None if extant_SimilarityGroupIDs == [] else extant_SimilarityGroupIDs
        
# -------------------------------------------------------------
# Assign "credit" and "selected" status
# -------------------------------------------------------------

def assign_status( grouped_observations, batches ):
    # Assign selected status
    '''
    For now I assign selected status in the following complicated manner
    https://docs.google.com/document/d/1hLUi-E4SOTWOLUEIUpcHVHJVSV4eIGUz5Uyb0OdQ8ok/edit?usp=sharing

    Do not select observations that have been explicitly replaced/remeasured by other observations.
    Do not select observations that have been labelled as "deleted", or some similar term.
    If exact duplicate (including submitting org/person/program ) : take latest as selected.
    If near-duplicates:
        Assume that "implicit remeasures" take priority. I.e. if the SAME person has re-submitted a near- (but not exact-) dup, then even if it is not marked as an explicit remeasure, treat it as taking priority over the earlier submission by the same person.
        If from a different person, then DEFAULT to taking the earlier observation (i.e. from the original discoverer) UNLESS the later observation meets explicit CRITERIA defining significant superiority. Criteria might include …
                The later submission uses a superior stellar catalog (e.g. GAIA-2)
                The later submission is from a preferred/expert person/source
                Some kind of manual MPC override
    
    Yet more complex criteria may be necessary at a later date
    '''
    # The discovery credit goes to ...
    credit_obsID = assign_discovery_credit(grouped_observations , batches)
    
    # obs that thave explicitly been replaced by some other obs
    replaced_obsIDs = [obs.Replaces for obs in grouped_observations if obs.Replaces is not None ]
    # obs that are neither replaced nor deleted
    selectable_obs  = [ obs for obs in grouped_observations if obs.ObsID not in replaced_obsIDs and obs.Deleted is not True]
 
    if not selectable_obs:
        pass
    else:
        # divide obs by submitting_actor
        obs_by_actor = defaultdict(list)
        for obs in selectable_obs :
            obs_by_actor( batches[obs.trkID].ActorID ).extend(obs)
        
        # if credit_obsID not selectable ... WHAT SHOULD WE DO ???
        if credit_obsID not in [ obs.ObsId for obs in selectable_obs ]:
            pass
        else:
            # Here we set the DEFAULT selected_ObsID
            # - This is the LATEST from the original submitter
            for actor, obs_list in obs_by_actor.items():
                if credit_obsID in [ obs.ObsId for obs in obs_list ]:
                    submissionsDates = np.asarray( [ batches[_.trkID].submissionDate for _ in obs_list ] )
                    indicees         = np.where( submissionsDates == np.max(submissionsDates))[0]
                    selected_Obs     = np.asarray(obs_list)[indicees][0]
                    
            # Here we check whether there are any other obs which are BETTER than the default
            for actor, obs_list in obs_by_actor.items():
                if credit_obsID not in [ obs.ObsId for obs in obs_list ]:
                    for obs in obs_list:
                        selected_Obs = self.__compare_obs(selected_Obs, obs)

    return credit_obsID, selected_Obs.ObsID


# -------------------------------------------------------------
# Internal methods
# -------------------------------------------------------------

def __compare_obs( selected_Obs, obs):
    '''
    We want / need some ability to compare observations
    Perhaps we could use an approach similar to orbfit:
     - use the observation with the lowest "weighted" uncertainty
    '''
    print(' compare_obs is doing NOTHING !!!!!')
    return selected_Obs



def assign_discovery_credit( grouped_observations , batches):
    '''
    For now I assign discovery credit to the earliest submissionDate
    More complex criteria may be necessary at a later date
    '''
    submissionsDates = np.asarray( [ batches[_.trkID].submissionDate for _ in grouped_observations if _.Deleted is not True ] )
    
    # All observations are deleted. No useful data
    if len(submissionsDates) == 0 :
        credit_obsID = None
    # Some usable observations exist: assign credit to earliest
    else:
        indicees         = np.where( submissionsDates == np.min(submissionsDates))[0]
        credit_obsID = np.asarray(grouped_observations)[indicees][0].ObsID

    return credit_obsID



