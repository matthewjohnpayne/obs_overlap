
# -------------------------------------------------------------
# Third Party Imports
# -------------------------------------------------------------
import sys, os

# -------------------------------------------------------------
# Local Imports
# -------------------------------------------------------------
sys.path.append(os.path.join(
                    os.path.dirname(
                        os.path.dirname(
                            os.path.realpath(__file__))), 'obs_overlap'))
print(os.path.join(
        os.path.dirname(
            os.path.dirname(
                os.path.realpath(__file__))), 'obs_overlap'))
from db import DB
from obs import Obs
import obs_group
from batch import Batch
from tracklet import Tracklet


def gen_input_data(db):
    # A list of synthetic observations organized into Tracklets submitted within Batches
    #
    #         SubmissionTime           , ActorID,
    #
    #                   RA          Dec             ObsTime                  ObsCode,  Replaces, pubStat,desig, Deleted
    #
    # The Batch, Tracklet, and Obs classes below are just being initialized
    # - Very little logic / calculation is being done
    # - It's mainly just declaring variables within each class.
    

    yield Batch('2020-04-20T14:32:16.458361' , 'A0' ,
        [Tracklet([ Obs(20.0,        30.0,       '2020-03-20T14:32:16.458361', '568',   None ,  None ,  None ,    None , db), #0
                    Obs(20.1,        30.1,       '2020-03-20T15:32:16.458361', '568',   None ,  None ,  None ,    None , db),#1
                    Obs(20.2,        30.2,       '2020-03-20T16:32:16.458361', '568',   None ,  None ,  None ,    None , db),#2
                ],
                db)
        ],
        db)
        
    yield Batch('2020-04-20T15:32:16.458361' , 'A1' ,
        [Tracklet([ Obs(10.,         20.,        '2020-03-20T14:32:16.458361', 'F51',   None ,  None ,  None ,    None , db),#3
                    Obs(11.,         21.,        '2020-03-20T14:32:16.458361', 'F51',   None ,  None ,  None ,    None , db),#4
                    Obs(12.,         22.,        '2020-03-20T14:32:16.458361', 'F51',   None ,  None ,  None ,    None , db),#5
                ],
                db)
        ],
        db)
        
    yield Batch('2020-04-20T16:32:16.458361' , 'A0' ,
        [Tracklet([ Obs(20.01,       30.0,       '2020-03-20T14:32:16.458361', '568',   None ,  None ,  None ,    None , db),#6
                    Obs(20.11,       30.1,       '2020-03-20T15:32:16.458361', '568',   None ,  None ,  None ,    None , db),#7
                    Obs(20.21,       30.2,       '2020-03-20T16:32:16.458361', '568',   None ,  None ,  None ,    None , db),#8
                ],
                db)
        ],
        db)
        
    yield Batch('2020-04-20T17:32:16.458361' , 'A0' ,
        [Tracklet([ Obs(20.01,       30.0,       '2020-03-20T14:32:16.458361', '568',   0    ,  None ,  None ,    None , db),#9  <=> #0 (Replaces)
                    Obs(20.11,       30.1,       '2020-03-20T15:32:16.458361', '568',   1    ,  None ,  None ,    None , db),#10 <=> #1 (Replaces)
                    Obs(20.21,       30.2,       '2020-03-20T16:32:16.458361', '568',   2    ,  None ,  None ,    None , db),#11 <=> #2 (Replaces)
                ],
                db)
        ],
        db)
        
    yield Batch('2020-04-20T18:32:16.458361' , 'A3' ,
        [Tracklet([ Obs(40.,         30.,        '2020-03-20T14:32:16.458361', 'T12',   None ,  None ,  None ,    None , db),#12
                    Obs(50.,         30.,        '2020-03-20T14:32:16.458361', 'T12',   None ,  None ,  None ,    None , db),#13
                ],
                db)
        ],
        db)
        
    yield Batch('2020-04-20T19:32:16.458361' , 'A4' ,
        [Tracklet([ Obs(40.001,      30.001,     '2020-03-20T14:32:17.458361', '568',   None ,  None ,  None ,    None , db),#14 <=> #12 (Near-Dup)
                    Obs(50.001,      30.001,     '2020-03-20T14:32:17.458361', '568',   None ,  None ,  None ,    None , db) #15 <=> #13 (Near-Dup)
                ],
                db)
        ],
        db)
        
    yield Batch('2020-04-20T20:32:16.458361' , 'A0' ,
        [Tracklet([ Obs(20.02,       30.0,       '2020-03-20T14:32:16.458361', '568',   None ,  None ,  None ,    None , db),#16
                    Obs(20.12,       30.1,       '2020-03-20T15:32:16.458361', '568',   None ,  None ,  None ,    None , db),#17
                    Obs(20.22,       30.2,       '2020-03-20T16:32:16.458361', '568',   None ,  None ,  None ,    None , db),#18
                    Obs(20.32,       30.3,       '2020-03-20T17:32:16.458361', '568',   None ,  None ,  None ,    None , db),#19
                ],
                db),
         Tracklet([ Obs(25.05,       35.0,       '2020-03-20T14:32:16.458361', '568',   None ,  None ,  None ,    True , db),#20  *Deleted
                    Obs(25.15,       35.1,       '2020-03-20T15:32:16.458361', '568',   None ,  None ,  None ,    True , db),#21  *Deleted
                    Obs(25.25,       35.2,       '2020-03-20T16:32:16.458361', '568',   None ,  None ,  None ,    True , db),#22  *Deleted
                ],
                db)
        ],
        db)
    

# -------------------------------------------------------------
# Test run
# -------------------------------------------------------------
if __name__ == '__main__':

    
    # Create a "DB" (just a class)
    db = DB()
    print(db.BATCHES.items())

    # Iterate through the input data
    # - We'll also print a bunch of data to illustrate progress
    for b in gen_input_data(db):
        print(f'BatchID={b.BatchID}')

        for TrackletID,t in b.tracklets.items():
            print(f'\t TrackletID={t.TrackletID}')

            # Do OBSERVATION-level processing ...
            # ~~~ I.e. Processing that would be done at the point of ingestion into
            #          the ACCEPTED OBSERVATION table
            for ObsID,o in t.observations.items():
                print(f'\t\t ObsID={o.ObsID}')

                # Use the functionality in Obs class to ...
                #  (i) look for "similar" observations
                # (ii) create an ObsGroup ...
                
                # We will need all observations known to this point
                # Obviously my data structures could be nicer ...
                known_obs = []
                for bID, bb in db.BATCHES.items():
                    for tID, tt in bb.tracklets.items():
                        known_obs.extend( list(tt.observations.values() ) )
                
                # Work out the similarity group for the new observation
                similar_obs = o.find_similar( o ,known_obs )

                # Work out the credit & seleted status for the ObsGroup
                SimilarityGroupID = obs_group.get_SimilarityGroupID(similar_obs)
                
                # Take care to assign the SimilarityGroupID to all of the obs in grouped_obs
                for _ in similar_obs:
                    db.BATCHES[_.BatchID].tracklets[_.TrackletID].observations[_.ObsID].SimilarityGroupID = SimilarityGroupID

                print(f'\t\t\t SimilarityGroupID={ SimilarityGroupID }')
                print(f'\t\t\t ObsIDs of similar_obs={ [ _.ObsID for _ in similar_obs] }')

                # Select the credit & primary observation from the similarity group
                credit_ObsID, primary_ObsID = obs_group.assign_status(similar_obs, db)
                print(f'\t\t\t credit_ObsID={credit_ObsID} primary_ObsID={primary_ObsID}')

                # At present this credit_ObsID, primary_ObsID is not being used / stored
                # Could store in a separate object / table
                # Could store as booleans against the obs


            # Now do the TRACKLET-level processing
            # I.e. This requires that observation-level & observation-group
            #      quantities be calculated
            
            # Establish the degree of tracklet overlap
            t.categorize_overlap( db )
            print(f't.overlap_category={t.overlap_category}')
        
            # Decide what processing needs to be done on the tracklet.
            # This will depend on the degree of overlap between the
            # observations in the tracklet and the previously-known observations.
            t.tracklet_processing_blackbox( {} , db)
        
    
