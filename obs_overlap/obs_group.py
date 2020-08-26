'''
MJP 2020_08_14

The class(es) in "obs_group" focus on the functions needed to
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


class ObsGroup():
    '''
    Operates on a group of "similar observations" (e.g. near-duplicate observations)
    Establishes the "credit" & "primary" observation for the group
    Categorizes the "overlap" nature of the group.
    '''
    def __init__(self, new_obs, db):
    
        # Work out the similarity group for the new observation
        # - The functionality is in "Obs" class. Not sure that makes sense ...
        self.observations = {obs.ObsID:obs for obs in new_obs.find_similar( new_obs ,self.get_all_known_obs(db) ) }
    
        # Assign SimilarityGroupID
        self.SimilarityGroupID = self.get_SimilarityGroupID( )
        
        # Take care to assign the SimilarityGroupID to all of the obs in self.observations
        for _ in self.observations.values():
            db.BATCHES[_.BatchID].tracklets[_.TrackletID].observations[_.ObsID].SimilarityGroupID = self.SimilarityGroupID
        
        # Work out the credit & primary observation for the similarity group
        # - This sets self.credit_ObsID & self.primary_ObsID
        self.credit_ObsID, self.primary_ObsID = None, None
        self.assign_status(db)
        
        # categorize the similarity group wrt the new observation
        # - This sets ... self.category, self.desig, self.TrackletIDs
        self.category, self.desig, self.TrackletIDs = None, None, None
        self.categorize_similarity_group_wrt_new_observation( db, new_obs )
        
        # Save self in database
        db.OBSGROUPS[self.SimilarityGroupID]=self

                    
    def get_all_known_obs(self,db):
        # We will need all observations known to this point
        # Obviously my data structures could be nicer ...
        known_obs = []
        for bID, bb in db.BATCHES.items():
            for tID, tt in bb.tracklets.items():
                known_obs.extend( list(tt.observations.values() ) )
        return known_obs
        
    # -------------------------------------------------------------
    # Set the ObsGroupID for the set of input observations
    # -------------------------------------------------------------
    def get_SimilarityGroupID(self, ):
        '''
        If SimilarityGroupID previously assigned, use minimum
        Otherwise, generate a new one
        '''
        extant_SimilarityGroupIDs = self.check_extant_SimilarityGroupIDs( )
        return SimilarityGroupID.get_next_from_db() if extant_SimilarityGroupIDs is None else np.min(extant_SimilarityGroupIDs)
        
    def check_extant_SimilarityGroupIDs(self,):
        ''' if we have a group, we want to assign the lowest extant SimilarityGroupID to all associated obs'''
        extant_SimilarityGroupIDs = [obs.SimilarityGroupID for obs in self.observations.values() if obs.SimilarityGroupID is not None]
        return None if extant_SimilarityGroupIDs == [] else extant_SimilarityGroupIDs

    # -------------------------------------------------------------
    # Work with pre-defined similarity groups
    # -------------------------------------------------------------


    def categorize_similarity_group_wrt_new_observation(self, db, new_obs ):
        '''
        
        A new observation ...
         - May overlap with a single DESIGNATION from multiple previous submissions
         - May overlap with multiple ITF
         - May overlap with multiple UNSELECTABLE
         - May *NOT* overlap with both DESIGNATION and ITF
         - May overlap with both DESIGNATION and UNSELECTABLE
         - May overlap with both ITF and UNSELECTABLE
        
        if:   self.primary_ObsID==None  : => The entire group is not selectable
        else:
            if only a SINGLE obs        : => The group gets SINGLE status
            else:
                if any DESIGNATION      : => The group gets DESIGNATION status [ & a designation is set ]
                else:
                    if any ITF          : => The group gets ITF status [ & TrackletIDs are listed ]
                    else
                                        : => Some kind of mistake ?
        
        sets:
        --------
        self.category : integer in [-1,0,1,2]
         -1 => UNSELECTABLE group
          0 => SINGLE (*NO* overlap)
         +1 => overlaps with observations of *DESIGNATED* object
         +2 => overlaps with observations of *ITF* tracklet
         
        '''
        
        if self.primary_ObsID is None :
            self.category = -1 ### UNSELECTABLE
        else:

            # Similarity group (excluding self)
            similar_obs = [so for so in self.observations.values() if so.ObsID != new_obs.ObsID ]

            # No overlap with any other objects : we hope that this is the most common case
            if len( similar_obs ) == 0 :
                self.category = 0 ### SINGLE
                
            # Some overlap with previously known observations
            else :
            
                # Does the observation overlap with anything that is DESIGNATED ?
                overlapped_designations = list(set([so.desig for so in similar_obs if so.ObsID in db.DESIGNATED ]))
                n_designated = len(overlapped_designations)
                assert n_designated <= 1, f'db.DESIGNATED is corrupt (> 1 desig overlapped): {overlapped_designations}'
                
                if n_designated:
                    self.category   = 1 ### DESIGNATED
                    self.desig      = overlapped_designations[0]

                # Does the observation overlap with anything in the ITF ?
                self.TrackletIDs = list(set([so.TrackletID for so in similar_obs if so.ObsID in db.ITF ]))
                n_itf = len(self.TrackletIDs)
                if n_itf:

                    # Check for overlap both DESIGNATED & ITF
                    # [[ SHOULD NOT BE POSSIBLE : WANT TO DEFEND AGAINST IT IN SUBSEQUENT PROCESSING STEPS ]]
                    assert not n_designated, f'n_designated={n_designated}, n_itf={n_itf}, which should be impossible '
                    
                    # If we got here, then all is fine, assign ITF overlap status
                    self.category = 2 ### ITF
                
                # Check that either n_designated or n_itf has been assigned within this loop
                assert n_designated or n_itf, 'neither n_itf not n_designated'
    
        assert self.category in [-1,0,1,2], f'self.category NOT in [-1,0,1,2]: {self.category}'
        return True

    # -------------------------------------------------------------
    # Assign "credit" and "selected" status
    # -------------------------------------------------------------

    def assign_status( self, db ):
        # Assign selected status
        '''
        For now I assign status in the following complicated manner
        https://docs.google.com/document/d/1hLUi-E4SOTWOLUEIUpcHVHJVSV4eIGUz5Uyb0OdQ8ok/edit?usp=sharing

        CREDIT OBSERVATION
        == Earliest
        
        PRIMARY OBSERVATION
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
        
            (iii) Yet more complex criteria may be necessary at a later date
        
        '''
        # The discovery credit goes to ...
        credit_obs = self.assign_discovery_credit(db)
        
        # (1) There may be no usable observations
        if credit_obs is None :
            credit_ObsID, primary_ObsID = None, None
        
        else:
            credit_ObsID = credit_obs.ObsID
            
            # Get the person/group that submitted the batch
            credit_Actor = db.BATCHES[credit_obs.BatchID].ActorID
        
            # obs that have explicitly been replaced by some other obs
            replaced_obsIDs = [obs.Replaces for obs in self.observations.values() if obs.Replaces is not None ]
            # we only consider obs that are neither replaced nor deleted
            selectable_obs  = [ obs for obs in self.observations.values() if obs.ObsID not in replaced_obsIDs and obs.Deleted is not True]
         

            # (2) There may be no selectable -primary observations
            if not selectable_obs:
                primary_ObsID = None

            # (3) There may be both credit & primary observations ...
            else:

                # divide obs according to the submitting_actor
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
                                primary_Obs = self.__compare_obs(primary_Obs, obs)
                                
                primary_ObsID=primary_Obs.ObsID

        # Set as properties of the object
        self.credit_ObsID = credit_ObsID
        self.primary_ObsID= primary_ObsID
        
        return True


    # -------------------------------------------------------------
    # Internal methods
    # -------------------------------------------------------------

    def __compare_obs( self, selected_Obs, obs):
        '''
        We want / need some ability to compare observations
        
        Perhaps we could use an approach similar to orbfit:
         - use the observation with the lowest "weighted" uncertainty
         
        # -------------------------------------------------------------
        # *** MICHAEL : MATT P. NEEDS TO FURTHER DEVELOP THIS LOGIC ***
        #
        # If there existed a "weighted_uncertainty" quantity ...
        # return selected_Obs if selected_Obs.weighted_uncertainty <= obs.weighted_uncertainty else obs
        # -------------------------------------------------------------
         
        For the sake of this demo, I will randomly select one of
        the observations
        '''
        return selected_Obs if np.random.random() > 0.5 else obs



    def assign_discovery_credit(self, db):
        '''
        For now I assign discovery credit to the earliest submissionDate
        More complex criteria may be necessary at a later date
        '''
                
        # Get the submission-date of the batch that contains the observations of interest
        # (NB - don't consider *Deleted* observations)
        submissionsDates = [db.BATCHES[o.BatchID].SubmissionTime for o in self.observations.values() if o.Deleted is not True]

        # All observations are deleted. No useful data
        if len(submissionsDates) == 0 :
            credit_obs = None
        # Some usable observations exist: assign credit to earliest
        else:
            # Sort together
            submissionsDates,grouped_observations = map(list, zip(*sorted(zip(submissionsDates, list(self.observations.values()) ))))
            credit_obs = grouped_observations[0]

        return credit_obs



