'''
MJP 2020_08_20

The classes in "processing" focus on the functions significantly
beyond the steps required to do the initial filing.

We are now moving into the area of down-stream processing,
orbit-fitting, etc

As such most/all of the processing functions in this module
are basically stub-functions / pseudo-code

'''
# -------------------------------------------------------------
# Third Party Imports
# -------------------------------------------------------------
import numpy as np ; np.random.seed(0)
from collections import namedtuple

# -------------------------------------------------------------
# Some named tuples used within Tracklet class
# -------------------------------------------------------------
suggested_itf    = namedtuple('suggested_itf',    ['MULTIPLE','TrackletIDList'])

def attempt_to_link_multiple_overlap(tracklet):
    '''
    May want / need to deal with tracklets whose
    constituent observations overlap multiple designated objects
    
    Easiest is just to automatically fail, and subsequently assign
    the tracklet to UNSELECTABLE
    '''
    return {'PASS': False }

def speculative_search(tracklet, db):
    '''
    This is expected to encompass
    (a) checkID-type approaches
     - check known orbits against this tracklet
    (b) pyTrax-type approaches
     - check ITF tracklets against this tracklet
    
    For this developmental / psuedo-code, I will just
    randomly assign a result
    '''
    print(" *** speculative_search *** ")
    # (1) Ignore the possibility of checkID matches
    #    => Don't bother populating "suggested_desig"
    
    # (2) Pretend that pyTrax has run, and assign
    # a random chance of success, and then subsequently,
    # randomly assign an ITF tracklet
    result_dict = { 'PASSED':  True if np.random.random() > 0.95 and list(db.ITF.keys()) else False }

    # (3) Populate other necessary quantities ...
    if result_dict['PASSED'] :
    
        # Instead of finding an ITF tracklet with a consistent motion,
        # just randomly choose one for the sake of development
        randomObsID = np.random.choice( list(db.ITF.keys()) )
        print('randomObsID=',randomObsID)

        # Find the TrackletID of that selected observation
        for b in db.BATCHES.values():
            for t in b.tracklets.values():
                for o in t.observations.values():
                    if o.ObsID == randomObsID:
                        TrackletID = o.TrackletID
                        break
        
        # Populating the suggested_itf namedtuple with a single TrackletID
        tracklet.suggested_itf = suggested_itf(False, [TrackletID])
        
    return result_dict
    
def comprehensive_check_and_orbitfit(tracklet):
    '''

    
    Some initial ideas related to this can be found in ...
    https://drive.google.com/file/d/1QqseCpV7PedW341iKPiv447uVElefs93/view?usp=sharing

    Code would need to ...
    # Collect necessary observations
    # - From any associated designated / itf / or the tracklet itself
    # Run the fit
    # Evaluate the fit
    # Populate a standard dictionary with results
    # Update any tracklet attributes as appropriate
    
    For this developmental / psuedo-code, I will just
    randomly assign a result (skewed towards assuming the
    fit worked)
    
    '''
    # (0) Set default quantities in results_dict ...
    result_dict = { 'PASSED' : False ,
                    'designation' : None,
                    'other_TrackletIDs' : [] }

    # (1) Pretend an orbit fit has run ...
    if np.random.random() > 0.05 : result_dict['PASSED']=True

    # (2) Populate other necessary quantities ...
    if result_dict['PASSED'] :
    
        # (2a) Get the deignation out of the supplied structures
        if tracklet.suggested_desig.DESIG is not None :
            result_dict['designation'] = tracklet.suggested_desig.DESIG
        elif tracklet.overlap_desig is not None :
            result_dict['designation'] = tracklet.overlap_desig.DESIGLIST[0]
        else:
            # might only have suggest itf ...
            pass
        
        # (2b) Get the ITF tracklet IDs out of the supplied structures
        # NB
        #   If this were a real fit, the tracklet ideas would not be simply
        #   "passed-through", but instead, only a subset of trackletIDs
        #   would be selected *if* they fitted the orbit 
        if tracklet.overlap_itf is not None :
            result_dict['other_TrackletIDs'].extend( tracklet.overlap_itf.TrackletIDList )
        if tracklet.suggested_itf is not None :
            result_dict['other_TrackletIDs'].extend( tracklet.suggested_itf.TrackletIDList )

    return result_dict
