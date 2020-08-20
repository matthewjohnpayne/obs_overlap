'''
MJP 2020_08_20

The classes in "processing" focus on the functions significantly
beyond the steps required to do the initial filing.

We are now moving into the area of down-stream processing,
orbit-fitting, etc

'''

def comprehensive_check_and_orbitfit(tracklet):
    '''
    The highest level functionality I'm willing to consider ...
    A conceptual end-to-end function that will do *all*
    necessary orbit-fitting, checking, etc etc etc
    
    As written, I am thinking of it being focussed around the
    task of deciding whether an incoming tracklet fits with some
    known object
    
    Some initial ideas behind this can be found in ...
    https://drive.google.com/file/d/1QqseCpV7PedW341iKPiv447uVElefs93/view?usp=sharing

    '''
    # Types of tracklet that this routine claims to be competant to
    # deal with
    assert tracklet.overlap_category in ['SINGLES','DESIGNATED', 'DESIGNATED+SINGLE', 'DESIGNATED+ITF','SINGLE+ITF']
    
    # Do some form of name comprehension similar to "processobs"
    designation_dict = do_name_comprehension(tracklet)
    
    # If we have a designated object to work with, get the previously known observations
    if tracklet.overlap_category in ['SINGLES','DESIGNATED', 'DESIGNATED+SINGLE', 'DESIGNATED+ITF'] and \
     designation_dict['PASSED']
        designated_obs = get_previously_known_designated_observations(designation_dict)
    else :
        designated_obs = []
        
    # If we have some overlap with ITF data, get the observations
    if tracklet.overlap_category in ['DESIGNATED+ITF','SINGLE+ITF'] :
        itf_obs = get_previously_known_itf_observations( tracklet )
    else:
        itf_obs = []
        
    # Run orbit-fitting and evaluation package
    orbfit_evaluation_dict = perform_and_evaluate_orbit_fit(    list(tracklet.observations.values()) ,
                                                                designated_obs,
                                                                itf_obs )

    pass
