obs_overlap 
- This code is intended to define the overall flow of logic / checks that I think might be required in order to check for duplicates / near-duplicates between submitted observations.
- It is written from the point of view of checking a "new" observation (labelled by an observation-ID, "target_obsID") against the collected mass of observations that would already be in an "accepted observations" table.
- It assumes that an ObsGroupID variable will be set to indicate which observations belong to the same observatitonal-group.
- It assumes a new ObsGroupID will only be generated if the "new" observation-ID does *not* share a group with anything else
- If there *are* multiple duplicate / near-duplicate observations, this implies some are already in the database, which implies they will already have assigned ObsGroupIDs which implied that all members of the group should be assigned the lowest extant ObsGroupID (there is a possibility that multiple ObsGroupIDs could be united by the arrival of a new observation that overlaps them both, but which did not themselves previously overlap).
- It's written using python-style logic, which will doubtless be better executed in a different manner when working on the database tables, but I just find this way of thinking easier...
-

test / execution
 - Running the code in the test directory (as below) will process a set of a dozen-or-so tracklets through the developed logic
 - There are (as yet) no formal tests, merely a print-out to screen demonstrating the fate of the processed tracklets 

> cd tests

> python3 test_obs_group_code.py 
