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
    def __init__(self,SubmissionTime, ActorID):

        self.BatchID            = BatchID.get_next_from_db()

        self.SubmissionTime     = dateutil.parser.isoparse(SubmissionTime)
        self.ActorID            = ActorID
        
        self.tracklets          = {}
        
    def associate_tracklet(tracklet):
        self.tracklets[tracklet.TrackletID] = tracklet


