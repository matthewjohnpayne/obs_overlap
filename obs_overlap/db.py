'''
MJP 2020_08_19

I was going to code this up in sqlite
But I decided that would take too much time, and distract
from the main point of trying to clarify the logic.

So this is just some classes to help me quickly mimic the main attributes

'''

# -------------------------------------------------------------
# Third Party Imports
# -------------------------------------------------------------
#import sqlite3


# -------------------------------------------------------------
# These classes act like DB-ID generators
# -------------------------------------------------------------
class DB_ID:
    ''' Class that mimics getting the next ID from a database'''
    total = -1

    @classmethod
    def get_next_from_db(self,):
        self.total += 1
        return self.total
        
class BatchID(DB_ID):
    total = -1
class TrackletID(DB_ID):
    total = -1
class AcceptedObsID(DB_ID):
    total = -1
class SimilarityGroupID(DB_ID):
    total = -1
class DesignatedObsID(DB_ID):
    total = -1
class ITFObsID(DB_ID):
    total = -1

# -------------------------------------------------------------
# This class acts like a set of DB tables
# -------------------------------------------------------------
class DB():
    def __init__(self,):
        self.BATCHES    = []
        self.TRACKLETS  = []
        self.ACCEPTED   = []
        self.OBSGROUPS  = []
        self.DESIGNATED = []
        self.ITF        = []

