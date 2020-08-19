"""Reactive component for SEIR intercity model

This script is meant to observe certain CouchDB database 
and react to any changes in the db appropriately. The 
script should watch for new experiments created in the 
'parameters' database and run the model with new parameter
as soon as a change is observed. 

A function to save the new state after running an 
experiment is also included herein.

THIS SCRIPT IS NOT ASYNCHRONOUS. THE OBSERVER IS A BLOCKING CODE."""

# Import required libraries
from pycouchdb.feedreader import BaseFeedReader
from datetime import datetime
import pycouchdb as pcdb
import pprint

# Define some constants that will be used throughout the script
# TODO: Implement better authentication strategy
SERVER_URL       = 'http://admin:testpassword@localhost:5984'
PARAM_DB_NAME    = 'intercity-seir-model-params'
STATE_DB_NAME    = 'intercity-seir-model-states'
MODEL_IDENTIFIER = 'intercity-seir-model'

# Enable easier debugging in development environment
ENV = 'DEV'

# Create server and two database objects
server           = pcdb.Server(SERVER_URL)
param_db         = server.database(PARAM_DB_NAME)
state_db         = server.database(STATE_DB_NAME)

# Useful in debugging
pp = pprint.PrettyPrinter(indent=3)

class ParameterWatcher(BaseFeedReader):
    """Implementation of BaseFeedReader that observes for 
    changes in the database and triggers appropriate action."""
    
    # 'seq 'is used for storing sequence id for last revision.
    # This is useful to avoid getting full list of all changes 
    # from the beginning.
    seq = ''
    
    def __init__(self):
        try: # get the latest sequence id to watch changes 'since'
            with open('latest_seq.txt', 'r') as f:
                self.seq = f.read()
                
        except FileNotFoundError:
            # Don't worry about this. 
            # The file will be created on first change.
            pass 
    
    def on_message(self, message):
        try:
            if (self.seq == '') | (self.seq != message['seq']):
                # We have a new change since last sequence Id
                with open('latest_seq.txt', 'w') as f:
                    # save new sequence id everywhere required
                    self.seq = message['seq']
                    f.write(self.seq)
        
            # If the change observed is not a deletion
            if 'deleted' not in message.keys():
                new_params = self._get_changed_doc(message['id'], message['changes']) 
                
                # TODO: interface with the actual model
                # TODO: Use the new parameters to run inference on the model 
                # TODO: Save the resulting model state to state_db
        
        except KeyError:
            # this check is necessary because if for some reason, 
            # the connection closes, the message sent will not have 
            # the keys 'seq', 'id' and 'changes'. 
            # We will just 'pass 'this block.
            pass            
      
    def _get_changed_doc(self, doc_id, revisions):
        doc = param_db.get(doc_id)
        if ENV == 'DEV':
            pp.pprint(doc)
            
        return doc
    
    def _add_new_experiment_state(self, exp_dict):    
        """Add new state in the db after running the experiment.
        
        Parameter
        ---------
        exp_dict: Experiment's result as a dictionary"""
        
        # Make sure these following keys exist!
        assert 'model_identifier' in exp_dict.keys()
        assert 'state' in exp_dict.keys()
        assert 'exp_version' in exp_dict.keys()
        
        assert 'S' in exp_dict['state'].keys()
        assert 'E' in exp_dict['state'].keys()
        assert 'Iu' in exp_dict['state'].keys()
        assert 'Ir' in exp_dict['state'].keys()
        
        if 'exp_date' not in exp_dict.keys():
            exp_dict['exp_date'] = datetime.today().strftime('%m-%d-%Y')        
        
        result = state_db.save(exp_dict) # save the result state
        assert '_id' in result.keys() # make sure the save operation succeded
        
        return result['_id']        
    
    def on_close(self):
        print('FeedReader ended')
        server.close()
        
        
def start_watch():
    paramWatcher = ParameterWatcher()
    
    param_db.changes_feed(
        paramWatcher, 
        heartbeat=1000,     # check if the connection is alive every 10s
        feed='continuous',
        since = None if paramWatcher.seq == '' else paramWatcher.seq
    )


if __name__ == '__main__':
    while (True):
        start_watch()
        # ideally, the below codes should never get executed
        # because the start_watch function is supposed to 
        # run till eternity.
        print('Connection Lost. Watching again.')
