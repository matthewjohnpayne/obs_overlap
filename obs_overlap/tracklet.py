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
import numpy as np ; np.random.seed(0)
from collections import namedtuple

# -------------------------------------------------------------
# Local Imports
# -------------------------------------------------------------
from db import TrackletID
import obs_group
import processing


# -------------------------------------------------------------
# Some named tuples used within Tracklet class
# -------------------------------------------------------------

# For labelling overlap from all obs in tracklet: see *categorize_overlap()*
overlap_category = namedtuple('overlap_category', ['SINGLE','DESIGNATED','ITF'])
# For labelling any designations overlapped by obs in tracklet: see *categorize_overlap()*
overlap_desig    = namedtuple('overlap_desig',    ['MULTIPLE','DESIGLIST'])
# Primarily for carrying desig suggested by submitter, but could come from (e.g.) checkID
suggested_desig  = namedtuple('suggested_desig',  ['VALID','DESIG'])
# For carrying any ITF tracklets overlapped by obs in tracklet
overlap_itf      = namedtuple('overlap_itf',      ['MULTIPLE','TrackletIDList'])
# For carrying ITF suggested by (e.g.) pyTrax
suggested_itf    = namedtuple('suggested_itf',    ['MULTIPLE','TrackletIDList'])

# -------------------------------------------------------------
# Tracklet Class <==> Accepted Observations Table
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

        # Storage related to overlapping tracklets, suggested designations, etc
        self.overlap_category   = None
        self.overlap_desig      = None
        self.suggested_desig    = None
        self.overlap_itf        = None
        self.suggested_itf      = None

        # Store self in db
        db.TRACKLETS[self.TrackletID] = self
    
    def do_name_comprehension(self,):
        '''
        Get the desig out of the contained observations
        
        In reality, some significant string-comprehension would likely be required
        
        For this developmental / psuedo-code, I will just look for "K20" at the start
        of the supplied designation
        
        '''
        desigs = list(set([o.desig for o in self.observations.values()]))
        assert len(desigs) == 1
        desig = desigs[0]
        self.suggested_desig = suggested_desig( True if desig is not None and desig[:3] == 'K20' else False, desig )
        return self.suggested_desig
        
    def consistent_designations(self,):
        '''
        Are the designations in overlap_desig & suggested_desig consistent ?
        '''
        return True if not self.overlap_desig.MULTIPLE and self.overlap_desig.DESIGLIST[0] == self.suggested_desig.DESIG else False
                 

    def primary_selected_observations_changed():
        '''
        I think I want a function that will say whether the
        addition of the new observations (in this tracklet)
        changed the selection of *any* of the primary observations

        '''
        return True if np.any([obs.ObsID == db.GROUPS[obs.SimilarityGroupID].PrimaryObsID for obs in self.observations.values()]) else False
        
        
    # -------------------------------------------------------------
    # Functions to understand overlap between new tracklet &
    # previously submitted tracklets
    # -------------------------------------------------------------

    def tracklet_processing_A____Top_level_process_handler(self,  param_dict , db):
        '''
        Populate tracklet-variables with hints as to the potential designated
        objects and/or tracklets that might be joined with this new tracklet
        
        Does this using
        (i) Similarity Groups
        (ii) Suggested designations (e.g. from the submitter)
        
        Then runs the logic to decide how to fit/process tracklet
        '''
        
        # (1) Categorize the overlap between the constituent observations and
        #     previously known observations
        # N.B. This sets ...
        # self.overlap_category,
        # self.overlap_desig,
        # self.overlap_itfvariable
        self.categorize_overlap(db)
        
        # (2) Do some form of name comprehension similar to "processobs"
        # N.B. Irrespective of overlap category ...
        #      ['SINGLE' , or even 'ITF' ]
        #      the tracklet may still come with a submitter-supplied designation
        # N.B. This populates
        #       self.suggested_desig
        self.do_name_comprehension()
        
        # (3) Sketch-out the logical flow of checks/orbit fits that
        #     will need to be done for the various cases
        #     Some initial ideas behind this can be found in ...
        #     https://drive.google.com/file/d/1QqseCpV7PedW341iKPiv447uVElefs93/view?usp=sharing
        #
        return self.tracklet_processing_B____Decide_if_and_how_to_fit(db)
        
        
    def tracklet_processing_B____Decide_if_and_how_to_fit(self,db):
        '''
        Torturous logic to decide on what should be done w.r.t.
        orbit-fitting, etc, to allow us to decide what object (if any)
        the new tracklet should be associated with.
        
        For tracklets that we are back-filling from the obs-table / flat-files, ...
        I think that we will have to grandfather them in (perhaps only performing
        a subset of the checks?) and only flag-up a subset of egregious errors
        
        For the sake of development, I am just going to put in some dummy functions
        that just return some kind of default PASS/FAIL value
         - the names of the functions (and the header) should give some indication
           of what each is intended to do
        
        This function assumes that the function *tracklet_processing_A____* has already
        been called and thus several critical variables populated.
        
        '''

        # Allow the possibility of doing things differently depending on whether or not
        # we are back-filling from previously-published stuff in the database
        """
        if 'MODE' in param_dict and param_dict['MODE'] == 'BACKFILL':
            pass#print('BACKFILL Mode: Lengthy checks will be SUPPRESSED')
        else:
            pass#print('Standard Processing Mode for New Observations')
        """

        # If tracklet is not selectable, assign as such and quit.
        if not self.SELECTABLE:
            self.assign_to_UNSELECTABLE(db)
            self.terminate_processing(db)
            result_dict = {'FINISHED':True }
            return result_dict

        # If any from D / DI / DS
        elif self.overlap_category.DESIGNATED :

            # If it does NOT overlap multiple designated objects
            if not self.overlap_desig.MULTIPLE:

                # If there was no user-supplied designation,
                # we can just go ahead and fit using the observations implied by DESIGNATED
                if not self.suggested_desig.VALID :
                    result_dict = {'FINISHED':False } ### Do orbit fit
                else:
                    # Check whether the user-supplied designation is consistent with the
                    # overlapped designation
                    if self.consistent_designations():

                        # If only DESIGNATED (D) (i.e. we've seen everything before),
                        if not self.overlap_category.ITF and not self.overlap_category.SINGLE:
                        
                            # Only bother with refitting if some of the new observations
                            # have become the primary
                            if self.primary_selected_observations_changed():
                                result_dict = {'FINISHED':False } ### Do orbit fit
                            else:
                                self.assign_to_DESIGNATED(db,designation_dict)
                                result_dict = {'FINISHED':True }

                        # If here, then DI or DS => Something new to try with the known designated object
                        else:
                            result_dict = {'FINISHED':False } ### Do orbit fit

                    # If the user-supplied & overlapped designations are INCONSISTENT
                    # => Probably set suggested desig to VALID=False and just
                    #    search as-if no designation was supplied
                    #    (just use the overlapped designation)
                    #
                    # NB
                    # *** *** ***      recursive function call     *** *** ***
                    #
                    else:
                        self.suggested_desig = suggested_desig(False, self.suggested_desig[1])
                        return self.tracklet_processing_B____Decide_if_and_how_to_fit(db)

            # If it overlaps multiple designated objects ,
            # I think we might want to label this tracklet as wrong
            # (but perhaps try "linking"?)
            else:
                link_dict = processing.attempt_to_link_multiple_overlap()
                if link_dict['PASS']:
                    result_dict = {'FINISHED': False } ### Do orbit fit
                else:
                    self.assign_to_UNSELECTABLE(db)
                    result_dict = {'FINISHED': True  }

        # If either from S / SI
        elif self.overlap_category.SINGLE :
            # It's going to be very common to have SINGLE + suggested desig
            if self.suggested_desig.VALID :
                result_dict = {'FINISHED':False } ### Do orbit fit
                
            # It's also going to be common to have SINGLE + no-desig (the current 'mbaitf' queue)
            # Also, SINGLE+ITF+no-desig is the standard C51 "extension" approach
            else:

                # Perform speculative "checkID" & "pyTrax" type searches
                # - Assume *speculative_search()* updates tracklet attributes
                search_dict = processing.speculative_search(self, db)
                if search_dict['PASSED']:
                    result_dict = {'FINISHED':False } ### Do orbit fit
                else:
                    self.assign_to_ITF(db)
                    result_dict = {'FINISHED':True }
                        
        # Only I
        elif self.overlap_category.ITF:
            self.assign_to_ITF(db)
            self.terminate_processing(db)
            result_dict = {'FINISHED':True }
                        
        # Unknown categorization
        else:
            print(f'HOW DID WE GET HERE? : Unexpected overlap_category : {self.overlap_category}')
            result_dict = {'FINISHED':True, 'ERROR':True , 'DEBUG':'Incomplete Categorization'}
            
            
            
            
            
            
        print('\t'*4,'tracklet_processing_B____Decide_if_and_how_to_fit: after logic, before orbitfit')
        print('\t'*4,'self.__dict__=...')
        for k,v in self.__dict__.items():
            print('\t'*5, k,v)
            
            
            
            
            
        # The tortured logic above means that if result_dict['FINISHED'] == True,
        # then the run is finished, while in contrast, result_dict['FINISHED'] == False
        # means that we are not finished and that *** we need to do an orbit-fit ***
        #
        # NB
        # *** *** *** program RETURNS from here if no further work required *** *** ***
        #
        if 'FINISHED' in result_dict and result_dict['FINISHED'] :
            self.terminate_processing(db)
            return result_dict
        else:
            orbit_fit_dict = processing.comprehensive_check_and_orbitfit(self)






        # Interpret results from orbit fit and take appropriate action
        if orbit_fit_dict['PASSED']:
            
            # Promote this new tracklet to designated status
            self.assign_to_DESIGNATED(db, orbit_fit_dict['designation'])
            
            # Were other tracklets involved, either from DI / IS / ...,
            # or from Speculative Link?
            # - if so, there may be some that need to be assigned too
            for other_TrackletID in orbit_fit_dict['other_TrackletIDs']:
                t = db.TRACKLETS[other_TrackletID]
                t.assign_to_DESIGNATED(db, orbit_fit_dict['designation'])
        

        else:
            if self.overlap_category.SINGLE and not self.overlap_category.DESIGNATED :
            
                # If we got here, then must have previously been ( S or SI ) + suggested_desig.VALID
                # As that didn't work, let's just force suggested_desig.VALID = False
                # Then when we re-run, it will go into the ( S or SI ) + speculative-search route above
                #
                # NB
                # *** *** ***      recursive function call     *** *** ***
                #
                self.suggested_desig = suggested_desig(False, self.suggested_desig[1])
                return self.tracklet_processing_B____Decide_if_and_how_to_fit(db)
                
            else:
                
                # If we got here, then the orbit-fit did not work
                # But recall that
                # (a) we cannot be just I (ITF-subset), as they don't get orbit-fit
                # (b) we cannot be S or SII (they are above)
                # (c) we must have some overlap (similarity group) with
                #     observations of previously DESIGNATED objects
                #     [D / DI / DS ]
                #
                # As such, I think it's now OK to officially set this
                # tracklet as being unselectable.
                # ...
                # But I feel that this needs clarification.
                # All of the previous steps have been based around
                # the new tracklet, and using it to calculate overlap, etc,
                # and ensure there are some new "primary observations" that
                # are work considering for orbit-fit as part of a designation.
                # Here we have established that this [D / DI / DS] tracklet
                # does *NOT* work.
                # So I believe that we can do not want to waste out time in future
                # on this tracklet.
                #
                # But what about the constituent observations? Do we want to allow
                # any of them to be selected and/or allow them to be primary-observations
                # in a group ?
                #
                self.assign_to_UNSELECTABLE(db)
                
                
        # Terminate with checks
        self.terminate_processing(db)
        result_dict = {'FINISHED':True }
        return result_dict

    def assign_to_DESIGNATED(self,db,designation):
        '''
        Tracklet is being assigned to DESIGNATED
        Assumes that previous checks have been done & that
        the tracklet really belongs in DESIGNATED
        
        NB: Probably need to do something else
         - e.g. set "desig" flag on consistituent observations
        
        '''
        for ObsID,obs  in self.observations.items():
            # Put it in the DESIGNATED table
            db.DESIGNATED[ObsID] = True
            # Make sure it knows its own designation
            self.observations[ObsID].desig = designation
            # Ensure it's not in the ITF
            if ObsID in db.ITF:
                del db.ITF[ObsID]
            
    def assign_to_UNSELECTABLE(self,db):
        '''
        Perhaps we need a deleted table / status : TBD
        '''
        for ObsID,obs  in self.observations.items():
            db.UNSELECTABLE[ObsID] = True
            # Ensure it's not in the ITF
            if ObsID in db.ITF:
                del db.ITF[ObsID]
            # Ensure its not in the DESIGNATED table
            if ObsID in db.DESIGNATED:
                del db.DESIGNATED[ObsID]
            # Ensure it's not confused about its own identity
            self.observations[ObsID].desig = None
            
    def assign_to_ITF(self,db):
        '''
        Tracklet is being assigned to the ITF
        Assumes that previous checks have been done & that either ...
        (i) the tracklet is just a subset of other ITF tracklet
        (ii) nothing could be done to match the tracklet to anything else
        (iii) ...
        '''
        for ObsID,obs  in self.observations.items():
            # Put it in the ITF table
            db.ITF[ObsID] = True
            # Ensure its not in the DESIGNATED table
            if ObsID in db.DESIGNATED:
                del db.DESIGNATED[ObsID]
            # Ensure it's not confused about its own identity
            self.observations[ObsID].desig = None
            
    def terminate_processing(self, db):
        '''
        In real life, some further steps may be required to properly
        populate the db & make other logical checks / calculations
        
        And we might want to change some kind of processing flag
        to show that processing is complete
        
        For this developmental sketch, perhaps nothing much is needed
        '''
        for ObsID,obs  in self.observations.items():
        
            # Here I am checking that each observation gets put into one and only one destination "table"
            # - I.e. it has to be assigned to DESIGNATED, ITF or DELETED
            #in_destinations = [ObsID in db.ITF[ObsID], ObsID in db.DELETED[ObsID], ObsID in db.DESIGNATED[ObsID] ]
            #assert len( [ _ for _ in in_destinations if _ ]) == 1 , f'Incorrect number of destination counts : {in_destinations} '
            
            # Here I am adding a flag to signify processing is complete
            self.observations[ObsID].PROCESSING_COMPLETE = True
            
  
            
    def categorize_overlap(self, db ):
        '''
        Categorization of overlap for entire tracklet
        This compares the overlap for each of the observations with their respective "similarilty-groups"
        
        returns (& sets self.overlap_category):
        --------
        overlap_category : STRING
         - overlap_category is in ['SINGLES', 'DESIGNATED','DESIGNATED+SINGLE', 'DESIGNATED+ITF', 'SINGLE+ITF', 'ITF']
         - 'SINGLES' => No overlap at all
         - 'DESIGNATED' => All obs overlap with previously submitted obs of designated objects
         - 'DESIGNATED+SINGLE' => Mix of SINGLES and DESIGNATED
         - 'DESIGNATED+ITF' => Mix of DESIGNATED and ITF (or perhaps DESIGNATED and SINGLES and ITF)
         - 'SINGLE+ITF' => Mix of SINGLES and ITF
         - 'ITF' => ll obs overlap with previously submitted obs that are in the ITF

        '''
        # Default values ...
        SELECTABLE = SINGLE = DESIGNATED = ITF = False

        # For each observation, use the *categorize_similarity_group_for_observation* function to
        # work out if there is some overlap, and if so, what it overlaps with
        overlaps, desigs, itf_tracklets = [],[],[]
        for obs in self.observations.values():
        
            #print('obs.__dict__', obs.__dict__)
            #print()
            #print(obs.SimilarityGroupID)
            #print()
            #   print('db.OBSGROUPS', type(db.OBSGROUPS), db.OBSGROUPS.keys())
        
            OG = db.OBSGROUPS[obs.SimilarityGroupID]
            
            overlaps.append( OG.category )
            if OG.desig is not None:
                desigs.append( OG.desig )
            if OG.TrackletIDs is not None:
                itf_tracklets.extend( OG.TrackletIDs )

        # Categorization of overlap for entire tracklet
        # I find this complicated to think about, so I'm going to try and be very clear in the layout of my logic
        #
        #
        # (0) Unselectable Tracklet
        #  - We are not in the business of subdividing tracklets
        #  - If any of the component observations are unselectable, then so is the entire tracklet
        if -1 not in overlaps:
            SELECTABLE = True
            
            # (A) Completely disjoint/all-singles: no overlap with known observations
            if     set(overlaps) == {0} :
                SINGLE = True
            # (B) All observations overlap only with designated objects
            elif   set(overlaps) == {1} :
                DESIGNATED = True
            # (C) Some observations overlap with designated objects AND the rest are SINGLE
            elif   set(overlaps) == {0,1} :
                DESIGNATED=SINGLE=True
            # (D) Some observations overlap with designated objects AND some overlap with ITF tracklets
            #     Not bothered about whether any are single are not.
            elif   set(overlaps) == {0,1,2}:
                DESIGNATED=SINGLE=ITF=True
            elif   set(overlaps) == {1,2}  :
                DESIGNATED=ITF=True
            # (E) Some observations overlap with ITF tracklets AND some are SINGLE
            elif   set(overlaps) == {0,2} :
                SINGLE=ITF=True
            # (F) All observations overlap only with ITF tracklets
            elif   set(overlaps) == {2} :
                ITF=True
            else:
                assert False, 'Should not see this message: poor categorization'

            assert not (SINGLE == DESIGNATED == ITF == False) , 'Nothing was set in categorize_overlap() '

        # Store overall category data
        self.SELECTABLE   = SELECTABLE
        self.overlap_category = overlap_category(SINGLE , DESIGNATED , ITF)
        
        # Record any overlap with designated objects
        if DESIGNATED:
            desigs = list(set([d for d in desigs if d != None]))
            MULTIPLE = True if len(desigs) > 1 else False
            self.overlap_desig = overlap_desig(MULTIPLE , desigs)
            
        # Record any overlap with ITF tracklets
        if ITF:
            itf_tracklets = list(set(itf_tracklets))
            MULTIPLE = True if len(itf_tracklets) > 1 else False
            self.overlap_itf = overlap_itf(MULTIPLE , itf_tracklets)


        return self.overlap_category, self.overlap_desig, self.overlap_itf


    
