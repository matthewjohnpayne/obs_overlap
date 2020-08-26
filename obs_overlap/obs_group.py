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
from collections import defaultdict, namedtuple
import numpy as np

# -------------------------------------------------------------
# Local Imports
# -------------------------------------------------------------
from db import SimilarityGroupID





# For whatever reason I have set this ObsGroup stuff up
# as a namedtuple rather than a class.
# Not sure there's any ovbvious reason at this point.
# Perhaps just my continuing uncertainty as to whether
# there needs to be an ObsGroup table or not.
ObsGroup = namedtuple('ObsGroup', ['CreditObsID','PrimaryObsID'])



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
# Work with pre-defined similarity groups
# -------------------------------------------------------------
def fetch_similarity_group(db, SimilarityGroupID):
    '''
    select all observations with the same group ID
     - obviously just a simple db operation
    '''
    known_obs = []
    for bID, bb in db.BATCHES.items():
        for tID, tt in bb.tracklets.items():
            known_obs.extend( list(tt.observations.values() ) )
    return [ko for ko in known_obs if ko.SimilarityGroupID==SimilarityGroupID]

def categorize_similarity_group_for_observation(db,obs):
    '''
    
    returns:
    --------
    overlap : integer
     - integer in [0,1,2]
     - 0 => *NO* overlap,
     - 1 => overlaps with observations of *DESIGNATED* object
     - 2 => overlaps with observations of *ITF* tracklet
    '''
    overlapped_designations = []
    overlapped_itf_tracklet_ids = []
    
    # Similarity group (excluding self)
    similar_obs = [so for so in fetch_similarity_group(db,obs.SimilarityGroupID) if so.ObsID != obs.ObsID ]

    # No overlap with any other objects : we hope that this is the most common case
    if len( similar_obs ) == 0 :
        overlap = 0
    # Some overlap with previously known observations
    else :
        # Does the observation overlap with anything that is DESIGNATED ?
        overlapped_designations = list(set([so.desig for so in similar_obs if so.ObsID in db.DESIGNATED ]))
        n_designated = len(overlapped_designations)
        assert n_designated <= 1, f'db.DESIGNATED is corrupt (> 1 desig overlapped): {overlapped_designations}'

        # Does the observation overlap with anything in the ITF ?
        overlapped_itf_tracklet_ids = list(set([so.TrackletID for so in similar_obs if so.ObsID in db.ITF ]))
        n_itf = len(overlapped_itf_tracklet_ids)

        # Does the observation overlap with anything that is unselectable ?
        # Why do this check?
        # Does the information ever get used ?
        #overlapped_UNSELECTABLE_tracklet_ids = list(set([so.TrackletID for so in similar_obs if so.ObsID in db.UNSELECTABLE ]))
        
        # Does the observation overlap both DESIGNATED & ITF ? [[ SHOULD NOT BE POSSIBLE : WANT TO DEFEND AGAINST IT IN SUBSEQUENT PROCESSING STEPS ]]
        n_both = len( [so for so in similar_obs if so.ObsID  in db.DESIGNATED and so.ObsID in db.ITF] )
        assert not n_both, f'n_both = {n_both} which should be impossible'

        # Categorization: 1=>Overlap with designated, 2=>Overlap with ITS tracklet(s)
        # NB I'm using 0 instead of 3 for if the overlap is only with an unslectable observation.
        # -- This may need to change
        overlap = 1 if n_designated else 2 if n_itf else 0
        
    assert overlap in [0,1,2]
    
    return overlap, None if not overlapped_designations else overlapped_designations[0], overlapped_itf_tracklet_ids

# -------------------------------------------------------------
# Assign "credit" and "selected" status
# -------------------------------------------------------------

def assign_status( grouped_observations, db ):
    # Assign selected status
    '''
    For now I assign selected status in the following complicated manner
    https://docs.google.com/document/d/1hLUi-E4SOTWOLUEIUpcHVHJVSV4eIGUz5Uyb0OdQ8ok/edit?usp=sharing

    CREDIT
    == Earliest
    
    PRIMARY
    Do not select observations as primary that have been explicitly replaced/remeasured by other observations.
    Do not select observations as primary that have been labelled as "deleted", or some similar term.
    Iterate through remaining selectable observations:
        (i) Start with any selectable observations with the same submitting "actor" as CREDIT observation :
        Irrespective of exact -vs- near-duplicate: take latest as selected.
        I.e. if the SAME person has re-submitted, then even if it is not marked as an explicit remeasure, treat it as taking priority over the earlier submission by the same person.
        This allows us to gracefully deal with situations like C51 resubmissions-and-extension.
        
        (ii) For any other "implicit remeasures" from "actors" other than the CREDIT actor
        only assign priority IF the implicit remeasure meets explicit CRITERIA defining significant superiority over the observation selected in (i).
        Criteria might include …
                The later submission uses a superior stellar catalog (e.g. GAIA-2)
                The later submission is from a preferred/expert person/source
                Some kind of manual MPC override
    
    (NB) Yet more complex criteria may be necessary at a later date
    
    '''
    # The discovery credit goes to ...
    credit_obs   = assign_discovery_credit(grouped_observations , db)
    
    # (1) There may be no usable observations
    if credit_obs is None :
        credit_ObsID, primary_ObsID = None, None
    
    else:
        credit_ObsID = credit_obs.ObsID
        credit_Actor = db.BATCHES[credit_obs.BatchID].ActorID
    
        # obs that thave explicitly been replaced by some other obs
        replaced_obsIDs = [obs.Replaces for obs in grouped_observations if obs.Replaces is not None ]
        # obs that are neither replaced nor deleted
        selectable_obs  = [ obs for obs in grouped_observations if obs.ObsID not in replaced_obsIDs and obs.Deleted is not True]
     

        # (2) There may be no selectable -primary observations
        if not selectable_obs:
            primary_ObsID = None
            
            

        # (3) There may be both credit & primary observations ...
        else:

            # divide obs by submitting_actor
            obs_by_actor = defaultdict(list)
            for obs in selectable_obs :
                obs_by_actor[ db.BATCHES[obs.BatchID].ActorID ].append(obs)            

            # Here we attempt to select the LATEST from the original submitter
            primary_Obs = None
            for actor, obs_list in obs_by_actor.items():
                if actor ==  credit_Actor:
                    submissionsDates = np.asarray( [ db.BATCHES[obs.BatchID].SubmissionTime for obs in obs_list ] )
                    # Sort together
                    submissionsDates,sorted_obs_list = map(list, zip(*sorted(zip(submissionsDates,obs_list))))
                    primary_Obs      = sorted_obs_list[-1] # LATEST
                    
            # Here we check whether there are any other obs which are BETTER than the default
            for actor, obs_list in obs_by_actor.items():
                if actor !=  credit_Actor:
                    for obs in obs_list:
                        if primary_Obs is None :
                            primary_Obs = obs
                        else:
                            primary_Obs = __compare_obs(primary_Obs, obs)
                            
            primary_ObsID=primary_Obs.ObsID

    return credit_ObsID, primary_ObsID


# -------------------------------------------------------------
# Internal methods
# -------------------------------------------------------------

def __compare_obs( selected_Obs, obs):
    '''
    We want / need some ability to compare observations
    
    Perhaps we could use an approach similar to orbfit:
     - use the observation with the lowest "weighted" uncertainty
     
    For the sake of this demo, I will randomly select one of
    the observations
    '''
    return selected_Obs if np.random.random() > 0.5 else obs 



def assign_discovery_credit( grouped_observations , db):
    '''
    For now I assign discovery credit to the earliest submissionDate
    More complex criteria may be necessary at a later date
    '''
            
    # Get the submission-date of the batch that contains the observations of interest
    # (NB - don't consider *Deleted* observations)
    submissionsDates = [db.BATCHES[o.BatchID].SubmissionTime for o in grouped_observations if o.Deleted is not True]

    # All observations are deleted. No useful data
    if len(submissionsDates) == 0 :
        credit_obs = None
    # Some usable observations exist: assign credit to earliest
    else:
        # Sort together
        submissionsDates,grouped_observations = map(list, zip(*sorted(zip(submissionsDates,grouped_observations))))
        credit_obs = grouped_observations[0]

    return credit_obs



