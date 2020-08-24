'''
MJP 2020_08_20

The classes in "processing" focus on the functions significantly
beyond the steps required to do the initial filing.

We are now moving into the area of down-stream processing,
orbit-fitting, etc

'''

def comprehensive_check_and_orbitfit(tracklet):
    return {'PASS':True}

def comprehensive_check_and_orbitfit_WIP(tracklet):
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
    # Types of tracklet that this routine claims to be competant to process
    assert tracklet.overlap_category in ['SINGLES','DESIGNATED', 'DESIGNATED+SINGLE', 'DESIGNATED+ITF','SINGLE+ITF', 'ITF']
    
    # Do some form of name comprehension similar to "processobs"
    # N.B. Irrespective of overlap category ['SINGLES' , ... 'SINGLE+ITF', ... or even 'ITF' ]
    # ... the tracklet may still come with a submitter-supplied designation
    designation_dict = do_name_comprehension(tracklet)
    
    # If we have a designated object to work with, get the previously known observations
    if tracklet.overlap_category in ['DESIGNATED', 'DESIGNATED+SINGLE', 'DESIGNATED+ITF'] or \
        designation_dict['PASSED']:
            designated_obs = get_previously_known_designated_observations(designation_dict)
    else :
        designated_obs = []
        
    # If we have some overlap with ITF data, get the observations
    if tracklet.overlap_category in ['DESIGNATED+ITF','SINGLE+ITF'] :
        itf_tracklets = get_overlapped_itf_tracklets( tracklet )
    else:
        itf_tracklets = []
        
    # If we have 'SINGLE+ITF', then run speculative search (~checkID)
    if tracklet.overlap_category == 'SINGLE+ITF':
        search_evaluation_dict = perform_speculative_search(    [tracklet] ,
                                                                itf_tracklets )
        if search_evaluation_dict['PASSED']:
            designated_tracklets = get_previously_known_designated_observations(search_evaluation_dict)
        else:
            tracklet.assign_to_ITF()
            tracklet.terminate_processing()
    
    # If we get this far, then either 'SINGLE+ITF' was success in perform_speculative_search, or
    # we have any of the other 4 : 'SINGLES','DESIGNATED', 'DESIGNATED+SINGLE', 'DESIGNATED+ITF'
    #
    # NB As written, designated_obs and/or itf_obs might be empty at this point
    # => Might have *only* obs from new tracklet
    # => perform_and_evaluate_orbit_fit needs to be able to cope with this.
    #
    # Run orbit-fitting and evaluation package
    orbfit_evaluation_dict = perform_and_evaluate_orbit_fit(    [tracklet] ,
                                                                designated_tracklets,
                                                                itf_tracklets )

    # If the orbit fit worked ...
    if orbfit_evaluation_dict['PASSED'] :
        tracklet.assign_to_DESIGNATED(designation_dict['designation'])
        
        # If any ITF observations were involved in this successful fit,
        # then remove from ITF & reassign to DESIGNATED
        if tracklet.overlap_category in ['SINGLE+ITF', 'DESIGNATED+ITF'] :
            for itf_tracklet in itf_tracklets:
                itf_tracklet.assign_to_DESIGNATED(designation_dict['designation'])
