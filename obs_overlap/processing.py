'''
MJP 2020_08_20

The classes in "processing" focus on the functions significantly
beyond the steps required to do the initial filing.

We are now moving into the area of down-stream processing,
orbit-fitting, etc

'''
importt numpy
def attempt_to_link_multiple_overlap(tracklet):
    '''
    May want / need to deal with tracklets whose
    constituent observations overlap multiple designated objects
    
    Easiest is just to automatically fail, and subsequently assign
    the tracklet to UNSELECTABLE
    '''
    return {'PASS': False }

def speculative_search(tracklet):
    '''
    This is expected to encompass
    (a) checkID-type approaches
     - check known orbits against this tracklet
    (b) pyTrax-type approaches
     - check ITF tracklets against this tracklet
    
    For this developmental / psuedo-code, I will just
    randomly assign a result
    '''
    # (1) Ignore the possibility of checkID matches
    
    # (2) Pretend that pyTrax has run, and assign
    # a random chance of success, and then subsequently,
    # randomly assign an ITF tracklet
    result_dict{ 'PASSED':  = True if np.random.random() > 0.5 else False }
    
    # (3) Populate other necessary quantities ...
    if result_dict['PASSED'] :
        randomObsID = np.random.choice( list(db.ITF.keys()) )
        TrackletID  = ...
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

    # (1) Pretend an orbit fit has run ...
    result_dict{ 'PASSED': True if np.random.random() > 0.05 else False }

    # (2) Populate other necessary quantities ...
    if result_dict['PASSED'] :
        pass
        
    return result_dict
