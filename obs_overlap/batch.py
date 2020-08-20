'''
MJP 2020_08_19
'''
# -------------------------------------------------------------
# Third Party Imports
# -------------------------------------------------------------
import dateutil.parser

# -------------------------------------------------------------
# Local Imports
# -------------------------------------------------------------
from db import BatchID

# -------------------------------------------------------------
# Batch Class <==> Batch Details Table
# -------------------------------------------------------------
class Batch():
    '''
    Real batches will obviously need more attributes than this
    This is just the subset I needed to get my code working
    
    N.B.
    "Actor" is intended to be a concept to allow for the assignment
    of unique (permanent?) IDs to submitting individuals / groups of
    individuals. Something like a collection of individual user IDs ?
    
    '''
    def __init__(self,SubmissionTime, ActorID, Tracklets, db):

        # Generate a unique ID (as if from db)
        self.BatchID            = BatchID.get_next_from_db()

        # Batch-level data
        self.SubmissionTime     = dateutil.parser.isoparse(SubmissionTime)
        self.ActorID            = ActorID
        
        # Store contained tracklets in a dictionary structure
        self.tracklets          = {t.TrackletID : t for t in Tracklets}

        # Tell the contained tracklets (and their observations) ...
        # ...what their parent BatchID is
        for TrackletID in self.tracklets:
            self.tracklets[TrackletID].BatchID = self.BatchID
            for ObsID in self.tracklets[TrackletID].observations:
                self.tracklets[TrackletID].observations[ObsID].BatchID = self.BatchID

        # Store self in db
        db.BATCHES[self.BatchID] = self
