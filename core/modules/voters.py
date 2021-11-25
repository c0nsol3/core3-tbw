from utility.utility import Utility

class Voters():
    def __init__(self, config, sql):
        self.config = config
        self.sql = sql

    def process_whitelist(self, voter_balances):
        adjusted_voters = {}
        for k, v in voter_balances.items():
            if k in self.config.whitelist_address:
                adjusted_voters[k] = v
        
        return adjusted_voters

    
    def process_blacklist(self, voter_balances):
        adjusted_voters = {}
        for k, v in voter_balances.items():
            if k not in self.config.blacklist_address:
                adjusted_voters[k] = v
        
        return adjusted_voters
    
    
    def process_voter_cap(self, voter_balances):
        adjusted_voters = {}
        
        # no voter cap
        if self.config.voter_cap == 0:
            adjusted_voters = voter_balances
        else:
            # get max cap
            max_votes = int(self.config.voter_cap * self.config.atomic)
            for k, v in voter_balances.items():
                if v > max_votes:
                    adjusted_voters[k] = max_votes
                else:
                    adjusted_voters[k] = v
        
        return adjusted_voters
    
    
    def process_voter_min(self, voter_balances):
        pass
    
    
    def process_anti_dilution(self, voter_balances):
        pass
