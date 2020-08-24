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
import numpy as np

# -------------------------------------------------------------
# Local Imports
# -------------------------------------------------------------
from db import TrackletID
import processing


# -------------------------------------------------------------
# Tracklett Class <==> Accepted Observations Table
# -------------------------------------------------------------
class Tracklet():
    '''
    Real tracklets will probably need more attributes than this
    This is just the subset I needed to get my code working
    '''
    def __init__(self, observations, db):
    
        # Generate a unique ID (as if from db)
        self.TrackletID = TrackletID.get_next_from_db()
        
        # Allow the parent batchID to be stored in tracklet
        #(this will be set by the parent)
        self.BatchID = None
    
        # Store contained observations in a dictionary structure
        self.observations = { o.ObsID : o for o in observations}
        
        # Tell the contained observations what their parent TrackletID is
        for ObsID in self.observations:
            self.observations[ObsID].TrackletID = self.TrackletID

        # Store self in db
        #db.TRACKLETS[self.TrackletID] = self
        
    # -------------------------------------------------------------
    # Functions to understand overlap between new tracklet &
    # previously submitted tracklets
    # -------------------------------------------------------------

    def tracklet_processing_blackbox(self,  param_dict , db):
        '''
        For *new* tracklets, I imagine a lengthy process that
        (i) checks whether this is any known designated object
         - this may involve a number of steps, including performing orbit fits
        (ii) checks whether this can be joined with any ITF tracklets
        (iii) ...
        
        For tracklets that we are back-filling from the obs-table / flat-files, ...
        I think that we will have to grandfather them in (perhaps only performing
        a subset of the checks?) and only flag-up a subset of egregious errors
        
        For the sake of development, I am just going to put in some dummy functions
        that just return some default PASS/FAIL value
         - the names of the functions (and the header) should give some indication
           of what it will neede to do
        
        '''
        # (0) May need to do things differently depending on whether we are back-filling
        # from previously-published stuff in the database
        if 'MODE' in param_dict and param_dict['MODE'] == 'BACKFILL':
            print('BACKFILL Mode: Lengthy checks will be SUPPRESSED')
        else:
            print('Standard Processing Mode for New Observations')
            
        # (1) Categorize the overlap between the constituent observations and
        #     previously known observations
        self.categorize_overlap(db)
        print(f'self.overlap_category={self.overlap_category}')
        
        # (2) May need to do further logical checks
        #     E.g. What if supplied desig differs from overlap ?
        #     E.g. For DESIGNATED, have any of the new observations been selected ?
        #     E.g. What if the different observations in the tracklet overlap different designated objects ?
        #     E.g. ...
        
        # (3) Sketch-out the logical flow of checks/orbit fits that
        #     will need to be done for the various cases
        #     Some initial ideas behind this can be found in ...
        #     https://drive.google.com/file/d/1QqseCpV7PedW341iKPiv447uVElefs93/view?usp=sharing
        
        if self.overlap_category == 'SINGLES' :
            processing.comprehensive_check_and_orbitfit(self)
            
        elif self.overlap_category == 'DESIGNATED' :
            if any_of_the_new_ones_are_primary :
                processing.comprehensive_check_and_orbitfit(self)
            else:
                self.assign_to_DESIGNATED(db, '???')
        
        elif self.overlap_category in ['DESIGNATED+SINGLE', 'DESIGNATED+ITF','SINGLE+ITF']:
            processing.comprehensive_check_and_orbitfit(self)

        elif self.overlap_category == 'ITF' :
            self.assign_to_ITF(db)

        else:
            sys.exit(f'HOW DID WE GET HERE? : Unexpected overlap_category : {overlap_category}')
        
        self.terminate_processing(db)

    def assign_to_DESIGNATED(self,db,designation):
        '''
        Tracklet is being assigned to DESIGNATED
        Assumes that previous checks have been done & that
        the tracklet really belongs in DESIGNATED
        
        NB: Probably need to do something else
         - e.g. set "desig" flag on consistituent observations
        
        '''
        for ObsID,obs  in self.observations.items():
            db.DESIGNATED[ObsID] = True
            self.observations[ObsID].desig = designation
            
    def assign_to_DELETED(self,db):
        '''
        Perhaps we need a deleted table / status : TBD
        '''
        for ObsID,obs  in self.observations.items():
            db.DELETED[ObsID] = True
            
    def assign_to_ITF(self,db):
        '''
        Tracklet is being assigned to the ITF
        Assumes that previous checks have been done & that either ...
        (i) the tracklet is just a subset of other ITF tracklet
        (ii) nothing could be done to match the tracklet to anything else
        (iii) ...
        '''
        for ObsID,obs  in self.observations.items():
            db.ITF[ObsID] = True
            
    def terminate_processing(self, db):
        '''
        In real life, some further steps may be required to properly
        populate the db & make other logical checks / calculations
        
        And we might want to change some king of processing flag in the
        ACCEPTED table to show that processing is complete?
        
        For this developmental sketch, perhaps nothing much is needed
        '''
        for ObsID,obs  in self.observations.items():
        
            # Here I am checking that each observation gets put into one and only one destination "table"
            # - I.e. it has to be assigned to DESIGNATED, ITF or DELETED
            #in_destinations = [ObsID in db.ITF[ObsID], ObsID in db.DELETED[ObsID], ObsID in db.DESIGNATED[ObsID] ]
            #assert len( [ _ for _ in in_destinations if _ ]) == 1 , f'Incorrect number of destination counts : {in_destinations} '
            
            # Here I am adding a flag to signify processing is complete
            self.observations[ObsID].PROCESSING_COMPLETE = True
            
            # This does not belong here
            # I am just putting it here toforce everything into the ITF
            # This is just temporary
            # Trying to get the overall code-flow working
            db.ITF[ObsID] = True
            
    def categorize_overlap(self, db ):
        '''
        Categorization of overlap for entire tracklet
        This compares the overlap for each of the observations with their respective "similarilty-groups"
        '''
        

        # We will need all observations known to this point
        # ***   Obviously my data structures could be nicer ...    ***
        # ***   THIS WOULD BE  BETTER DONE AS AN SQL QUERY !!!  ***
        #
        known_obs = []
        for bID, bb in db.BATCHES.items():
            for tID, tt in bb.tracklets.items():
                known_obs.extend( list(tt.observations.values() ) )
        
        # Count the number of ObsGroupID members for each new_tracklet_observation
        # NB: At this point, the known_obs *DOES* contain tracklet_observations
        #
        # If there is some overlap, then we probably need to work out what it overlaps with
        # I think this needs to be a comparison against a "DESIGNATED" table and an "ITF" table
        overlaps = []
        for o in self.observations.values():
        
            # Similarity group (excluding self)
            similar_obs = [ko for ko in known_obs if ko.SimilarityGroupID==o.SimilarityGroupID and ko.ObsID != o.ObsID ]
                        
            # No overlap with any other objects : we hope that this is the most common case
            if len( similar_obs ) == 0 :
                overlap = 0
            # Some overlap with previously known observations
            else :
                print('else')
                # Does the observation overlap with anything that is DESIGNATED ?
                n_designated = len( [so for so in similar_obs if so.ObsID in db.DESIGNATED ] )
                
                # Does the observation overlap with anything in the ITF ?
                n_itf = len( [so for so in similar_obs if so.ObsID in db.ITF ] )

                # Does the observation overlap with NEITHER ? [[ HOW IS THIS POSSIBLE ??? ]]
                n_neither = len( [so for so in similar_obs if so.ObsID not in db.DESIGNATED and so.ObsID not in db.ITF] )
                assert not n_neither, f'n_neither = {n_neither} which should be impossible: o.ObsID={o.ObsID}, []={[so.ObsID for so in similar_obs if so.ObsID not in db.DESIGNATED and so.ObsID not in db.ITF]}'

                # Does the observation overlap with BOTH ? [[ HOW IS THIS POSSIBLE ??? : WANT TO DEVEND AGAINST IT IN SUBSEQUENT PROCESSING STEPS ]]
                n_both = len( [so for so in similar_obs if so.ObsID  in db.DESIGNATED and so.ObsID in db.ITF] )
                assert not n_both, f'n_both = {n_both} which should be impossible'

                overlap = 1 if n_designated else 2
                
            assert overlap in [0,1,2]
            overlaps.append(overlap)
            
        # Categorization of overlap for entire tracklet
        # I find this complicated to think about, so I'm going to try and be very clear in the layout of my logic
        # (A) Completely disjoint/all-singles: no overlap with known observations
        if     set(overlaps) == {0} :
            overlap_category = 'SINGLES'
        # (B) All observations overlap only with designated objects
        elif   set(overlaps) == {1} :
            overlap_category = 'DESIGNATED'
        # (C) Some observations overlap with designated objects AND the rest are SINGLE
        elif   set(overlaps) == {0,1} :
            overlap_category = 'DESIGNATED+SINGLE'
        # (D) Some observations overlap with designated objects AND some overlap with ITF tracklets
        #     Not bothered about whether any are single are not.
        elif   set(overlaps) == {0,1,2} or  set(overlaps) == {1,2}  :
            overlap_category = 'DESIGNATED+ITF'
        # (E) Some observations overlap with ITF tracklets AND some are SINGLE
        elif   set(overlaps) == {0,2} :
            overlap_category = 'SINGLE+ITF'
        # (F) All observations overlap only with ITF tracklets
        elif   set(overlaps) == {2} :
            overlap_category = 'ITF'
        else:
            overlap_category = 'UNKNOWN'
        assert overlap_category != 'UNKNOWN' , f'overlap_category = {overlap_category}'
        
        self.overlap_category = overlap_category
        return self.overlap_category


