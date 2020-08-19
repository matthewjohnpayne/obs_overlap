
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


# -------------------------------------------------------------
# Test run
# -------------------------------------------------------------
if __name__ == '__main__':

    # A list of synthetic observations organized into Trackleta submitted within Batches
    #
    #         SubmissionTime           , ActorID,
    #
    #                   RA          Dec             ObsTime                  ObsCode,  Replaces,trkID, pubStat,desig, Deleted
    #
    # The Batch, Tracklet, and Obs classes below are just being initialized
    # - Very little logic / calculation is being done
    # - It's mainly just declaring variables within each class.
    input_data = [
    
    (   Batch('2020-04-20T14:32:16.458361' , 'A0' ),
        [Tracklet([ Obs(20.0,        30.0,       '2020-03-20T14:32:16.458361', '568',   None , None,  None ,  None ,    None ), #0
                    Obs(20.1,        30.1,       '2020-03-20T15:32:16.458361', '568',   None , None,  None ,  None ,    None ),#1
                    Obs(20.2,        30.2,       '2020-03-20T16:32:16.458361', '568',   None , None,  None ,  None ,    None ),#2
                ])
        ]),
    (   Batch('2020-04-20T15:32:16.458361' , 'A1' ),
        [Tracklet([ Obs(10.,         20.,        '2020-03-20T14:32:16.458361', 'F51',   None , None,  None ,  None ,    None ),#3
                    Obs(11.,         21.,        '2020-03-20T14:32:16.458361', 'F51',   None , None,  None ,  None ,    None ),#4
                    Obs(12.,         22.,        '2020-03-20T14:32:16.458361', 'F51',   None , None,  None ,  None ,    None ),#5
                ])
        ]),
    (   Batch('2020-04-20T16:32:16.458361' , 'A0' ),
        [Tracklet([ Obs(20.01,       30.0,       '2020-03-20T14:32:16.458361', '568',   None , None,  None ,  None ,    None ),#6
                    Obs(20.11,       30.1,       '2020-03-20T15:32:16.458361', '568',   None , None,  None ,  None ,    None ),#7
                    Obs(20.21,       30.2,       '2020-03-20T16:32:16.458361', '568',   None , None,  None ,  None ,    None ),#8
                ])
        ]),
    (   Batch('2020-04-20T17:32:16.458361' , 'A0' ),
        [Tracklet([ Obs(20.01,       30.0,       '2020-03-20T14:32:16.458361', '568',   0    , None,  None ,  None ,    None ),#9  <=> #0 (Replaces)
                    Obs(20.11,       30.1,       '2020-03-20T15:32:16.458361', '568',   1    , None,  None ,  None ,    None ),#10 <=> #1 (Replaces)
                    Obs(20.21,       30.2,       '2020-03-20T16:32:16.458361', '568',   2    , None,  None ,  None ,    None ),#11 <=> #2 (Replaces)
                ])
        ]),
    (   Batch('2020-04-20T18:32:16.458361' , 'A3' ),
        [Tracklet([ Obs(40.,         30.,        '2020-03-20T14:32:16.458361', 'T12',   None , None,  None ,  None ,    None ),#12
                    Obs(50.,         30.,        '2020-03-20T14:32:16.458361', 'T12',   None , None,  None ,  None ,    None ), #13
                ])
        ]),
    (   Batch('2020-04-20T19:32:16.458361' , 'A4' ),
        [Tracklet([ Obs(40.001,      30.001,     '2020-03-20T14:32:17.458361', '568',   None , None,  None ,  None ,    None ),#14 <=> #12 (Near-Dup)
                    Obs(50.001,      30.001,     '2020-03-20T14:32:17.458361', '568',   None , None,  None ,  None ,    None ) #15 <=> #13 (Near-Dup)
                ])
        ]),
    (   Batch('2020-04-20T20:32:16.458361' , 'A0' ),
        [Tracklet([ Obs(20.02,       30.0,       '2020-03-20T14:32:16.458361', '568',   None , None,  None ,  None ,    None ),#16
                    Obs(20.12,       30.1,       '2020-03-20T15:32:16.458361', '568',   None , None,  None ,  None ,    None ),#17
                    Obs(20.22,       30.2,       '2020-03-20T16:32:16.458361', '568',   None , None,  None ,  None ,    None ),#18
                    Obs(20.32,       30.3,       '2020-03-20T17:32:16.458361', '568',   None , None,  None ,  None ,    None ),#19
                ]),
         Tracklet([ Obs(25.05,       35.0,       '2020-03-20T14:32:16.458361', '568',   None , None,  None ,  None ,    True ),#20  *Deleted
                    Obs(25.15,       35.1,       '2020-03-20T15:32:16.458361', '568',   None , None,  None ,  None ,    True ),#21  *Deleted
                    Obs(25.25,       35.2,       '2020-03-20T16:32:16.458361', '568',   None , None,  None ,  None ,    True ),#22  *Deleted
                ])
        ]),
    ]

    # Create a "DB" (just a class)
    db = DB()
    
    # Now let's loop through the input data and start doing some calculations
    # - We'll also print a bunch of data to illustrate progress
    for b, tracklet_list in input_data:
        db.BATCHES.append(b)
        print(f'BatchID={db.BATCHES[-1].BatchID}')

        for t in tracklet_list:
            db.TRACKLETS.append(t)
            print(f'\t TrackletID={db.TRACKLETS[-1].TrackletID}')

            for ObsID,o in t.observations.items():
                
                # Use the functionality in Obs class to ...
                #  (i) look for "similar" observations
                # (ii) create an ObsGroup ...
            
                # Work out the similarity group for the new observation
                grouped_obs = o.find_similar( o , db.ACCEPTED)
                db.ACCEPTED.append(o)
                print(f'\t\t ObsID={db.ACCEPTED[-1].ObsID}')
                print(f'\t\t\t ObsIDs of grouped_obs={ [ _.ObsID for _ in grouped_obs] }')

                # Work out the credit & seleted status for the ObsGroup
                SimilarityGroupID = obs_group.get_SimilarityGroupID(grouped_obs)
                
                # Take care to assign the SimilarityGroupID to all of the obs in grouped_obs
                for _ in grouped_obs:
                    db.ACCEPTED[_.ObsID].SimilarityGroupID = SimilarityGroupID
                    print(f'\t\t\t\t  ObsID={_.ObsID}  SimilarityGroupID={_.SimilarityGroupID}')
                credit_ObsID, selected_ObsID = obs_group.assign_status(grouped_obs, db.BATCHES)
                print(f'credit_ObsID={credit_ObsID} selected_ObsID={selected_ObsID}')
                #DB.OBSGROUPS.append(new_obs)

            """

            # 
        
        for o in DB.ACCEPTED:
            print(o.__dict__)
        
        # Establish the degree of tracklet overlap
        #categorize_overlap( tracklet_observations , known_obs , destination_dict)
        """

        
    
